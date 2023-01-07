import unittest

from edg import *


class CanConnector(Connector):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource.empty(), optional=True)
    self.gnd = self.Port(GroundSource.empty())
    self.differential = self.Port(CanDiffPort().empty(), [Output])

    self.conn = self.Block(PassiveConnector())
    self.connect(self.pwr, self.conn.pins.request('2').adapt_to(VoltageSource(
      voltage_out=(7, 14) * Volt,  # TODO get limits from CAN power brick?
      current_limits=(0, 0.15) * Amp  # TODO get actual limits from ???
    )))
    self.connect(self.gnd, self.conn.pins.request('3').adapt_to(GroundSource()))
    self.connect(self.differential.canh, self.conn.pins.request('4').adapt_to(DigitalSource()))
    self.connect(self.differential.canl, self.conn.pins.request('5').adapt_to(DigitalSource()))


class TofArrayTest(JlcBoardTop):
  """A ToF LiDAR array with application as emulating a laser harp and demonstrating another array topology.
  """
  def __init__(self):
    super().__init__()

    # design configuration variables
    self.tof_count = self.Parameter(IntExpr(5))

  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.can = self.Block(CanConnector())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
      self.usb.gnd, self.can.gnd)
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

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw1, ), self.sw1_chain = self.chain(
        imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))
      # realistically it would be cleaner for the RGB to be separate, but this demonstrates packing
      (self.leds, ), self.leds_chain = self.chain(
        imp.Block(IndicatorSinkLedArray(self.tof_count + 3)), self.mcu.gpio.request_vector('leds'))

      self.tof = imp.Block(Vl53l0xArray(self.tof_count))
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.mcu.i2c.request('i2c'),
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.tof.i2c)
      self.connect(self.mcu.gpio.request_vector('tof_xshut'), self.tof.xshut)

      (self.usb_esd, ), self.usb_chain = self.chain(
        self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

      (self.tp_can, self.xcvr, self.can_esd), self.can_chain = self.chain(
        self.mcu.can.request('can'), imp.Block(CanControllerTestPoint()),
        imp.Block(Sn65hvd230()), imp.Block(CanEsdDiode()), self.can.differential
      )

    # 5V DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.tp_spk, self.spk_dac, self.tp_spk_in, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.gpio.request('spk'),
        imp.Block(DigitalTestPoint()),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
        imp.Block(AnalogTestPoint()),
        imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
        self.Block(Speaker()))

      # limit the power draw of the speaker to not overcurrent the USB source
      # this indicates that the device will only be run at partial power
      (self.spk_pwr, ), _ = self.chain(
        self.vusb,
        self.Block(ForcedVoltageCurrentDraw((0, 0.05)*Amp)),
        self.spk_drv.pwr
      )

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

    self.lemur = self.Block(LemurLogo())

  def multipack(self) -> None:
    self.res1 = self.PackedBlock(ResistorArray())
    self.pack(self.res1.elements.request('0'), ['leds', 'led[0]', 'res'])
    self.pack(self.res1.elements.request('1'), ['leds', 'led[1]', 'res'])
    self.pack(self.res1.elements.request('2'), ['rgb', 'device', 'red_res'])
    self.pack(self.res1.elements.request('3'), ['rgb', 'device', 'green_res'])

    self.res2 = self.PackedBlock(ResistorArray())
    self.pack(self.res2.elements.request('0'), ['rgb', 'device', 'blue_res'])
    self.pack(self.res2.elements.request('1'), ['leds', 'led[2]', 'res'])
    self.pack(self.res2.elements.request('2'), ['leds', 'led[3]', 'res'])
    self.pack(self.res2.elements.request('3'), ['leds', 'led[4]', 'res'])

    self.rgb = self.PackedBlock(IndicatorSinkPackedRgbLed())
    self.pack(self.rgb.red, ['leds', 'led[5]'])
    self.pack(self.rgb.green, ['leds', 'led[6]'])
    self.pack(self.rgb.blue, ['leds', 'led[7]'])


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['reg_3v3'], Ldl1117),  # TBD find one that is in stock
        (['spk', 'conn'], JstPhKVertical),
        (['can', 'conn'], MolexSl),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'spk=11',  # PWMable pin, with TIMx_CHx function
          'sw1=19',
          'leds_0=20',
          'leds_1=25',
          'leds_5=26',  # RGB R
          'leds_6=27',  # RGB G
          'leds_7=28',  # RGB B
          'leds_2=29',
          'leds_3=30',
          'leds_4=31',
          'tof_xshut_0=42',
          'tof_xshut_1=41',
          'tof_xshut_2=4',
          'tof_xshut_3=3',
          'tof_xshut_4=2',
        ]),
      ],
      class_refinements=[
        (SwdCortexTargetWithSwoTdiConnector, SwdCortexTargetTc2050),
        (PassiveConnector, PinHeader254),
        (Speaker, ConnectorSpeaker),
      ],
    )


class TofArrayTestTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TofArrayTest)
