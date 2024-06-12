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
    self.gnd = self.Export(self.conn.pins.request('3').adapt_to(Ground()),
                           [Common])
    self.out = self.Export(self.conn.pins.request('2').adapt_to(AnalogSource.from_supply(
      self.gnd, self.pwr
    )), [Output])


class I2cConnector(Connector, Block):
  """Generic I2C connector, QWIIC pinning (gnd/vcc/sda/scl)"""
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PassiveConnector())

    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()),
                           [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink()),
                           [Power])

    self.i2c = self.Port(I2cTarget(DigitalBidir.empty()), [InOut])
    self.connect(self.i2c.sda, self.conn.pins.request('3').adapt_to(DigitalBidir()))
    self.connect(self.i2c.scl, self.conn.pins.request('4').adapt_to(DigitalBidir()))


class BldcHallSensor(Connector, Block):
  """Generic BLDC hall sensor, as +5v, U, V, W, GND"""
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PassiveConnector())

    self.pwr = self.Export(self.conn.pins.request('1').adapt_to(VoltageSink(
      voltage_limits=5*Volt(tol=0.1),
    )), [Power])
    self.gnd = self.Export(self.conn.pins.request('5').adapt_to(Ground()),
                           [Common])

    self.phases = self.Port(Vector(DigitalSingleSource.empty()))
    phase_model = DigitalSingleSource.low_from_supply(self.gnd)
    for (pin, name) in [('2', 'u'), ('3', 'v'), ('4', 'w')]:
      phase = self.phases.append_elt(DigitalSingleSource.empty(), name)
      self.require(phase.is_connected(), f"all phases {name} must be connected")
      self.connect(phase, self.conn.pins.request(pin).adapt_to(phase_model))


class BldcController(JlcBoardTop):
  """Test BLDC (brushless DC motor) driver circuit with position feedback and USB PD
  """
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(IoController())
    mcu_pwr = self.mcu.with_mixin(IoControllerPowerOut())
    mcu_usb = self.mcu.with_mixin(IoControllerUsbOut())

    self.motor_pwr = self.Block(LipoConnector(voltage=(2.5, 4.2)*Volt*6, actual_voltage=(2.5, 4.2)*Volt*6))

    self.vusb = self.connect(mcu_usb.vusb_out)
    self.v3v3 = self.connect(mcu_pwr.pwr_out)
    self.gnd = self.connect(self.mcu.gnd, self.motor_pwr.gnd)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))
      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

      i2c_bus = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp, self.i2c), _ = self.chain(
        i2c_bus, imp.Block(I2cPullup()), imp.Block(I2cTestPoint()), imp.Block(I2cConnector()))

      (self.ref_div, self.ref_buf, self.ref_tp), _ = self.chain(
        self.v3v3,
        imp.Block(VoltageDivider(output_voltage=1.5*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower()),
        self.Block(AnalogTestPoint())
      )
      self.vref = self.ref_buf.output

    # HALL SENSOR
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.hall = imp.Block(BldcHallSensor())
      self.connect(self.vusb, self.hall.pwr)

      (self.hall_pull, self.hall_tp), _ = self.chain(self.hall.phases,
                                                self.Block(PullupResistorArray(4.7*kOhm(tol=0.05))),
                                                self.Block(DigitalArrayTestPoint()),
                                                self.mcu.gpio.request_vector('hall'))
      self.connect(self.hall_pull.pwr, self.v3v3)

    # BLDC CONTROLLER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.vsense = imp.Block(VoltageSenseDivider(full_scale_voltage=(3.0, 3.3)*Volt,
                                                  impedance=10*kOhm(tol=0.2)))
      self.connect(self.motor_pwr.pwr, self.vsense.input)
      (self.vsense_tp, ), _ = self.chain(self.vsense.output, self.Block(AnalogTestPoint()), self.mcu.adc.request('vsense'))

      self.isense = imp.Block(OpampCurrentSensor(
        resistance=0.05*Ohm(tol=0.01),
        ratio=Range.from_tolerance(10, 0.05), input_impedance=10*kOhm(tol=0.05)
      ))
      self.connect(self.motor_pwr.pwr, self.isense.pwr_in, self.isense.pwr)
      self.connect(self.isense.ref, self.vref)
      (self.isense_tp, self.isense_clamp), _ = self.chain(
        self.isense.out,
        self.Block(AnalogTestPoint()),
        imp.Block(AnalogClampResistor()),
        self.mcu.adc.request('isense'))

      self.bldc_drv = imp.Block(Drv8313())
      self.connect(self.isense.pwr_out, self.bldc_drv.pwr)

      self.connect(self.mcu.gpio.request('bldc_reset'), self.bldc_drv.nreset)
      (self.bldc_fault_tp, ), _ = self.chain(self.mcu.gpio.request('bldc_fault'),
                                             self.Block(DigitalTestPoint()),
                                             self.bldc_drv.nfault)
      (self.bldc_en_tp, ), _ = self.chain(self.mcu.gpio.request_vector('bldc_en'),
                                          self.Block(DigitalArrayTestPoint()),
                                          self.bldc_drv.ens)
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
            .connected(self.mcu.gnd, self.bldc_drv.pgnds.request(i))

        self.curr_amp[i] = imp.Block(Amplifier(Range.from_tolerance(20, 0.05)))
        self.connect(self.curr_amp[i].pwr, self.v3v3)
        (_, self.curr_tp[i], ), _ = self.chain(self.curr[i].sense_out, self.curr_amp[i],
                                            self.Block(AnalogTestPoint()),
                                            self.mcu.adc.request(f'curr_{i}'))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Feather_Nrf52840),
        (['isense', 'amp', 'amp'], Opa197)
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'ledb=3',
          'isense=5',
          'vsense=6',
          'ledg=7',
          'curr_3=8',
          'curr_2=9',
          'curr_1=10',
          'bldc_in_1=11',
          'bldc_en_1=12',
          'bldc_in_2=13',
          'bldc_en_2=14',
          'bldc_in_3=15',
          'ledr=16',
          'bldc_en_3=17',
          'bldc_reset=18',
          'bldc_fault=19',
          'sw1=20',
          'i2c.sda=21',
          'i2c.scl=22',
          'hall_u=23',
          'hall_v=24',
          'hall_w=25',
        ]),
        (['isense', 'sense', 'res', 'res', 'require_basic_part'], False),
        (['curr[1]', 'res', 'res', 'require_basic_part'], False),
        (['curr[1]', 'res', 'res', 'footprint_spec'], 'Resistor_SMD:R_2512_6332Metric'),
        (['curr[2]', 'res', 'res', 'require_basic_part'], ParamValue(['curr[1]', 'res', 'res', 'require_basic_part'])),
        (['curr[2]', 'res', 'res', 'footprint_spec'], ParamValue(['curr[1]', 'res', 'res', 'footprint_spec'])),
        (['curr[3]', 'res', 'res', 'require_basic_part'], ParamValue(['curr[1]', 'res', 'res', 'require_basic_part'])),
        (['curr[3]', 'res', 'res', 'footprint_spec'], ParamValue(['curr[1]', 'res', 'res', 'footprint_spec'])),

        (["bldc_drv", "vm_cap_bulk", "cap", "voltage_rating_derating"], 0.6),  # allow using a 50V cap
        (["bldc_drv", "cp_cap", "voltage_rating_derating"], 0.6),  # allow using a 50V cap

        (["hall", "pwr", "voltage_limits"], Range(4, 5.5)),  # allow with the Feather Vbus diode drop
      ],
      class_refinements=[
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
      ],
    )


class BldcControllerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(BldcController)
