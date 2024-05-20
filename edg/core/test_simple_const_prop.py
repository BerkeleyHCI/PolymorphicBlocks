import unittest

from .. import edgir
from . import *


class TestConstPropInternal(Block):
  def __init__(self) -> None:
    super().__init__()

    self.float_param = self.Parameter(FloatExpr())
    self.range_param = self.Parameter(RangeExpr())


class TestParameterConstProp(Block):
  def __init__(self) -> None:
    super().__init__()

    self.float_const = self.Parameter(FloatExpr())
    self.float_param = self.Parameter(FloatExpr())

    self.range_const = self.Parameter(RangeExpr())
    self.range_param = self.Parameter(RangeExpr())

  def contents(self):
    self.assign(self.float_const, 2.0)
    self.assign(self.float_param, self.float_const)

    self.assign(self.range_const, Range(1.0, 42.0))
    self.assign(self.range_param, self.range_const)

    self.block = self.Block(TestConstPropInternal())
    self.assign(self.block.float_param, self.float_param)
    self.assign(self.block.range_param, self.range_param)


class ConstPropTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.compiled = ScalaCompiler.compile(TestParameterConstProp)

  def test_float_prop(self) -> None:
    self.assertEqual(self.compiled.get_value(['float_const']), 2.0)
    self.assertEqual(self.compiled.get_value(['block', 'float_param']), 2.0)

  def test_range_prop(self) -> None:
    self.assertEqual(self.compiled.get_value(['range_const']), Range(1.0, 42.0))
    self.assertEqual(self.compiled.get_value(['block', 'range_param']), Range(1.0, 42.0))


class TestPortConstPropLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.a = self.Port(TestPortConstPropPort())
    self.b = self.Port(TestPortConstPropPort())

    self.a_float_param = self.Parameter(FloatExpr())
    self.b_float_param = self.Parameter(FloatExpr())

    self.assign(self.a_float_param, self.a.float_param)
    self.assign(self.b_float_param, self.b.float_param)


class TestPortConstPropPort(Port[TestPortConstPropLink]):
  link_type = TestPortConstPropLink

  def __init__(self) -> None:
    super().__init__()
    self.float_param = self.Parameter(FloatExpr())


class TestPortConstPropInnerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortConstPropPort(), optional=True)


class TestPortConstPropOuterBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.inner = self.Block(TestPortConstPropInnerBlock())
    self.port = self.Port(TestPortConstPropPort())
    self.connect(self.inner.port, self.port)


class TestPortConstPropTopBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block1 = self.Block(TestPortConstPropInnerBlock())
    self.block2 = self.Block(TestPortConstPropOuterBlock())  # dummy, just to infer a connection
    self.link = self.connect(self.block1.port, self.block2.port)
    self.assign(self.block1.port.float_param, 3.5)


class ConstPropPortTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.compiled = ScalaCompiler.compile(TestPortConstPropTopBlock)

  def test_port_param_prop(self) -> None:
    self.assertEqual(self.compiled.get_value(['block1', 'port', 'float_param']), 3.5)
    self.assertEqual(self.compiled.get_value(['link', 'a', 'float_param']), 3.5)
    self.assertEqual(self.compiled.get_value(['link', 'a_float_param']), 3.5)

  def test_connected_link(self) -> None:
    self.assertEqual(self.compiled.get_value(['block1', 'port', edgir.IS_CONNECTED]), True)
    self.assertEqual(self.compiled.get_value(['block2', 'port', edgir.IS_CONNECTED]), True)
    self.assertEqual(self.compiled.get_value(['block2', 'inner', 'port', edgir.IS_CONNECTED]), True)


class TestDisconnectedTopBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block1 = self.Block(TestPortConstPropInnerBlock())
    self.assign(self.block1.port.float_param, 3.5)


class DisconnectedPortTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.compiled = ScalaCompiler.compile(TestDisconnectedTopBlock)

  def test_disconnected_link(self) -> None:
    self.assertEqual(self.compiled.get_value(['block1', 'port', edgir.IS_CONNECTED]), False)


class TestPortConstPropBundleLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.a = self.Port(TestPortConstPropBundle())
    self.b = self.Port(TestPortConstPropBundle())

    self.elt1_link = self.connect(self.a.elt1, self.b.elt1)
    self.elt2_link = self.connect(self.a.elt2, self.b.elt2)


class TestPortConstPropBundle(Bundle[TestPortConstPropBundleLink]):
  link_type = TestPortConstPropBundleLink

  def __init__(self) -> None:
    super().__init__()
    self.elt1 = self.Port(TestPortConstPropPort())
    self.elt2 = self.Port(TestPortConstPropPort())


class TestPortConstPropBundleInnerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortConstPropBundle())


class TestPortConstPropBundleTopBlock(Block):
  def __init__(self) -> None:
    super().__init__()

  def contents(self) -> None:
    self.block1 = self.Block(TestPortConstPropBundleInnerBlock())
    self.block2 = self.Block(TestPortConstPropBundleInnerBlock())  # dummy, just to infer a connection
    self.link = self.connect(self.block1.port, self.block2.port)

    self.assign(self.block1.port.elt1.float_param, 3.5)
    self.assign(self.block1.port.elt2.float_param, 6.0)


class ConstPropBundleTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.compiled = ScalaCompiler.compile(TestPortConstPropBundleTopBlock)

  def test_port_param_prop(self) -> None:
    self.assertEqual(self.compiled.get_value(['block1', 'port', 'elt1', 'float_param']), 3.5)
    self.assertEqual(self.compiled.get_value(['block1', 'port', 'elt2', 'float_param']), 6.0)

    self.assertEqual(self.compiled.get_value(['link', 'a', 'elt1', 'float_param']), 3.5)
    self.assertEqual(self.compiled.get_value(['link', 'a', 'elt2', 'float_param']), 6.0)

    self.assertEqual(self.compiled.get_value(['link', 'elt1_link', 'a', 'float_param']), 3.5)
    self.assertEqual(self.compiled.get_value(['link', 'elt2_link', 'a', 'float_param']), 6.0)

    self.assertEqual(self.compiled.get_value(['link', 'elt1_link', 'a_float_param']), 3.5)
    self.assertEqual(self.compiled.get_value(['link', 'elt2_link', 'a_float_param']), 6.0)

  def test_connected_link(self) -> None:
    self.assertEqual(self.compiled.get_value(['block1', 'port', edgir.IS_CONNECTED]), True)
    self.assertEqual(self.compiled.get_value(['block2', 'port', edgir.IS_CONNECTED]), True)
    # Note: inner ports IS_CONNECTED is not defined

    self.assertEqual(self.compiled.get_value(['link', 'a', edgir.IS_CONNECTED]), True)
    self.assertEqual(self.compiled.get_value(['link', 'b', edgir.IS_CONNECTED]), True)

    self.assertEqual(self.compiled.get_value(['link', 'elt1_link', 'a', edgir.IS_CONNECTED]), True)
    self.assertEqual(self.compiled.get_value(['link', 'elt1_link', 'b', edgir.IS_CONNECTED]), True)
    self.assertEqual(self.compiled.get_value(['link', 'elt2_link', 'a', edgir.IS_CONNECTED]), True)
    self.assertEqual(self.compiled.get_value(['link', 'elt2_link', 'b', edgir.IS_CONNECTED]), True)
