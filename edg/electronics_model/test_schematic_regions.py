"""Measured-region regressions independent of human visual acceptance."""

import unittest
import importlib
from types import SimpleNamespace
from unittest.mock import patch

from ..core import Block, ScalaCompiler
from .KiCadSchematicExporter import (
    KiCadSchematicExporter,
    SchematicExportOptions,
    SchematicPlacement,
    PhysicalComponent,
    children,
    generic,
    SymbolView,
    node,
    _RegionDrawing,
)
from .KiCadSchematicLayout import ground_bounds, ground_rotation, annotation_position, graphic_bounds
from .KiCadSchematicPlanner import SchematicRegion, SchematicRegionPlacement, SchematicSheet
from .RefdesRefinementPass import RefdesRefinementPass
from .test_schematic_export import GeneratedMappedBoard


class TwoCircuitParts(Block):
    def contents(self):
        super().contents()
        self.a = self.Block(GeneratedMappedBoard())
        self.b = self.Block(GeneratedMappedBoard())


class ContinuationCollisionBoard(Block):
    def contents(self):
        super().contents()
        self.foo = self.Block(TwoCircuitParts())
        setattr(self, "foo /2", self.Block(GeneratedMappedBoard()))


class SchematicRegionTest(unittest.TestCase):
    def test_ground_graphic_points_away_from_adjacent_pin_rows(self):
        # The contact remains at the stub endpoint; the complete graphic must
        # extend outwards, never down into the next connector/IC pin row.
        for direction, rotation in ((0, 270), (90, 0), (180, 90), (270, 180)):
            self.assertEqual(ground_rotation(direction), rotation)
            xmin, ymin, xmax, ymax = ground_bounds(100, 100, direction)
            if direction == 0:
                self.assertLess(xmin, 100)
                self.assertEqual(xmax, 100)
            elif direction == 180:
                self.assertEqual(xmin, 100)
                self.assertGreater(xmax, 100)
            elif direction == 90:
                self.assertEqual(ymin, 100)
                self.assertGreater(ymax, 100)
            else:
                self.assertLess(ymin, 100)
                self.assertEqual(ymax, 100)

    def test_default_ic_fields_clear_ground_stub_and_graphic(self):
        component = PhysicalComponent("ic", "U1", "Test:FP", "device", {"1": "gnd"}, None, "IC")
        view = generic(component)
        _, _, _, bottom = graphic_bounds(view)
        _, field_y, _ = annotation_position(component, view, 100, 100, 0)
        self.assertGreater(field_y - 1.27, 100 + bottom + 3.81 + 4.445)

    def test_short_inter_region_wire_requires_a_clear_corridor(self):
        definition = node(
            "symbol",
            "Test:C",
            node("symbol", "C_0_1", node("rectangle", node("start", -1.27, 1.27), node("end", 1.27, -1.27))),
        )
        view = SymbolView(definition, [("1", 0, -3.81, 270), ("2", 0, 3.81, 90)], "Device:C")
        regions = {}
        components = []
        for index in range(2):
            name = "cap" + str(index)
            component = PhysicalComponent(
                name, "C" + str(index + 1), "Test:FP", "100nF", {"1": "pwr", "2": "gnd"}, None, name
            )
            components.append(component)
            spec = SchematicRegion(name, name, "root", (name,), (50, 50, 80, 100))
            regions[name] = _RegionDrawing(spec, [(component, 65, 75, 0)], [], [])
        board = SimpleNamespace(
            regions=regions,
            views={c.path: view for c in components},
            pin_nets={(c.path, pin): net for c in components for pin, net in (("1", "v3v3"), ("2", "gnd"))},
            names={"v3v3": "v3v3", "gnd": "gnd"},
        )
        sheet = SchematicSheet(
            "sheet",
            "Caps",
            "root",
            (SchematicRegionPlacement("cap0", 20, 40), SchematicRegionPlacement("cap1", 58, 40)),
        )
        clear = []
        KiCadSchematicExporter._inter_region_wires(clear, board, sheet, "id", [])
        self.assertEqual(len(children(clear, "wire")), 1)
        blocked = []
        KiCadSchematicExporter._inter_region_wires(blocked, board, sheet, "id", [("other_net", (54, 50), (54, 60))])
        self.assertFalse(children(blocked, "wire"))

    def test_unwrapped_value_reserves_full_rendered_width(self):
        component = PhysicalComponent("x", "U1", "Test:FP", "W" * 40, {}, None, "Tiny")
        view = generic(component)
        bounds = KiCadSchematicExporter._region_bounds([(component, 70, 80, 0)], {"x": view}, {}, {}, [], "Tiny")
        self.assertGreaterEqual(bounds[2] - bounds[0], 40 * 1.27 + 7.99)

    def test_heading_wrap_and_measured_width(self):
        component = PhysicalComponent("x", "U1", "Test:FP", "part", {}, None, "Tiny")
        view = generic(component)
        short = KiCadSchematicExporter._region_bounds([(component, 70, 80, 0)], {"x": view}, {}, {}, [], "X")
        long = KiCadSchematicExporter._region_bounds(
            [(component, 70, 80, 0)], {"x": view}, {}, {}, [], "functional " * 20
        )
        self.assertLess(long[1], short[1])
        self.assertGreaterEqual(long[2] - long[0], 42)

    def test_literal_name_cannot_overwrite_another_groups_continuation(self):
        compiled = ScalaCompiler.compile(ContinuationCollisionBoard)
        compiled.append_values(RefdesRefinementPass().run(compiled))

        def split_every_member(members, views, pin_nets):
            return [[(c, 70, 80, 0)] for c in members]

        with patch.object(
            importlib.import_module(__package__ + ".KiCadSchematicExporter"),
            "place_group",
            side_effect=split_every_member,
        ):
            regions, _ = KiCadSchematicExporter().prepare_regions(compiled, SchematicExportOptions("Collision"))
        paths = [path for region in regions for path in region.components]
        self.assertEqual(len(paths), 3)
        self.assertEqual(len(set(paths)), 3)
        self.assertEqual(len({r.id for r in regions}), 3)


if __name__ == "__main__":
    unittest.main()
