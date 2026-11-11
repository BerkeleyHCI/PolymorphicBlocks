import unittest
from types import SimpleNamespace

from .KiCadCompositeSymbols import resistor_array_symbol
from .KiCadSchematicExporter import PhysicalComponent
from typing import Any


def component_fixture(*, pins: dict[str, str], mapping: dict[str, Any] | None = None) -> PhysicalComponent:
    return PhysicalComponent("fixture", "RN1", "FP", "fixture", pins, mapping, "fixture")


class CompositeSchematicSymbolTest(unittest.TestCase):
    classes = ["edg.vendor_parts.jlc.JlcResistorArray.JlcResistorArray"]

    def test_pairing_follows_roles_not_pad_order(self) -> None:
        c = component_fixture(pins={"1": "a.0", "8": "b.0", "2": "a.1", "7": "b.1"})
        result = resistor_array_symbol(c, self.classes)
        assert result is not None
        definition, pins, lib_id = result
        locations = {number: (x, y) for number, x, y, angle in pins}
        self.assertEqual(locations["1"][1], locations["8"][1])
        self.assertEqual(locations["2"][1], locations["7"][1])
        self.assertNotEqual(locations["1"][1], locations["2"][1])
        self.assertEqual(set(locations), set(c.pins))
        self.assertEqual((definition, pins, lib_id), resistor_array_symbol(c, self.classes))

    def test_incomplete_unknown_and_ambiguous_roles_are_not_guessed(self) -> None:
        for inventory in (
            {"1": "a.0"},
            {"1": "ports.1", "2": "ports.2"},
            {"1": "a.0", "2": "a.0", "3": "b.0"},
        ):
            self.assertIsNone(resistor_array_symbol(component_fixture(pins=inventory), self.classes))
        self.assertIsNone(resistor_array_symbol(component_fixture(pins={"1": "a.0", "2": "b.0"}), ["Other"]))

    def test_custom_pin_names_have_distinct_embedded_identities(self) -> None:
        a = component_fixture(pins={"1": "a.0", "8": "b.0"}, mapping={"pin_names": {"1": "CHANNEL_A"}})
        b = component_fixture(pins=dict(a.pins), mapping={"pin_names": {"1": "CHANNEL_B"}})
        a_symbol, b_symbol = resistor_array_symbol(a, self.classes), resistor_array_symbol(b, self.classes)
        assert a_symbol is not None and b_symbol is not None
        self.assertNotEqual(a_symbol[2], b_symbol[2])
        self.assertEqual(a_symbol[1], b_symbol[1])
