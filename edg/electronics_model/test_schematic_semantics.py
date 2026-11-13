"""Regression cases for missing meaning and overprinted two-terminal fallbacks."""

from __future__ import annotations
from ..core import CompiledDesign
from .KiCadSchematicExporter import PhysicalComponent

import unittest
from types import SimpleNamespace
from .KiCadSchematicExporter import generic, KiCadSchematicExporter
from .KiCadSchematicLabels import readable_labels
from .KiCadSchematicRoles import infer_pin_names, infer_description


class SchematicSemanticsTest(unittest.TestCase):
    def test_authored_boundary_roles_only_rearrange_generic_pin_graphics(self) -> None:
        component = PhysicalComponent(
            "interface",
            "U1",
            "Test:IC",
            "Interface",
            {"1": "port_a", "2": "port_b", "3": "port_c", "4": "port_d"},
            None,
            "Interface",
        )
        component.presentation_pin_roles = {"1": "input", "2": "output", "3": "supply", "4": "return"}
        view = generic(component)
        pins = {n: (x, y) for n, x, y, _ in view.pins}
        self.assertEqual(set(pins), set(component.pins))
        self.assertLess(pins["1"][0], 0)
        self.assertGreater(pins["2"][0], 0)
        self.assertLess(pins["3"][1], 0)
        self.assertGreater(pins["4"][1], 0)

    def test_declared_power_driver_ports_face_power_stage(self) -> None:
        outputs = ("gate1", "sw", "cboot", "btst1", "btst2", "hidrv1", "lodrv2", "tgup", "tgdn")
        names = {"1": "in1", **{str(i + 2): name for i, name in enumerate(outputs)}, "20": "gnd"}
        component = PhysicalComponent("driver", "U1", "Test:Package", "Driver", names, None, "Power")
        view = generic(component)
        pins = {n: (x, y, a) for n, x, y, a in view.pins}
        self.assertEqual(set(pins), set(component.pins))
        self.assertLess(pins["1"][0], 0)
        for number, name in names.items():
            if name in outputs:
                self.assertGreater(pins[number][0], 0)
                self.assertEqual(pins[number][2], 180)

    def test_two_pin_fallback_escapes_opposite_sides(self) -> None:
        component = PhysicalComponent("filter", "FB1", "Test:Package", "Filter", {"1": "a", "2": "b"}, None, "Power")
        view = generic(component)
        pins = {n: (x, y, a) for n, x, y, a in view.pins}
        self.assertLess(pins["1"][0], 0)
        self.assertGreater(pins["2"][0], 0)
        self.assertEqual(pins["1"][2], 0)
        self.assertEqual(pins["2"][2], 180)

    def test_display_connector_pin_meaning_requires_verified_model(self) -> None:
        component = PhysicalComponent(
            "oled.device.conn",
            "J1",
            "Test:Connector",
            "FPC",
            {"9": "pins.9", "28": "pins.28", "14": "pins.14"},
            None,
            "Display",
        )
        classes = ["edg.parts.display.oled.Er_Oled_096_1_1.Er_Oled_096_1_1_Device", "edg.parts.connector.Fpc.Afc01"]
        self.assertEqual(infer_pin_names(component, classes), {"9": "VDD", "28": "VCC", "14": "RES"})
        self.assertIn("charge pump", infer_description(component, classes))
        self.assertEqual(infer_pin_names(component, classes[:-1] + ["UnknownConnector"]), {})
        component.pins["9"] = "pins.28"
        self.assertEqual(infer_pin_names(component, classes), {})

    def test_verified_fpc_flip_requires_compiled_length(self) -> None:
        component = PhysicalComponent(
            "oled.conn.conn",
            "J1",
            "Test:FPC",
            "FPC",
            {"2": "pins.2", "16": "pins.16", "24": "pins.24"},
            None,
            "Display",
        )
        classes = [
            "edg.parts.display.oled.Er_Oled_022.Er_Oled022_1_Device",
            "edg.parts.connector.Fpc.Fpc050BottomFlip",
            "edg.parts.connector.Fpc.Afc07Top",
        ]
        self.assertEqual(infer_pin_names(component, classes), {})
        self.assertEqual(infer_pin_names(component, classes, 30), {})
        self.assertEqual(infer_pin_names(component, classes, 24), {"2": "VCC", "16": "RES", "24": "VSS"})

    def test_clock_and_protection_values_ignore_parasitic_capacitance(self) -> None:
        from unittest.mock import Mock
        from .NetlistGenerator import NetBlock

        def block(cls: str) -> NetBlock:
            return Mock(
                spec=NetBlock,
                path_classes=[SimpleNamespace(target=SimpleNamespace(name=cls))],
                full_path=SimpleNamespace(to_tuple=lambda: ("device",)),
                part="VerifiedPart (Vendor)",
                value="fallback",
            )

        values = {("device", "actual_capacitance"): 0.0, ("device", "actual_frequency"): 16e6}
        compiled = Mock(spec=CompiledDesign)
        compiled.get_value.side_effect = lambda key: values.get(key)
        self.assertEqual(KiCadSchematicExporter._display_value(compiled, block("edg.Crystal")), "16MHz")
        self.assertEqual(KiCadSchematicExporter._display_value(compiled, block("edg.ZenerDiode")), "VerifiedPart")
        values[("device", "actual_capacitance")] = 0.9999999999999999e-6
        self.assertEqual(KiCadSchematicExporter._display_value(compiled, block("edg.Capacitor")), "1µF")
        self.assertEqual(
            KiCadSchematicExporter._display_value(
                compiled, block("project.Bulk100Cap"), {"lib_id": "Device:C_Polarized"}
            ),
            "1µF",
        )

    def test_short_labels_are_injective_and_order_independent(self) -> None:
        names = ["a.b.c.d", "x.b.c.d", "v3v3", "unicode.接口", "a name", "N_61206e616d65"]
        labels = readable_labels(names)
        self.assertEqual(labels, readable_labels(reversed(names)))
        self.assertEqual(len(set(labels.values())), len(names))
        self.assertEqual(labels["v3v3"], "v3v3")
        self.assertNotEqual(labels["a.b.c.d"], labels["x.b.c.d"])
