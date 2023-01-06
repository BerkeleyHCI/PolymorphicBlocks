import unittest
from typing import Type

import edgir
from edg_core import Range
from electronics_model import KiCadSchematicBlock, VoltageSink, Ground, AnalogSource


class KiCadBlackboxBlock(KiCadSchematicBlock):
    """Block with a blackbox part, a sub-blocks that only knows it has a footprint and pins and doesn't
    map to one of the abstract types."""
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(VoltageSink.empty())
        self.gnd = self.Port(Ground.empty())
        self.pwr = self.Port(AnalogSource.empty())
        self.import_kicad(self.file_path("resources", "test_kicad_import_blackbox.kicad_sch"),
                          conversions={  # ideal ports only here
                              'pwr': VoltageSink(),
                              'gnd': Ground(),
                              'out': AnalogSource(),
                          })


class KiCadImportProtoTestCase(unittest.TestCase):
    def check_connectivity(self, cls: Type[KiCadSchematicBlock]):
        """Checks the connectivity of the generated proto, since the examples have similar structures."""
        pb = KiCadBlackboxBlock()._elaborated_def_to_proto()
        constraints = list(map(lambda pair: pair.value, pb.constraints))

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'Test_Net_1'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'C1'
        expected_conn.connected.block_port.ref.steps.add().name = 'neg'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'Test_Net_1'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'R2'
        expected_conn.connected.block_port.ref.steps.add().name = 'b'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'node'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'R1'
        expected_conn.connected.block_port.ref.steps.add().name = 'b'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'node'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'C1'
        expected_conn.connected.block_port.ref.steps.add().name = 'pos'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'node'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'R2'
        expected_conn.connected.block_port.ref.steps.add().name = 'a'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'PORT_A'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'R1'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'a'
        self.assertIn(expected_conn, constraints)

        self.assertIn(edgir.AssignLit(['R1', 'resistance'], Range.from_tolerance(51, 0.05)), constraints)
        self.assertIn(edgir.AssignLit(['R2', 'resistance'], Range.from_tolerance(51, 0.05)), constraints)

        self.assertIn(edgir.AssignLit(['C1', 'capacitance'], Range.from_tolerance(47e-6, 0.2)), constraints)
        self.assertIn(edgir.AssignLit(['C1', 'voltage'], Range(0, 6.3)), constraints)
