import unittest
from ..core import Block
from .test_netlist import NetlistTestCase, TestFakeSource, TestFakeSink, NetBlock
from . import WrapperFootprintBlock, VoltageSink


class SinkWrapperBlock(WrapperFootprintBlock):
  """Wrapper block with a single footprint for two internal sinks whose footprints are ignored."""
  def __init__(self) -> None:
    super().__init__()

    self.pos = self.Port(VoltageSink.empty())
    self.neg = self.Port(VoltageSink.empty())

  def contents(self) -> None:
    super().contents()

    self.load1 = self.Block(TestFakeSink())
    self.load2 = self.Block(TestFakeSink())
    self.connect(self.pos, self.load1.pos, self.load2.pos)
    self.connect(self.neg, self.load1.neg, self.load2.neg)

    self.footprint(  # only this footprint shows up
      'L', 'Inductor_SMD:L_0603_1608Metric',  # distinct footprint and value from internal blocks
      {
        '1': self.pos,
        '2': self.neg
      },
      value='100'
    )


class TestWrapperCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.source = self.Block(TestFakeSource())
    self.sink = self.Block(SinkWrapperBlock())

    self.vpos = self.connect(self.source.pos, self.sink.pos)
    self.gnd = self.connect(self.source.neg, self.sink.neg)



class NetlistWrapperTestCase(unittest.TestCase):
  def test_warpper_netlist(self) -> None:
    net = NetlistTestCase.generate_net(TestWrapperCircuit)

    self.assertIn(NetBlock('Inductor_SMD:L_0603_1608Metric', 'L1', '', '100',
                           ['sink'], ['sink'],
                           ['edg.electronics_model.test_netlist_wrapper.SinkWrapperBlock']), net.blocks)
    self.assertEqual(len(net.blocks), 2)  # should only generate top-level source and sink