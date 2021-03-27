import unittest

from edg import *


class LightsConnector(Connector, CircuitBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
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

    self.current_draw = self.Parameter(RangeExpr(current_draw))

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.control = ElementDict[DigitalSink]()

    for i in range(2):
      self.control[i] = self.Port(DigitalSink())

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

    self.vin = self.connect(self.pwr_conn.pwr)  # TODO should autogenerate better names in future
    self.gnd = self.connect(self.pwr_conn.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.pwr_conn.gnd, [Common]),
    ) as imp:
      (self.pwr, ), _ = self.chain(
        self.pwr_conn.pwr,
        imp.Block(Tps561201(output_voltage=3.3*Volt(tol=0.05))))

    self.v3v3 = self.connect(self.pwr.pwr_out)

    self.outline = self.Block(Outline_Pn1332())
    self.duck = self.Block(DuckLogo())

    with self.implicit_connect(
      ImplicitConnect(self.pwr.pwr_out, [Power]),
      ImplicitConnect(self.pwr.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48(frequency=12 * MHertz(tol=0.005)))
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetHeader()), self.mcu.swd)
      (self.crystal, ), _ = self.chain(self.mcu.xtal, imp.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005))))  # TODO can we not specify this and instead infer from MCU specs?

      (self.can, ), self.can_chain = self.chain(self.mcu.new_io(CanControllerPort), imp.Block(CalSolCanBlock()))

      # TODO need proper support for exported unconnected ports
      self.can_gnd_load = self.Block(VoltageLoad())
      self.connect(self.can.can_gnd, self.can_gnd_load.pwr)
      self.can_pwr_load = self.Block(VoltageLoad())
      self.connect(self.can.can_pwr, self.can_pwr_load.pwr)

      (self.vsense, ), self.vsense_chain = self.chain(
        self.pwr_conn.pwr,
        imp.Block(VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)),
        self.mcu.new_io(AnalogSink))

      self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # CAN RGB
      self.rgb1_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb1.red)
      self.rgb1_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb1.green)
      self.rgb1_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb1.blue)

      self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # system RGB 2
      self.rgb2_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb2.red)
      self.rgb2_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb2.green)
      self.rgb2_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb2.blue)

    self.limit_light_current = self.Block(ForcedVoltageCurrentDraw((0, 2.5) * Amp))
    self.connect(self.pwr_conn.pwr, self.limit_light_current.pwr_in)
    with self.implicit_connect(
        ImplicitConnect(self.limit_light_current.pwr_out, [Power]),
        ImplicitConnect(self.pwr.gnd, [Common]),
    ) as imp:
      self.light = ElementDict[LightsDriver]()
      for i in range(4):
        light = self.light[i] = imp.Block(LightsDriver((0, 0.5) * Amp))

      self.light_00_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[0].control[0])
      self.light_01_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[0].control[1])
      self.light_10_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[1].control[0])
      self.light_11_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[1].control[1])
      self.light_20_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[2].control[0])
      self.light_21_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[2].control[1])
      self.light_30_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[3].control[0])
      self.light_31_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[3].control[1])

      for i in range(2):
        light = self.light[4+i] = imp.Block(LightsDriver((0, 3) * Amp))

      self.light_40_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[4].control[0])
      self.light_41_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[4].control[1])
      self.light_50_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[5].control[0])
      self.light_51_net = self.connect(self.mcu.new_io(DigitalBidir), self.light[5].control[1])

    self.hole = ElementDict[MountingHole]()
    for i in range(4):
      self.hole[i] = self.Block(MountingHole_M4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([
          'can_chain_0.txd=43',
          'can_chain_0.rxd=44',
          'vsense_chain_1=21',
          'rgb1_red_net=28',
          'rgb1_grn_net=23',
          'rgb1_blue_net=22',
          'rgb2_red_net=18',
          'rgb2_grn_net=15',
          'rgb2_blue_net=13',
          'light_00_net=12',
          'light_01_net=8',
          'light_10_net=7',
          'light_11_net=6',
          'light_20_net=4',
          'light_21_net=3',
          'light_30_net=2',
          'light_31_net=1',
          'light_40_net=48',
          'light_41_net=47',
          'light_50_net=46',
          'light_51_net=45',
        ]))
      ]
    )


class HighSwitchTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TestHighSwitch)
