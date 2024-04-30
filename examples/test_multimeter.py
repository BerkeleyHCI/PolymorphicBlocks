import unittest
from typing import List, Dict

from edg import *


class ResistorMux(Interface, KiCadImportableBlock, GeneratorBlock):
  """Generates an array of resistors with one side muxed and the other end an array. Passive-typed.
  Specify an infinite resistance for an open circuit."""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'edg_importable:ResistorMux'
    return {
      'control': self.control, 'sw': self.com, 'com': self.input,
      'V+': self.pwr,  'V-': self.gnd
    }

  @init_in_parent
  def __init__(self, resistances: ArrayRangeLike):
    super().__init__()

    self.switch = self.Block(AnalogSwitch())

    self.pwr = self.Export(self.switch.pwr, [Power])
    self.gnd = self.Export(self.switch.gnd, [Common])

    self.control = self.Export(self.switch.control)
    self.input = self.Port(Passive.empty())  # resistor side
    self.com = self.Export(self.switch.com)  # switch side

    self.resistances = self.ArgParameter(resistances)
    self.generator_param(self.resistances)

  def generate(self):
    super().generate()
    self.res = ElementDict[Resistor]()
    for i, resistance in enumerate(self.get(self.resistances)):
      if resistance.upper == float('inf'):  # open circuit for this step
        self.dummy = self.Block(DummyPassive())
        self.connect(self.dummy.io, self.switch.inputs.request(str(i)))
      else:
        res = self.res[i] = self.Block(Resistor(resistance))
        self.connect(res.a, self.input)
        self.connect(res.b, self.switch.inputs.request(str(i)))


class MultimeterAnalog(KiCadSchematicBlock, Block):
  """Analog measurement stage for the volts stage of the multimeter.
  Includes a 1M input resistor and a variable divider.
  Purely DC sampling, and true-RMS functionality needs to be implemented in firmware

  TODO: support wider ranges, to be implemented with port array support
  """
  @init_in_parent
  def __init__(self):
    super().__init__()

    # TODO: separate Vref?
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.input_positive = self.Port(AnalogSink.empty())
    self.input_negative = self.Port(AnalogSink.empty())
    self.output = self.Port(AnalogSource.empty())

    self.select = self.Port(Vector(DigitalSink.empty()))

  def contents(self):
    super().contents()

    self.res = self.Block(Resistor(1*MOhm(tol=0.01), voltage=self.input_positive.link().voltage))
    self.range = self.Block(ResistorMux([
      1*kOhm(tol=0.01),  # 1:1000 step (+/- 1 kV range)
      10*kOhm(tol=0.01),  # 1:100 step (+/- 100 V range)
      100*kOhm(tol=0.01),  # 1:10 step (+/- 10 V range)
      Range(float('inf'), float('inf'))  # 1:1 step, open circuit
    ]))

    output_voltage = self.pwr.link().voltage.hull(self.gnd.link().voltage)
    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'input_positive': AnalogSink(),
        'output': AnalogSource(  # assumed clamped by the switch in the resistor mux
          voltage_out=output_voltage,
          signal_out=output_voltage,
          current_limits=(-10, 10)*mAmp,
          impedance=1*mOhm(tol=0)
        ),
        'input_negative': AnalogSink(),
      })


class MultimeterCurrentDriver(KiCadSchematicBlock, Block):
  """Protected constant-current stage for the multimeter driver.
  """
  @init_in_parent
  def __init__(self, voltage_rating: RangeLike = RangeExpr()):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.output = self.Port(AnalogSink.empty())  # TBD this should be some kind of AnalogBidirectional

    self.control = self.Port(AnalogSink.empty())
    self.select = self.Port(Vector(DigitalSink.empty()))
    self.enable = self.Port(DigitalSink.empty())

    self.voltage_rating = self.ArgParameter(voltage_rating)

  def contents(self):
    super().contents()
    max_in_voltage = self.control.link().voltage.upper()

    self.fet = self.Block(Fet.PFet(
      drain_voltage=self.voltage_rating,  # protect against negative overvoltage
      drain_current=(0, max_in_voltage / 1000),  # approx lowest resistance - TODO properly model the resistor mux
      gate_voltage=(max_in_voltage, max_in_voltage),  # allow all
    ))
    self.amp = self.Block(Opamp())
    self.range = self.Block(ResistorMux([
      1*kOhm(tol=0.01),  # 1 mA range
      10*kOhm(tol=0.01),  # 100 uA range
      100*kOhm(tol=0.01),  # 10 uA range
      1*MOhm(tol=0.01),  # 1 uA range (for MOhm measurements)
    ]))
    self.sw = self.Block(AnalogMuxer())

    self.diode = self.Block(Diode(
      reverse_voltage=self.voltage_rating,  # protect against positive overvoltage
      current=(0, max_in_voltage / 1000),  # approx lowest resistance - TODO properly model the resistor mux
      voltage_drop=(0, 1)*Volt,  # TODO kind of arbitrary
      reverse_recovery_time=RangeExpr.ALL
    ))

    # this is connected in HDL (instead of schematic) because it needs a type conversion (from array[1] to element)
    self.connect(self.sw.control.request(), self.enable)

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'fet.S': AnalogSink(),
        'fet.G': AnalogSink(),
        'range.com': VoltageSink(
          current_draw=(0, max_in_voltage / 1000)  # approx lowest resistance - TODO properly model the resistor mux
        ),
        'range.sw': AnalogSource(
          voltage_out=(0, max_in_voltage),
          signal_out=(0, max_in_voltage),
          impedance=(1, 1000)*kOhm  # TODO properly model resistor mux
        ),
        'output': AnalogSink(  # TODO should be analog source
          voltage_limits=self.voltage_rating
        )
      })


class Multimeter(JlcBoardTop):
  """A BLE multimeter with volts/ohms/diode mode - everything but the curent mode.
  Basically an ADC and programmable constant current driver with ranging circuits.
  Good up to the specified VOLTAGE_RATING, in any measurement mode.

  IMPORTANT: HIGH VOLTAGE SAFETY ALSO DEPENDS ON MECHANICAL DESIGN AND LAYOUT.
    NOT RECOMMENDED FOR USAGE ON HIGH VOLTAGES.
  IMPORTANT: THERE IS NO INPUT OVERLOAD PROTECTION.
    DO NOT PLUG INTO MAINS, WHERE VERY HIGH VOLTAGE TRANSIENTS (kV level) ARE POSSIBLE.
  IMPORTANT: THE USB PORT IS NOT ELECTRICALLY ISOLATED. DO NOT MEASURE NON-ISOLATED
    CIRCUITS WHILE USB IS PLUGGED IN. BE AWARE OF GROUND PATHS.
  """

  def contents(self) -> None:
    super().contents()
    VOLTAGE_RATING = (0, 250) * Volt

    # also support LiIon AA batteries
    self.bat = self.Block(AABattery(voltage=(1.1, 4.2)*Volt, actual_voltage=(1.1, 4.2)*Volt))

    # Data-only USB port, for example to connect to a computer that can't source USB PD
    # so the PD port can be connected to a dedicated power brick.
    self.data_usb = self.Block(UsbCReceptacle())

    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
      self.bat.gnd, self.data_usb.gnd)

    self.gnd = self.connect(self.gnd_merge.pwr_out)
    self.vbat = self.connect(self.bat.pwr)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.gate, self.reg_5v, self.tp_5v, self.prot_5v,
       self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vbat,
        imp.Block(SoftPowerSwitch()),
        imp.Block(BoostConverter(output_voltage=(4.5, 5.2)*Volt)),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(5.2, 6.5)*Volt)),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v5v = self.connect(self.reg_5v.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_analog, self.tp_analog, self.prot_analog), _ = self.chain(
        self.v5v,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.vanalog = self.connect(self.reg_analog.pwr_out)

    # DIGITAL DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Mdbt50q_1mv2())  # needed to define required Vusb
      # TODO ideally this would have a Ble mixin, but mixins can't be applied to the concrete microcontroller

      (self.vbatsense, ), _ = self.chain(self.gate.pwr_out,  # TODO update to use VoltageSenseDivider
                                         imp.Block(VoltageDivider(output_voltage=(0.6, 3)*Volt, impedance=(100, 1000)*Ohm)),
                                         self.mcu.adc.request('vbatsense'))

      (self.usb_esd, ), _ = self.chain(self.data_usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())
      self.connect(self.mcu.pwr_usb, self.data_usb.pwr)

      self.chain(self.gate.btn_out, self.mcu.gpio.request('sw0'))
      self.chain(self.mcu.gpio.request('gate_control'), self.gate.control)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.gpio.request_vector('rgb'), self.rgb.signals)

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))
      (self.sw2, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw2'))

      lcd_spi = self.mcu.spi.request('lcd_spi')
      self.lcd = imp.Block(Qt096t_if09())
      self.connect(self.reg_3v3.pwr_out.as_digital_source(), self.lcd.led)
      self.connect(self.mcu.gpio.request('lcd_reset'), self.lcd.reset)
      self.connect(self.mcu.gpio.request('lcd_rs'), self.lcd.rs)
      self.connect(lcd_spi, self.lcd.spi)  # MISO unused
      self.connect(self.mcu.gpio.request('lcd_cs'), self.lcd.cs)

    # SPEAKER DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.gpio.request('spk'),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
        self.Block(AnalogTestPoint()),
        imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
        self.Block(Speaker()))

      # the AA battery is incapable of driving this at full power,
      # so this indicates it will be run at only partial power
      (self.spk_pwr, ), _ = self.chain(
        self.v5v,
        self.Block(ForcedVoltageCurrentDraw((0, 0.05)*Amp)),
        self.spk_drv.pwr
      )

    # ANALOG DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vanalog, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.ref_div, self.ref_buf), _ = self.chain(
        self.vanalog,
        imp.Block(VoltageDivider(output_voltage=1.62*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower())
      )
      self.vcenter = self.connect(self.ref_buf.output)

      # NEGATIVE PORT
      # 'virtual ground' can be switched between GND (low impedance for the current driver)
      # and Vdd/2 (high impedance, but can measure negative voltages)
      self.inn = self.Block(BananaSafetyJack())
      self.inn_mux = imp.Block(AnalogMuxer()).mux_to(
        inputs=[self.gnd_merge.pwr_out.as_analog_source(), self.ref_buf.output]
      )
      self.inn_merge = self.Block(MergedAnalogSource()).connected_from(
        self.inn_mux.out, self.inn.port.adapt_to(AnalogSource()))

      self.connect(self.mcu.gpio.request_vector('inn_control'), self.inn_mux.control)

      # POSITIVE PORT
      self.inp = self.Block(BananaSafetyJack())
      inp_port = self.inp.port.adapt_to(AnalogSource(
        voltage_out=VOLTAGE_RATING,
        signal_out=VOLTAGE_RATING,
        current_limits=(0, 10)*mAmp,
        impedance=(0, 100)*Ohm,
      ))

      # MEASUREMENT / SIGNAL CONDITIONING CIRCUITS
      adc_spi = self.mcu.spi.request('adc_spi')
      self.measure = imp.Block(MultimeterAnalog())
      self.connect(self.measure.input_positive, inp_port)
      self.connect(self.measure.input_negative, self.inn_merge.output)
      (self.measure_buffer, self.tp_measure), self.meas_chain = self.chain(
        self.measure.output,
        imp.Block(OpampFollower()),
        self.Block(AnalogTestPoint()))
      (self.adc, ), _ = self.chain(
        imp.Block(Mcp3561()),
        adc_spi)
      self.connect(self.adc.pwr, self.v3v3)
      self.connect(self.adc.pwra, self.vanalog)
      self.connect(self.adc.vins.request('0'), self.measure_buffer.output)
      self.connect(self.adc.vins.request('1'), self.inn_merge.output)
      self.connect(self.mcu.gpio.request_vector('measure_select'), self.measure.select)
      self.connect(self.mcu.gpio.request('adc_cs'), self.adc.cs)

      # DRIVER CIRCUITS
      self.driver = imp.Block(MultimeterCurrentDriver(
        voltage_rating=VOLTAGE_RATING
      ))
      self.connect(self.driver.output, inp_port)
      (self.driver_dac, ), _ = self.chain(
        self.mcu.gpio.request('driver_control'),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 100*Hertz(tol=0.5))),
        self.driver.control)
      self.connect(self.mcu.gpio.request_vector('driver_select'), self.driver.select)
      self.connect(self.mcu.gpio.request('driver_enable'), self.driver.enable)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_5v'], Xc9142),
        (['reg_3v3'], Lp5907),  # could be a cheaper LDO actually
        (['reg_analog'], Lp5907),
        (['measure', 'range', 'switch'], AnalogSwitchTree),
        (['driver', 'range', 'switch'], AnalogSwitchTree),
        (['measure', 'res'], GenericChipResistor),
        (['spk', 'conn'], JstPhKVertical),

        (['driver', 'fet'], CustomFet),
        (['driver', 'diode'], CustomDiode),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'adc_spi.miso=24',
          'adc_spi.mosi=26',
          'adc_spi.sck=37',
          'adc_cs=39',
          'inn_control_0=41',
          'measure_select_0_0=42',
          'measure_select_1_0=43',
          'driver_select_1_0=44',
          'driver_select_0_0=46',
          'driver_enable=48',
          'gate_control=49',
          'sw0=50',
          'driver_control=45',  # high frequency PWM

          'sw1=16',
          'lcd_cs=17',
          'lcd_spi.sck=18',
          'lcd_spi.mosi=19',
          'lcd_spi.miso=NC',
          'lcd_rs=10',
          'lcd_reset=8',
          'sw2=3',

          'spk=36',
          'vbatsense=9',

          'rgb_blue=6',
          'rgb_red=4',
          'rgb_green=5',
        ]),
        (['mcu', 'swd_swo_pin'], 'P1.00'),
        (['reg_5v', 'power_path', 'dutycycle_limit'], Range(float('-inf'), float('inf'))),  # allow the regulator to go into tracking mode
        (['reg_5v', 'ripple_current_factor'], Range(0.75, 1.0)),  # smaller inductor
        (['reg_5v', 'fb', 'div', 'series'], 12),  # JLC has limited resistors
        (['measure', 'res', 'footprint_spec'], 'Resistor_SMD:R_2512_6332Metric'),  # beefy input resistor
        (['measure', 'res', 'fp_mfr'], 'Bourns Inc.'),
        (['measure', 'res', 'fp_part'], 'CHV2512-F*-1004***'),
        # IMPORTANT! Most 2512 resistors are rated to ~200V working voltage, this one is up to 3kV.

        # pin footprints to re-select parts with newer parts tables
        (['driver', 'fet', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-23'),  # Q3
        (['driver', 'fet', 'manufacturer_spec'], 'Infineon Technologies'),
        (['driver', 'fet', 'part_spec'], 'BSR92PH6327XTSA1'),
        (['driver', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),
        (['driver', 'diode', 'manufacturer_spec'], 'Micro Commercial Co'),
        (['driver', 'diode', 'part_spec'], 'GS1G-LTP'),
        (['gate', 'amp_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-23'),  # Q2
        (['gate', 'pwr_fet', 'footprint_spec'], ParamValue(['gate', 'amp_fet', 'footprint_spec'])),  # Q1
        (['gate', 'ctl_diode', 'footprint_spec'], 'Diode_SMD:D_SOD-323'),  # D1
        (['gate', 'btn_diode', 'footprint_spec'], ParamValue(['gate', 'ctl_diode', 'footprint_spec'])),  # D2
        # (['reg_5v', 'power_path', 'inductor', 'footprint_spec'], 'Inductor_SMD:L_0805_2012Metric'),  # L1

        (['prot_3v3', 'diode', 'footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (['prot_analog', 'diode', 'footprint_spec'], 'Diode_SMD:D_SOD-123'),

        # JLC does not have frequency specs, must be checked TODO
        (['reg_5v', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
      ],
      class_values=[
        (AnalogSwitchTree, ['switch_size'], 2),
      ],
      class_refinements=[
        (SwdCortexTargetConnector, SwdCortexTargetTc2050),
        (TagConnect, TagConnectNonLegged),
        (Opamp, Tlv9061),  # higher precision opamps
        (BananaSafetyJack, Fcr7350),
        (AnalogSwitch, Nlas4157),
        (Speaker, ConnectorSpeaker),
      ],
    )


class MultimeterTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(Multimeter)
