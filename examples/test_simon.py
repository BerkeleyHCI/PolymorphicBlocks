import unittest

from edg import *


class DomeButtonConnector(FootprintBlock):
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
    self.v5v = self.connect(self.mcu.pwr_5v)
    self.v3v3 = self.connect(self.mcu.pwr_3v3)
    self.gnd = self.connect(self.mcu.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.v5v, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.spk_drv, self.spk), _ = self.chain(
        self.mcu.dac.allocate('spk'),
        imp.Block(Lm4871()),
        self.Block(Speaker()))

    with self.implicit_connect(
      ImplicitConnect(self.v3v3, [Power]),
      ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.rgb = imp.Block(IndicatorSinkRgbLed())  # status RGB
      self.connect(self.mcu.gpio.allocate_vector('rgb'), self.rgb.signals)

      (self.sw, self.sw_pull), _ = self.chain(
        imp.Block(DigitalSwitch()), imp.Block(PullupResistor(10 * kOhm(tol=0.05))),
        self.mcu.gpio.allocate('sw'))

      self.btn = ElementDict[DomeButtonConnector]()
      self.btn_pull = ElementDict[PullupResistor]()
      self.btn_drv = ElementDict[HighSideSwitch]()  # TODO move to 12v
      self.btn_zeroed_current = ElementDict[HighSideSwitch]()  # TODO move to 12v
      for i in range(4):
        conn = self.btn[i] = imp.Block(DomeButtonConnector())
        pull = self.btn_pull[i] = imp.Block(PullupResistor(10 * kOhm(tol=0.05)))
        self.connect(pull.io, conn.sw1, self.mcu.gpio.allocate(f'btn_sw{i}'))

    self.pwr = self.Block(Ap3012(output_voltage=12*Volt(tol=0.1)))
    self.connect(self.v5v, self.pwr.pwr_in)
    self.connect(self.gnd, self.pwr.gnd)
    self.v12 = self.connect(self.pwr.pwr_out)
    with self.implicit_connect(
        ImplicitConnect(self.v12, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      for i in range(4):
        driver = self.btn_drv[i] = imp.Block(HighSideSwitch(frequency=(0.1, 10) * kHertz))
        self.connect(self.mcu.gpio.allocate(f'btn_drv{i}'), driver.control)
        if i == 0:  # only one draws current, since we assume only one will be lit at any point in time
          self.connect(driver.output, self.btn[i].led_a)
        else:
          (self.btn_zeroed_current[i],), _ = self.chain(
            driver.output,
            self.Block(ForcedDigitalSinkCurrentDraw((0, 0))),
            self.btn[i].led_a)

    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'spk=24',
          'rgb_red=15',
          'rgb_green=14',
          'rgb_blue=13',
          'sw=27',
          'btn_drv0=5',
          'btn_sw0=6',
          'btn_drv1=7',
          'btn_sw1=8',
          'btn_drv2=9',
          'btn_sw2=10',
          'btn_drv3=11',
          'btn_sw3=12',
        ]),
        # JLC does not have frequency specs, must be checked TODO
        (['pwr', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
      ],
      instance_refinements=[
        (['spk', 'conn'], JstPhK),
      ],
      class_refinements=[
        (Speaker, ConnectorSpeaker),
      ]
    )


class SimonTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TestSimon)
