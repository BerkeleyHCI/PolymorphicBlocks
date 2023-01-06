# this class lives in electronics_abstract_parts since it requires the Resistor
import unittest

from edg_core import Block, Range, Refinements, InOut
from electronics_model import FootprintBlock, Passive
from electronics_abstract_parts import Resistor
from electronics_model.test_netlist import NetlistTestCase
from electronics_model.test_kicad_import_blackbox import KiCadBlackboxBlock
from electronics_model.footprint import Pin, Block as FBlock  # TODO cleanup naming


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

    self.assertEqual(net.nets['dut.pwr'], [
      Pin('dut.U1', '1')
    ])
    self.assertEqual(net.nets['dut.gnd'], [
      Pin('dut.U1', '3')
    ])
    self.assertEqual(net.nets['dut.node.0'], [
      Pin('dut.U1', '2'),
      Pin('dut.res', '1')
    ])
    self.assertEqual(net.nets['dut.out'], [
      Pin('dut.res', '2')
    ])
    self.assertEqual(net.blocks['dut.U1'], FBlock('Package_TO_SOT_SMD:SOT-23', 'U1',
                                                  # expected value is wonky because netlisting combines part and value
                                                  'Sensor_Temperature:MCP9700AT-ETT', 'Sensor_Temperature:MCP9700AT-ETT - MCP9700AT-ETT',
                                                  ['dut', 'U1'], ['dut', 'U1'],
                                                  ['electronics_model.test_kicad_import_blackbox.KiCadBlackboxBlock',
                                                   'electronics_model.KiCadSchematicBlock.KiCadBlackboxComponent']))
    self.assertEqual(net.blocks['dut.res'], FBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '',
                                                   ['dut', 'res'], ['dut', 'res'],
                                                   ['electronics_model.test_kicad_import_blackbox.KiCadBlackboxBlock',
                                                    'electronics_abstract_parts.test_kicad_import_netlist.DummyResistor']))
