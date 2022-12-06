import unittest

from . import *


class AnalogSourceBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(AnalogSource())


class AnalogSinkInfiniteBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(AnalogSink(
      impedance=RangeExpr.INF,
    ))


class AnalogSinkOneOhmBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(AnalogSink(
      impedance=(1, 1)*Ohm,
    ))


class AnalogTwoInfiniteTest(Block):
  def __init__(self):
    super().__init__()
    self.source = self.Block(AnalogSourceBlock())
    self.sink1 = self.Block(AnalogSinkInfiniteBlock())
    self.sink2 = self.Block(AnalogSinkInfiniteBlock())
    self.link = self.connect(self.source.port, self.sink1.port, self.sink2.port)


class AnalogTwoOneOhmTest(Block):
  def __init__(self):
    super().__init__()
    self.source = self.Block(AnalogSourceBlock())
    self.sink1 = self.Block(AnalogSinkOneOhmBlock())
    self.sink2 = self.Block(AnalogSinkOneOhmBlock())
    self.link = self.connect(self.source.port, self.sink1.port, self.sink2.port)


class AnalogMixedTest(Block):
  def __init__(self):
    super().__init__()
    self.source = self.Block(AnalogSourceBlock())
    self.sink1 = self.Block(AnalogSinkInfiniteBlock())
    self.sink2 = self.Block(AnalogSinkOneOhmBlock())
    self.link = self.connect(self.source.port, self.sink1.port, self.sink2.port)


class AnalogLinkTestCase(unittest.TestCase):
  def test_analog_two_infinite(self) -> None:
    compiled = ScalaCompiler.compile(AnalogTwoInfiniteTest)
    self.assertEqual(compiled.get_value(['link', 'sink_impedance']),
                     Range(float('inf'), float('inf')))

  def test_analog_two_one_ohm(self) -> None:
    compiled = ScalaCompiler.compile(AnalogTwoOneOhmTest)
    self.assertEqual(compiled.get_value(['link', 'sink_impedance']),
                     Range(0.5, 0.5))

  def test_analog_mixed(self) -> None:
    compiled = ScalaCompiler.compile(AnalogMixedTest)
    self.assertEqual(compiled.get_value(['link', 'sink_impedance']),
                     Range(1.0, 1.0))
