import unittest
from types import SimpleNamespace

from .KiCadCompositeSymbols import resistor_array_symbol


class CompositeSchematicSymbolTest(unittest.TestCase):
    classes = ["edg.vendor_parts.jlc.JlcResistorArray.JlcResistorArray"]

    def test_pairing_follows_roles_not_pad_order(self):
        c = SimpleNamespace(pins={"1": "a.0", "8": "b.0", "2": "a.1", "7": "b.1"})
        definition, pins, lib_id = resistor_array_symbol(c, self.classes)
        locations = {number: (x, y) for number, x, y, angle in pins}
        self.assertEqual(locations["1"][1], locations["8"][1])
        self.assertEqual(locations["2"][1], locations["7"][1])
        self.assertNotEqual(locations["1"][1], locations["2"][1])
        self.assertEqual(set(locations), set(c.pins))
        self.assertEqual((definition, pins, lib_id), resistor_array_symbol(c, self.classes))

    def test_incomplete_unknown_and_ambiguous_roles_are_not_guessed(self):
        for inventory in (
            {"1": "a.0"},
            {"1": "ports.1", "2": "ports.2"},
            {"1": "a.0", "2": "a.0", "3": "b.0"},
        ):
            self.assertIsNone(resistor_array_symbol(SimpleNamespace(pins=inventory), self.classes))
        self.assertIsNone(resistor_array_symbol(SimpleNamespace(pins={"1": "a.0", "2": "b.0"}), ["Other"]))

    def test_custom_pin_names_have_distinct_embedded_identities(self):
        a = SimpleNamespace(pins={"1": "a.0", "8": "b.0"}, mapping={"pin_names": {"1": "CHANNEL_A"}})
        b = SimpleNamespace(pins=dict(a.pins), mapping={"pin_names": {"1": "CHANNEL_B"}})
        self.assertNotEqual(resistor_array_symbol(a, self.classes)[2], resistor_array_symbol(b, self.classes)[2])
        self.assertEqual(resistor_array_symbol(a, self.classes)[1], resistor_array_symbol(b, self.classes)[1])
