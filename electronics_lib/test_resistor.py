from typing import *
import unittest

from electronics_abstract_parts import *
import electronics_model
import electronics_abstract_parts
from . import *

class ResistorTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.driver = Driver([electronics_model, electronics_abstract_parts])

  def test_basic_resistor(self) -> None:
    pb = self.driver.generate_block(ChipResistor(
      resistance=1 * kOhm(tol=0.1),
      power=(0, 0)*Watt
    )).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Resistor_SMD:R_0603_1608Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '1k, 1%, 0.1W'),
                  pb.constraints.values())

  def test_power_resistor(self) -> None:
    pb = self.driver.generate_block(ChipResistor(
      resistance=1 * kOhm(tol=0.1),
      power=(0, .24)*Watt
    )).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Resistor_SMD:R_1206_3216Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '1k, 1%, 0.25W'),
                  pb.constraints.values())

  def test_non_e12_resistor(self) -> None:
    pb = self.driver.generate_block(ChipResistor(
      resistance=8.06 * kOhm(tol=0.01),
      power=(0, 0)*Watt
    )).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Resistor_SMD:R_0603_1608Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '8.06k, 1%, 0.1W'),
                  pb.constraints.values())

  def test_footprint(self) -> None:
    pb = self.driver.generate_block(ChipResistor(
      resistance=1 * kOhm(tol=0.1),
      power=(0, 0)*Watt,
    ), {
      TransformUtil.Path.empty().append_param('footprint_name'): 'Resistor_SMD:R_1206_3216Metric',
    }).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Resistor_SMD:R_1206_3216Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '1k, 1%, 0.25W'),
                  pb.constraints.values())
