import unittest

from edg import *


class LightsConnector(Connector, FootprintBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])  # unused, doesn't draw anything
    self.gnd = self.Port(Ground(), [Common])
    self.out = ElementDict[DigitalSink]()
    for i in range(2):
      self.out[i] = self.Port(DigitalSink(current_draw=current_draw))

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_vert_4pin',
      {
        '1': self.pwr,
        '2': self.out[0],
        '3': self.out[1],
        '4': self.gnd,
      },
      mfr='Molex', part='5600200420'
    )


class LightsDriver(Block):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.current_draw = current_draw

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.control = ElementDict[DigitalSink]()

    for i in range(2):
      self.control[i] = self.Port(DigitalSink.empty())

  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.conn = imp.Block(LightsConnector(current_draw=self.current_draw))
      self.drv = ElementDict[Block]()

      for i in range(2):
        driver = self.drv[i] = imp.Block(HighSideSwitch(frequency=(0.1, 10) * kHertz))
        self.connect(self.control[i], driver.control)
        self.connect(driver.output, self.conn.out[i])


class TestHighSwitch(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.pwr_conn = self.Block(CalSolPowerConnector())

    self.vin = self.connect(self.pwr_conn.pwr)
    self.gnd = self.connect(self.pwr_conn.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.pwr, ), _ = self.chain(
        self.vin,
        imp.Block(Tps561201(output_voltage=3.3*Volt(tol=0.05))))

    self.v3v3 = self.connect(self.pwr.pwr_out)

    self.outline = self.Block(Outline_Pn1332())
    self.duck = self.Block(DuckLogo())

    with self.implicit_connect(
      ImplicitConnect(self.v3v3, [Power]),
      ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.can, ), self.can_chain = self.chain(self.mcu.can.request('can'), imp.Block(CalSolCanBlock()))

      # TODO need proper support for exported unconnected ports
      self.can_gnd_load = self.Block(VoltageLoad())
      self.connect(self.can.can_gnd, self.can_gnd_load.pwr)
      self.can_pwr_load = self.Block(VoltageLoad())
      self.connect(self.can.can_pwr, self.can_pwr_load.pwr)

      (self.vsense, ), _ = self.chain(  # TODO update to use VoltageSenseDivider
        self.vin,
        imp.Block(VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)),
        self.mcu.adc.request('vsense'))

      self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # CAN RGB
      self.connect(self.mcu.gpio.request_vector('rgb1'), self.rgb1.signals)

      self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # system RGB 2
      self.connect(self.mcu.gpio.request_vector('rgb2'), self.rgb2.signals)

    self.limit_light_current = self.Block(ForcedVoltageCurrentDraw((0, 2.5) * Amp))
    self.connect(self.vin, self.limit_light_current.pwr_in)
    with self.implicit_connect(
        ImplicitConnect(self.limit_light_current.pwr_out, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.light = ElementDict[LightsDriver]()
      for i in range(4):
        light = self.light[i] = imp.Block(LightsDriver((0, 0.5) * Amp))
        self.connect(self.mcu.gpio.request(f'light_{i}0'), light.control[0])
        self.connect(self.mcu.gpio.request(f'light_{i}1'), light.control[1])

      for i in range(4, 6):
        light = self.light[i] = imp.Block(LightsDriver((0, 3) * Amp))
        self.connect(self.mcu.gpio.request(f'light_{i}0'), light.control[0])
        self.connect(self.mcu.gpio.request(f'light_{i}1'), light.control[1])

    self.hole = ElementDict[MountingHole]()
    for i in range(4):
      self.hole[i] = self.Block(MountingHole_M4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Lpc1549_48),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'can.txd=43',
          'can.rxd=44',
          'vsense=21',
          'rgb1_red=28',
          'rgb1_green=23',
          'rgb1_blue=22',
          'rgb2_red=18',
          'rgb2_green=15',
          'rgb2_blue=13',
          'light_00=12',
          'light_01=8',
          'light_10=7',
          'light_11=6',
          'light_20=4',
          'light_21=3',
          'light_30=2',
          'light_31=1',
          'light_40=48',
          'light_41=47',
          'light_50=46',
          'light_51=45',
        ]),
        (['mcu', 'swd_swo_pin'], 'PIO0_8'),
        # JLC does not have frequency specs, must be checked TODO
        (['pwr', 'power_path', 'inductor', 'ignore_frequency'], True),
        # JLC does not have gate charge spec, so ignore the power calc TODO
        (['light[0]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[0]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[1]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[1]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[2]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[2]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[3]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[3]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[4]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[4]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[5]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[5]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
      ]
    )


class HighSwitchTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TestHighSwitch)
