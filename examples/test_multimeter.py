import unittest

from edg import *


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
    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.input_positive = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())

    self.select = self.Port(DigitalSink())  # divider or not

  def contents(self):
    super().contents()

    self.res = self.Block(Resistor(1*MOhm(tol=0.01)))
    self.connect(self.res.a.as_analog_sink(), self.input_positive)
    self.range = self.Block(AnalogDemuxer())
    self.connect(self.range.pwr, self.pwr)
    self.connect(self.range.gnd, self.gnd)
    self.connect(self.select, self.range.control)
    # TODO add a dedicated TVS diode, this relies on the TVS diodes in the analog switch
    # to drop the voltage to safe limits
    self.connect(self.res.b.as_analog_source(
      voltage_out=(self.gnd.link().voltage.lower(), self.pwr.link().voltage.upper()),
      current_limits=(-10, 10)*mAmp,
      impedance=1*mOhm
    ), self.range.input, self.output)
    self.rdiv = self.Block(Resistor(100*Ohm(tol=0.01)))
    self.connect(self.rdiv.a.as_analog_sink(), self.range.out0)
    self.connect(self.rdiv.b.as_ground(), self.gnd)
    (self.range1_nc, ), _ = self.chain(
      self.range.out1,
      self.Block(DummyAnalogSink())
    )


class MultimeterCurrentDriver(Block):
  """Protected constant-current stage for the multimeter driver.

  TODO: this uses an analog voltage which gives limited dynamic range,
    instead this should range by switching across several resistors
  """
  @init_in_parent
  def __init__(self, resistance: RangeLike = RangeExpr(), voltage_rating: RangeLike = RangeExpr()):
    super().__init__()

    # TODO: separate Vref?
    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.output = self.Port(AnalogSink())  # TBD this should be some kind of AnalogBidirectional

    self.control = self.Port(AnalogSink())
    self.enable = self.Port(DigitalSink())

    self.resistance = self.Parameter(RangeExpr(resistance))
    self.voltage_rating = self.Parameter(RangeExpr(voltage_rating))

  def contents(self):
    super().contents()
    max_in_voltage = self.control.link().voltage.upper()

    self.res = self.Block(Resistor(
      resistance=self.resistance
    ))
    self.connect(self.pwr, self.res.a.as_voltage_sink(
      current_draw=(0, max_in_voltage / self.resistance.lower())
    ))
    self.fet = self.Block(PFet(
      drain_voltage=(0, max_in_voltage),
      drain_current=(0, max_in_voltage / self.resistance.lower()),
      gate_voltage=(max_in_voltage, max_in_voltage),  # allow all
      rds_on=(0, 10)*Ohm,  # TODO kind of arbitrary
      gate_charge=RangeExpr.ALL,
      power=0*Watt  # TODO ignored
    ))
    self.connect(self.res.b, self.fet.source)

    self.amp = self.Block(Opamp())
    self.connect(self.amp.pwr, self.pwr)
    self.connect(self.amp.gnd, self.gnd)
    self.connect(self.amp.inp, self.control)
    self.connect(self.amp.inn, self.res.b.as_analog_source(
      voltage_out=(0, max_in_voltage),
      impedance=self.res.actual_resistance
    ))

    self.sw = self.Block(AnalogMuxer())
    self.connect(self.sw.pwr, self.pwr)
    self.connect(self.sw.gnd, self.gnd)
    self.connect(self.enable, self.sw.control)
    self.connect(self.fet.source.as_analog_source(), self.sw.input0)
    self.connect(self.amp.out, self.sw.input1)
    self.connect(self.sw.out, self.fet.gate.as_analog_sink())

    self.diode = self.Block(Diode(
      reverse_voltage=self.voltage_rating,
      current=(0, max_in_voltage / self.resistance.lower()),
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
    self.pwr_in = self.Port(VoltageSink(
      current_draw=RangeExpr(),
      voltage_limits=RangeExpr.ALL
    ), [Input])
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL
    ), [Output])
    self.gnd = self.Port(Ground(), [Common])

    self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)

    self.btn_out = self.Port(DigitalSingleSource())
    self.control = self.Port(DigitalSink())  # digital level control - gnd-referenced NFET gate

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
      rds_on=(0, max_voltage / max_current / 10),  # TODO kind of arbitrary, should really be lower
      gate_charge=(0, float('inf')),
      power=0*Watt  # TODO ignored
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
      gate_voltage=(self.control.link().output_thresholds.upper(), self.control.link().voltage.upper()),
      rds_on=RangeExpr.ALL,  # negligible
      gate_charge=RangeExpr.ALL,
      power=0*Watt  # TODO ignored
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
    self.btn = self.Block(Switch())
    self.connect(self.btn.a, self.ctl_diode.cathode, self.btn_diode.cathode)
    self.connect(self.gnd, self.amp_fet.source.as_ground(), self.amp_res.b.as_ground(),
                 self.btn.b.as_ground())

    self.connect(self.btn_diode.anode.as_digital_single_source(
      voltage_out=self.gnd.link().voltage,  # TODO model diode drop,
      output_thresholds=(self.gnd.link().voltage.upper(), float('inf')),
      low_signal_driver=True
    ), self.btn_out)

    self.connect(self.pull_res.b, self.ctl_diode.anode, self.pwr_fet.gate, self.amp_fet.drain)


class MultimeterTest(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.bat = self.Block(AABattery())

    # Data-only USB port, for example to connect to a computer that can't source USB PD
    # so the PD port can be connected to a dedicated power brick.
    self.data_usb = self.Block(UsbCReceptacle())

    self.gnd_merge = self.Block(MergedVoltageSource())
    self.connect(self.bat.gnd, self.gnd_merge.sink1)
    self.connect(self.data_usb.gnd, self.gnd_merge.sink2)

    self.gnd = self.connect(self.gnd_merge.source)
    self.vbat = self.connect(self.bat.pwr)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd_merge.source, [Common]),
    ) as imp:
      (self.gate, self.reg_5v, self.reg_3v3, self.led_3v3), _ = self.chain(
        self.bat.pwr,
        imp.Block(FetPowerGate()),
        imp.Block(BoostConverter(output_voltage=(3.8, 4.3)*Volt)),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(VoltageIndicatorLed())
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.ref_div, self.ref_buf), _ = self.chain(
        self.reg_3v3.pwr_out,
        imp.Block(VoltageDivider(output_voltage=1.62*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower())
      )
      self.connect(self.reg_3v3.pwr_out, self.ref_buf.pwr)
      self.vcenter = self.connect(self.ref_buf.output)

    # DIGITAL DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.reg_3v3.pwr_out, [Power]),
        ImplicitConnect(self.reg_3v3.gnd, [Common]),
    ) as imp:
      self.prot_3v3 = imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.75)*Volt))

      self.mcu = imp.Block(Holyiot_18010_Nrf52840())
      (self.swd, ), self.swd_chain = self.chain(imp.Block(SwdCortexTargetWithTdiConnector()), self.mcu.swd)

      (self.usb_esd, ), _ = self.chain(self.data_usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb_0)

      self.sw0_net = self.chain(self.gate.btn_out, self.mcu.new_io(DigitalBidir))
      self.gate_control_net = self.chain(self.mcu.new_io(DigitalBidir), self.gate.control)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_r_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.red)
      self.rgb_g_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.green)
      self.rgb_b_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.blue)

      (self.sw1, ), self.sw1_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      (self.sw2, ), self.sw2_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      # TODO next revision: proper navigation switch

      shared_spi = self.mcu.new_io(SpiMaster)
      self.spi_net = self.connect(shared_spi)

      self.lcd = imp.Block(Qt096t_if09())
      self.connect(self.reg_3v3.pwr_out.as_digital_source(), self.lcd.led)
      self.lcd_reset_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.reset)
      self.lcd_rs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.rs)
      self.connect(shared_spi, self.lcd.spi)  # MISO unused
      self.lcd_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.cs)

    # SPEAKER DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.reg_5v.gnd, [Common]),
    ) as imp:
      (self.spk_dac, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.new_io(DigitalBidir),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 20*kHertz(tol=0.2))),
        imp.Block(Lm4871()),
        self.Block(Speaker()))

      # the AA battery is incapable of driving this at full power,
      # so this indicates it will be run at only partial power
      (self.spk_pwr, ), _ = self.chain(
        self.reg_5v.pwr_out,
        self.Block(ForcedVoltageCurrentDraw((0, 0.1)*Amp)),
        self.spk_drv.pwr
      )

    # ANALOG DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.reg_3v3.pwr_out, [Power]),
        ImplicitConnect(self.reg_3v3.gnd, [Common]),
    ) as imp:
      # NEGATIVE PORT
      # 'virtual ground' can be switched between GND (low impedance for the current driver)
      # and Vdd/2 (high impedance, but can measure negative voltages)
      self.inn = self.Block(BananaSafetyJack())
      self.inn_mux = imp.Block(AnalogMuxer())
      self.connect(self.inn_mux.out, self.inn.port.as_analog_sink())
      # TODO remove this with proper bridging adapters
      from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource
      self.gnd_src = self.Block(VoltageSinkAdapterAnalogSource())
      self.connect(self.gnd_src.src, self.gnd_merge.source)
      self.connect(self.inn_mux.input0, self.gnd_src.dst)
      self.connect(self.inn_mux.input1, self.ref_buf.output)
      self.inn_control_net = self.connect(self.mcu.new_io(DigitalBidir), self.inn_mux.control)

      # POSITIVE PORT
      self.inp = self.Block(BananaSafetyJack())
      inp_port = self.inp.port.as_analog_source(
        voltage_out=(0, 300)*Volt,
        current_limits=(0, 10)*mAmp,
        impedance=(0, 100)*Ohm,
      )

      # MEASUREMENT / SIGNAL CONDITIONING CIRCUITS
      self.measure = imp.Block(MultimeterAnalog())
      self.connect(self.measure.input_positive, inp_port)
      (self.measure_buffer, self.adc), self.measure_chain = self.chain(
        self.measure.output,
        imp.Block(OpampFollower()),
        imp.Block(Mcp3201()),
        shared_spi)
      self.measure_select_net = self.connect(self.mcu.new_io(DigitalBidir), self.measure.select)

      # External ADC option, semi-pin-compatible with high resolution MCP3550/1/3 ADCs
      self.adc_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.adc.cs)
      self.connect(self.reg_3v3.pwr_out, self.adc.ref)

      # DRIVER CIRCUITS
      self.driver = imp.Block(MultimeterCurrentDriver(
        resistance=1 * kOhm(tol=0.1),
        voltage_rating=(0, 300)*Volt
      ))
      self.connect(self.driver.output, inp_port)
      (self.driver_dac, ), self.driver_control_chain = self.chain(
        self.mcu.new_io(DigitalBidir),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 1*kHertz(tol=0.5))),
        self.driver.control)
      self.driver_enable_net = self.connect(self.mcu.new_io(DigitalBidir), self.driver.enable)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

    self.jlc_th1 = self.Block(JlcToolingHole())
    self.jlc_th2 = self.Block(JlcToolingHole())
    self.jlc_th3 = self.Block(JlcToolingHole())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_5v'], Ltc3429),
        (['reg_3v3'], Xc6209),
        (['measure', 'res'], ChipResistor),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([
          'rgb_r_net=36',
          'rgb_b_net=2',
          'rgb_g_net=3',

          'spi_net.miso=28',
          'adc_cs_net=27',
          'lcd_cs_net=26',

          'spi_net.sck=20',
          'spi_net.mosi=19',
          'lcd_rs_net=18',
          'lcd_reset_net=17',

          'spk_chain_0=15',

          'measure_select_net=30',
          'gate_control_net_0=29',

          'sw0_net_0=13',
          'driver_control_chain_0=12',
          'driver_enable_net=11',

          'sw1_chain_0=33',
          'sw2_chain_0=6',

          'inn_control_net=4',
          'swd_chain_0.swo=5',
        ])),
        (['reg_5v', 'dutycycle_limit'], Range(0, float('inf'))),  # allow the regulator to go into tracking mode
        (['reg_5v', 'ripple_current_factor'], Range(0.75, 1.0)),  # smaller inductor
        (['reg_5v', 'fb', 'div', 'series'], 12),  # JLC has limited resistors
        (['measure', 'res', 'footprint_spec'], 'Resistor_SMD:R_2512_6332Metric'),

        # pin footprints to re-select parts with newer parts tables
        (['driver', 'fet', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-23'),  # Q3
        (['gate', 'amp_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-23'),  # Q2
        (['gate', 'ctl_diode', 'footprint_spec'], 'Diode_SMD:D_SOD-323'),  # D1
        (['gate', 'btn_diode', 'footprint_spec'], 'Diode_SMD:D_SOD-323'),  # D2
        (['gate', 'pwr_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-23'),  # Q1
        (['reg_5v', 'inductor', 'footprint_spec'], 'Inductor_SMD:L_0805_2012Metric'),  # L1
      ],
      class_refinements=[
        (SwdCortexTargetWithTdiConnector, SwdCortexTargetTc2050),
        (Opamp, Tlv9061),  # higher precision opamps
        (BananaSafetyJack, Fcr7350),
        (Capacitor, JlcCapacitor),
        (Resistor, JlcResistor),
        (AnalogSwitch, Nlas4157)
      ],
    )


class MultimeterTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(MultimeterTest)
