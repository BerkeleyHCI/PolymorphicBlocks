import unittest

from .. import edgir
from . import *


class KiCadConversionBlock(KiCadSchematicBlock):
    """Block generates a Passive-to-VoltageSource adapter."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(VoltageSource.empty())
        self.import_kicad(self.file_path("resources", "test_kicad_import.kicad_sch"),
                          conversions={
                              'R1.1': VoltageSource()  # ideal port
                          })


class KiCadBoundaryConversionBlock(KiCadSchematicBlock):
    """Block generates a Passive-to-VoltageSource adapter on the boundary port."""
    def __init__(self) -> None:
        super().__init__()
        self.PORT_A = self.Port(VoltageSource.empty())
        self.import_kicad(self.file_path("resources", "test_kicad_import.kicad_sch"),
                          conversions={
                              'PORT_A': VoltageSource()  # ideal port
                          })


class KiCadImportProtoTestCase(unittest.TestCase):
    def test_conversion_block(self):
        # because this generates an adapter, the structure differs from the other KiCad import tests
        # this also doesn't re-check the other structure, only the conversions
        # (and that it doesn't connection-error out in the first place)
        pb = KiCadConversionBlock()._elaborated_def_to_proto()
        self.validate(pb)

    def test_boundary_conversion_block(self):
        pb = KiCadBoundaryConversionBlock()._elaborated_def_to_proto()
        self.validate(pb)

    def validate(self, pb: edgir.HierarchyBlock):
        constraints = list(map(lambda pair: pair.value, pb.constraints))

        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'PORT_A'
        expected_conn.exported.internal_block_port.ref.steps.add().name = '(adapter)R1.a'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'dst'
        self.assertIn(expected_conn, constraints)
