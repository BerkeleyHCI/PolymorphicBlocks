import unittest
from typing import Type, List

import edgir
from edg_core import *
from .CircuitBlock import FootprintBlock
from .NetlistGenerator import NetlistTransform, NetPin as RawNetPin, NetBlock as RawNetBlock, Net
from .RefdesRefinementPass import RefdesRefinementPass
from .VoltagePorts import VoltageSource, VoltageSink


# wrapper / convenience constructors
def NetPin(block_path: List[str], pin_name: str) -> RawNetPin:
  return RawNetPin(TransformUtil.Path(tuple(block_path), (), (), ()), pin_name)

def NetBlock(footprint: str, refdes: str, part: str, value: str, full_path: List[str], path: List[str],
             class_path: List[str]) -> RawNetBlock:
  return RawNetBlock(footprint, refdes, part, value,
                     TransformUtil.Path(tuple(full_path), (), (), ()), path,
                     [edgir.libpath(cls) for cls in class_path])


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

    self.pos = self.Port(VoltageSink.empty())
    self.neg = self.Port(VoltageSink.empty())


class TestFakeSink(TestBaseFakeSink, FootprintBlock):
  def contents(self) -> None:
    super().contents()
    self.pos.init_from(VoltageSink())
    self.neg.init_from(VoltageSink())
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
  @staticmethod
  def generate_net(design: Type[Block], refinements: Refinements = Refinements()):
    compiled = ScalaCompiler.compile(design, refinements)
    compiled.append_values(RefdesRefinementPass().run(compiled))
    return NetlistTransform(compiled).run()

  def test_basic_netlist(self) -> None:
    net = self.generate_net(TestBasicCircuit)

    self.assertIn(Net('vpos', [
      NetPin(['source'], '1'),
      NetPin(['sink'], '1')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink').append_port('pos'),
    ]), net.nets)
    self.assertIn(Net('gnd', [
      NetPin(['source'], '2'),
      NetPin(['sink'], '2')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink').append_port('neg'),
    ]), net.nets)
    self.assertIn(NetBlock('Capacitor_SMD:C_0603_1608Metric', 'C1', '', '1uF',
                           ['source'], ['source'],
                           ['electronics_model.test_netlist.TestFakeSource']), net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                           ['sink'], ['sink'],
                           ['electronics_model.test_netlist.TestFakeSink']), net.blocks)

  def test_multisink_netlist(self) -> None:
    net = self.generate_net(TestMultisinkCircuit)

    self.assertIn(Net('vpos', [
      NetPin(['source'], '1'),
      NetPin(['sink1'], '1'),
      NetPin(['sink2'], '1')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink1').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink2').append_port('pos'),
    ]), net.nets)
    self.assertIn(Net('gnd', [
      NetPin(['source'], '2'),
      NetPin(['sink1'], '2'),
      NetPin(['sink2'], '2')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink1').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink2').append_port('neg'),
    ]), net.nets)
    self.assertIn(NetBlock('Capacitor_SMD:C_0603_1608Metric', 'C1', '', '1uF',
                           ['source'], ['source'], ['electronics_model.test_netlist.TestFakeSource']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                           ['sink1'], ['sink1'], ['electronics_model.test_netlist.TestFakeSink']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R2', '', '1k',
                           ['sink2'], ['sink2'], ['electronics_model.test_netlist.TestFakeSink']),
                  net.blocks)

  def test_multinet_netlist(self) -> None:
    net = self.generate_net(TestMultinetCircuit)

    self.assertIn(Net('vin', [
      NetPin(['source'], '1'),
      NetPin(['adapter'], '3')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('pos'),
      TransformUtil.Path.empty().append_block('adapter').append_port('pos_in'),
    ]), net.nets)
    self.assertIn(Net('vout', [
      NetPin(['adapter'], '2'),
      NetPin(['sink'], '1')
    ], [
      TransformUtil.Path.empty().append_block('adapter').append_port('pos_out'),
      TransformUtil.Path.empty().append_block('sink').append_port('pos'),
    ]), net.nets)
    self.assertIn(Net('gnd', [
      NetPin(['source'], '2'),
      NetPin(['adapter'], '1'),
      NetPin(['sink'], '2')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('neg'),
      TransformUtil.Path.empty().append_block('adapter').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink').append_port('neg'),
    ]), net.nets)
    self.assertIn(NetBlock('Capacitor_SMD:C_0603_1608Metric', 'C1', '', '1uF',
                           ['source'], ['source'], ['electronics_model.test_netlist.TestFakeSource']),
                  net.blocks)
    self.assertIn(NetBlock('Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'U1', '', 'LD1117V33',
                           ['adapter'], ['adapter'], ['electronics_model.test_netlist.TestFakeAdapter']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                           ['sink'], ['sink'], ['electronics_model.test_netlist.TestFakeSink']),
                  net.blocks)

  def test_hierarchy_netlist(self) -> None:
    net = self.generate_net(TestHierarchyCircuit)

    self.assertIn(Net('vpos', [
      NetPin(['source'], '1'),
      NetPin(['sink', 'block'], '1')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink', 'block').append_port('pos'),
    ]), net.nets)
    self.assertIn(Net('gnd', [
      NetPin(['source'], '2'),
      NetPin(['sink', 'block'], '2')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink', 'block').append_port('neg'),
    ]), net.nets)
    self.assertIn(NetBlock('Capacitor_SMD:C_0603_1608Metric', 'C1', '', '1uF',
                           ['source'], ['source'], ['electronics_model.test_netlist.TestFakeSource']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                           ['sink', 'block'], ['sink'], ['electronics_model.test_netlist.TestFakeSinkHierarchy']),
                  net.blocks)

  def test_dual_hierarchy_netlist(self) -> None:
    net = self.generate_net(TestDualHierarchyCircuit)

    self.assertIn(Net('vpos', [
      NetPin(['source'], '1'),
      NetPin(['sink', 'block1'], '1'),
      NetPin(['sink', 'block2'], '1')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink', 'block1').append_port('pos'),
      TransformUtil.Path.empty().append_block('sink', 'block2').append_port('pos'),
    ]), net.nets)
    self.assertIn(Net('gnd', [
      NetPin(['source'], '2'),
      NetPin(['sink', 'block1'], '2'),
      NetPin(['sink', 'block2'], '2')
    ], [
      TransformUtil.Path.empty().append_block('source').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink', 'block1').append_port('neg'),
      TransformUtil.Path.empty().append_block('sink', 'block2').append_port('neg'),
    ]), net.nets)
    self.assertIn(NetBlock('Capacitor_SMD:C_0603_1608Metric', 'C1', '', '1uF',
                           ['source'], ['source'], ['electronics_model.test_netlist.TestFakeSource']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                           ['sink', 'block1'], ['sink', 'block1'],
                           ['electronics_model.test_netlist.TestFakeDualSinkHierarchy',
                            'electronics_model.test_netlist.TestFakeSink']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R2', '', '1k',
                           ['sink', 'block2'], ['sink', 'block2'],
                           ['electronics_model.test_netlist.TestFakeDualSinkHierarchy',
                            'electronics_model.test_netlist.TestFakeSink']),
                  net.blocks)
