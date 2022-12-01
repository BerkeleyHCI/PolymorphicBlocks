import unittest

import edgir
from . import *


class TestBlock(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.port_1 = self.Port(VoltageSink())
    self.port_2 = self.Port(VoltageSink())

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'R', 'Resistor_SMD:R_0603_1608Metric',
      {
        '1': self.port_1,
        '2': self.port_2
      },
      value='1k'
    )


class FootprintTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = TestBlock()._elaborated_def_to_proto()

  def test_footprint(self):
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    self.assertIn(edgir.AssignLit(['fp_footprint'], 'Resistor_SMD:R_0603_1608Metric'), constraints)
    self.assertIn(edgir.AssignLit(['fp_value'], '1k'), constraints)
    self.assertIn(edgir.AssignLit(['fp_refdes_prefix'], 'R'), constraints)

    expected_pinning = edgir.Metadata()
    path = edgir.ValueExpr()
    path.ref.steps.add().name = 'port_1'
    expected_pinning.members.node['1'].bin_leaf = path.SerializeToString()
    path = edgir.ValueExpr()
    path.ref.steps.add().name = 'port_2'
    expected_pinning.members.node['2'].bin_leaf = path.SerializeToString()
    self.assertEqual(self.pb.meta.members.node['pinning'], expected_pinning)
