import os
import unittest

import edgir
from electronics_model import Passive
from electronics_model.KiCadSchematicBlock import KiCadSchematicBlock
from electronics_abstract_parts import Resistor, Capacitor, Volt, Ohm, Farad


def example_filepath(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), "resources", filename)

class KiCadBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(example_filepath("test_kicad_import.kicad_sch"))


class KiCadTunnelBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad, including using net labels as a tunnel."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(example_filepath("test_kicad_import_tunnel.kicad_sch"))


class KiCadInlineBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad, using inline Python in the symbol value."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(example_filepath("test_kicad_import_inline.kicad_sch"))


class KiCadInlineVarsBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad, using inline Python that references
    local variables defined in the HDL."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(example_filepath("test_kicad_import_inline_vars.kicad_sch"), {
            'r1_res': 51*Ohm(tol=0.05),
            'r2_res': 51*Ohm(tol=0.05),
            'c1_cap': 47*Farad(tol=0.05),
            'in_voltage': (0, 6.3)*Volt,
        })


class KiCadCodePartsBock(KiCadSchematicBlock):
    """Block that has subblocks defined in HDL but connectivity defined in KiCad."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.R1 = self.Block(Resistor(51*Ohm(tol=0.05)))
        self.R2 = self.Block(Resistor(51*Ohm(tol=0.05)))
        self.C1 = self.Block(Capacitor(47*Farad(tol=0.05), (0, 6.3)*Volt))
        self.import_kicad(example_filepath("test_kicad_import_codeparts.kicad_sch"))


class KiCadImportProtoTestCase(unittest.TestCase):
    def test_block(self):
        pb = KiCadBlock()._elaborated_def_to_proto()
        self.check_connectivity(pb)

    def test_tunnel_block(self):
        pb = KiCadTunnelBlock()._elaborated_def_to_proto()
        self.check_connectivity(pb)

    def test_inline_block(self):
        pb = KiCadInlineBlock()._elaborated_def_to_proto()
        self.check_connectivity(pb)

    def test_inline_vars_block(self):
        pb = KiCadInlineVarsBlock()._elaborated_def_to_proto()
        self.check_connectivity(pb)

    def test_codeparts_block(self):
        pb = KiCadCodePartsBock()._elaborated_def_to_proto()
        self.check_connectivity(pb)

    def check_connectivity(self, pb: edgir.HierarchyBlock):
        """Checks the connectivity of the generated proto, since the examples have similar structures."""
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
        expected_conn.connected.link_port.ref.steps.add().name = 'anon_link_0'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'R1'
        expected_conn.connected.block_port.ref.steps.add().name = 'b'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'anon_link_0'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'C1'
        expected_conn.connected.block_port.ref.steps.add().name = 'pos'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'anon_link_0'
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
