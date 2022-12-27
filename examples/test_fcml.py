import unittest

from edg import *
from .test_bldc import PowerOutConnector


class DiscreteMutlilevelBuckConverter(GeneratorBlock):
  """Flying capacitor multilevel buck converter. Trades more switches for smaller inductor size:
  for number of levels N, inductor value is reduced by a factor of (N-1)^2.
  2 levels is standard switching converter (1 pair of switches in a synchronous topology).
  Each additional level adds another switch pair.
  Even number of levels generally have good balancing, odd number of levels may have balancing issues.

  Controls are broken out at the top level, at logic level referenced to the converter ground.
  Requires both a power voltage source and gate drive voltage source.

  Instead of a target output voltage (since the output is controlled by external PWMs), this takes
  in operating duty ratios for component sizing. Current is calculated by current drawn at the output.

  Generates a bootstrap capacitor ladder to generate the gate drive voltages for each switch.
  Generates a gate driver for each switch pair, in normal operation each gate driver should be
  either be high or low (but not both or none).
  Generates a digital isolator for each gate driver that is offset from ground.
  """
  @init_in_parent
  def __init__(self, levels: IntLike, ratios: RangeLike, frequency: RangeLike, *,
               inductor_current_ripple: RangeLike, fet_rds: RangeLike = (0, 0.1)*Ohm):
    super().__init__()
    self.pwr_in = self.Port(VoltageSink.empty())
    self.pwr_out = self.Port(VoltageSource.empty())
    self.gnd = self.Port(Ground.empty(), [Common])

    self.pwr_gate = self.Port(VoltageSink.empty())
    self.pwms = self.Port(Vector(DigitalSink.empty()))

    self.frequency = self.ArgParameter(frequency)
    self.inductor_current_ripple = self.ArgParameter(inductor_current_ripple)
    self.fet_rds = self.ArgParameter(fet_rds)

    self.generator(self.generate, levels, ratios)

  def generate(self, levels: int, ratios: Range):
    assert levels >= 2, "levels must be 2 or more"
    self.power_path = self.Block(BuckConverterPowerPath(
      self.pwr_in.link().voltage, self.pwr_in.link().voltage * ratios, self.frequency,
      self.pwr_out.link().current_drawn, (0, 1.5)*Amp,
      inductor_current_ripple=self.inductor_current_ripple,
      dutycycle_limit=(0, 1)
    ))
    self.connect(self.power_path.pwr_in, self.pwr_in)
    self.connect(self.power_path.pwr_out, self.pwr_out)
    self.connect(self.power_path.gnd, self.gnd)

    self.driver = ElementDict[HalfBridgeDriver]()  # [0, levels-1)
    self.isolator = ElementDict[DigitalIsolator]()  # [1, levels-1), unneeded at 0
    self.low_fet = ElementDict[Fet]()  # [0, levels-1)
    self.high_fet = ElementDict[Fet]()
    self.flying_cap = ElementDict[Capacitor]()  # [1 ... levels-1), excluding main input cap
    self.boot_diode = ElementDict[Diode]()  # [1, 2*(levels-1)), associated with the powered FET
    self.boot_cap = ElementDict[Capacitor]()  # similar indexing to boot_diode

    fet_model = Fet.NFet(
      drain_voltage=self.pwr_in.link().voltage,
      drain_current=(0, self.power_path.peak_current),
      gate_voltage=self.pwr_gate.link().voltage,  # TODO account for boot diode drop
      rds_on=self.fet_rds
    )
    flying_cap_model = Capacitor(
      capacitance=1*uFarad(tol=0.2),  # TODO size cap
      voltage=self.pwr_in.link().voltage
    )

    low_prev = self.gnd
    high_prev = self.pwr_in
    low_boot_prev = self.pwr_gate
    high_boot_prev = None

    for level in range(levels - 1):
      self.low_fet[level] = low_fet = self.Block(fet_model)
      low_source = low_fet.source.adapt_to(VoltageSink())
      self.connect(low_prev, low_source)
      low_prev = low_fet.drain.adapt_to(VoltageSource())

      self.high_fet[level] = high_fet = self.Block(fet_model)
      if level == 0:  # this connects to pwr_in and needs a current draw model
        high_source_model = VoltageSink(current_draw=self.power_path.switch.link().current_drawn)
      else:
        high_source_model = VoltageSink()
      high_drain = high_fet.drain.adapt_to(high_source_model)
      self.connect(high_prev, high_drain)
      high_prev = high_fet.source.adapt_to(VoltageSource())

      if level > 0:  # generate flying cap, if not the main input cap
        self.flying_cap[level] = flying_cap = self.Block(flying_cap_model)
        self.connect(low_source, flying_cap.neg.adapt_to(VoltageSink()))
        self.connect(high_drain, flying_cap.pos.adapt_to(VoltageSink()))

    # TODO connect high_prev, which conflicts b/c it's VoltageSource as well
    self.connect(low_prev, self.power_path.switch)

    self.pwms.defined()  # allows structural generation, TODO remove me


class FcmlTest(JlcBoardTop):
  """FPGA + FCML (flying cpacitor multilevel converter) test circuit
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      self.conv = imp.Block(DiscreteMutlilevelBuckConverter(
        4, (0.15, 0.5), 100*kHertz(tol=0),
        inductor_current_ripple=(0.1, 2)*Amp
      ))
      self.conv_out = imp.Block(PowerOutConnector((0, 2)*Amp))
      self.connect(self.conv.pwr_in, self.vusb)
      self.connect(self.conv.pwr_out, self.conv_out.pwr)
    # TODO

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))
      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())
      self.connect(self.mcu.gpio.request_vector('pwm'), self.conv.pwms)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),  # TODO replace with FPGA
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class FcmlTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(FcmlTest)
