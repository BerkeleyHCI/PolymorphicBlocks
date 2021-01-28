import unittest
import sys

from . import *
from .SimpleConstProp import *


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

    self.assign(self.range_const, (1.0, 42.0))
    self.assign(self.range_param, self.range_const)

    self.block = self.Block(TestConstPropInternal())
    self.assign(self.block.float_param, self.float_param)
    self.assign(self.block.range_param, self.range_param)


class ConstPropTestCase(unittest.TestCase):
  def setUp(self) -> None:
    driver = Driver([sys.modules[__name__]])
    design = driver.generate_block(TestParameterConstProp())
    with open("TestParameterConstProp.edg", 'wb') as f:
      f.write(design.SerializeToString())

    self.const_prop = SimpleConstPropTransform()
    self.const_prop.transform_design(design)

  def test_float_prop(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_param('float_const')),
                     2.0)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block').append_param('float_param')),
                     2.0)

  def test_range_prop(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_param('range_const')),
                     Interval(1.0, 42.0))
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block').append_param('range_param')),
                     Interval(1.0, 42.0))

  def test_range_subset(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_param('range_subset')),
                     SubsetInterval(3.0, 18.0))

  def test_range_override(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_param('range_override')),
                     Interval(10.0, 11.0))


class TestPortConstPropLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.a = self.Port(TestPortConstPropPort())
    self.b = self.Port(TestPortConstPropPort())

    self.constrain(self.a.float_param == self.b.float_param)


class TestPortConstPropPort(Port[TestPortConstPropLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = TestPortConstPropLink
    self.float_param = self.Parameter(FloatExpr())


class TestPortConstPropInnerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(TestPortConstPropPort())


class TestPortConstPropTopBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.export = self.Port(TestPortConstPropPort())

  def contents(self) -> None:
    self.block1 = self.Block(TestPortConstPropInnerBlock())
    self.block2 = self.Block(TestPortConstPropInnerBlock())
    self.link = self.connect(self.block1.port, self.block2.port)
    self.constrain(self.block1.port.float_param == 3.1)

    self.export_block = self.Block(TestPortConstPropInnerBlock())
    self.connect(self.export_block.port, self.export)
    self.constrain(self.export_block.port.float_param == 6.0)


class ConstPropPortTestCase(unittest.TestCase):
  def setUp(self) -> None:
    driver = Driver([sys.modules[__name__]])
    design = driver.generate_block(TestPortConstPropTopBlock())
    with open("TestPortConstPropTopBlock.edg", 'wb') as f:
      f.write(design.SerializeToString())

    self.const_prop = SimpleConstPropTransform()
    self.const_prop.transform_design(design)

  def test_port_param_prop(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block1').append_port('port').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_port('a').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_port('b').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block2').append_port('port').append_param('float_param')),
                     3.1)

    # TODO this technically isn't fully connected to a link
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_port('export').append_param('float_param')),
                     6.0)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('export_block').append_port('port').append_param('float_param')),
                     6.0)

  def test_unconnected_link(self) -> None:
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_port('export')),
                     None)
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('export_block').append_port('port')),
                     None)

  def test_connected_link(self) -> None:
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block1').append_port('port')),
                     tfu.Path.empty().append_link('link').append_port('a'))
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block2').append_port('port')),
                     tfu.Path.empty().append_link('link').append_port('b'))


class TestPortConstPropBundleLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.a = self.Port(TestPortConstPropBundle())
    self.b = self.Port(TestPortConstPropBundle())

    self.elt1_link = self.connect(self.a.elt1, self.b.elt1)
    self.elt2_link = self.connect(self.a.elt2, self.b.elt2)


class TestPortConstPropBundle(Bundle[TestPortConstPropBundleLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = TestPortConstPropBundleLink

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
    self.block2 = self.Block(TestPortConstPropBundleInnerBlock())
    self.link = self.connect(self.block1.port, self.block2.port)

    self.constrain(self.block1.port.elt1.float_param == 3.1)
    self.constrain(self.block1.port.elt2.float_param == 6.0)


class ConstPropBundleTestCase(unittest.TestCase):
  def setUp(self) -> None:
    driver = Driver([sys.modules[__name__]])
    design = driver.generate_block(TestPortConstPropBundleTopBlock())
    with open("TestPortConstPropBundleTopBlock.edg", 'wb') as f:
      f.write(design.SerializeToString())

    self.const_prop = SimpleConstPropTransform()
    self.const_prop.transform_design(design)

  def test_port_param_prop(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block1').append_port('port').append_port('elt1').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block1').append_port('port').append_port('elt2').append_param('float_param')),
                     6.0)

    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_port('a').append_port('elt1').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_port('a').append_port('elt2').append_param('float_param')),
                     6.0)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_link('elt1_link').append_port('a').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_link('elt2_link').append_port('a').append_param('float_param')),
                     6.0)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_link('elt1_link').append_port('b').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_link('elt2_link').append_port('b').append_param('float_param')),
                     6.0)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_port('b').append_port('elt1').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_port('b').append_port('elt2').append_param('float_param')),
                     6.0)

    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block2').append_port('port').append_port('elt1').append_param('float_param')),
                     3.1)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_block('block2').append_port('port').append_port('elt2').append_param('float_param')),
                     6.0)

  def test_connected_link(self) -> None:
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block1').append_port('port')),
                     tfu.Path.empty().append_link('link').append_port('a'))
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block2').append_port('port')),
                     tfu.Path.empty().append_link('link').append_port('b'))

    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block1').append_port('port').append_port('elt1')),
                     tfu.Path.empty().append_link('link').append_link('elt1_link').append_port('a'))
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block2').append_port('port').append_port('elt1')),
                     tfu.Path.empty().append_link('link').append_link('elt1_link').append_port('b'))

    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block1').append_port('port').append_port('elt2')),
                     tfu.Path.empty().append_link('link').append_link('elt2_link').append_port('a'))
    self.assertEqual(self.const_prop.get_port_link(tfu.Path.empty().append_block('block2').append_port('port').append_port('elt2')),
                     tfu.Path.empty().append_link('link').append_link('elt2_link').append_port('b'))

