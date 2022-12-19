import unittest

from edg_core import *
from .CircuitPackingBlock import PackedVoltageSource
from .footprint import Pin, Block as FBlock  # TODO cleanup naming
from .test_netlist import TestFakeSource, TestFakeSink, TestBaseFakeSink
from .test_netlist import NetlistTestCase


class TestFakeSinkElement(TestBaseFakeSink):
  # just exists to not be an abstract part
  pass


class TestPackedSink(MultipackBlock):
  def __init__(self) -> None:
    super().__init__()

    self.elements = self.PackedPart(PackedBlockArray(TestFakeSinkElement()))
    self.pos = self.PackedExport(self.elements.ports_array(lambda x: x.pos))
    self.neg = self.PackedExport(self.elements.ports_array(lambda x: x.neg))

  def contents(self) -> None:
    super().contents()

    self.pos_comb = self.Block(PackedVoltageSource())
    self.connect(self.pos, self.pos_comb.pwr_ins)
    self.neg_comb = self.Block(PackedVoltageSource())
    self.connect(self.neg, self.neg_comb.pwr_ins)

    self.device = self.Block(TestFakeSink())
    self.connect(self.device.pos, self.pos_comb.pwr_out)
    self.connect(self.device.neg, self.neg_comb.pwr_out)


class TestPackedDevices(DesignTop):
  def contents(self) -> None:
    super().contents()

    self.source = self.Block(TestFakeSource())
    self.sink1 = self.Block(TestBaseFakeSink())
    self.sink2 = self.Block(TestBaseFakeSink())

    self.vpos = self.connect(self.source.pos, self.sink1.pos, self.sink2.pos)
    self.gnd = self.connect(self.source.neg, self.sink1.neg, self.sink2.neg)

  def multipack(self) -> None:
    self.sink = self.PackedBlock(TestPackedSink())
    self.pack(self.sink.elements.request('1'), ['sink1'])
    self.pack(self.sink.elements.request('2'), ['sink2'])


class TestInvalidPackedDevices(DesignTop):
  def contents(self) -> None:
    super().contents()

    self.source1 = self.Block(TestFakeSource())
    self.sink1 = self.Block(TestBaseFakeSink())
    self.vpos1 = self.connect(self.source1.pos, self.sink1.pos)
    self.gnd1 = self.connect(self.source1.neg, self.sink1.neg)

    self.source2 = self.Block(TestFakeSource())
    self.sink2 = self.Block(TestBaseFakeSink())
    self.vpos2 = self.connect(self.source2.pos, self.sink2.pos)
    self.gnd2 = self.connect(self.source2.neg, self.sink2.neg)

  def multipack(self) -> None:
      self.sink = self.PackedBlock(TestPackedSink())
      self.pack(self.sink.elements.request('1'), ['sink1'])
      self.pack(self.sink.elements.request('2'), ['sink2'])


class MultipackNetlistTestCase(unittest.TestCase):
  def test_packed_netlist(self) -> None:
    net = NetlistTestCase.generate_net(TestPackedDevices)

    self.assertEqual(net.nets['vpos'], [
      Pin('source', '1'),
      Pin('sink.device', '1')
    ])
    self.assertEqual(net.nets['gnd'], [
      Pin('source', '2'),
      Pin('sink.device', '2')
    ])
    self.assertEqual(net.blocks['source'], FBlock('Capacitor_SMD:C_0603_1608Metric', 'C1', '', '1uF',
                                                  ['source'], ['source'],
                                                  ['electronics_model.test_netlist.TestFakeSource']))
    self.assertEqual(net.blocks['sink.device'], FBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                                                       ['sink', 'device'], ['sink', 'device'],
                                                       ['electronics_model.test_multipack_netlist.TestPackedSink',
                                                        'electronics_model.test_netlist.TestFakeSink']))

  def test_invalid_netlist(self) -> None:
    from .NetlistGenerator import InvalidPackingException
    with self.assertRaises(InvalidPackingException):
      NetlistTestCase.generate_net(TestInvalidPackedDevices)
