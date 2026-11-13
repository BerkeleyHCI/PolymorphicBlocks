"""Fields remain fixed from local routing through sheet translation."""

from __future__ import annotations
from .KiCadSchematicExporter import PhysicalComponent, SymbolView

import unittest
from dataclasses import replace
from .KiCadSchematicExporter import node, S
from .KiCadSchematicLayout import annotation_position, annotation_bounds, freeze_annotations, graphic_bounds
from .KiCadSchematicScene import segment_box


class SchematicAnnotationsTest(unittest.TestCase):
    def test_arc_body_bounds_follow_the_selected_sweep(self) -> None:
        for midpoint, angle, expected in (
            ((3, 4), 0, (-4, -5, 4, -3)),  # Minor arc reaches beyond all three defining points.
            ((3, -4), 0, (-5, -3, 5, 5)),  # Same endpoints, major arc around the other side.
            ((3, -4), 90, (-3, -5, 5, 5)),
            ((0, 3), 0, (-4, -3, 4, -3)),  # Collinear input retains its endpoints.
        ):
            with self.subTest(midpoint=midpoint, angle=angle):
                arc = node("arc", node("start", -4, 3), node("mid", *midpoint), node("end", 4, 3))
                view = SymbolView(node("symbol", "Test:Arc", node("symbol", "Arc_0_1", arc)), [], "Test:Arc")
                self.assertEqual(graphic_bounds(view, angle, include_pins=False), expected)

    def fixture(self) -> tuple[PhysicalComponent, SymbolView]:
        # Geometry and labels of PDU hv_or.q1: rotated PowerPAK FET, with
        # three coincident source pins and a long manufacturer value.
        pins: list[tuple[str, float, float, float]] = [
            ("4", -5.08, 0, 0),
            ("5", 2.54, 5.08, 270),
            ("1", 2.54, -5.08, 90),
            ("2", 2.54, -5.08, 90),
            ("3", 2.54, -5.08, 90),
        ]
        body = node("symbol", "FET_0_1", node("circle", node("center", 1.651, 0), node("radius", 2.794)))
        terminals = node(
            "symbol",
            "FET_1_1",
            *[
                node(
                    "pin",
                    S("passive"),
                    S("line"),
                    node("at", x, y, a),
                    node("length", 2.54),
                    node("name", number),
                    node("number", number),
                )
                for number, x, y, a in pins
            ],
        )
        view = SymbolView(node("symbol", "Transistor_FET:test", body, terminals), pins, "Transistor_FET:test")
        component = PhysicalComponent(
            "hv_or.q1", "Q2", "Package_SO:PowerPAK_SO-8_Single", "SIR882BDP-T1-RE3-HXY", {}, None, "hv_or"
        )
        component.net_labels = {
            "4": "hv_or + tp_gnd + others/hv_or.ic.gate1",
            "5": "hv_or.pwr_out",
            **{n: "xt60_in.pwr" for n in ("1", "2", "3")},
        }
        component.placement_evidence = {"pattern": "power-path"}
        return component, view

    def test_annotation_selection_is_translation_invariant(self) -> None:
        component, view = self.fixture()
        local = annotation_position(component, view, 130.81, 114.30, 90)
        for dx, dy in ((-11.29, -21.31), (200.123, 30.777), (-110.81, 0)):
            translated = annotation_position(component, view, 130.81 + dx, 114.30 + dy, 90)
            self.assertAlmostEqual(translated[0], local[0] + dx)
            self.assertAlmostEqual(translated[1], local[1] + dy)

    def test_frozen_fields_are_shared_by_routing_and_serialization(self) -> None:
        component, view = self.fixture()
        frozen, x, y, angle = freeze_annotations([(component, 130.81, 114.30, 90)], {component.path: view})[0]
        self.assertIsNone(component.annotation)
        self.assertEqual(frozen.placement_evidence, component.placement_evidence)
        assert frozen.annotation is not None
        before = annotation_bounds(frozen, *frozen.annotation, angle)
        dx, dy = -11.29, -21.31
        rendered = replace(frozen, annotation=(frozen.annotation[0] + dx, frozen.annotation[1] + dy))
        at = annotation_position(rendered, view, x + dx, y + dy, angle)
        after = annotation_bounds(rendered, at[0], at[1], angle)
        for old, new, shift in zip(before, after, (dx, dy, dx, dy)):
            self.assertAlmostEqual(new, old + shift)
        # The native Q2 failure wire must have the same field collision verdict
        # before and after sheet translation; rerendering cannot move the field.
        wire = ((148.73, 87.91), (148.73, 123.47))
        self.assertEqual(
            segment_box(*wire, after),
            segment_box((wire[0][0] - dx, wire[0][1] - dy), (wire[1][0] - dx, wire[1][1] - dy), before),
        )
        repacked = freeze_annotations([(component, 220, 180, 90)], {component.path: view})[0][0]
        self.assertNotEqual(repacked.annotation, frozen.annotation)
        self.assertIsNone(component.annotation)

    def test_explicit_annotations_remain_authoritative(self) -> None:
        component, view = self.fixture()
        component.annotation = (60, 80)
        frozen = freeze_annotations([(component, 130, 114, 90)], {component.path: view})[0][0]
        self.assertEqual(frozen.annotation, (60, 80))
        self.assertEqual(component.annotation, (60, 80))
