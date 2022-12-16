import unittest

import os.path
from collections import Set
from typing import Tuple

from .KiCadSchematicParser import KiCadSchematic, ParsedNet


def net_to_tuple(net: ParsedNet) -> Tuple[Set[str], Set[str]]:
  """Converts a ParsedNet to a tuple of net labels and net pins, so it can be compared during unit testing."""
  labels = set([x.name for x in net.labels])
  pins = set([f"{x.refdes}.{x.pin_number}" for x in net.pins])
  return (labels, pins)


class KicadSchematicParserTest(unittest.TestCase):
  def test_kicad(self):
    with open(os.path.join(os.path.dirname(__file__), "resources", "test_kicad_import.kicad_sch"), "r") as file:
      file_data = file.read()
    sch = KiCadSchematic(file_data)
    nets = [net_to_tuple(x) for x in sch.nets]
    self.assertEqual(len(nets), 3)
    self.assertIn(({'PORT_A'}, {'R1.1'}), nets)
    self.assertIn((set(), {'R1.2', 'R2.1', 'C1.1'}), nets)
    self.assertIn(({'Test_Net_1'}, {'R2.2', 'C1.2'}), nets)

    symbols = [(x.refdes, x.lib) for x in sch.symbols]
    self.assertIn(('R1', 'Device:R'), symbols)
    self.assertIn(('R2', 'Device:R'), symbols)
    self.assertIn(('C1', 'Device:C'), symbols)
