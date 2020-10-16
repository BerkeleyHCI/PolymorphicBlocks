import os
import unittest
import sys

from edg import *


class LightsConnector(Connector, CircuitBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSink(), [Power])
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

    self.pwr = self.Port(ElectricalSink(), [Power])
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


class TestHighSwitch(CircuitBlock):
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

      (self.can, ), _ = self.chain(self.mcu.new_io(CanControllerPort, pin=[43, 44]), imp.Block(CalSolCanBlock()))

      (self.vsense, ), _ = self.chain(
        self.pwr_conn.pwr,
        imp.Block(VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)),
        self.mcu.new_io(AnalogSink, pin=21))

      self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # CAN RGB
      self.connect(self.mcu.new_io(DigitalBidir, pin=28), self.rgb1.red)
      self.connect(self.mcu.new_io(DigitalBidir, pin=23), self.rgb1.green)
      self.connect(self.mcu.new_io(DigitalBidir, pin=22), self.rgb1.blue)

      self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # system RGB 2
      self.connect(self.mcu.new_io(DigitalBidir, pin=18), self.rgb2.red)
      self.connect(self.mcu.new_io(DigitalBidir, pin=15), self.rgb2.green)
      self.connect(self.mcu.new_io(DigitalBidir, pin=13), self.rgb2.blue)

    self.limit_light_current = self.Block(ForcedElectricalCurrentDraw((0, 2.5)*Amp))
    self.connect(self.pwr_conn.pwr, self.limit_light_current.pwr_in)
    with self.implicit_connect(
        ImplicitConnect(self.limit_light_current.pwr_out, [Power]),
        ImplicitConnect(self.pwr.gnd, [Common]),
    ) as imp:
      self.light = ElementDict[LightsDriver]()
      for i in range(4):
        light = self.light[i] = imp.Block(LightsDriver((0, 0.5) * Amp))

      self.connect(self.mcu.new_io(DigitalBidir, pin=12), self.light[0].control[0])
      self.connect(self.mcu.new_io(DigitalBidir, pin=8), self.light[0].control[1])
      self.connect(self.mcu.new_io(DigitalBidir, pin=7), self.light[1].control[0])
      self.connect(self.mcu.new_io(DigitalBidir, pin=6), self.light[1].control[1])
      self.connect(self.mcu.new_io(DigitalBidir, pin=4), self.light[2].control[0])
      self.connect(self.mcu.new_io(DigitalBidir, pin=3), self.light[2].control[1])
      self.connect(self.mcu.new_io(DigitalBidir, pin=2), self.light[3].control[0])
      self.connect(self.mcu.new_io(DigitalBidir, pin=1), self.light[3].control[1])

      for i in range(2):
        light = self.light[4+i] = imp.Block(LightsDriver((0, 3) * Amp))

      self.connect(self.mcu.new_io(DigitalBidir, pin=48), self.light[4].control[0])
      self.connect(self.mcu.new_io(DigitalBidir, pin=47), self.light[4].control[1])
      self.connect(self.mcu.new_io(DigitalBidir, pin=46), self.light[5].control[0])
      self.connect(self.mcu.new_io(DigitalBidir, pin=45), self.light[5].control[1])

    self.hole = ElementDict[MountingHole]()
    for i in range(4):
      self.hole[i] = self.Block(MountingHole_M4())


class HighSwitchTestCase(unittest.TestCase):
  def test_design(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      TestHighSwitch(),
      os.path.splitext(__file__)[0]
    )
