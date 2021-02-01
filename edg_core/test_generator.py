import unittest

from . import *
from .ScalaCompilerInterface import ScalaCompiler
from .CompilerUtils import *


class TestGeneratorAssign(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.float_param = self.Parameter(FloatExpr())
    self.add_generator(self.float_gen)

  def float_gen(self) -> None:
    self.assign(self.float_param, 2.0)


class TestGeneratorDependency(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.float_preset = self.Parameter(FloatExpr(3.0))
    self.float_param = self.Parameter(FloatExpr())
    self.add_generator(self.float_gen, self.float_preset)

  def float_gen(self) -> None:
    self.assign(self.float_param, self.get(self.float_preset) * 2)


class TestGeneratorMultiDependency(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.float_preset = self.Parameter(FloatExpr(5.0))
    self.float_param1 = self.Parameter(FloatExpr())
    self.float_param2 = self.Parameter(FloatExpr())
    self.add_generator(self.float_gen1, self.float_preset)
    self.add_generator(self.float_gen2, self.float_param1)

  def float_gen1(self) -> None:
    self.assign1 = self.assign(self.float_param1, self.get(self.float_preset) * 3)

  def float_gen2(self) -> None:
    # TODO better name inference to avoid name collisions in multiple generates
    self.assign2 = self.assign(self.float_param2, self.get(self.float_param1) + 7)


class TestGenerator(unittest.TestCase):
  def test_generator_assign(self):
    compiled_design = ScalaCompiler.compile(TestGeneratorAssign)
    solved = designSolvedValues(compiled_design)
    self.assertIn(makeSolved(['float_param'], 2.0), solved)

  def test_generator_dependency(self):
    compiled_design = ScalaCompiler.compile(TestGeneratorDependency)
    solved = designSolvedValues(compiled_design)
    self.assertIn(makeSolved(['float_param'], 6.0), solved)

  def test_generator_multi_dependency(self):
    compiled_design = ScalaCompiler.compile(TestGeneratorMultiDependency)
    solved = designSolvedValues(compiled_design)
    self.assertIn(makeSolved(['float_param1'], 15.0), solved)
    self.assertIn(makeSolved(['float_param2'], 22.0), solved)


class TestLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.source = self.Port(TestPortSource(), optional=True)
    self.sinks = self.Port(Vector(TestPortSink()), optional=True)
    self.source_float = self.Parameter(FloatExpr(self.source.float_param))
    self.sinks_range = self.Parameter(RangeExpr(self.sinks.intersection(lambda x: x.range_param)))


class TestPortSource(Port[TestLink]):
  def __init__(self, float_value: FloatLike = FloatExpr()) -> None:
    super().__init__()
    self.link_type = TestLink
    self.float_param = self.Parameter(FloatExpr(float_value))


class TestPortSink(Port[TestLink]):
  def __init__(self, range_value: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.link_type = TestLink
    self.range_param = self.Parameter(RangeExpr(range_value))


class TestBlockSource(Block):
  @init_in_parent
  def __init__(self, float_value: FloatLike = FloatExpr()) -> None:
    super().__init__()
    self.port = self.Port(TestPortSource(float_value))


class TestBlockSink(Block):
  @init_in_parent
  def __init__(self, range_value: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.port = self.Port(TestPortSink(range_value))


class TestGeneratorIsConnected(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortSource(2.0), optional=True)
    self.add_generator(self.generate, self.port.is_connected())
    self.connected = self.Parameter(BoolExpr())

  def generate(self) -> None:
    if self.get(self.port.is_connected()):
      self.assign(self.connected, True)
    else:
      self.assign(self.connected, False)


class TestGeneratorConnectedTop(Block):
  def __init__(self):
    super().__init__()
    self.generator = self.Block(TestGeneratorIsConnected())
    self.sink = self.Block(TestBlockSink((0.5, 2.5)))
    self.link = self.connect(self.generator.port, self.sink.port)


class TestGeneratorNotConnectedTop(Block):
  def __init__(self):
    super().__init__()
    self.generator = self.Block(TestGeneratorIsConnected())


class TestGeneratorInnerConnect(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortSource(), optional=True)
    self.add_generator(self.generate)

  def generate(self) -> None:
    self.inner = self.Block(TestBlockSource(4.5))
    self.connect(self.inner.port, self.port)


class TestGeneratorInnerConnectTop(Block):
  def __init__(self):
    super().__init__()
    self.generator = self.Block(TestGeneratorInnerConnect())
    self.sink = self.Block(TestBlockSink((1.5, 3.5)))
    self.link = self.connect(self.generator.port, self.sink.port)


class TestGeneratorConnect(unittest.TestCase):
  def test_generator_connected(self):
    compiled_design = ScalaCompiler.compile(TestGeneratorConnectedTop)
    solved = designSolvedValues(compiled_design)
    self.assertIn(makeSolved(['generator', 'connected'], True), solved)
    self.assertIn(makeSolved(['link', 'source_float'], 2.0), solved)
    self.assertIn(makeSolved(['link', 'sinks_range'], (0.5, 2.5)), solved)

  def test_generator_not_connected(self):
    compiled_design = ScalaCompiler.compile(TestGeneratorNotConnectedTop)
    solved = designSolvedValues(compiled_design)
    self.assertIn(makeSolved(['generator', 'connected'], False), solved)

  def test_generator_inner_connect(self):
    compiled_design = ScalaCompiler.compile(TestGeneratorInnerConnectTop)
    solved = designSolvedValues(compiled_design)
    self.assertIn(makeSolved(['link', 'source_float'], 4.5), solved)
    self.assertIn(makeSolved(['link', 'sinks_range'], (1.5, 3.5)), solved)


class TestGeneratorException(BaseException):
  pass


class TestGeneratorFailure(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.float_param = self.Parameter(FloatExpr(41.0))
    self.add_generator(self.errorfn, self.float_param)

  def errorfn(self) -> None:
    def helperfn() -> None:
      raise TestGeneratorException("test text")
    helperfn()


class GeneratorFailureTestCase(unittest.TestCase):
  def test_metadata(self) -> None:
    compiled_design = ScalaCompiler.compile(TestGeneratorFailure)
    pb = compiled_design.design.contents

    self.assertIn('GenerateError_errorfn', pb.meta.members.node)

    self.assertIn("TestGeneratorException",
                  pb.meta.members.node['GenerateError_errorfn'].error.message)
    self.assertIn("test text",
                  pb.meta.members.node['GenerateError_errorfn'].error.message)
    self.assertIn("float_param=41",
                  pb.meta.members.node['GenerateError_errorfn'].error.message)

    self.assertIn("errorfn",
                  pb.meta.members.node['GenerateError_errorfn'].error.traceback)
    self.assertIn("helperfn",
                  pb.meta.members.node['GenerateError_errorfn'].error.traceback)
