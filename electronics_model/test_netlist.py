import unittest

from typing import Type
from edg_core import *
from .footprint import Pin, Block as FBlock  # TODO cleanup naming
from .CircuitBlock import FootprintBlock
from .VoltagePorts import VoltageSource, VoltageSink
from .NetlistGenerator import NetlistTransform


class TestFakeSource(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pos = self.Port(VoltageSource())
    self.neg = self.Port(VoltageSource())

  def contents(self) -> None:
    super().contents()
    self.footprint(  # beefy (ok, not really) capacitor
      'C', 'Capacitor_SMD:C_0603_1608Metric',
      {
        '1': self.pos,
        '2': self.neg
      },
      value='1uF'
    )


@abstract_block
class TestBaseFakeSink(Block):  # abstract base class to support multipacking
  def __init__(self) -> None:
    super().__init__()

    self.pos = self.Port(VoltageSink())
    self.neg = self.Port(VoltageSink())


class TestFakeSink(TestBaseFakeSink, FootprintBlock):
  def contents(self) -> None:
    super().contents()
    self.footprint(  # load resistor
      'R', 'Resistor_SMD:R_0603_1608Metric',
      {
        '1': self.pos,
        '2': self.neg
      },
      value='1k'
    )


class TestBasicCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.source = self.Block(TestFakeSource())
    self.sink = self.Block(TestFakeSink())

    self.vpos = self.connect(self.source.pos, self.sink.pos)
    self.gnd = self.connect(self.source.neg, self.sink.neg)


class TestMultisinkCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.source = self.Block(TestFakeSource())
    self.sink1 = self.Block(TestFakeSink())
    self.sink2 = self.Block(TestFakeSink())  # TODO make it 4.7k so it's different value

    self.vpos = self.connect(self.source.pos, self.sink1.pos, self.sink2.pos)
    self.gnd = self.connect(self.source.neg, self.sink1.neg, self.sink2.neg)


class TestFakeAdapter(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pos_in = self.Port(VoltageSink())
    self.pos_out = self.Port(VoltageSource())
    self.neg = self.Port(VoltageSink())

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
      {
        '1': self.neg,
        '2': self.pos_out,
        '3': self.pos_in,
      },
      value='LD1117V33'  # not quite correct but roll with it
    )


class TestMultinetCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.source = self.Block(TestFakeSource())
    self.adapter = self.Block(TestFakeAdapter())
    self.sink = self.Block(TestFakeSink())

    self.vin = self.connect(self.source.pos, self.adapter.pos_in)
    self.vout = self.connect(self.adapter.pos_out, self.sink.pos)
    self.gnd = self.connect(self.source.neg, self.adapter.neg, self.sink.neg)


class TestFakeSinkHierarchy(Block):
  def __init__(self) -> None:
    super().__init__()

    self.pos = self.Port(VoltageSink.empty())
    self.neg = self.Port(VoltageSink.empty())

  def contents(self) -> None:
    super().contents()

    self.block = self.Block(TestFakeSink())

    self.vpos = self.connect(self.pos, self.block.pos)
    self.vneg = self.connect(self.neg, self.block.neg)


class TestHierarchyCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.source = self.Block(TestFakeSource())
    self.sink = self.Block(TestFakeSinkHierarchy())

    self.vpos = self.connect(self.source.pos, self.sink.pos)
    self.gnd = self.connect(self.source.neg, self.sink.neg)


class TestFakeDualSinkHierarchy(Block):
  def __init__(self) -> None:
    super().__init__()

    self.pos = self.Port(VoltageSink.empty())
    self.neg = self.Port(VoltageSink.empty())

  def contents(self) -> None:
    super().contents()

    self.block1 = self.Block(TestFakeSink())
    self.block2 = self.Block(TestFakeSink())

    self.vpos = self.connect(self.pos, self.block1.pos, self.block2.pos)
    self.vneg = self.connect(self.neg, self.block1.neg, self.block2.neg)


class TestDualHierarchyCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.source = self.Block(TestFakeSource())
    self.sink = self.Block(TestFakeDualSinkHierarchy())

    self.vpos = self.connect(self.source.pos, self.sink.pos)
    self.gnd = self.connect(self.source.neg, self.sink.neg)


class NetlistTestCase(unittest.TestCase):
  def generate_net(self, design: Type[Block]):
    compiled = ScalaCompiler.compile(design)
    return NetlistTransform(compiled).run()

  def test_basic_netlist(self) -> None:
    net = self.generate_net(TestBasicCircuit)

    self.assertEqual(net.nets['vpos'], {
      Pin('source', '1'),
      Pin('sink', '1')
    })
    self.assertEqual(net.nets['gnd'], {
      Pin('source', '2'),
      Pin('sink', '2')
    })
    self.assertEqual(net.blocks['source'], FBlock('Capacitor_SMD:C_0603_1608Metric', '1uF',
                                                  ['source'], ['electronics_model.test_netlist.TestFakeSource']))
    self.assertEqual(net.blocks['sink'], FBlock('Resistor_SMD:R_0603_1608Metric', '1k',
                                                ['sink'], ['electronics_model.test_netlist.TestFakeSink']))

  def test_multisink_netlist(self) -> None:
    net = self.generate_net(TestMultisinkCircuit)

    self.assertEqual(net.nets['vpos'], {
      Pin('source', '1'),
      Pin('sink1', '1'),
      Pin('sink2', '1')
    })
    self.assertEqual(net.nets['gnd'], {
      Pin('source', '2'),
      Pin('sink1', '2'),
      Pin('sink2', '2')
    })
    self.assertEqual(net.blocks['source'], FBlock('Capacitor_SMD:C_0603_1608Metric', '1uF',
                                                  ['source'], ['electronics_model.test_netlist.TestFakeSource']))
    self.assertEqual(net.blocks['sink1'], FBlock('Resistor_SMD:R_0603_1608Metric', '1k',
                                                 ['sink1'], ['electronics_model.test_netlist.TestFakeSink']))
    self.assertEqual(net.blocks['sink2'], FBlock('Resistor_SMD:R_0603_1608Metric', '1k',
                                                 ['sink2'], ['electronics_model.test_netlist.TestFakeSink']))

  def test_multinet_netlist(self) -> None:
    net = self.generate_net(TestMultinetCircuit)

    self.assertEqual(net.nets['vin'], {
      Pin('source', '1'),
      Pin('adapter', '3')
    })
    self.assertEqual(net.nets['vout'], {
      Pin('adapter', '2'),
      Pin('sink', '1')
    })
    self.assertEqual(net.nets['gnd'], {
      Pin('source', '2'),
      Pin('adapter', '1'),
      Pin('sink', '2')
    })
    self.assertEqual(net.blocks['source'], FBlock('Capacitor_SMD:C_0603_1608Metric', '1uF',
                                                  ['source'], ['electronics_model.test_netlist.TestFakeSource']))
    self.assertEqual(net.blocks['adapter'], FBlock('Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'LD1117V33',
                                                   ['adapter'], ['electronics_model.test_netlist.TestFakeAdapter']))
    self.assertEqual(net.blocks['sink'], FBlock('Resistor_SMD:R_0603_1608Metric', '1k',
                                                ['sink'], ['electronics_model.test_netlist.TestFakeSink']))

  def test_hierarchy_netlist(self) -> None:
    net = self.generate_net(TestHierarchyCircuit)

    self.assertEqual(net.nets['vpos'], {
      Pin('source', '1'),
      Pin('sink', '1')
    })
    self.assertEqual(net.nets['gnd'], {
      Pin('source', '2'),
      Pin('sink', '2')
    })
    self.assertEqual(net.blocks['source'], FBlock('Capacitor_SMD:C_0603_1608Metric', '1uF',
                                                  ['source'], ['electronics_model.test_netlist.TestFakeSource']))
    self.assertEqual(net.blocks['sink'], FBlock('Resistor_SMD:R_0603_1608Metric', '1k',
                                                ['sink'], ['electronics_model.test_netlist.TestFakeSinkHierarchy']))

  def test_dual_hierarchy_netlist(self) -> None:
    net = self.generate_net(TestDualHierarchyCircuit)

    self.assertEqual(net.nets['vpos'], {
      Pin('source', '1'),
      Pin('sink.block1', '1'),
      Pin('sink.block2', '1')
    })
    self.assertEqual(net.nets['gnd'], {
      Pin('source', '2'),
      Pin('sink.block1', '2'),
      Pin('sink.block2', '2')
    })
    self.assertEqual(net.blocks['source'], FBlock('Capacitor_SMD:C_0603_1608Metric', '1uF',
                                                  ['source'], ['electronics_model.test_netlist.TestFakeSource']))
    self.assertEqual(net.blocks['sink.block1'], FBlock('Resistor_SMD:R_0603_1608Metric', '1k',
                                                       ['sink', 'block1'],
                                                       ['electronics_model.test_netlist.TestFakeDualSinkHierarchy',
                                                        'electronics_model.test_netlist.TestFakeSink']))
    self.assertEqual(net.blocks['sink.block2'], FBlock('Resistor_SMD:R_0603_1608Metric', '1k',
                                                       ['sink', 'block2'],
                                                       ['electronics_model.test_netlist.TestFakeDualSinkHierarchy',
                                                        'electronics_model.test_netlist.TestFakeSink']))
