import unittest
from typing import List

from edg import *


class ResistorMux(GeneratorBlock):
  """Generates an array of resistors with one side muxed and the other end an array. Passive-typed.
  Specify an infinite resistance for an open circuit."""
  @init_in_parent
  def __init__(self, resistances: ArrayRangeLike):
    super().__init__()

    self.switch = self.Block(AnalogSwitch())

    self.pwr = self.Export(self.switch.pwr, [Power])
    self.gnd = self.Export(self.switch.gnd, [Common])

    self.control = self.Export(self.switch.control)
    self.input = self.Port(Passive.empty())  # resistor side
    self.com = self.Export(self.switch.com)  # switch side

    self.generator(self.generate, resistances)

  def generate(self, resistances: List[Range]):
    self.res = ElementDict[Resistor]()
    for i, resistance in enumerate(resistances):
      if resistance.upper == float('inf'):  # open circuit for this step
        self.dummy = self.Block(DummyPassive())
        self.connect(self.dummy.io, self.switch.inputs.allocate(str(i)))
      else:
        res = self.res[i] = self.Block(Resistor(resistance))
        self.connect(res.a, self.input)
        self.connect(res.b, self.switch.inputs.allocate(str(i)))


class MultimeterAnalog(Block):
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

    self.res = self.Block(Resistor(1*MOhm(tol=0.01)))
    self.connect(self.res.a.as_analog_sink(), self.input_positive)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
        ImplicitConnect(self.pwr, [Power]),
    ) as imp:
      self.range = imp.Block(ResistorMux([
        1*kOhm(tol=0.01),  # 1:1000 step (+/- 1 kV range)
        10*kOhm(tol=0.01),  # 1:100 step (+/- 100 V range)
        100*kOhm(tol=0.01),  # 1:10 step (+/- 10 V range)
        Range(float('inf'), float('inf'))  # 1:1 step, open circuit
      ]))
      self.connect(self.range.input.as_analog_sink(), self.input_negative)
      self.connect(self.res.b.as_analog_source(
        voltage_out=(self.gnd.link().voltage.lower(), self.pwr.link().voltage.upper()),
        current_limits=(-10, 10)*mAmp,
        impedance=1*mOhm(tol=0)
      ), self.range.com.as_analog_sink(), self.output)

      self.connect(self.select, self.range.control)


class MultimeterCurrentDriver(Block):
  """Protected constant-current stage for the multimeter driver.
  """
  @init_in_parent
  def __init__(self, voltage_rating: RangeLike = RangeExpr()):
    super().__init__()

    # TODO: separate Vref?
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

    self.fet = self.Block(PFet(
      drain_voltage=self.voltage_rating,  # protect against negative overvoltage
      drain_current=(0, max_in_voltage / 1000),  # approx lowest resistance - TODO properly model the resistor mux
      gate_voltage=(max_in_voltage, max_in_voltage),  # allow all
    ))

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
        ImplicitConnect(self.pwr, [Power]),
    ) as imp:
      self.amp = imp.Block(Opamp())
      self.connect(self.amp.inp, self.control)

      self.range = imp.Block(ResistorMux([
        1*kOhm(tol=0.01),  # 1 mA range
        10*kOhm(tol=0.01),  # 100 uA range
        100*kOhm(tol=0.01),  # 10 uA range
        1*MOhm(tol=0.01),  # 1 uA range (for MOhm measurements)
      ]))
      self.connect(self.pwr, self.range.input.as_voltage_sink(
        current_draw=(0, max_in_voltage / 1000)  # approx lowest resistance - TODO properly model the resistor mux
      ))
      fet_source_node = self.fet.source.as_analog_sink()
      self.connect(
        self.amp.inn,
        fet_source_node,
        self.range.com.as_analog_source(
          voltage_out=(0, max_in_voltage),
          impedance=(1, 1000)*kOhm  # TODO properly model resistor mux
        ))

      self.connect(self.select, self.range.control)

      self.sw = imp.Block(AnalogMuxer()).mux_to(  # enable switch
        [fet_source_node, self.amp.out],
        self.fet.gate.as_analog_sink()
      )
      self.connect(self.enable, self.sw.control.allocate())

    self.diode = self.Block(Diode(
      reverse_voltage=self.voltage_rating,  # protect against positive overvoltage
      current=(0, max_in_voltage / 1000),  # approx lowest resistance - TODO properly model the resistor mux
      voltage_drop=(0, 1)*Volt,  # TODO kind of arbitrary
      reverse_recovery_time=RangeExpr.ALL
    ))
    self.connect(self.fet.drain, self.diode.anode)
    self.connect(self.diode.cathode.as_analog_sink(  # TODO should be analog source
      voltage_limits=self.voltage_rating
    ), self.output)


class FetPowerGate(Block):
  """A high-side PFET power gate that has a button to power on, can be latched
  on by an external signal, and provides the button output as a signal.
  """
  def __init__(self):
    super().__init__()
    self.pwr_in = self.Port(VoltageSink.empty(), [Input])
    self.pwr_out = self.Port(VoltageSource.empty(), [Output])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)

    self.btn_out = self.Port(DigitalSingleSource.empty())
    self.control = self.Port(DigitalSink.empty())  # digital level control - gnd-referenced NFET gate

  def contents(self):
    super().contents()

    max_voltage = self.control.link().voltage.upper()
    max_current = self.pwr_out.link().current_drawn.upper()

    self.pull_res = self.Block(Resistor(
      resistance=10*kOhm(tol=0.05)  # TODO kind of arbitrrary
    ))
    self.connect(self.pwr_in, self.pull_res.a.as_voltage_sink())
    self.pwr_fet = self.Block(PFet(
      drain_voltage=(0, max_voltage),
      drain_current=(0, max_current),
      gate_voltage=(max_voltage, max_voltage),  # TODO this ignores the diode drop
    ))
    self.connect(self.pwr_in, self.pwr_fet.source.as_voltage_sink(
      current_draw=self.pwr_out.link().current_drawn,
      voltage_limits=RangeExpr.ALL,
    ))
    self.connect(self.pwr_fet.drain.as_voltage_source(
      voltage_out = self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL,
    ), self.pwr_out)

    self.amp_res = self.Block(Resistor(
      resistance=10*kOhm(tol=0.05)  # TODO kind of arbitrary
    ))
    self.amp_fet = self.Block(NFet(
      drain_voltage=(0, max_voltage),
      drain_current=(0, 0),  # effectively no current
      gate_voltage=(self.control.link().output_thresholds.upper(), self.control.link().voltage.upper())
    ))
    self.connect(self.control, self.amp_fet.gate.as_digital_sink(), self.amp_res.a.as_digital_sink())  # TODO more modeling here?

    self.ctl_diode = self.Block(Diode(
      reverse_voltage=(0, max_voltage),
      current=RangeExpr.ZERO,  # effectively no current
      voltage_drop=(0, 0.4)*Volt,  # TODO kind of arbitrary - should be parameterized
      reverse_recovery_time=RangeExpr.ALL
    ))
    self.btn_diode = self.Block(Diode(
      reverse_voltage=(0, max_voltage),
      current=RangeExpr.ZERO,  # effectively no current
      voltage_drop=(0, 0.4)*Volt,  # TODO kind of arbitrary - should be parameterized
      reverse_recovery_time=RangeExpr.ALL
    ))
    self.btn = self.Block(Switch(voltage=0*Volt(tol=0)))  # TODO - actually model switch voltage
    self.connect(self.btn.a, self.ctl_diode.cathode, self.btn_diode.cathode)
    self.connect(self.gnd, self.amp_fet.source.as_ground(), self.amp_res.b.as_ground(),
                 self.btn.b.as_ground())

    self.connect(self.btn_diode.anode.as_digital_single_source(
      voltage_out=self.gnd.link().voltage,  # TODO model diode drop,
      output_thresholds=(self.gnd.link().voltage.upper(), float('inf')),
      low_signal_driver=True
    ), self.btn_out)

    self.connect(self.pull_res.b, self.ctl_diode.anode, self.pwr_fet.gate, self.amp_fet.drain)


class MultimeterTest(JlcBoardTop):
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
        imp.Block(FetPowerGate()),
        imp.Block(BoostConverter(output_voltage=(4.5, 5.5)*Volt)),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(5.5, 7.0)*Volt)),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.75)*Volt))
      )
      self.v5v = self.connect(self.reg_5v.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_analog, self.tp_analog, self.prot_analog), _ = self.chain(
        self.v5v,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.75)*Volt))
      )
      self.vanalog = self.connect(self.reg_analog.pwr_out)

    # DIGITAL DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Mdbt50q_1mv2())

      (self.vbatsense, ), _ = self.chain(self.gate.pwr_out,
                                         imp.Block(VoltageDivider(output_voltage=(0.6, 3)*Volt, impedance=(100, 1000)*Ohm)),
                                         self.mcu.adc.allocate('vbatsense'))

      (self.usb_esd, ), _ = self.chain(self.data_usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.allocate())
      self.connect(self.mcu.pwr_usb, self.data_usb.pwr)

      self.chain(self.gate.btn_out, self.mcu.gpio.allocate('sw0'))
      self.chain(self.mcu.gpio.allocate('gate_control'), self.gate.control)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.gpio.allocate_vector('rgb'), self.rgb.signals)

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.allocate('sw1'))
      (self.sw2, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.allocate('sw2'))

      lcd_spi = self.mcu.spi.allocate('lcd_spi')
      self.lcd = imp.Block(Qt096t_if09())
      self.connect(self.reg_3v3.pwr_out.as_digital_source(), self.lcd.led)
      self.connect(self.mcu.gpio.allocate('lcd_reset'), self.lcd.reset)
      self.connect(self.mcu.gpio.allocate('lcd_rs'), self.lcd.rs)
      self.connect(lcd_spi, self.lcd.spi)  # MISO unused
      self.connect(self.mcu.gpio.allocate('lcd_cs'), self.lcd.cs)

    # SPEAKER DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.gpio.allocate('spk'),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
        self.Block(AnalogTestPoint()),
        imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
        self.Block(Speaker()))

      # the AA battery is incapable of driving this at full power,
      # so this indicates it will be run at only partial power
      (self.spk_pwr, ), _ = self.chain(
        self.v5v,
        self.Block(ForcedVoltageCurrentDraw((0, 0.1)*Amp)),
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

      # # TODO remove this with proper bridging adapters
      from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource
      self.gnd_src = self.Block(VoltageSinkAdapterAnalogSource())
      self.connect(self.gnd_src.src, self.gnd)

      self.inn_mux = imp.Block(AnalogMuxer()).mux_to(
        inputs=[self.gnd_src.dst, self.ref_buf.output]
      )
      self.inn_merge = self.Block(MergedAnalogSource()).connected_from(
        self.inn_mux.out, self.inn.port.as_analog_source())

      self.connect(self.mcu.gpio.allocate_vector('inn_control'), self.inn_mux.control)

      # POSITIVE PORT
      self.inp = self.Block(BananaSafetyJack())
      inp_port = self.inp.port.as_analog_source(
        voltage_out=VOLTAGE_RATING,
        current_limits=(0, 10)*mAmp,
        impedance=(0, 100)*Ohm,
      )

      # MEASUREMENT / SIGNAL CONDITIONING CIRCUITS
      adc_spi = self.mcu.spi.allocate('adc_spi')
      self.measure = imp.Block(MultimeterAnalog())
      self.connect(self.measure.input_positive, inp_port)
      self.connect(self.measure.input_negative, self.inn_merge.output)
      (self.measure_buffer, self.tp_measure), _ = self.chain(
        self.measure.output,
        imp.Block(OpampFollower()),
        self.Block(AnalogTestPoint()))
      (self.adc, ), _ = self.chain(
        imp.Block(Mcp3561()),
        adc_spi)
      self.connect(self.adc.pwr, self.v3v3)
      self.connect(self.adc.pwra, self.vanalog)
      self.connect(self.adc.vins.allocate('0'), self.measure_buffer.output)
      self.connect(self.adc.vins.allocate('1'), self.inn_merge.output)
      self.connect(self.mcu.gpio.allocate_vector('measure_select'), self.measure.select)
      self.connect(self.mcu.gpio.allocate('adc_cs'), self.adc.cs)

      self.adc_vref = self.connect(self.adc.vref)
      (self.tp_vref, ), _ = self.chain(
        self.adc.vref,
        self.Block(VoltageTestPoint()))

      # DRIVER CIRCUITS
      self.driver = imp.Block(MultimeterCurrentDriver(
        voltage_rating=VOLTAGE_RATING
      ))
      self.connect(self.driver.output, inp_port)
      (self.driver_dac, ), _ = self.chain(
        self.mcu.gpio.allocate('driver_control'),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 100*Hertz(tol=0.5))),
        self.driver.control)
      self.connect(self.mcu.gpio.allocate_vector('driver_select'), self.driver.select)
      self.connect(self.mcu.gpio.allocate('driver_enable'), self.driver.enable)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

    self.m1 = self.Block(MountingHole())
    self.m2 = self.Block(MountingHole())


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_5v'], Xc9142),
        (['reg_3v3'], Lp5907),  # could be a cheaper LDO actually
        (['reg_analog'], Lp5907),
        (['measure', 'range', 'switch'], AnalogSwitchTree),
        (['driver', 'range', 'switch'], AnalogSwitchTree),
        (['measure', 'res'], ChipResistor),
        (['spk', 'conn'], JstPhK),
      ],
      instance_values=[
        (['measure', 'range', 'switch', 'switch_size'], 2),
        (['driver', 'range', 'switch', 'switch_size'], 2),
        (['mcu', 'pin_assigns'], ';'.join([
          # TODO reassign for this differently-pinned device
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
        ])),
        (['reg_5v', 'power_path', 'dutycycle_limit'], Range(float('-inf'), float('inf'))),  # allow the regulator to go into tracking mode
        (['reg_5v', 'ripple_current_factor'], Range(0.75, 1.0)),  # smaller inductor
        (['reg_5v', 'fb', 'div', 'series'], 12),  # JLC has limited resistors
        (['measure', 'res', 'footprint'], 'Resistor_SMD:R_2512_6332Metric'),  # beefy input resistor
        (['measure', 'res', 'fp_mfr'], 'Bourns Inc.'),
        (['measure', 'res', 'fp_part'], 'CHV2512-F*-1004***'),
        # IMPORTANT! Most 2512 resistors are rated to ~200V working voltage, this one is up to 3kV.

        # pin footprints to re-select parts with newer parts tables
        (['driver', 'fet', 'footprint'], 'Package_TO_SOT_SMD:SOT-23'),  # Q3
        (['gate', 'amp_fet', 'footprint'], 'Package_TO_SOT_SMD:SOT-23'),  # Q2
        (['gate', 'ctl_diode', 'footprint'], 'Diode_SMD:D_SOD-323'),  # D1
        (['gate', 'btn_diode', 'footprint'], 'Diode_SMD:D_SOD-323'),  # D2
        (['gate', 'pwr_fet', 'footprint'], 'Package_TO_SOT_SMD:SOT-23'),  # Q1
        (['reg_5v', 'power_path', 'inductor', 'footprint'], 'Inductor_SMD:L_0805_2012Metric'),  # L1
      ],
      class_values=[
        # (AnalogSwitchTree, ['switch_size'], 2),  # TODO this breaks because of parameter resolution ordering
      ],
      class_refinements=[
        (SwdCortexTargetWithTdiConnector, SwdCortexTargetTc2050Nl),
        (Opamp, Tlv9061),  # higher precision opamps
        (BananaSafetyJack, Fcr7350),
        (AnalogSwitch, Nlas4157),
        (Speaker, ConnectorSpeaker),
        (MountingHole, MountingHole_M3),
      ],
    )


class MultimeterTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(MultimeterTest)
