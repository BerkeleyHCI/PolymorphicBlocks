import unittest

from electronics_abstract_parts import *
import electronics_abstract_parts
import electronics_model
from . import *
from . import Passives

class CapacitorTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.driver = Driver([electronics_model, electronics_abstract_parts, Passives])

  def test_capacitor(self) -> None:
    pb = self.driver.generate_block(SmtCeramicCapacitor(
      capacitance=0.1 * uFarad(tol=0.2),
      voltage=(0, 3.3) * Volt
    )).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Capacitor_SMD:C_0603_1608Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['part'], 'CL10B104KB8NNNC'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '0.1µF, 50V'),
                  pb.constraints.values())

  def test_capacitor_part(self) -> None:
    pb = self.driver.generate_block(SmtCeramicCapacitor(
      capacitance=0.1 * uFarad(tol=0.2),
      voltage=(0, 3.3) * Volt,
    ), {
      TransformUtil.Path.empty().append_param('part'): 'CL31B104KBCNNNC',
    }).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Capacitor_SMD:C_1206_3216Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['part'], 'CL31B104KBCNNNC'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '0.1µF, 50V'),
                  pb.constraints.values())

  def test_capacitor_footprint(self) -> None:
    pb = self.driver.generate_block(SmtCeramicCapacitor(
      capacitance=0.1 * uFarad(tol=0.2),
      voltage=(0, 3.3) * Volt,
    ), {
      TransformUtil.Path.empty().append_param('footprint_name'): 'Capacitor_SMD:C_1206_3216Metric',
    }).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Capacitor_SMD:C_1206_3216Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['part'], 'CL31B104KBCNNNC'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '0.1µF, 50V'),
                  pb.constraints.values())

  def test_multi_capacitor(self) -> None:
    pb = self.driver.generate_block(SmtCeramicCapacitor(
      capacitance=(150, 1000) * uFarad,
      voltage=(0, 3.3) * Volt
    )).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Capacitor_SMD:C_1206_3216Metric'),
                  pb.blocks['c_0'].hierarchy.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['part'], 'CL31A107MQHNNNE'),
                  pb.blocks['c_0'].hierarchy.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '100µF, 6.3V'),
                  pb.blocks['c_0'].hierarchy.constraints.values())

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Capacitor_SMD:C_1206_3216Metric'),
                  pb.blocks['c_1'].hierarchy.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['part'], 'CL31A107MQHNNNE'),
                  pb.blocks['c_1'].hierarchy.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '100µF, 6.3V'),
                  pb.blocks['c_1'].hierarchy.constraints.values())
