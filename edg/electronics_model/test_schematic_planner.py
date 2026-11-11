"""Whole-region planning is deterministic and rejects unsafe edited plans."""

import copy
import json
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from .KiCadSchematicPlanner import (
    SchematicRegion,
    SchematicRegionPlacement,
    SchematicSheet,
    SchematicSheetPlan,
    SchematicSheetPlanner,
    USABLE_BOUNDS,
    OVERVIEW_BOUNDS,
)


def region(identity, width=80, height=50, scope="(root)", title=None, components=None, kind="circuit"):
    return SchematicRegion(
        identity,
        title or identity,
        scope,
        (identity + ".part",) if components is None else components,
        (-5, -10, width - 5, height - 10),
        kind,
    )


class SchematicPlannerTest(unittest.TestCase):
    def setUp(self):
        self.planner = SchematicSheetPlanner()

    def test_packs_whole_regions_together_and_is_order_independent(self):
        regions = [region("controller"), region("power", 120, 70), region("usb", 70, 40)]
        first = self.planner.plan_regions(regions, "fingerprint")
        second = self.planner.plan_regions(list(reversed(regions)), "fingerprint")
        self.assertEqual(first, second)
        self.assertEqual(len(first.sheets), 1)
        self.assertEqual({p.region_id for p in first.sheets[0].regions}, {r.id for r in regions})
        self.assertEqual(first.sheets[0].regions[0].region_id, "power")
        self.assertEqual(first.regions[0].components, ("controller.part",))

    def test_reserves_native_title_block(self):
        plan = self.planner.plan_regions([region("a", 200, 200), region("b", 140, 80), region("c", 140, 80)], "f")
        regions = {r.id: r for r in plan.regions}
        for sheet in plan.sheets:
            for p in sheet.regions:
                r = regions[p.region_id]
                self.assertTrue(p.x + r.bounds[2] - r.bounds[0] <= 230 or p.y + r.bounds[3] - r.bounds[1] <= 245)

    def test_json_round_trip_is_strict_and_does_not_alias_input(self):
        plan = self.planner.plan_regions([region("power")], "fingerprint")
        data = json.loads(json.dumps(plan.to_dict()))
        self.assertEqual(SchematicSheetPlan.from_dict(data), plan)
        adopted = self.planner.plan_regions(plan.regions, "fingerprint", requested=data)
        self.assertEqual(adopted.sheets, plan.sheets)
        data["regions"][0]["components"][0] = "mutated"
        self.assertEqual(plan.regions[0].components, ("power.part",))
        bad = plan.to_dict()
        bad["approved"] = True
        with self.assertRaisesRegex(ValueError, "unknown or missing"):
            SchematicSheetPlan.from_dict(bad)
        bad = plan.to_dict()
        bad["sheets"][0]["regions"][0]["x"] = True
        with self.assertRaisesRegex(ValueError, "finite number"):
            SchematicSheetPlan.from_dict(bad)
        bad = plan.to_dict()
        bad["overview"] = "yes"
        with self.assertRaisesRegex(ValueError, "boolean"):
            SchematicSheetPlan.from_dict(bad)

    def test_assignment_aliases_unknown_ambiguous_and_conflicting(self):
        regions = [region("root::Power", title="Power"), region("root::USB", title="USB")]
        plan = self.planner.plan_regions(regions, "f", assignments={"Power": "Supply", "root::Power": "Supply"})
        self.assertEqual(
            next(s.title for s in plan.sheets if any(p.region_id == "root::Power" for p in s.regions)), "Supply"
        )
        with self.assertRaisesRegex(ValueError, "unknown assignment"):
            self.planner.plan_regions(regions, "f", assignments={"typo": "Supply"})
        with self.assertRaisesRegex(ValueError, "conflicting assignments"):
            self.planner.plan_regions(regions, "f", assignments={"Power": "Supply", "root::Power": "Other"})
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.planner.plan_regions(
                [region("a", title="Power"), region("b", title="Power", scope="other")],
                "f",
                assignments={"Power": "Supply"},
            )

    def test_requested_plan_rejects_stale_fingerprint_geometry_and_membership(self):
        regions = [region("a"), region("b")]
        plan = self.planner.plan_regions(regions, "f")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.planner.plan_regions(regions, "new", requested=plan)
        bad = plan.to_dict()
        bad["regions"][0]["components"] = ["different.part"]
        with self.assertRaisesRegex(ValueError, "membership"):
            self.planner.plan_regions(regions, "f", requested=bad)
        bad = plan.to_dict()
        bad["regions"][0]["bounds"][2] -= 1
        with self.assertRaisesRegex(ValueError, "bounds or membership"):
            self.planner.plan_regions(regions, "f", requested=bad)
        bad = plan.to_dict()
        bad["sheets"][0]["regions"].pop()
        with self.assertRaisesRegex(ValueError, "exactly once"):
            self.planner.plan_regions(regions, "f", requested=bad)
        bad = plan.to_dict()
        bad["sheets"][0]["regions"].append(copy.deepcopy(bad["sheets"][0]["regions"][0]))
        with self.assertRaisesRegex(ValueError, "more than once"):
            SchematicSheetPlan.from_dict(bad)

    def test_requested_plan_rejects_overlap_small_gutter_outside_and_nonfinite(self):
        regions = [region("a", 50, 30), region("b", 50, 30)]
        plan = self.planner.plan_regions(regions, "f")
        for x, y, message in [(20, 40, "overlap"), (77, 40, "gutter"), (394, 40, "outside")]:
            bad = plan.to_dict()
            bad["sheets"][0]["regions"][1].update(x=x, y=y)
            with self.assertRaisesRegex(ValueError, message):
                SchematicSheetPlan.from_dict(bad)
        for value in (math.inf, math.nan, True):
            with self.assertRaisesRegex(ValueError, "finite number"):
                SchematicRegionPlacement("a", value, 40)

    def test_board_scopes_do_not_merge_even_with_heavy_adjacency(self):
        regions = [region("left", scope="one"), region("right", scope="two")]
        plan = self.planner.plan_regions(regions, "f", adjacency={("left", "right"): 1000})
        self.assertEqual(len(plan.sheets), 2)
        self.assertEqual({s.scope for s in plan.sheets}, {"one", "two"})
        bad = plan.to_dict()
        bad["sheets"][0]["scope"] = "two"
        with self.assertRaisesRegex(ValueError, "between board scopes"):
            SchematicSheetPlan.from_dict(bad)

    def test_explicit_fixed_set_can_continue_without_cropping(self):
        regions = [region("a", 300, 150), region("b", 300, 150)]
        plan = self.planner.plan_regions(regions, "f", assignments={"a": "Power", "b": "Power"})
        self.assertEqual({s.title for s in plan.sheets}, {"Overview", "Power /1", "Power /2"})
        self.assertTrue(any(d.startswith("continuation:") for d in plan.diagnostics))
        with self.assertRaisesRegex(ValueError, "exceeds usable A3.*no content was cropped"):
            self.planner.plan_regions([region("oversize", 400, 250)], "f")
        with self.assertRaisesRegex(ValueError, "overview inset"):
            self.planner.plan_regions([region("mechanical", 200, 70)], "f", assignments={"mechanical": "Overview"})

    def test_root_overview_contains_only_explicit_inset_regions(self):
        regions = [region("mechanical", 230, 20), region("power", 100, 100), region("mcu", 100, 100)]
        plan = self.planner.plan_regions(
            regions, "f", assignments={"mechanical": "Overview", "power": "Power", "mcu": "MCU"}
        )
        overview = next(s for s in plan.sheets if s.id == "overview")
        self.assertEqual(overview.title, "Overview")
        self.assertEqual(overview.regions[0].region_id, "mechanical")
        self.assertEqual((overview.regions[0].x, overview.regions[0].y), OVERVIEW_BOUNDS[:2])
        bad = plan.to_dict()
        bad["sheets"][0]["regions"][0]["y"] = 100
        with self.assertRaisesRegex(ValueError, "outside usable"):
            SchematicSheetPlan.from_dict(bad)

    def test_overview_rules_and_empty_design(self):
        one = self.planner.plan_regions([region("a")], "f")
        self.assertEqual(len(one.sheets), 1)
        multiple = self.planner.plan_regions([region("a", 300, 150), region("b", 300, 150)], "f")
        self.assertEqual(len(multiple.sheets), 3)
        self.assertEqual(multiple.sheets[0].id, "overview")
        no_overview = self.planner.plan_regions(multiple.regions, "f", overview=False)
        self.assertEqual(len(no_overview.sheets), 2)
        empty = self.planner.plan_regions([region("empty", components=())], "f")
        self.assertEqual(len(empty.sheets), 1)
        self.assertEqual(SchematicSheetPlan.from_dict(empty.to_dict()), empty)
        standalone_empty = self.planner.plan_regions([], "f")
        self.assertEqual(standalone_empty.sheets[0].id, "overview")
        with self.assertRaisesRegex(ValueError, "only an overview"):
            SchematicSheet("empty", "Empty", "scope", ())

    def test_adjacency_prefers_a_connected_sheet_when_both_fit(self):
        # First two regions cannot share a sheet; the small third can fit either.
        regions = [region("a", 250, 150), region("b", 250, 150), region("c", 40, 40)]
        plan = self.planner.plan_regions(regions, "f", adjacency={("b", "c"): 5})
        locations = {p.region_id: s.id for s in plan.sheets for p in s.regions}
        self.assertEqual(locations["b"], locations["c"])
        self.assertNotEqual(locations["a"], locations["c"])
        self.assertTrue(any(d.startswith("cross_sheet_connections:") for d in plan.diagnostics))

    def test_continuations_are_numbered_within_functional_title(self):
        regions = [region("a", 300, 150, title="Control"),
                   region("b", 300, 150, title="Control /2"),
                   region("c", 300, 150, title="USB")]
        plan = self.planner.plan_regions(regions, "f")
        self.assertEqual({s.title for s in plan.sheets}, {"Overview", "Control /1", "Control /2", "USB"})

    def test_continuation_page_order_is_numeric(self):
        regions = [region(f"r{i:02}", 300, 150, title="Control") for i in range(12)]
        plan = self.planner.plan_regions(regions, "f")
        self.assertEqual([s.title for s in plan.sheets if s.id != "overview"],
                         [f"Control /{i}" for i in range(1, 13)])

    def test_mixed_titles_follow_underlying_region_continuations(self):
        from .KiCadSchematicPlanner import _continuation_order
        regions = {r.id: r for r in [region('a', title='bms'), region('b', title='bms /2'),
                                    region('c', title='bms /3'), region('d', title='epd'),
                                    region('e', title='epd /2')]}
        sheets = [SchematicSheet('a', 'bms + alert', '(root)', (SchematicRegionPlacement('a', 20, 40),)),
                  SchematicSheet('b', 'bms + vbus', '(root)', (SchematicRegionPlacement('b', 20, 40),)),
                  SchematicSheet('c', 'bms + logic', '(root)', (SchematicRegionPlacement('c', 20, 40),)),
                  SchematicSheet('d', 'epd', '(root)', (SchematicRegionPlacement('d', 20, 40),)),
                  SchematicSheet('e', 'balance + epd', '(root)', (SchematicRegionPlacement('e', 20, 40),))]
        ordered = _continuation_order(list(reversed(sheets)), regions, [])
        indices = {s.id: i for i, s in enumerate(ordered)}
        self.assertLess(indices['a'], indices['b'])
        self.assertLess(indices['b'], indices['c'])
        self.assertLess(indices['d'], indices['e'])
        self.assertEqual(ordered, _continuation_order(sheets, regions, []))

    def test_array_ranges_remain_ordered_when_first_page_waits_for_epd(self):
        from .KiCadSchematicPlanner import _continuation_order
        regions = {r.id: r for r in [region('a', title='balance[0,1]'),
                    region('b', title='balance[2,3]'), region('c', title='balance[4,5]'),
                    region('d', title='epd'), region('e', title='epd /2')]}
        sheets = [SchematicSheet('a', 'balance + epd', '(root)',
                       (SchematicRegionPlacement('a', 20, 40), SchematicRegionPlacement('e', 20, 100))),
                  SchematicSheet('b', 'balance', '(root)', (SchematicRegionPlacement('b', 20, 40),)),
                  SchematicSheet('c', 'balance', '(root)', (SchematicRegionPlacement('c', 20, 40),)),
                  SchematicSheet('d', 'epd', '(root)', (SchematicRegionPlacement('d', 20, 40),))]
        diagnostics = []
        ordered = _continuation_order(sheets, regions, diagnostics)
        self.assertEqual([sheet.id for sheet in ordered], ['d', 'a', 'b', 'c'])
        self.assertFalse(diagnostics)

    def test_signal_neighbour_is_packed_before_unrelated_larger_region(self):
        regions = [region("a", 250, 150), region("b", 200, 60), region("c", 100, 60)]
        plan = self.planner.plan_regions(regions, "f", adjacency={("a", "c"): 5})
        sheet = next(s for s in plan.sheets if any(p.region_id == "a" for p in s.regions))
        self.assertEqual([p.region_id for p in sheet.regions][:2], ["a", "c"])

    def test_duplicate_component_ownership_and_unsafe_requested_assignment(self):
        with self.assertRaisesRegex(ValueError, "more than one region"):
            self.planner.plan_regions([region("a", components=("same",)), region("b", components=("same",))], "f")
        regions = [region("a")]
        plan = self.planner.plan_regions(regions, "f", assignments={"a": "Supply"})
        with self.assertRaisesRegex(ValueError, "conflicts with sheet assignment"):
            self.planner.plan_regions(regions, "f", requested=plan, assignments={"a": "Other"})

    def test_mechanical_kind_defaults_to_overview_and_explicit_override_wins(self):
        regions = [region("root::holes", 230, 20, title="Any title", kind="mechanical"), region("power")]
        plan = self.planner.plan_regions(regions, "f")
        overview = next(sheet for sheet in plan.sheets if sheet.id == "overview")
        self.assertEqual([p.region_id for p in overview.regions], ["root::holes"])
        for assignments in ({"root::holes": "Assembly notes"}, {"Any title": "Assembly notes"}):
            plan = self.planner.plan_regions(regions, "f", assignments=assignments)
            sheet = next(sheet for sheet in plan.sheets if sheet.title == "Assembly notes")
            self.assertEqual([p.region_id for p in sheet.regions], ["root::holes"])
            self.assertFalse(next(sheet for sheet in plan.sheets if sheet.id == "overview").regions)
        # A title alone does not classify a circuit as mechanical.
        ordinary = self.planner.plan_regions([region("ordinary", title="Mechanical notes")], "f")
        self.assertNotEqual(ordinary.sheets[0].id, "overview")

    def test_kind_json_compatibility_and_validation(self):
        ordinary = region("circuit")
        self.assertNotIn("kind", ordinary.to_dict())
        self.assertEqual(SchematicRegion.from_dict(ordinary.to_dict()).kind, "circuit")
        mechanical = region("holes", 230, 20, kind="mechanical")
        self.assertEqual(SchematicRegion.from_dict(mechanical.to_dict()), mechanical)
        plan = self.planner.plan_regions([mechanical], "f")
        self.assertEqual(SchematicSheetPlan.from_dict(plan.to_dict()), plan)
        with self.assertRaisesRegex(ValueError, "region kind"):
            region("bad", kind="guess")
        with self.assertRaisesRegex(ValueError, "empty region"):
            region("bad", kind="empty")
        empty = region("empty", components=(), kind="empty")
        self.assertEqual(SchematicRegion.from_dict(empty.to_dict()), empty)

    def test_plan_convenience_delegates_to_prepared_regions(self):
        regions = (region("a"),)
        options = SimpleNamespace(sheet_assignments={}, sheet_plan=None)
        from .KiCadSchematicExporter import KiCadSchematicExporter

        expected = self.planner.plan_regions(regions, "f")
        compiled = object()
        with patch.object(KiCadSchematicExporter, "_plan_compiled", return_value=expected, create=True) as prepare:
            plan = self.planner.plan(compiled, options)
        prepare.assert_called_once_with(compiled, options)
        self.assertIs(plan, expected)
        self.assertEqual(plan.fingerprint, "f")
        self.assertEqual(plan.regions, regions)


if __name__ == "__main__":
    unittest.main()
