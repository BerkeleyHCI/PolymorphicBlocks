import unittest

from edg import *


class BldcConnector(Connector, Block):
  """Parameterizable-current connector to an external BLDC motor."""
  @init_in_parent
  def __init__(self, max_current: FloatLike):
    super().__init__()
    self.conn = self.Block(PassiveConnector())
    self.phases = self.Port(Vector(DigitalSink.empty()))

    phase_model = DigitalSink(
      current_draw=(-max_current, max_current)
    )
    for i in ['1', '2', '3']:
      phase_i = self.phases.append_elt(DigitalSink.empty(), i)
      self.require(phase_i.is_connected(), f"all phases {i} must be connected")
      self.connect(phase_i, self.conn.pins.request(i).adapt_to(phase_model))


class MagneticEncoder(Connector, Magnetometer, Block):
  """Connector to AS5600 mangetic encoder,
  https://ams.com/documents/20143/36005/AS5600_DS000365_5-00.pdf"""
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PassiveConnector())

    self.pwr = self.Export(self.conn.pins.request('1').adapt_to(VoltageSink(
      voltage_limits=(3.0, 5.5),  # 3.0-3.6 for 3.3v mode, 4.5-5.5 for 5v mode
      current_draw=(1.5, 6.5)*mAmp,  # supply current LPM3-NOM, excluding burn-in
    )), [Power])
    self.out = self.Export(self.conn.pins.request('2').adapt_to(AnalogSource(
      voltage_out=(0, self.pwr.link().voltage.upper())
    )), [Output])
    self.gnd = self.Export(self.conn.pins.request('3').adapt_to(Ground()),
                           [Common])


class I2cConnector(Connector, Block):
  """Generic I2C connector, QWIIC pinning (gnd/vcc/sda/scl)"""
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PassiveConnector())

    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()),
                           [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink()),
                           [Power])

    self.i2c = self.Port(I2cSlave(DigitalBidir.empty()), [InOut])
    self.connect(self.i2c.sda, self.conn.pins.request('3').adapt_to(DigitalBidir()))
    self.connect(self.i2c.scl, self.conn.pins.request('4').adapt_to(DigitalBidir()))


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


class BldcController(JlcBoardTop):
  """Test BLDC (brushless DC motor) driver circuit with position feedback and USB PD
  """
  def contents(self) -> None:
    super().contents()

    # technically this needs to bootstrap w/ 5v before the MCU
    # negotiates a higher voltage, but the BLDC driver needs
    # at least 8v, so this "assumes" the USB will be at least 9v
    self.usb = self.Block(UsbCReceptacle(
      voltage_out=(9.0*0.9, 12*1.1)*Volt,
      current_limits=(0, 5)*Amp))

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.prot_vusb, self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
        imp.Block(ProtectionZenerDiode(voltage=15*Volt(tol=0.1))),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_5v, self.tp_5v), _ = self.chain(
        self.vusb,
        imp.Block(LinearRegulator(output_voltage=5.0*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
      )
      self.v5 = self.connect(self.reg_5v.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

      self.pd = imp.Block(Fusb302b())
      self.connect(self.usb.pwr, self.pd.vbus)
      self.connect(self.usb.cc, self.pd.cc)
      i2c_bus = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), _ = self.chain(
        i2c_bus, imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.pd.i2c)
      self.connect(self.mcu.gpio.request('pd_int'), self.pd.int)

      (self.mag, ), _ = self.chain(imp.Block(MagneticEncoder()), self.mcu.adc.request('mag'))
      (self.i2c, ), _ = self.chain(imp.Block(I2cConnector()), i2c_bus)

    # BLDC CONTROLLER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.bldc_drv = imp.Block(Drv8313())
      self.connect(self.vusb, self.bldc_drv.pwr)

      self.connect(self.mcu.gpio.request('bldc_reset'), self.bldc_drv.nreset)
      (self.bldc_fault_tp, ), _ = self.chain(self.mcu.gpio.request('bldc_fault'),
                                             self.Block(DigitalTestPoint()),
                                             self.bldc_drv.nfault)
      self.connect(self.mcu.gpio.request_vector('bldc_en'), self.bldc_drv.ens)
      (self.bldc_in_tp, ), _ = self.chain(self.mcu.gpio.request_vector('bldc_in'),
                                          self.Block(DigitalArrayTestPoint()),
                                          self.bldc_drv.ins)

      self.bldc = imp.Block(BldcConnector(2.5 * Amp))  # maximum of DRV8313
      self.connect(self.bldc_drv.outs.request_vector(), self.bldc.phases)

      self.curr = ElementDict[CurrentSenseResistor]()
      self.curr_amp = ElementDict[Amplifier]()
      self.curr_tp = ElementDict[AnalogTestPoint]()
      for i in ['1', '2', '3']:
        self.curr[i] = self.Block(CurrentSenseResistor(50*mOhm(tol=0.05), sense_in_reqd=False))\
            .connected(self.usb.gnd, self.bldc_drv.pgnds.request(i))

        self.curr_amp[i] = imp.Block(Amplifier(Range.from_tolerance(20, 0.05)))
        self.connect(self.curr_amp[i].pwr, self.v3v3)
        (_, self.curr_tp[i], ), _ = self.chain(self.curr[i].sense_out, self.curr_amp[i],
                                            self.Block(AnalogTestPoint()),
                                            self.mcu.adc.request(f'curr_{i}'))

    # 5V DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v5, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.rgb_pull, self.rgb_tp, self.rgb, ), _ = self.chain(
        self.mcu.gpio.request('rgb').as_open_drain(),
        imp.Block(PullupResistor(10*kOhm(tol=0.05))),
        imp.Block(DigitalTestPoint()),
        imp.Block(Sk6812Mini_E()))

    # BUCK BOOST TEST CIRCUIT
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.conv_foced_voltage = self.Block(ForcedVoltage(20*Volt(tol=0)))  # force tighter duty cycles
      self.connect(self.vusb, self.conv_foced_voltage.pwr_in)
      self.conv = imp.Block(CustomBuckBoostConverter((14, 28)*Volt,
                                                     voltage_drop=(0, 0.75)*Volt,
                                                     pwm_frequency=(1000, 1000)*kHertz,
                                                     ripple_current_factor=(0.01, 1.0),
                                                     rds_on=(0, 0.1)*Ohm))
      self.connect(self.conv.pwr_in, self.conv_foced_voltage.pwr_out)
      (self.buck_pull, self.buck_tp), _ = self.chain(self.mcu.gpio.request('buck_pwm'),
                                                     imp.Block(PulldownResistor(1*kOhm(tol=0.05))),
                                                     self.Block(DigitalTestPoint()),
                                                     self.conv.buck_pwm)
      (self.boost_pull, self.boost_tp), _ = self.chain(self.mcu.gpio.request('boost_pwm'),
                                                       imp.Block(PulldownResistor(1*kOhm(tol=0.05))),
                                                       self.Block(DigitalTestPoint()),
                                                       self.conv.boost_pwm)
      self.conv_out = imp.Block(PowerOutConnector((0, 0.50)*Amp))
      self.connect(self.conv.pwr_out, self.conv_out.pwr)

      # TODO update to use VoltageSenseDivider
      div_model = VoltageDivider(output_voltage=(1.0, 3.3)*Volt, impedance=(100, 1000) * Ohm)
      (self.conv_sense, ), _ = self.chain(self.conv.pwr_out, imp.Block(div_model), self.mcu.adc.request('conv_sense'))

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.lemur = self.Block(LemurLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['reg_3v3'], Ldl1117),
        (['reg_5v'], Ldl1117),
        (['sw1', 'package'], KailhSocket),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'bldc_reset=26',
          'bldc_fault=25',
          'bldc_en_3=22',
          'bldc_in_3=21',
          'bldc_en_2=20',
          'bldc_in_2=19',
          'bldc_en_1=18',
          'bldc_in_1=17',
          'curr_3=16',
          'curr_2=14',
          'curr_1=15',

          'buck_pwm=11',
          'boost_pwm=12',
          'conv_sense=13',

          'sw1=38',
          'rgb=40',

          'i2c=I2C1',  # TODO this should be inferred, see issue 169
          'i2c.scl=42',
          'i2c.sda=43',
          'pd_int=45',
        ]),
        (['mcu', 'swd_swo_pin'], 'PB3'),  # TODO maybe use a UART capable pin
        (['curr[1]', 'res', 'res', 'require_basic_part'], False),
        (['curr[1]', 'res', 'res', 'footprint_spec'], 'Resistor_SMD:R_2512_6332Metric'),
        (['curr[2]', 'res', 'res', 'require_basic_part'], ParamValue(['curr[1]', 'res', 'res', 'require_basic_part'])),
        (['curr[2]', 'res', 'res', 'footprint_spec'], ParamValue(['curr[1]', 'res', 'res', 'footprint_spec'])),
        (['curr[3]', 'res', 'res', 'require_basic_part'], ParamValue(['curr[1]', 'res', 'res', 'require_basic_part'])),
        (['curr[3]', 'res', 'res', 'footprint_spec'], ParamValue(['curr[1]', 'res', 'res', 'footprint_spec'])),

        # doesn't seem to be available at JLC
        # (['conv', 'in_high_switch', 'drv', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'),
        (['conv', 'out_low_switch', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'),

        # JLC does not have frequency specs, must be checked TODO
        (['conv', 'power_path', 'inductor', 'ignore_frequency'], True),
        (['conv', 'power_path', 'inductor', 'lcsc_part'], 'C497840'),  # selected part out of stock

        # keep netlist footprints as libraries change
        (['conv', 'in_high_switch', 'drv', 'footprint_spec'], 'Package_TO_SOT_SMD:TO-252-2'),
      ],
      class_refinements=[
        (SwdCortexTargetWithSwoTdiConnector, SwdCortexTargetTc2050),
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        # for compatibility, this board was manufactured before derating was supported and does not compile otherwise
        (Capacitor, ["voltage_rating_derating"], 1.0),
      ],
    )


class BldcControllerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(BldcController)
