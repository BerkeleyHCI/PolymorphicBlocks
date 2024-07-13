import unittest
from typing import Optional, Dict

from edg import *


class PowerOutConnector(Connector, Block):
  """Parameterized current draw voltage output connector"""
  @init_in_parent
  def __init__(self, current: RangeLike):
    super().__init__()
    self.conn = self.Block(PassiveConnector())
    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()), [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink(
      current_draw=current
    )), [Power])


class SeriesPowerDiode(DiscreteApplication, KiCadImportableBlock):
  """Series diode that propagates voltage"""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'Device:D'
    return {'A': self.pwr_in, 'K': self.pwr_out}

  @init_in_parent
  def __init__(self, reverse_voltage: RangeExpr, current: RangeExpr, voltage_drop: RangeExpr) -> None:
    super().__init__()

    self.pwr_out = self.Port(VoltageSource.empty(), [Output])  # forward declaration
    self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])  # forward declaration

    self.diode = self.Block(Diode(
      reverse_voltage=reverse_voltage, current=current,
      voltage_drop=voltage_drop
    ))

    self.connect(self.pwr_in, self.diode.anode.adapt_to(VoltageSink(
      voltage_limits=(-float('inf'), float('inf')),
      current_draw=self.pwr_out.link().current_drawn
    )))
    self.connect(self.pwr_out, self.diode.cathode.adapt_to(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,  # ignore voltage drop
      current_limits=Range.all()
    )))


class MultilevelSwitchingCell(InternalSubcircuit, KiCadSchematicBlock, GeneratorBlock):
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
               in_voltage: RangeLike, frequency: RangeLike, fet_rds: RangeLike,
               gate_res: RangeLike):
    super().__init__()
    # in is generally towards the supply side, out is towards the inductor side
    self.low_in = self.Port(Ground.empty())
    self.low_out = self.Port(VoltageSource.empty())
    self.low_boot_in = self.Port(VoltageSink.empty())  # bootstrap voltage for the prior cell, except if is_first
    self.low_boot_out = self.Port(VoltageSource.empty())  # bootstrap voltage for this cell
    self.high_in = self.Port(VoltageSink.empty())
    self.high_out = self.Port(VoltageSource.empty())
    # except for high boot they're reversed, out is towards the supply side
    self.high_boot_out = self.Port(VoltageSource.empty(), optional=True)
    self.high_boot_in = self.Port(VoltageSink.empty())

    # control signals
    self.gnd_ctl = self.Port(Ground.empty())
    self.pwr_ctl = self.Port(VoltageSink.empty())
    self.low_pwm = self.Port(DigitalSink.empty())
    self.high_pwm = self.Port(DigitalSink.empty())

    self.in_voltage = self.ArgParameter(in_voltage)
    self.frequency = self.ArgParameter(frequency)
    self.fet_rds = self.ArgParameter(fet_rds)
    self.gate_res = self.ArgParameter(gate_res)

    self.is_first = self.ArgParameter(is_first)
    self.generator_param(self.is_first, self.high_boot_out.is_connected())

  def generate(self):
    super().generate()
    # control path is still defined in HDL
    if self.get(self.is_first):
      low_pwm: Port[DigitalLink] = self.low_pwm
      high_pwm: Port[DigitalLink] = self.high_pwm
      self.gnd_ctl.init_from(Ground())  # ideal port, not connected
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

    self.driver = self.Block(HalfBridgeDriver(False))
    self.connect(self.driver.gnd, self.low_in)
    self.connect(self.driver.pwr, self.low_boot_out)
    driver_indep = self.driver.with_mixin(HalfBridgeDriverIndependent())
    self.connect(driver_indep.high_in, high_pwm)
    self.connect(driver_indep.low_in, low_pwm)
    self.connect(self.driver.high_gnd, self.high_out.as_ground((0, 0)*Amp))  # TODO model driver current

    if self.get(self.high_boot_out.is_connected()):  # leave port disconnected if not used, to avoid an unsolved interface
      self.connect(self.driver.high_pwr, self.high_boot_out)  # schematic connected to boot diode

    # size the flying cap for max voltage change at max current
    # Q = C dv => C = I*t / dV
    MAX_FLYING_CAP_DV_PERCENT = 0.08
    flying_cap_capacitance = self.high_out.link().current_drawn.upper() / self.frequency.lower() / (self.in_voltage.upper() * MAX_FLYING_CAP_DV_PERCENT)

    self.import_kicad(
      self.file_path("resources", f"{self.__class__.__name__}_{self.get(self.is_first)}.kicad_sch"),
      locals={
        'fet_model': Fet.NFet(
          drain_voltage=self.in_voltage,
          drain_current=(0, self.high_out.link().current_drawn.upper()),
          gate_voltage=self.low_boot_out.link().voltage,  # TODO account for boot diode drop
          rds_on=self.fet_rds
        ),
        'flying_cap_model': Capacitor(  # flying cap
          capacitance=(flying_cap_capacitance, float('inf')*Farad),
          voltage=self.in_voltage,
          exact_capacitance=True
        ),
        'boot_diode_model': SeriesPowerDiode(
          reverse_voltage=self.in_voltage + self.low_boot_in.link().voltage,  # upper bound
          current=(0, 0)*Amp,  # TODO model current draw, though it's probably negligibly small
          voltage_drop=(0, 0.6)*Volt  # arbitrary to limit gate voltage droop
        ),
        'boot_cap_model': Capacitor(
          capacitance=0.1*uFarad(tol=0.2),
          voltage=self.low_boot_in.link().voltage
        ),
        'gate_res_model': Resistor(self.gate_res),
      },
      nodes={
        'low_gate': self.driver.low_out,
        'high_gate': self.driver.high_out,
        'high_boot_out_node': self.driver.high_pwr
      },
      conversions={
        'low_in': Ground(),  # TODO better conventions for Ground vs VoltageSink|Source
        'low_out': VoltageSource(
          voltage_out=self.low_in.link().voltage
        ),
        'high_in': VoltageSink(
          current_draw=self.high_out.link().current_drawn
        ),
        'high_out': VoltageSource(
          voltage_out=self.low_in.link().voltage
        ),
        'low_boot_cap.1': VoltageSink(),
        'high_boot_cap.1': VoltageSink(),
        'low_gate': DigitalSink(),  # TODO model gate current draw
        'high_gate': DigitalSink(),  # TODO model gate current draw
      })


class DiscreteMutlilevelBuckConverter(PowerConditioner, GeneratorBlock):
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

    self.levels = self.ArgParameter(levels)
    self.ratios = self.ArgParameter(ratios)
    self.generator_param(self.levels, self.ratios)

  def generate(self):
    super().generate()
    levels = self.get(self.levels)
    assert levels >= 2, "levels must be 2 or more"
    self.power_path = self.Block(BuckConverterPowerPath(
      self.pwr_in.link().voltage, self.pwr_in.link().voltage * self.get(self.ratios), self.frequency,
      self.pwr_out.link().current_drawn, Range.all(),  # TODO add current limits from FETs
      inductor_current_ripple=self.inductor_current_ripple,
      input_voltage_ripple=250*mVolt,
      output_voltage_ripple=25*mVolt,  # TODO plumb through to user config
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
        fet_rds=self.fet_rds,
        gate_res=22*Ohm(tol=0.05)
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
        self.connect(sw.low_in, last_sw.low_out.as_ground((0, 0)*Amp))  # TODO ground current modeling
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


class Fcml(JlcBoardTop):
  """FPGA + FCML (flying cpacitor multilevel converter) test circuit,
  plus a bunch of other hardware blocks to test like RP2040"""
  def contents(self) -> None:
    super().contents()

    self.usb_mcu = self.Block(UsbCReceptacle())
    self.usb_fpga = self.Block(UsbCReceptacle())

    self.conv_in = self.Block(LipoConnector(voltage=20*Volt(tol=0), actual_voltage=20*Volt(tol=0)))

    self.vusb_merge = self.Block(MergedVoltageSource()).connected_from(
      self.usb_mcu.pwr, self.usb_fpga.pwr)
    self.vusb = self.connect(self.vusb_merge.pwr_out)
    self.gnd = self.connect(self.usb_mcu.gnd, self.usb_fpga.gnd, self.conv_in.gnd)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.vusb_merge.pwr_out)
    self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb_mcu.gnd)

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
      self.tp_conv_out = self.Block(VoltageTestPoint()).connected(self.conv.pwr_out)
      self.tp_conv_gnd = self.Block(GroundTestPoint()).connected(self.conv.gnd)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      # FPGA BLOCK
      self.fpga = imp.Block(Ice40up5k_Sg48())
      (self.cdone, ), _ = self.chain(self.fpga.cdone, imp.Block(IndicatorLed()))
      (self.fpga_osc, ), _ = self.chain(imp.Block(Oscillator(48*MHertz(tol=0.005))), self.fpga.gpio.request('osc'))

      (self.fpga_sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.fpga.gpio.request('sw'))
      (self.fpga_led, ), _ = self.chain(self.fpga.gpio.request_vector('led'), imp.Block(IndicatorLedArray(4)))

      # need to name the USB chain so the USB net has the _N and _P postfix for differential traces
      (self.usb_fpga_bitbang, self.usb_fpga_esd), self.usb_fpga_chain = self.chain(
        imp.Block(UsbBitBang()).connected_from(
          self.fpga.gpio.request('usb_dp_pull'), self.fpga.gpio.request('usb_dp'), self.fpga.gpio.request('usb_dm')),
        imp.Block(UsbEsdDiode()),
        self.usb_fpga.usb)

      # MICROCONTROLLER BLOCK
      self.mcu = imp.Block(IoController())

      (self.mcu_sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))
      (self.mcu_leds, ), _ = self.chain(self.mcu.gpio.request_vector('led'), imp.Block(IndicatorLedArray(4)))

      (self.usb_mcu_esd, ), self.usb_mcu_chain = self.chain(
        self.mcu.usb.request('usb'), imp.Block(UsbEsdDiode()), self.usb_mcu.usb)

      self.tp_fpga = ElementDict[DigitalTestPoint]()
      for i in range(4):
        (self.tp_fpga[i],), _ = self.chain(self.mcu.gpio.request(f'fpga{i}'),
                                       self.Block(DigitalTestPoint()),
                                       self.fpga.gpio.request(f'mcu{i}'))

      # FCML CONTROL BLOCK
      (self.pwm_filter, self.tp_pwm), _ = self.chain(
        self.fpga.gpio.request_vector('pwm'),
        self.Block(DigitalArrayTestPoint()),
        imp.Block(DigitalLowPassRcArray(150*Ohm(tol=0.05), 7*MHertz(tol=0.2))),
        self.conv.pwms)

    # SENSING
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      div_model = VoltageSenseDivider(full_scale_voltage=1.5*Volt(tol=0.05), impedance=(100, 1000)*Ohm)
      (self.conv_in_sense, ), _ = self.chain(self.conv.pwr_in, imp.Block(div_model),
                                             self.mcu.adc.request('conv_in_sense'))
      (self.conv_out_sense, ), _ = self.chain(self.conv.pwr_out, imp.Block(div_model),
                                              self.mcu.adc.request('conv_out_sense'))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Rp2040),
        (['reg_3v3'], Ldl1117),
        (['fpga', 'vcc_reg'], Lp5907),
        (['reg_vgate'], Ap3012),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'sw=29',
          'led_0=34',
          'led_1=35',
          'led_2=36',
          'led_3=37',

          'conv_in_sense=38',
          'conv_out_sense=39',

          'fpga0=14',
          'fpga1=13',
          'fpga2=12',
          'fpga3=11',
        ]),
        (['mcu', 'swd_swo_pin'], 'GPIO0'),  # UART0 TX
        (['mcu', 'swd_tdi_pin'], 'GPIO1'),  # UART0 RX
        (['fpga', 'pin_assigns'], [
          'osc=IOB_45a_G1',  # use a global buffer input for clock
          'sw=32',
          'led_0=21',
          'led_1=20',
          'led_2=19',
          'led_3=18',

          'pwm_0H=48',
          'pwm_0L=47',
          'pwm_1H=46',
          'pwm_1L=45',
          'pwm_2H=44',
          'pwm_2L=43',

          'usb_dm=25',
          'usb_dp=26',
          'usb_dp_pull=27',

          'mcu0=2',
          'mcu1=3',
          'mcu2=4',
          'mcu3=6',
       ]),

        # flying caps need to be beefier for high current rating (which isn't modeled)
        (['conv', 'sw[1]', 'cap', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric'),
        (['conv', 'sw[2]', 'cap', 'footprint_spec'], ParamValue(['conv', 'sw[1]', 'cap', 'footprint_spec'])),

        # JLC does not have frequency specs, must be checked TODO
        (['conv', 'power_path', 'inductor', 'part'], 'NR8040T4R7N'),  # peg to prior part selection
        (['conv', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['reg_vgate', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),

        # a bugfix for the SPI flash current draw increased the current beyond the USB port's capabilities
        # this hack-patch keeps the example building
        (['vusb', 'current_drawn'], Range(0.0311, 0.500)),
      ],
      class_refinements=[
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (TestPoint, CompactKeystone5015),
        (HalfBridgeDriver, Ir2301),
        (DigitalIsolator, Cbmud1200l),
        (LinearRegulator, Ap2204k),  # for all the switching cells
        (UsbEsdDiode, Pgb102st23),  # for common parts with the rest of the panel
      ],
      class_values=[
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (Fet, ['footprint_spec'], 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'),  # don't seem to be alternatives
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
        # for compatibility, this board was laid out before derating was supported and does not compile otherwise
        (Capacitor, ["voltage_rating_derating"], 1.0),
      ],
    )


class FcmlTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(Fcml)
