import unittest

from . import *
from .ScalaCompilerInterface import ScalaCompiler, ScalaCompilerInstance


class TestGeneratorAssign(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorAssign())


class GeneratorAssign(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    # Because this doesn't have dependency parameters, this is the top-level design
    self.float_param = self.Parameter(FloatExpr())
    self.generator(self.float_gen)

  def float_gen(self) -> None:
    self.assign(self.float_param, 2.0)


class TestGeneratorDependency(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorDependency(3.0))


class GeneratorDependency(GeneratorBlock):
  @init_in_parent
  def __init__(self, float_preset: FloatLike) -> None:
    super().__init__()
    self.float_param = self.Parameter(FloatExpr())
    self.generator(self.float_gen, float_preset)

  def float_gen(self, float_preset: float) -> None:
    self.assign(self.float_param, float_preset * 2)


class TestGeneratorMultiParameter(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorMultiParameter(5.0, 10.0))


class GeneratorMultiParameter(GeneratorBlock):
  @init_in_parent
  def __init__(self, float_preset1: FloatLike, float_preset2: FloatLike) -> None:
    super().__init__()
    self.float_param1 = self.Parameter(FloatExpr())
    self.float_param2 = self.Parameter(FloatExpr())
    self.generator(self.float_gen, float_preset1, float_preset2)

  def float_gen(self, float_preset1: float, float_preset2: float) -> None:
    self.assign1 = self.assign(self.float_param1, float_preset1 * 3)
    self.assign2 = self.assign(self.float_param2, float_preset2 + 7)


class TestGenerator(unittest.TestCase):
  def test_generator_assign(self):
    compiled = ScalaCompiler.compile(TestGeneratorAssign)

    self.assertEqual(compiled.get_value(['block', 'float_param']), 2.0)

  def test_generator_dependency(self):
    compiled = ScalaCompiler.compile(TestGeneratorDependency)

    self.assertEqual(compiled.get_value(['block', 'float_param']), 6.0)

  def test_generator_multi_dependency(self):
    compiled = ScalaCompiler.compile(TestGeneratorMultiParameter)

    self.assertEqual(compiled.get_value(['block', 'float_param1']), 15.0)
    self.assertEqual(compiled.get_value(['block', 'float_param2']), 17.0)


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
  def __init__(self, float_value: FloatLike) -> None:
    super().__init__()
    self.port = self.Port(TestPortSource(float_value))


class TestBlockSink(Block):
  @init_in_parent
  def __init__(self, range_value: RangeLike) -> None:
    super().__init__()
    self.port = self.Port(TestPortSink(range_value))


class GeneratorIsConnected(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortSource(2.0), optional=True)
    self.generator(self.generate_assign, self.port.is_connected())
    self.connected = self.Parameter(BoolExpr())

  def generate_assign(self, connected: bool) -> None:
    if connected:
      self.assign(self.connected, True)
    else:
      self.assign(self.connected, False)


class TestGeneratorConnectedTop(Block):
  def __init__(self):
    super().__init__()
    self.generator = self.Block(GeneratorIsConnected())
    self.sink = self.Block(TestBlockSink((0.5, 2.5)))
    self.link = self.connect(self.generator.port, self.sink.port)


class TestGeneratorNotConnectedTop(Block):
  def __init__(self):
    super().__init__()
    self.generator = self.Block(GeneratorIsConnected())


class GeneratorInnerConnect(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortSource(), optional=True)
    self.generator(self.generate)

  def generate(self) -> None:
    self.inner = self.Block(TestBlockSource(4.5))
    self.connect(self.inner.port, self.port)


class TestGeneratorInnerConnectTop(Block):
  def __init__(self):
    super().__init__()
    self.generator = self.Block(GeneratorInnerConnect())
    self.sink = self.Block(TestBlockSink((1.5, 3.5)))
    self.link = self.connect(self.generator.port, self.sink.port)


class TestGeneratorConnect(unittest.TestCase):
  def test_generator_connected(self):
    compiled = ScalaCompiler.compile(TestGeneratorConnectedTop)

    self.assertEqual(compiled.get_value(['generator', 'connected']), True)
    self.assertEqual(compiled.get_value(['link', 'source_float']), 2.0)
    self.assertEqual(compiled.get_value(['link', 'sinks_range']), Range(0.5, 2.5))

  def test_generator_not_connected(self):
    compiled = ScalaCompiler.compile(TestGeneratorNotConnectedTop)

    self.assertEqual(compiled.get_value(['generator', 'connected']), False)

  def test_generator_inner_connect(self):
    compiled = ScalaCompiler.compile(TestGeneratorInnerConnectTop)

    self.assertEqual(compiled.get_value(['link', 'source_float']), 4.5)
    self.assertEqual(compiled.get_value(['link', 'sinks_range']), Range(1.5, 3.5))


class TestGeneratorException(BaseException):
  pass


class TestGeneratorFailure(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorFailure())


class GeneratorFailure(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.generator(self.errorfn)

  def errorfn(self) -> None:
    def helperfn() -> None:
      raise TestGeneratorException("test text")
    helperfn()


class GeneratorFailureTestCase(unittest.TestCase):
  def test_metadata(self) -> None:
    # if we don't suppress the output, the error from the generator propagates to the test console
    compiler = ScalaCompilerInstance(suppress_stderr=True)
    with self.assertRaises(CompilerCheckError) as context:
      compiler.compile(TestGeneratorFailure)
    compiler.close()  # if we don't close it, we get a ResourceWarning
