# this class lives in electronics_abstract_parts since it requires the Resistor
import unittest

from edg_core import Block, Range, Refinements, InOut, TransformUtil
from electronics_model import FootprintBlock, Passive
from electronics_abstract_parts import Resistor
from electronics_model.test_netlist import NetlistTestCase, Net, NetPin, NetBlock
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
    # note, dut pruned out from paths since it's the only block in the top-level
    self.assertIn(Net('dut.pwr', [
      NetPin(['dut', 'U1'], '1')
    ], [
      TransformUtil.Path.empty().append_block('dut').append_port('pwr'),
      TransformUtil.Path.empty().append_block('dut', 'U1').append_port('ports', '1'),
      TransformUtil.Path.empty().append_block('dummypwr').append_port('port'),
    ]), net.nets)
    self.assertIn(Net('dut.gnd', [
      NetPin(['dut', 'U1'], '3')
    ], [
      TransformUtil.Path.empty().append_block('dut').append_port('gnd'),
      TransformUtil.Path.empty().append_block('dut', 'U1').append_port('ports', '3'),
      TransformUtil.Path.empty().append_block('dummygnd').append_port('port'),
    ]), net.nets)
    self.assertIn(Net('dut.node', [
      NetPin(['dut', 'U1'], '2'),
      NetPin(['dut', 'res'], '1')
    ], [
      TransformUtil.Path.empty().append_block('dut', 'U1').append_port('ports', '2'),
      TransformUtil.Path.empty().append_block('dut', 'res').append_port('a'),
    ]), net.nets)
    self.assertIn(Net('dut.out', [
      NetPin(['dut', 'res'], '2')
    ], [
      TransformUtil.Path.empty().append_block('dut').append_port('out'),
      TransformUtil.Path.empty().append_block('dut', 'res').append_port('b'),
      TransformUtil.Path.empty().append_block('dummyout').append_port('port'),
    ]), net.nets)
    self.assertIn(NetBlock('Package_TO_SOT_SMD:SOT-23', 'U1',
                           # expected value is wonky because netlisting combines part and value
                           'Sensor_Temperature:MCP9700AT-ETT', 'MCP9700AT-ETT',
                           ['dut', 'U1'], ['U1'],
                           ['electronics_model.KiCadSchematicBlock.KiCadBlackbox']),
                  net.blocks)
    self.assertIn(NetBlock('Symbol:Symbol_ESD-Logo_CopperTop', 'SYM1',
                           # expected value is wonky because netlisting combines part and value
                           'Graphic:SYM_ESD_Small', 'SYM_ESD_Small',
                           ['dut', 'SYM1'], ['SYM1'],
                           ['electronics_model.KiCadSchematicBlock.KiCadBlackbox']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '',
                           ['dut', 'res'], ['res'],
                           ['electronics_abstract_parts.test_kicad_import_netlist.DummyResistor']),
                  net.blocks)
