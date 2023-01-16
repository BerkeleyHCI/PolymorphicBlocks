import unittest

import os.path
from typing import Set, Tuple, Type

from .KiCadSchematicParser import KiCadSchematic, ParsedNet, KiCadGlobalLabel, KiCadLabel


def net_to_tuple(net: ParsedNet) -> Tuple[Set[Tuple[Type, str]], Set[str]]:
  """Converts a ParsedNet to a tuple of net labels and net pins, so it can be compared during unit testing."""
  labels = set([(x.__class__, x.name) for x in net.labels])
  pins = set([f"{x.refdes}.{x.pin_number}" for x in net.pins])
  return (labels, pins)


class KiCadSchematicParserTest(unittest.TestCase):
  def test_kicad(self):
    self.check_schematic_rcs("test_kicad_import.kicad_sch")

  def test_kicad_rot(self):
    self.check_schematic_rcs("test_kicad_import_rot.kicad_sch")

  def test_kicad_tunnel(self):
    self.check_schematic_rcs("test_kicad_import_tunnel.kicad_sch")

  def test_kicad_power(self):
    self.check_schematic_rcs("test_kicad_import_power.kicad_sch")

  def test_kicad_modified_symbol(self):
    self.check_schematic_rcs("test_kicad_import_modified_symbol.kicad_sch")

  def check_schematic_rcs(self, filename):
    with open(os.path.join(os.path.dirname(__file__), "resources", filename), "r") as file:
      file_data = file.read()
    sch = KiCadSchematic(file_data)
    nets = [net_to_tuple(x) for x in sch.nets]
    self.assertEqual(len(nets), 3)
    self.assertIn(({(KiCadGlobalLabel, 'PORT_A')}, {'R1.1'}), nets)
    self.assertIn(({(KiCadLabel, 'node')}, {'R1.2', 'R2.1', 'C1.1'}), nets)
    self.assertIn(({(KiCadLabel, 'Test_Net_1')}, {'R2.2', 'C1.2'}), nets)

    symbols = [(x.refdes, x.lib) for x in sch.symbols]
    self.assertIn(('R1', 'Device:R'), symbols)
    self.assertIn(('R2', 'Device:R'), symbols)
    self.assertIn(('C1', 'Device:C'), symbols)

  def test_kicad_mirrorx(self):
    self.check_schematic_fet("test_kicad_import_mirrorx.kicad_sch")

  def test_kicad_mirrory(self):
    self.check_schematic_fet("test_kicad_import_mirrory.kicad_sch")

  def test_kicad_mirrory_rot(self):
    self.check_schematic_fet("test_kicad_import_mirrory_rot.kicad_sch")

  def check_schematic_fet(self, filename):
    """R and Cs are symmetric and don't test for mirroring well."""
    with open(os.path.join(os.path.dirname(__file__), "resources", filename), "r") as file:
      file_data = file.read()
    sch = KiCadSchematic(file_data)
    nets = [net_to_tuple(x) for x in sch.nets]

    self.assertIn(({(KiCadGlobalLabel, 'drain')}, {'Q1.1'}), nets)
    self.assertIn(({(KiCadGlobalLabel, 'gate')}, {'Q1.2'}), nets)
    self.assertIn(({(KiCadGlobalLabel, 'source')}, {'Q1.3'}), nets)

  def test_connectedports(self):
    """Schematic with two connected ports without components."""
    with open(os.path.join(os.path.dirname(__file__), "resources", "test_kicad_import_connectedports.kicad_sch"), "r") as file:
      file_data = file.read()
    sch = KiCadSchematic(file_data)
    nets = [net_to_tuple(x) for x in sch.nets]

    self.assertIn(({(KiCadGlobalLabel, 'a'), (KiCadGlobalLabel, 'b')}, {}), nets)
