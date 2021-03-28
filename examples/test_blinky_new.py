import unittest

from edg import *


class NewBlinkyEmpty(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()


class NewBlinkyOvervolt(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Lpc1549_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.digital[0], self.led.signal)
    self.connect(self.mcu.gnd, self.led.gnd)
    self.jack = self.Block(Pj_102a(voltage_out=5*Volt(tol=0.1)))
    self.swd = self.Block(SwdCortexTargetHeader())
    self.connect(self.jack.pwr, self.mcu.pwr, self.swd.pwr)
    self.connect(self.swd.swd, self.mcu.swd)
    self.connect(self.mcu.gnd, self.swd.gnd, self.jack.gnd)


class NewBlinkyBuck(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Lpc1549_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.digital[0], self.led.signal)
    self.connect(self.mcu.gnd, self.led.gnd)
    self.jack = self.Block(Pj_102a(voltage_out=5*Volt(tol=0.1)))
    self.swd = self.Block(SwdCortexTargetHeader())
    self.connect(self.mcu.pwr, self.swd.pwr)
    self.connect(self.swd.swd, self.mcu.swd)
    self.connect(self.mcu.gnd, self.swd.gnd, self.jack.gnd)
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.connect(self.jack.pwr, self.buck.pwr_in)
    self.connect(self.jack.gnd, self.buck.gnd)
    self.connect(self.mcu.pwr, self.buck.pwr_out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class NewBlinkyRefactored(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.jack = self.Block(Pj_102a(voltage_out=5*Volt(tol=0.1)))
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.connect(self.jack.pwr, self.buck.pwr_in)
    self.connect(self.jack.gnd, self.buck.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.jack.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48())
      self.swd = imp.Block(SwdCortexTargetHeader())
      self.connect(self.swd.swd, self.mcu.swd)

      self.led = ElementDict()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.digital[i], self.led[i].signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class BlinkyNewTestCase(unittest.TestCase):
  def test_design_empty(self) -> None:
    compile_board_inplace(NewBlinkyEmpty)

  def test_design_broken(self) -> None:
    with self.assertRaises(CompilerCheckError):
      compile_board_inplace(NewBlinkyOvervolt)

  def test_design_buck(self) -> None:
    compile_board_inplace(NewBlinkyBuck)

  def test_design_refactored(self) -> None:
    compile_board_inplace(NewBlinkyRefactored)
