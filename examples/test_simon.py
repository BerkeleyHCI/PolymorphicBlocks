import unittest

from edg import *


class DomeButtonConnector(CircuitBlock):
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.led_a = self.Port(DigitalSink(
      voltage_limits=(0, 15) * Volt,  # arbitrary +3v tolerance
      current_draw=(0, 10)*mAmp  # TODO characterize current draw
    ))
    self.led_k = self.Port(Ground(), [Common])  # TODO should be agnostic to high / low sided drive
    self.sw2 = self.Port(Ground(), [Common])
    self.sw1 = self.Port(DigitalSingleSource.low_from_supply(self.sw2))

  def contents(self) -> None:
    super().contents()

    self.footprint(
      'J', 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
      {
        '1': self.led_a,
        '2': self.led_k,
        '3': self.sw1,
        '4': self.sw2,
      },
      mfr='Sparkfun', part='COM-09181'  # TODO different colors
    )


class TestSimon(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Nucleo_F303k8())

    with self.implicit_connect(
        ImplicitConnect(self.mcu.pwr_5v, [Power]),
        ImplicitConnect(self.mcu.gnd, [Common]),
    ) as imp:
      (self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.new_io(AnalogSource),
        imp.Block(Lm4871()),
        self.Block(Speaker()))

    with self.implicit_connect(
      ImplicitConnect(self.mcu.pwr_3v3, [Power]),
      ImplicitConnect(self.mcu.gnd, [Common]),
    ) as imp:
      self.rgb = imp.Block(IndicatorSinkRgbLed())  # status RGB
      self.rgb_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.red)
      self.rgb_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.green)
      self.rgb_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.blue)

      (self.sw, self.sw_pull), self.sw_chain = self.chain(
        imp.Block(DigitalSwitch()), imp.Block(PullupResistor(10 * kOhm(tol=0.05))),
        self.mcu.new_io(DigitalBidir))

      self.btn = ElementDict[DomeButtonConnector]()
      self.btn_pull = ElementDict[PullupResistor]()
      self.btn_drv = ElementDict[HighSideSwitch]()  # TODO move to 12v
      self.btn_zeroed_current = ElementDict[HighSideSwitch]()  # TODO move to 12v
      for i in range(4):
        conn = self.btn[i] = imp.Block(DomeButtonConnector())
        pull = self.btn_pull[i] = imp.Block(PullupResistor(10 * kOhm(tol=0.05)))
        self.connect(pull.io, conn.sw1)

    self.pwr = self.Block(Ap3012(output_voltage=12*Volt(tol=0.1)))

    self.v3v3 = self.connect(self.mcu.pwr_3v3)
    self.v5 = self.connect(self.pwr.pwr_in, self.mcu.pwr_5v)
    self.gnd = self.connect(self.pwr.gnd, self.mcu.gnd)
    self.v12 = self.connect(self.pwr.pwr_out)
    with self.implicit_connect(
        ImplicitConnect(self.pwr.pwr_out, [Power]),
        ImplicitConnect(self.mcu.gnd, [Common]),
    ) as imp:
      for i in range(4):
        driver = self.btn_drv[i] = imp.Block(HighSideSwitch(frequency=(0.1, 10) * kHertz))
        if i == 0:  # only one draws current, since we assume only one will be lit at any point in time
          self.connect(driver.output, self.btn[i].led_a)
        else:
          (self.btn_zeroed_current[i],), _ = self.chain(
            driver.output,
            self.Block(ForcedDigitalSinkCurrentDraw((0, 0))),
            self.btn[i].led_a)

    self.btn_drv0_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn_drv[0].control)
    self.btn_sw0_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn[0].sw1)
    self.btn_drv1_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn_drv[1].control)
    self.btn_sw1_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn[1].sw1)
    self.btn_drv2_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn_drv[2].control)
    self.btn_sw2_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn[2].sw1)
    self.btn_drv3_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn_drv[3].control)
    self.btn_sw3_net = self.connect(self.mcu.new_io(DigitalBidir), self.btn[3].sw1)

    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([
          'spk_chain_0=24',
          'rgb_red_net=15',
          'rgb_grn_net=14',
          'rgb_blue_net=13',
          'sw_chain_0=27',
          'btn_drv0_net=5',
          'btn_sw0_net=6',
          'btn_drv1_net=7',
          'btn_sw1_net=8',
          'btn_drv2_net=9',
          'btn_sw2_net=10',
          'btn_drv3_net=11',
          'btn_sw3_net=12',
        ]))
      ]
    )


class SimonTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TestSimon)
