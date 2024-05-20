import unittest

from .. import edgir
from ...core import Builder
from . import *


class KiCadBlackboxBlock(KiCadSchematicBlock):
    """Block with a blackbox part, a sub-blocks that only knows it has a footprint and pins and doesn't
    map to one of the abstract types."""
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(Passive.empty())
        self.gnd = self.Port(Passive.empty())
        self.out = self.Port(Passive.empty())
        self.import_kicad(self.file_path("resources", "test_kicad_import_blackbox.kicad_sch"))


class KiCadBlackboxBlockAutoadapt(KiCadSchematicBlock):
    """Same example as above, but with typed ports and auto-adaptor generation."""
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(VoltageSink.empty())
        self.gnd = self.Port(Ground.empty())
        self.out = self.Port(AnalogSource.empty())
        self.import_kicad(self.file_path("resources", "test_kicad_import_blackbox.kicad_sch"),
                          auto_adapt=True)


class KiCadImportBlackboxTestCase(unittest.TestCase):
    def test_import_blackbox(self):
        # the elaborate_toplevel wrapper is needed since the inner block uses array ports
        pb = Builder.builder.elaborate_toplevel(KiCadBlackboxBlock())
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

        self.assertIn(edgir.AssignLit(['SYM1', 'kicad_refdes_prefix'], 'SYM'), constraints)
        self.assertIn(edgir.AssignLit(['SYM1', 'kicad_footprint'], 'Symbol:Symbol_ESD-Logo_CopperTop'), constraints)

    def test_import_blackbox_autoadapt(self):
        # the elaborate_toplevel wrapper is needed since the inner block uses array ports
        pb = Builder.builder.elaborate_toplevel(KiCadBlackboxBlockAutoadapt())
        constraints = list(map(lambda pair: pair.value, pb.constraints))

        # just check an adapter has been generated, don't need to check the details
        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'pwr'
        expected_conn.exported.internal_block_port.ref.steps.add().name = '(adapter)U1.ports.1'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'dst'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'gnd'
        expected_conn.exported.internal_block_port.ref.steps.add().name = '(adapter)U1.ports.3'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'dst'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()  # this one should be unchanged
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
        expected_conn.exported.internal_block_port.ref.steps.add().name = '(adapter)res.b'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'dst'
        self.assertIn(expected_conn, constraints)

        # blackbox definition not checked again
