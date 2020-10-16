import unittest

from electronics_abstract_parts import *
import electronics_model
import electronics_abstract_parts
from . import *

class InductorTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.driver = Driver([electronics_model, electronics_abstract_parts])

  def test_inductor(self) -> None:
    pb = self.driver.generate_block(SmtInductor(
      inductance=2.2 * uHenry(tol=0.2),
      frequency=(0, 1) * MHertz,
      current=(0, 500) * mAmp
    )).contents

    self.assertIn(edgir.EqualsValueExpr(['footprint_name'], 'Inductor_SMD:L_0805_2012Metric'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['part'], 'MLZ2012N2R2LT000'),
                  pb.constraints.values())
    self.assertIn(edgir.EqualsValueExpr(['value'], '2.2µH, 800mA'),
                  pb.constraints.values())
