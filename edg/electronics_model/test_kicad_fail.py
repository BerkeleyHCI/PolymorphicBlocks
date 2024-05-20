import unittest

from . import *


class KiCadMissingPort(KiCadSchematicBlock):
    """This block lacks the PORT_A port."""
    def __init__(self) -> None:
        super().__init__()
        self.import_kicad(self.file_path("resources", "test_kicad_import.kicad_sch"))


class KiCadAliasedPort(KiCadSchematicBlock):
    """This aliases Test_Net_1 as a port."""
    def __init__(self) -> None:
        super().__init__()
        self.Test_Net_1 = self.Port(Passive())
        self.import_kicad(self.file_path("resources", "test_kicad_import.kicad_sch"))


class KiCadAliasedLink(KiCadSchematicBlock):
    """This aliases Test_Net_1 as an existing link."""
    def __init__(self) -> None:
        super().__init__()
        self.Test_Net_1 = 0
        self.import_kicad(self.file_path("resources", "test_kicad_import.kicad_sch"))


class KiCadImportFailTestCase(unittest.TestCase):
    def test_missing_port(self):
        with self.assertRaises(Exception):
            KiCadMissingPort()._elaborated_def_to_proto()

    def test_aliased_port(self):
        with self.assertRaises(Exception):
            KiCadAliasedPort()._elaborated_def_to_proto()

    def test_aliased_link(self):
        with self.assertRaises(Exception):
            KiCadAliasedLink()._elaborated_def_to_proto()
