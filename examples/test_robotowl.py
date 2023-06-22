import unittest

from edg import *

from .test_robotdriver import PwmConnector, LedConnector


class PhotodiodeSensor(LightSensor, KiCadSchematicBlock, Block):
  """Simple photodiode-based light sensor"""
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.out = self.Port(AnalogSource.empty(), [Output])

  def contents(self):
    super().contents()
    self.import_kicad(
      self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'r.1': VoltageSink(),
        'r.2': AnalogSink(),  # arbitrary to make the connection legal
        'pd.A': Ground(),
        'pd.K': AnalogSource(
          voltage_out=self.pwr.link().voltage.hull(self.gnd.link().voltage)
          # TODO: what is the impedance?
        ),
      })


class OledConnector(Connector, Block):
  """Connector for an I2C OLED"""
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PinHeader254())

    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()),
                           [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink()),
                           [Power])

    self.i2c = self.Port(I2cSlave(DigitalBidir.empty()), [InOut])
    self.connect(self.i2c.scl, self.conn.pins.request('3').adapt_to(DigitalBidir()))
    self.connect(self.i2c.sda, self.conn.pins.request('4').adapt_to(DigitalBidir()))


class RobotOwl(JlcBoardTop):
  """Controller for a robot owl with a ESP32S3 dev board w/ camera, audio, and peripherals.

  Note, 9 free IOs available
  3 I2S out
  2 I2S in (digital PDM)
  2 PWM
  2 I2C - optionally multiplexed onto camera pins
  1 NPX
  1 analog
  """
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Freenove_Esp32s3_Wroom())

    self.gnd = self.connect(self.mcu.gnd_out)
    self.vusb = self.connect(self.mcu.vusb_out)
    self.v3v3 = self.connect(self.mcu.pwr_out)

    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.mcu.gnd_out)
    self.tp_usb = self.Block(VoltageTestPoint()).connected(self.mcu.vusb_out)
    self.tp_3v3 = self.Block(VoltageTestPoint()).connected(self.mcu.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.oled, ), _ = self.chain(
        self.mcu.cam_i2c,
        imp.Block(OledConnector())
      )

      self.mic = imp.Block(Sd18ob261())
      self.connect(self.mic.clk, self.mcu.gpio.request('mic_clk'))
      self.connect(self.mic.data, self.mcu.gpio.request('mic_data'))

      (self.photodiode, ), _ = self.chain(
        imp.Block(PhotodiodeSensor()),
        self.mcu.adc.request('photodiode')
      )

    # VBATT DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.spk_drv, self.spk), _ = self.chain(
        self.mcu.i2s.request('speaker'),
        imp.Block(Max98357a()),
        self.Block(Speaker())
      )

      self.servo = ElementDict[PwmConnector]()
      for i in range(2):
        (self.servo[i], ), _ = self.chain(
          self.mcu.gpio.request(f'servo{i}'),
          imp.Block(PwmConnector((0, 200)*mAmp))
        )

      self.ws2812bArray = imp.Block(NeopixelArray(12))
      self.extNeopixels = imp.Block(LedConnector())
      self.connect(self.mcu.ws2812, self.ws2812bArray.din)
      self.connect(self.ws2812bArray.dout, self.extNeopixels.din)

    # Mounting holes
    self.m = ElementDict[MountingHole]()
    for i in range(2):
      self.m[i] = self.Block(MountingHole())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'photodiode=GPIO1',
          'servo0=24',
          'servo1=25',
          'mic_data=19',
          'mic_clk=12',
          'speaker.sd=37',
          'speaker.sck=36',
          'speaker.ws=35'
        ]),
        (['mcu', 'ic', 'fp_footprint'], 'edg:Freenove_ESP32S3-WROOM_Expansion'),
        (['mcu', 'vusb_out', 'current_limits'], Range(0, 3)),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),  # default connector series unless otherwise specified
        (TestPoint, CompactKeystone5015),
        (Speaker, ConnectorSpeaker),
        (MountingHole, MountingHole_M3),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ],
    )


class RobotOwlTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotOwl)
