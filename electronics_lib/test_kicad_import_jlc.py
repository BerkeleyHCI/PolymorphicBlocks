import unittest

import edgir
from edg_core import Builder
from electronics_model import KiCadSchematicBlock, Passive
from .JlcBlackbox import KiCadJlcBlackbox  # needed for import_kicad


class JlcBlackboxBlock(KiCadSchematicBlock):
    """Block with a blackbox part, a sub-blocks that only knows it has a footprint and pins and doesn't
    map to one of the abstract types."""
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(Passive.empty())
        self.gnd = self.Port(Passive.empty())
        self.out = self.Port(Passive.empty())
        self.import_kicad(self.file_path("resources", "test_kicad_import_jlc.kicad_sch"))


class JlcImportBlackboxTestCase(unittest.TestCase):
    def test_import_blackbox(self):
        # the elaborate_toplevel wrapper is needed since the inner block uses array ports
        pb = Builder.builder.elaborate_toplevel(JlcBlackboxBlock())
        constraints = list(map(lambda pair: pair.value, pb.constraints))

        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'pwr'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'U1'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'ports'
        expected_conn.exported.internal_block_port.ref.steps.add().allocate = '1'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'gnd'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'U1'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'ports'
        expected_conn.exported.internal_block_port.ref.steps.add().allocate = '3'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'node'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'U1'
        expected_conn.connected.block_port.ref.steps.add().name = 'ports'
        expected_conn.connected.block_port.ref.steps.add().allocate = '2'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'node'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'res'
        expected_conn.connected.block_port.ref.steps.add().name = 'a'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'out'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'res'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'b'
        self.assertIn(expected_conn, constraints)

        # resistor not checked, responsibility of another test
        # U1.kicad_pins not checked, because array assign syntax is wonky
        self.assertIn(edgir.AssignLit(['U1', 'kicad_refdes_prefix'], 'U'), constraints)
        self.assertIn(edgir.AssignLit(['U1', 'kicad_footprint'], 'Package_TO_SOT_SMD:SOT-23'), constraints)
        self.assertIn(edgir.AssignLit(['U1', 'kicad_part'], 'Sensor_Temperature:MCP9700AT-ETT'), constraints)
        self.assertIn(edgir.AssignLit(['U1', 'kicad_value'], 'MCP9700AT-ETT'), constraints)
        self.assertIn(edgir.AssignLit(['U1', 'kicad_datasheet'], 'http://ww1.microchip.com/downloads/en/DeviceDoc/21942e.pdf'), constraints)
        self.assertIn(edgir.AssignLit(['U1', 'kicad_jlcpcb_part'], 'C127949'), constraints)
