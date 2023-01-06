# this class lives in electronics_abstract_parts since it requires the Resistor
import unittest

from edg_core import Block, Range, Refinements, InOut
from electronics_model import FootprintBlock, Passive
from electronics_abstract_parts import Resistor
from electronics_model.test_netlist import NetlistTestCase
from electronics_model.test_kicad_import_blackbox import KiCadBlackboxBlock


class PassiveDummy(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(Passive(), [InOut])


class KiCadBlackboxTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(KiCadBlackboxBlock())
    (self.dummypwr, ), _ = self.chain(self.dut.pwr, self.Block(PassiveDummy()))
    (self.dummygnd, ), _ = self.chain(self.dut.gnd, self.Block(PassiveDummy()))
    (self.dummyout, ), _ = self.chain(self.dut.out, self.Block(PassiveDummy()))


class DummyResistor(Resistor, FootprintBlock):
  def __init__(self):
    super().__init__(Range.all())
    self.footprint('R', 'Resistor_SMD:R_0603_1608Metric',
                   {'1': self.a,
                    '2': self.b,
                    })



class KiCadImportBlackboxTestCase(unittest.TestCase):
  def test_netlist(self):
    net = NetlistTestCase.generate_net(KiCadBlackboxTop, refinements=Refinements(
      class_refinements=[
        (Resistor, DummyResistor),
      ]
    ))
    print(net)

