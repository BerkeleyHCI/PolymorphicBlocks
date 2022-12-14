import unittest

import os.path

from .KicadSchematicParser import KicadSchematic


class KicadSchematicParserTest(unittest.TestCase):
  def test_kicad(self):
    with open(os.path.join(os.path.dirname(__file__), "resources", "test_kicad_import.kicad_sch"), "r") as file:
      file_data = file.read()
    sch = KicadSchematic(file_data)
