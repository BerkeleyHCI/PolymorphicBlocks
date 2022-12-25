import unittest
from typing import Type

import edgir
from edg_core import Range
from electronics_model import KiCadSchematicBlock, Passive, VoltageSource
from electronics_abstract_parts import Resistor, Capacitor, Volt, Ohm, uFarad


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
