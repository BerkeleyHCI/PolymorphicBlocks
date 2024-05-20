import unittest

from .. import edgir
from . import *

class KiCadBundleBlock(KiCadSchematicBlock):
    """Block where the global labels are a bundle connection."""
    def __init__(self) -> None:
        super().__init__()
        self.A = self.Port(UartPort(DigitalBidir.empty()))
        self.import_kicad(self.file_path("resources", "test_kicad_import_bundle.kicad_sch"),
                          conversions={
                              'R1.1': DigitalSource(),  # ideal port
                              'R1.2': DigitalSink(),  # ideal port
                          })


class KiCadImportProtoTestCase(unittest.TestCase):
    def test_conversion_block(self):
        # because this generates an adapter, the structure differs from the other KiCad import tests
        # this also doesn't re-check the other structure, only the conversions
        # (and that it doesn't connection-error out in the first place)
        pb = KiCadBundleBlock()._elaborated_def_to_proto()
        constraints = list(map(lambda pair: pair.value, pb.constraints))

        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'A'
        expected_conn.exported.exterior_port.ref.steps.add().name = 'tx'
        expected_conn.exported.internal_block_port.ref.steps.add().name = '(adapter)R1.a'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'dst'

        self.assertIn(expected_conn, constraints)
        expected_conn = edgir.ValueExpr()
        expected_conn.exported.exterior_port.ref.steps.add().name = 'A'
        expected_conn.exported.exterior_port.ref.steps.add().name = 'rx'
        expected_conn.exported.internal_block_port.ref.steps.add().name = '(adapter)R1.b'
        expected_conn.exported.internal_block_port.ref.steps.add().name = 'dst'
        self.assertIn(expected_conn, constraints)
