import unittest
from typing import Type

import edgir
from edg_core import Range
from electronics_abstract_parts import Resistor, Capacitor, Volt, Ohm, uFarad
from electronics_model import KiCadSchematicBlock, Passive


# Note that all the below blocks are the same circuit (component values and connectivity)
# but defined in slightly different ways.
# Rotation and mirroring are not checked here, but tested in the schematic parser.
class KiCadBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import.kicad_sch"))


class KiCadBlockAliasedPinName(KiCadSchematicBlock):
    """Block with a symbol that has the same pin name and number."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import_aliasedpinname.kicad_sch"))


class KiCadHierarchyLabelBlock(KiCadSchematicBlock):
    """Block that uses a hierarchy label for its port mapping."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import_hierarchical_label.kicad_sch"))


class KiCadTunnelBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad, including using net labels as a tunnel."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import_tunnel.kicad_sch"))


class KiCadInlineBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad, using inline Python in the symbol value."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import_inline.kicad_sch"))


class KiCadInlineVarsBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad, using inline Python that references
    local variables defined in the HDL."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import_inline_vars.kicad_sch"), {
            'r1_res': 51*Ohm(tol=0.05),
            'r2_res': 51*Ohm(tol=0.05),
            'c1_cap': 47*uFarad(tol=0.2),
            'in_voltage': (0, 6.3)*Volt,
        })


class KiCadCodePartsBock(KiCadSchematicBlock):
    """Block that has subblocks defined in HDL but connectivity defined in KiCad."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.R1 = self.Block(Resistor(51*Ohm(tol=0.05)))
        self.R2 = self.Block(Resistor(51*Ohm(tol=0.05)))
        self.C1 = self.Block(Capacitor(47*uFarad(tol=0.2), (0, 6.3)*Volt))
        self.import_kicad(self.file_path("resources", "test_kicad_import_codeparts.kicad_sch"))


class KiCadNodeBlock(KiCadSchematicBlock):
    """Block that has its implementation completely defined in KiCad."""
    def __init__(self) -> None:
        super().__init__()
        self.R1 = self.Block(Resistor(51*Ohm(tol=0.05)))
        self.PORT_A = self.Export(self.R1.a)
        self.import_kicad(self.file_path("resources", "test_kicad_import_node.kicad_sch"),
                          nodes={
                              'node': self.R1.b
                          })
        self.node = self.connect(self.R1.b)  # give it a name, must be after the import to not conflict


class KiCadPowerBlock(KiCadSchematicBlock):
    """Block using Power symbols (eg, Vdd, GND) as internal non-named tunnels."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import_power.kicad_sch"))


class KiCadModifiedSymbolBlock(KiCadSchematicBlock):
    """Imports a schematic with a modified (sheet-specific) symbol."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import_modified_symbol.kicad_sch"))


class KiCadBlockAliasedPort(KiCadSchematicBlock):
    """Block that has a port with the same name as an internal net."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(Passive())
        self.GND = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import.kicad_sch"))


class KiCadImportProtoTestCase(unittest.TestCase):
    def test_block(self):
        self.check_connectivity(KiCadBlock)

    def test_block_aliased_pin_name(self):
        self.check_connectivity(KiCadBlockAliasedPinName)

    def test_hierarchy_label_block(self):
        self.check_connectivity(KiCadHierarchyLabelBlock)

    def test_tunnel_block(self):
        self.check_connectivity(KiCadTunnelBlock)

    def test_inline_block(self):
        self.check_connectivity(KiCadInlineBlock)

    def test_inline_vars_block(self):
        self.check_connectivity(KiCadInlineVarsBlock)

    def test_codeparts_block(self):
        self.check_connectivity(KiCadCodePartsBock)

    def test_node_block(self):
        self.check_connectivity(KiCadNodeBlock)

    def test_power_block(self):
        self.check_connectivity(KiCadPowerBlock)

    def test_modified_symbol_block(self):
        self.check_connectivity(KiCadModifiedSymbolBlock)

    def test_aliased_port(self):
        with self.assertRaises(AssertionError):
            self.check_connectivity(KiCadBlockAliasedPort)

    def check_connectivity(self, cls: Type[KiCadSchematicBlock]):
        """Checks the connectivity of the generated proto, since the examples have similar structures."""
        pb = cls()._elaborated_def_to_proto()
        constraints = list(map(lambda pair: pair.value, pb.constraints))

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'GND'
        expected_conn.connected.link_port.ref.steps.add().name = 'passives'
        expected_conn.connected.link_port.ref.steps.add().allocate = ''
        expected_conn.connected.block_port.ref.steps.add().name = 'C1'
        expected_conn.connected.block_port.ref.steps.add().name = 'neg'
        self.assertIn(expected_conn, constraints)

        expected_conn = edgir.ValueExpr()
        expected_conn.connected.link_port.ref.steps.add().name = 'GND'
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
