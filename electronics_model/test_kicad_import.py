import os
import unittest

import edgir
from edg import BoardTop
from electronics_model import Passive
from electronics_model.KiCadSchematicBlock import KiCadSchematicBlock


class KiCadBlock(KiCadSchematicBlock):
    def __init__(self) -> None:
        super().__init__()

        self.PORT_A = self.Port(Passive())

    def contents(self) -> None:
        super().contents()

        self.import_kicad(os.path.join(os.path.dirname(__file__), "resources", "test_kicad_import.net"))


class KiCadImportProtoTestCase(unittest.TestCase):
    def test_kicad(self):
        pb = KiCadBlock()._elaborated_def_to_proto()
        constraints = list(map(lambda pair: pair.value, pb.constraints))

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'Test_Net_1_link'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'C1'
        expected_conn.connected.block_port.ref.steps.add().name = 'neg'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'Test_Net_1_link'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'R2'
        expected_conn.connected.block_port.ref.steps.add().name = 'b'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'Net-(C1-Pad1)_link'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'R1'
        expected_conn.connected.block_port.ref.steps.add().name = 'b'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'Net-(C1-Pad1)_link'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'C1'
        expected_conn.connected.block_port.ref.steps.add().name = 'pos'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'Net-(C1-Pad1)_link'
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
