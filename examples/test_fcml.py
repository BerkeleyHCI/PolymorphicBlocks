import unittest
from typing import Optional

from edg import *
from .test_robotdriver import LipoConnector
from .test_bldc import PowerOutConnector, CompactKeystone5015


class MultilevelSwitchingCell(GeneratorBlock):
  """A switching cell for one level of a multilevel converter, consisting of a high FET,
  low FET, gate driver, isolator (if needed), and bootstrap circuit (for the gate driver).

  This is its own block to allow hierarchical replicate in layout.

  Current and voltage are provided via the ports.

  The first cell (closest to the power supply) is different in that:
  - it does not generate an isolator, since signals are already ground-referenced
  - it does not generate a low-side bootstrap diode and cap, since voltage is provided
  - it does not generate a flying capacitor on the input, since that is the input cap"""
  @init_in_parent
  def __init__(self, is_first: BoolLike = False, *,
               in_voltage: RangeLike, frequency: RangeLike, fet_rds: RangeLike):
    super().__init__()
    # in is generally towards the supply side, out is towards the inductor side
    self.low_in = self.Port(VoltageSink.empty())
    self.low_out = self.Port(VoltageSource.empty())
    self.low_boot_in = self.Port(VoltageSink.empty())  # bootstrap voltage for the prior cell, except if is_first
    self.low_boot_out = self.Port(VoltageSource.empty())  # bootstrap voltage for this cell
    self.high_in = self.Port(VoltageSink.empty())
    self.high_out = self.Port(VoltageSource.empty())
    # except for high boot they're reversed, out is towards the supply side
    self.high_boot_out = self.Port(VoltageSource.empty(), optional=True)
    self.high_boot_in = self.Port(VoltageSink.empty())

    # control signals
    self.gnd_ctl = self.Port(VoltageSink.empty())
    self.pwr_ctl = self.Port(VoltageSink.empty())
    self.low_pwm = self.Port(DigitalSink.empty())
    self.high_pwm = self.Port(DigitalSink.empty())

    self.in_voltage = self.ArgParameter(in_voltage)
    self.frequency = self.ArgParameter(frequency)
    self.fet_rds = self.ArgParameter(fet_rds)

    self.generator(self.generate, is_first, self.high_boot_out.is_connected())

  def generate(self, is_first: bool, high_boot_out_connected: bool):
    # power path
    fet_model = Fet.NFet(
      drain_voltage=self.in_voltage,
      drain_current=(0, self.high_out.link().current_drawn.upper()),
      gate_voltage=self.low_boot_out.link().voltage,  # TODO account for boot diode drop
      rds_on=self.fet_rds
    )
    self.low_fet = self.Block(fet_model)
    self.connect(self.low_fet.source.adapt_to(VoltageSink(
      current_draw=self.low_out.link().current_drawn
    )), self.low_in)
    self.connect(self.low_fet.drain.adapt_to(VoltageSource(
      voltage_out=self.low_in.link().voltage
    )), self.low_out)
    self.high_fet = self.Block(fet_model)
    self.connect(self.high_fet.drain.adapt_to(VoltageSink(
      current_draw=self.high_out.link().current_drawn
    )), self.high_in)
    self.connect(self.high_fet.source.adapt_to(VoltageSource(
      voltage_out=self.low_in.link().voltage
    )), self.high_out)

    # size the flying cap for max voltage change at max current
    # Q = C dv => C = I*t / dV
    MAX_FLYING_CAP_DV_PERCENT = 0.08
    capacitance = self.high_out.link().current_drawn.upper() / self.frequency.lower() / (self.in_voltage.upper() * MAX_FLYING_CAP_DV_PERCENT)
    self.cap = self.Block(Capacitor(  # flying cap
      capacitance=(capacitance, float('inf')*Farad),
      voltage=self.in_voltage
    ))
    self.connect(self.cap.neg.adapt_to(VoltageSink()), self.low_in)
    self.connect(self.cap.pos.adapt_to(VoltageSink()), self.high_in)

    # bootstrap path
    boot_diode_model = Diode(
      reverse_voltage=self.in_voltage + self.low_boot_in.link().voltage,  # upper bound
      current=(0, 0)*Amp,  # TODO model current draw, though it's probably negligibly small
      voltage_drop=(0, 0.6)*Volt  # arbitrary to limit gate voltage droop
    )
    boot_cap_model = Capacitor(
      capacitance=0.1*uFarad(tol=0.2),
      voltage=self.low_boot_in.link().voltage
    )
    if is_first:
      self.connect(self.low_boot_out, self.low_boot_in)
    else:
      self.low_boot_diode = self.Block(boot_diode_model)
      low_boot = self.low_boot_diode.cathode.adapt_to(VoltageSource(
        voltage_out=self.low_boot_in.link().voltage
      ))
      self.connect(self.low_boot_in, self.low_boot_diode.anode.adapt_to(VoltageSink(
        current_draw=low_boot.link().current_drawn
      )))
      self.connect(self.low_boot_out, low_boot)
      self.low_boot_cap = self.Block(boot_cap_model)
      self.connect(self.low_boot_cap.neg.adapt_to(VoltageSink()), self.low_in)
      self.connect(self.low_boot_cap.pos.adapt_to(VoltageSink()), low_boot)

    self.high_boot_diode = self.Block(boot_diode_model)
    high_boot = self.high_boot_diode.cathode.adapt_to(VoltageSource(
      voltage_out=self.high_boot_in.link().voltage
    ))
    self.connect(self.high_boot_in, self.high_boot_diode.anode.adapt_to(VoltageSink(
      current_draw=high_boot.link().current_drawn
    )))
    self.high_boot_cap = self.Block(boot_cap_model)
    self.connect(self.high_boot_cap.neg.adapt_to(VoltageSink()), self.high_out)
    self.connect(self.high_boot_cap.pos.adapt_to(VoltageSink()), high_boot)

    if high_boot_out_connected:  # don't connect the port is it's not used since there isn't a downstream model
      self.connect(self.high_boot_out, high_boot)  # TODO PLACEHOLDER

    # signal path
    if is_first:
      low_pwm: Port[DigitalLink] = self.low_pwm
      high_pwm: Port[DigitalLink] = self.high_pwm
      self.gnd_ctl.init_from(VoltageSink())  # ideal port, not connected
      self.pwr_ctl.init_from(VoltageSink())  # ideal port, not connected
    else:
      self.ldo = self.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.1)))
      self.connect(self.ldo.gnd, self.low_in)
      self.connect(self.ldo.pwr_in, self.low_boot_out)
      self.iso = self.Block(DigitalIsolator())
      self.connect(self.iso.gnd_a, self.gnd_ctl)
      self.connect(self.iso.pwr_a, self.pwr_ctl)
      self.connect(self.iso.gnd_b, self.low_in)
      self.connect(self.iso.pwr_b, self.ldo.pwr_out)
      self.connect(self.iso.in_a.request(f'high'), self.high_pwm)
      self.connect(self.iso.in_a.request(f'low'), self.low_pwm)
      high_pwm = self.iso.out_b.request(f'high')
      low_pwm = self.iso.out_b.request(f'low')

    self.driver = self.Block(HalfBridgeDriver())
    self.connect(self.driver.gnd, self.low_in)
    self.connect(self.driver.pwr, self.low_boot_out)
    self.connect(self.driver.high_in, high_pwm)
    self.connect(self.driver.low_in, low_pwm)
    self.connect(self.driver.high_gnd, self.high_out)
    self.connect(self.driver.high_pwr, high_boot)
    self.connect(self.driver.low_out, self.low_fet.gate.adapt_to(DigitalSink()))
    self.connect(self.driver.high_out, self.high_fet.gate.adapt_to(DigitalSink()))


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
    self.pwr_ctl = self.Port(VoltageSink.empty())
    self.pwms = self.Port(Vector(DigitalSink.empty()))

    self.frequency = self.ArgParameter(frequency)
    self.inductor_current_ripple = self.ArgParameter(inductor_current_ripple)
    self.fet_rds = self.ArgParameter(fet_rds)

    self.generator(self.generate, levels, ratios)

  def generate(self, levels: int, ratios: Range):
    assert levels >= 2, "levels must be 2 or more"
    self.power_path = self.Block(BuckConverterPowerPath(
      self.pwr_in.link().voltage, self.pwr_in.link().voltage * ratios, self.frequency,
      self.pwr_out.link().current_drawn, self.pwr_out.link().current_drawn,
      inductor_current_ripple=self.inductor_current_ripple,
      input_voltage_ripple=250*mVolt,
      dutycycle_limit=(0, 1),
      inductor_scale=(levels - 1)**2
    ))
    self.connect(self.power_path.pwr_in, self.pwr_in)
    self.connect(self.power_path.pwr_out, self.pwr_out)
    self.connect(self.power_path.gnd, self.gnd)

    self.sw = ElementDict[MultilevelSwitchingCell]()
    last_sw: Optional[MultilevelSwitchingCell] = None
    for level in range(levels - 1):
      self.sw[level] = sw = self.Block(MultilevelSwitchingCell(
        last_sw is None,
        in_voltage=self.pwr_in.link().voltage,
        frequency=self.frequency,
        fet_rds=self.fet_rds
      ))
      self.connect(sw.gnd_ctl, self.gnd)
      self.connect(sw.pwr_ctl, self.pwr_ctl)
      self.connect(sw.low_pwm, self.pwms.append_elt(DigitalSink.empty(), f'{level}L'))
      self.connect(sw.high_pwm, self.pwms.append_elt(DigitalSink.empty(), f'{level}H'))
      if last_sw is None:
        self.connect(sw.low_in, self.gnd)
        self.connect(sw.high_in, self.pwr_in)
        self.connect(sw.low_boot_in, self.pwr_gate)
      else:
        self.connect(sw.low_in, last_sw.low_out)
        self.connect(sw.high_in, last_sw.high_out)
        self.connect(sw.low_boot_in, last_sw.low_boot_out)
        self.connect(sw.high_boot_out, last_sw.high_boot_in)

      last_sw = sw

    assert last_sw is not None
    self.connect(last_sw.low_boot_out, last_sw.high_boot_in)
    self.sw_merge = self.Block(MergedVoltageSource()).connected_from(
      last_sw.low_out, last_sw.high_out
    )
    self.connect(self.sw_merge.pwr_out, self.power_path.switch)


class FcmlTest(JlcBoardTop):
  """FPGA + FCML (flying cpacitor multilevel converter) test circuit
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.conv_in = self.Block(LipoConnector(actual_voltage=20*Volt(tol=0)))

    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
      self.usb.gnd, self.conv_in.gnd)
    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.gnd_merge.pwr_out)

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

      (self.reg_vgate, self.tp_vgate), _ = self.chain(
        self.vusb,
        imp.Block(BoostConverter(output_voltage=9*Volt(tol=0.1))),
        self.Block(VoltageTestPoint())
      )
      self.vgate = self.connect(self.reg_vgate.pwr_out)

      self.conv = imp.Block(DiscreteMutlilevelBuckConverter(
        4, (0.15, 0.5), 100*kHertz(tol=0),
        inductor_current_ripple=(0.1, 1)*Amp,
        fet_rds=(0, 0.010)*Ohm
      ))
      self.conv_out = imp.Block(PowerOutConnector((0, 3)*Amp))
      self.connect(self.conv.pwr_in, self.conv_in.pwr)
      self.connect(self.conv.pwr_out, self.conv_out.pwr)
      self.connect(self.conv.pwr_gate, self.vgate)
      self.connect(self.conv.pwr_ctl, self.v3v3)

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
        (['reg_vgate'], Ap3012),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),

        # flying caps need to be beefier for high current rating (which isn't modeled)
        (['conv', 'sw[1]', 'cap', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric'),
        (['conv', 'sw[2]', 'cap', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric'),

        # JLC does not have frequency specs, must be checked TODO
        (['conv', 'power_path', 'inductor', 'ignore_frequency'], True),
        (['reg_vgate', 'power_path', 'inductor', 'ignore_frequency'], True),
      ],
      class_refinements=[
        (SwdCortexTargetWithTdiConnector, SwdCortexTargetTc2050),
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (TestPoint, CompactKeystone5015),
        (HalfBridgeDriver, Ir2301),
        (DigitalIsolator, Cbmud1200l),
        (LinearRegulator, Ap2204k),  # for all the switching cells
      ],
      class_values=[
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (Fet, ['footprint_spec'], 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'),  # don't seem to be alternatives
      ],
    )


class FcmlTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(FcmlTest)
