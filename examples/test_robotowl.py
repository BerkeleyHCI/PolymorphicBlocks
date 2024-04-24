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
        'pwr': VoltageSink(),
        'gnd': Ground(),
        'out': AnalogSource(
          voltage_out=self.pwr.link().voltage.hull(self.gnd.link().voltage),
          signal_out=self.pwr.link().voltage.hull(self.gnd.link().voltage),
          # TODO: what is the impedance?
        ),
      })


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

    self.mcu = self.Block(IoController())
    mcu_pwr = self.mcu.with_mixin(IoControllerPowerOut())
    mcu_usb = self.mcu.with_mixin(IoControllerUsbOut())
    mcu_i2s = self.mcu.with_mixin(IoControllerI2s())

    self.gnd = self.connect(mcu_pwr.gnd_out)
    self.vusb = self.connect(mcu_usb.vusb_out)
    self.v3v3 = self.connect(mcu_pwr.pwr_out)

    self.tp_gnd = self.Block(VoltageTestPoint()).connected(mcu_pwr.gnd_out)
    self.tp_usb = self.Block(VoltageTestPoint()).connected(mcu_usb.vusb_out)
    self.tp_3v3 = self.Block(VoltageTestPoint()).connected(mcu_pwr.pwr_out)

    (self.reg_12v, self.tp_12v), _ = self.chain(
      self.vusb,
      self.Block(BoostConverter(output_voltage=(12, 15)*Volt)),
      self.Block(VoltageTestPoint())
    )
    self.connect(self.reg_12v.gnd, self.gnd)
    self.v12 = self.connect(self.reg_12v.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mic = imp.Block(Sd18ob261())
      self.connect(self.mic.clk, self.mcu.gpio.request('mic_clk'))
      self.connect(self.mic.data, self.mcu.gpio.request('mic_data'))

      (self.photodiode, ), _ = self.chain(
        imp.Block(PhotodiodeSensor()),
        self.mcu.adc.request('photodiode')
      )

      self.oled22 = imp.Block(Er_Oled022_1())
      self.connect(self.v3v3, self.oled22.pwr)
      self.connect(self.v12, self.oled22.vcc)
      self.connect(self.oled22.i2c, self.mcu.i2c.request('oled'))
      (self.oled_rst, self.oled_pull), _ = self.chain(
        imp.Block(Apx803s(reset_threshold=(2.88, 2.98)*Volt)),  # -29 variant used on Adafruit boards
        imp.Block(PullupResistor(10*kOhm(tol=0.05))),
        self.oled22.reset
      )

    # VBATT DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.spk_drv, self.spk), _ = self.chain(
        mcu_i2s.i2s.request('speaker'),
        imp.Block(Max98357a()),
        self.Block(Speaker())
      )

      self.servo = ElementDict[PwmConnector]()
      for i in range(2):
        (self.servo[i], ), _ = self.chain(
          self.mcu.gpio.request(f'servo{i}'),
          imp.Block(PwmConnector((0, 200)*mAmp))
        )

      (self.ws2812bArray, self.extNeopixels), _ = self.chain(
        self.mcu.gpio.request('ws2812'),
        imp.Block(NeopixelArray(12)),
        imp.Block(LedConnector())
      )

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Freenove_Esp32s3_Wroom),
        (['reg_12v'], Ap3012),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'photodiode=GPIO1',
          'servo0=25',
          'servo1=24',
          'mic_data=19',
          'mic_clk=12',
          'speaker.sd=36',
          'speaker.sck=35',
          'speaker.ws=37',
          'ws2812=26',  # WS2812
          'oled=CAM_SCCB',
        ]),
        (['mcu', 'fp_footprint'], 'edg:Freenove_ESP32S3-WROOM_Expansion'),
        (['mcu', 'vusb_out', 'current_limits'], Range(0, 3)),
        (['photodiode', 'out', 'signal_out'], Range(0, 2.2)),  # discard the extra range to make it ESP compatible

        (['reg_12v', 'power_path', 'inductor', 'part'], "CBC3225T470KR"),
        (['reg_12v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 7e6)),
        # compatibility with what was manufactured
        (['spk_drv', 'ic', 'footprint_spec'], 'Package_BGA:Maxim_WLP-9_1.595x1.415_Layout3x3_P0.4mm_Ball0.27mm_Pad0.25mm_NSMD')
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),  # default connector series unless otherwise specified
        (PinHeader254, PinHeader254Horizontal),
        (TestPoint, CompactKeystone5015),
        (Speaker, ConnectorSpeaker),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
        (Er_Oled022_1, ["iref_res", "resistance"], Range.from_tolerance(820e3, 0.1)),  # use a basic part
        (Er_Oled022_1, ["device", "vcc", "voltage_limits"], Range(12, 15)),  # allow it to be a bit lower
      ],
    )


class RobotOwlTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotOwl)
