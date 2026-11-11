"""Overview relationships are witnessed presentation, never electrical wiring."""

from __future__ import annotations
from typing import Any
from pathlib import Path
from .KiCadSchematicTypes import SExpr
from .KiCadSchematicPlanner import SchematicSheetPlan

import json
import unittest
from dataclasses import replace
import tempfile
import shutil
import subprocess
import sexpdata
from .KiCadSchematicExporter import _PreparedBoard, _RegionDrawing

from .KiCadSchematicOverview import (
    SchematicOverview,
    SchematicOverviewBlock,
    SchematicOverviewLink,
    build_overviews,
    render_overview,
)
from .KiCadSchematicPlanner import SchematicRegion, SchematicSheetPlanner
from .KiCadSchematicExporter import KiCadSchematicExporter, SchematicExportOptions, children, uid


def fixture(count: int = 3, scope: str = "board") -> tuple[_PreparedBoard, SchematicSheetPlan]:
    regions = tuple(
        SchematicRegion(scope + str(i), "Function " + str(i), scope, (scope + str(i) + ".part",), (0, 0, 50, 20))
        for i in range(count)
    )
    plan = SchematicSheetPlanner().plan_regions(regions, "fingerprint", assignments={r.id: r.title for r in regions})
    board = _PreparedBoard(
        scope=scope,
        prefix=scope,
        root_id=scope,
        views={},
        pin_nets={},
        names={},
        regions={r.id: _RegionDrawing(r, [], [], []) for r in regions},
        net_regions={
            "gnd": set(r.id for r in regions),
            "supply": set(r.id for r in regions),
            "data": set(r.id for r in regions[:2]),
        },
    )
    return board, plan


class SchematicOverviewTest(unittest.TestCase):
    def test_data_contract_and_malformed_inputs(self) -> None:
        data = {
            "blocks": [dict(sheet="Function 0", title="Source", summary="Power entry", column=0, row=1)],
            "links": [dict(source="Function 0", target="Function 1", label="Supply", nets=["supply"], directed=True)],
        }
        self.assertEqual(SchematicOverview.from_dict(data).to_dict(), data)
        invalid: dict[str, Any]
        for invalid in (
            {"callback": "execute"},
            {"blocks": {}},
            {"links": {}},
            {"blocks": [dict(data["blocks"][0], column=True)]},
            {"blocks": [dict(data["blocks"][0], row=4)]},
            {"blocks": [dict(data["blocks"][0], title="x" * 49)]},
            {"links": [dict(data["links"][0], directed="yes")]},
            {"links": [dict(data["links"][0], nets=[{}])]},
            {"links": [dict(data["links"][0], nets=[])]},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                SchematicOverview.from_dict(invalid)

    def test_authored_flow_requires_actual_shared_nets(self) -> None:
        board, plan = fixture()
        custom = SchematicOverview(
            links=(SchematicOverviewLink("Function 0", "Function 1", "Supply", ("supply",), True),)
        )
        data = build_overviews([board], plan, custom)["boards"][0]
        link = data["connections"][0]
        self.assertTrue(link["directed"])
        self.assertEqual(link["origin"], "authored")
        self.assertEqual(link["nets"], ["supply"])
        for net in ("invented", "gnd"):
            with self.assertRaisesRegex(ValueError, "does not connect"):
                build_overviews(
                    [board],
                    plan,
                    SchematicOverview(links=(SchematicOverviewLink("Function 0", "Function 1", "Invalid", (net,)),)),
                )
        with self.assertRaisesRegex(ValueError, "different sheets"):
            build_overviews(
                [board],
                plan,
                SchematicOverview(links=(SchematicOverviewLink("Function 0", "Function 0", "Self", ("supply",)),)),
            )
        with self.assertRaisesRegex(ValueError, "unknown or ambiguous"):
            build_overviews(
                [board],
                plan,
                SchematicOverview(links=(SchematicOverviewLink("Unknown", "Function 0", "Missing", ("supply",)),)),
            )

    def test_automatic_relationships_are_undirected_and_repeatable(self) -> None:
        board, plan = fixture()
        a = build_overviews([board], plan)
        b = build_overviews([board], plan)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        data = a["boards"][0]
        self.assertEqual(data["components"], 3)
        self.assertEqual(len(data["nodes"]), 3)
        self.assertTrue(data["connections"])
        self.assertTrue(all(not l["directed"] and "gnd" not in l["nets"] for l in data["connections"]))
        self.assertEqual(data["omitted_connection_pairs"], 1)

    def test_key_only_relationship_names_actual_endpoint_pages(self) -> None:
        board, plan = fixture(10)
        data = build_overviews([board], plan)["boards"][0]
        by_id = {n["sheet_id"]: n for n in data["nodes"]}
        self.assertEqual(len(data["connections"]), 8)
        for link in data["connections"]:
            # Exercise the fallback independently of routing-order heuristics.
            link["path"] = []
            link["status"] = "legend_only"
            self.assertEqual(
                link["endpoints"],
                [
                    dict(sheet_id=identity, sheet_title=by_id[identity]["sheet_title"], page=by_id[identity]["page"])
                    for identity in (link["source"], link["target"])
                ],
            )
        doc: SExpr = []
        render_overview(doc, board, data, SchematicExportOptions("Overview"))
        texts = {children(t, "uuid")[0][1]: t for t in children(doc, "text")}
        for link in data["connections"]:
            item = texts[uid(board.prefix, "overview", link["id"] + "-key")]
            for endpoint in link["endpoints"]:
                self.assertIn(f"Sheet {endpoint['page']}", item[1])
            self.assertIn("key only", item[1])
            for role in ("-key", "-key-label"):
                item = texts[uid(board.prefix, "overview", link["id"] + role)]
                x, y, angle = children(item, "at")[0][1:]
                self.assertGreaterEqual(y, 190)
                self.assertLess(y + 1.27, 203)
                self.assertLess(x + len(item[1]) * 1.27, 410)

    def test_summary_does_not_contradict_sheet_continuation_title(self) -> None:
        board, plan = fixture(2)
        original = next(iter(board.regions))
        board.regions[original].spec = replace(board.regions[original].spec, title="Balance /5")
        data = build_overviews([board], plan)["boards"][0]
        item = next(n for n in data["nodes"] if "Balance /5" in n["regions"])
        self.assertEqual(item["summary"], "Balance")
        self.assertEqual(item["sheet_title"], next(s.title for s in plan.sheets if s.id == item["sheet_id"]))

    def test_custom_cards_reserve_cells_and_detect_duplicates(self) -> None:
        board, plan = fixture()
        a = SchematicOverviewBlock("Function 1", "Controller", "Unicode μC", 0, 0)
        data = build_overviews([board], plan, SchematicOverview(blocks=(a,)))["boards"][0]
        self.assertEqual(len({(n["column"], n["row"]) for n in data["nodes"]}), 3)
        b = SchematicOverviewBlock("Function 0", "Input", "Power", 0, 0)
        with self.assertRaisesRegex(ValueError, "same grid cell"):
            build_overviews([board], plan, SchematicOverview(blocks=(a, b)))
        with self.assertRaisesRegex(ValueError, "duplicate overview block"):
            build_overviews([board], plan, SchematicOverview(blocks=(a, a)))

    def test_lines_are_graphics_and_sheet_navigation_is_preserved(self) -> None:
        board, plan = fixture()
        data = build_overviews([board], plan)["boards"][0]
        doc: SExpr = []
        for n in data["nodes"]:
            KiCadSchematicExporter._sheet_link(
                doc,
                board.prefix,
                uid(board.prefix, n["sheet_id"]),
                "/root",
                n["sheet_title"],
                n["sheet_id"] + ".kicad_sch",
                20,
                50,
                n["page"],
            )
        before = [children(s, "instances") for s in children(doc, "sheet")]
        render_overview(doc, board, data, SchematicExportOptions("Overview"))
        self.assertEqual(before, [children(s, "instances") for s in children(doc, "sheet")])
        self.assertEqual(len(children(doc, "sheet")), 3)
        self.assertTrue(children(doc, "polyline"))
        self.assertFalse(children(doc, "wire"))
        self.assertFalse(children(doc, "symbol"))
        self.assertFalse(any(children(s, "pin") for s in children(doc, "sheet")))
        for s in children(doc, "sheet"):
            self.assertEqual(children(s, "size")[0][1:], [83.82, 27.94])
        for link in data["connections"]:
            for p, q in zip(link["path"], link["path"][1:]):
                self.assertTrue(p[0] == q[0] or p[1] == q[1])

    def test_dense_branch_routes_reserve_stubs_and_clear_identifier_text(self) -> None:
        from .KiCadSchematicOverview import _segment_cells, _tag_box, _intersects

        board, plan = fixture(7)
        cells = ((0, 1), (1, 1), (2, 1), (3, 0), (3, 1), (3, 2), (3, 3))
        pairs = ((0, 1), (1, 2), (2, 3), (2, 4), (2, 5), (2, 6), (0, 2))
        custom = SchematicOverview(
            blocks=tuple(
                SchematicOverviewBlock(f"Function {i}", f"Function {i}", "Support circuit", *cell)
                for i, cell in enumerate(cells)
            ),
            links=tuple(
                SchematicOverviewLink(f"Function {a}", f"Function {b}", f"Relationship {i}", ("supply",), True)
                for i, (a, b) in enumerate(pairs)
            ),
        )
        data = build_overviews([board], plan, custom)["boards"][0]
        self.assertFalse(data["diagnostics"])
        occupied: set[tuple[int, int]] = set()
        strokes = []
        for link in data["connections"]:
            self.assertEqual(link["status"], "drawn")
            self.assertIsNotNone(link["tag"])
            path = link["path"]
            route = set()
            for a, b in zip(path, path[1:]):
                route.update(_segment_cells(a, b))
                strokes.append(
                    (min(a[0], b[0]) - 0.125, min(a[1], b[1]) - 0.125, max(a[0], b[0]) + 0.125, max(a[1], b[1]) + 0.125)
                )
            self.assertFalse(route & occupied, link["id"])
            occupied.update(route)
            for a, b, c in zip(path, path[1:], path[2:]):
                self.assertGreaterEqual((b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1]), 0)
        boxes = [_tag_box(link["tag"]) for link in data["connections"]]
        for i, box in enumerate(boxes):
            self.assertFalse(any(_intersects(box, line) for line in strokes))
            self.assertFalse(any(_intersects(box, other) for other in boxes[i + 1 :]))
            self.assertFalse(any(_intersects(box, n["bounds"]) for n in data["nodes"]))

    def test_multi_board_selectors_and_cross_scope_links(self) -> None:
        from .KiCadSchematicPlanner import SchematicSheetPlan

        a, pa = fixture(2, "a")
        b, pb = fixture(2, "b")
        plan = SchematicSheetPlan("fingerprint", pa.regions + pb.regions, pa.sheets + pb.sheets)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            build_overviews(
                [a, b],
                plan,
                SchematicOverview(blocks=(SchematicOverviewBlock("Function 0", "Title", "Summary", 0, 0),)),
            )
        sa = next(s for s in pa.sheets if s.id != "overview")
        sb = next(s for s in pb.sheets if s.id != "overview")
        with self.assertRaisesRegex(ValueError, "one board scope"):
            build_overviews(
                [a, b], plan, SchematicOverview(links=(SchematicOverviewLink(sa.id, sb.id, "Cross", ("supply",)),))
            )
        data = build_overviews([a, b], plan)
        self.assertEqual(len(data["boards"]), 2)
        self.assertTrue(all(d["components"] == 2 for d in data["boards"]))
        self.assertTrue(all([n["page"] for n in d["nodes"]] == [2, 3] for d in data["boards"]))

    def test_large_inventory_falls_back_without_dropping_sheets(self) -> None:
        board, plan = fixture(41)
        data = build_overviews([board], plan)["boards"][0]
        self.assertEqual(data["mode"], "directory")
        self.assertEqual(len(data["nodes"]), 41)
        self.assertFalse(data["connections"])
        self.assertEqual(data["components"], 41)
        self.assertTrue(all(node["section"] for node in data["nodes"]))
        self.assertEqual({node["page"] for node in data["nodes"]}, set(range(2, 43)))
        self.assertTrue(all(node["bounds"][2] < 410 and node["bounds"][3] < 205 for node in data["nodes"]))
        with self.assertRaisesRegex(ValueError, "at most 16 sheets"):
            build_overviews(
                [board],
                plan,
                SchematicOverview(blocks=(SchematicOverviewBlock("Function 0", "Title", "Summary", 0, 0),)),
            )

    def test_paginated_directory_machine_geometry_matches_actual_links(self) -> None:
        # Contents nesting begins at 41; 49 must remain supported rather than
        # overflowing the old grouped-directory capacity or dropping navigation.
        for count in (41, 49):
            with self.subTest(count=count):
                board, plan = fixture(count)
                data = build_overviews([board], plan)["boards"][0]
                self.assertEqual(data["directory_layout"], "paginated")
                self.assertEqual(sum(p["sheets"] for p in data["directory_pages"]), count)
                options = SchematicExportOptions("Directory")
                root = KiCadSchematicExporter._document(uid("root"), options, "f", "Overview")
                documents = {}
                for page in data["directory_pages"]:
                    identity = uid(board.prefix, "contents", str(page["index"]))
                    documents[page["filename"]] = KiCadSchematicExporter._document(
                        identity, options, "f", page["title"]
                    )
                    x, y = page["bounds"][:2]
                    KiCadSchematicExporter._sheet_link(
                        root, board.prefix, identity, "/root", page["title"], page["filename"], x, y, page["page"]
                    )
                for index, item in enumerate(data["nodes"]):
                    slot = index % 40
                    document = documents[item["directory_document"]]
                    # Actual serializer placement, independently of evidence.
                    x, y = 20 + (slot // 10) * 90, 50 + (slot % 10) * 14
                    KiCadSchematicExporter._sheet_link(
                        document,
                        board.prefix,
                        uid(board.prefix, item["sheet_id"]),
                        "/contents",
                        item["sheet_title"],
                        "circuit.kicad_sch",
                        x,
                        y,
                        item["page"],
                    )
                    link = children(document, "sheet")[-1]
                    at, size = children(link, "at")[0][1:], children(link, "size")[0][1:]
                    self.assertEqual(item["bounds"], [at[0], at[1], at[0] + size[0], at[1] + size[1]])
                render_overview(root, board, data, options)
                links = children(root, "sheet")
                self.assertEqual(len(links), len(data["directory_pages"]))
                for link, page in zip(links, data["directory_pages"]):
                    at, size = children(link, "at")[0][1:], children(link, "size")[0][1:]
                    self.assertEqual(page["bounds"], [at[0], at[1], at[0] + size[0], at[1] + size[1]])
                titles = [item[1] for item in children(root, "text")]
                self.assertTrue(any("40 sheets / 40 components" in text for text in titles))

    def test_compiled_preview_bundle_staleness_and_native_truth(self) -> None:
        from ..core import ScalaCompiler
        from ..electronics_interfaces.test_netlist import TestBasicCircuit
        from .RefdesRefinementPass import RefdesRefinementPass
        from .NetlistGenerator import NetlistTransform
        from .SchematicVerification import verify_schematic_netlist
        from .KiCadSchematicExporter import SchematicPlacement

        compiled = ScalaCompiler.compile(TestBasicCircuit)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        options = SchematicExportOptions(
            "OverviewFixture",
            placements={"source": SchematicPlacement("Power", 70, 80), "sink": SchematicPlacement("Load", 100, 80)},
            sheet_assignments={"Power": "Power", "Load": "Load"},
        )
        old_plan = SchematicSheetPlanner().plan(compiled, options)
        nets = next(iter(NetlistTransform(compiled).run().values()))
        shared = next(n.name for n in nets.nets if len(n.pins) > 1 and "gnd" not in n.name.lower())
        custom = SchematicOverview(
            blocks=(
                SchematicOverviewBlock("Power", "Input", "Source support", 0, 1),
                SchematicOverviewBlock("Load", "Output", "Load support", 1, 1),
            ),
            links=(SchematicOverviewLink("Power", "Load", "Physical association", (shared,), True),),
        )
        options = replace(options, overview=custom)
        exporter = KiCadSchematicExporter()
        with self.assertRaisesRegex(ValueError, "stale sheet plan"):
            exporter.export(compiled, replace(options, sheet_plan=old_plan))
        bundle = exporter.export(compiled, options)
        self.assertEqual(json.loads(bundle.files["overview.json"]), exporter.overview(compiled, options))
        self.assertEqual(bundle.files, exporter.export(compiled, options).files)
        manifest = json.loads(bundle.files["manifest.json"])
        root = manifest["boards"][0]["root"]
        tree = sexpdata.loads(bundle.files[root])
        page = children(children(children(tree, "sheet_instances")[0], "path")[0], "page")[0][1]
        self.assertEqual(page, "1")
        self.assertEqual(sum(n.endswith(".kicad_sch") for n in bundle.files), 3)
        if shutil.which("kicad-cli"):
            with tempfile.TemporaryDirectory() as directory:
                bundle.write(Path(directory))
                xml = Path(directory) / "truth.xml"
                subprocess.run(
                    [
                        "kicad-cli",
                        "sch",
                        "export",
                        "netlist",
                        "--format",
                        "kicadxml",
                        "-o",
                        str(xml),
                        str(Path(directory) / root),
                    ],
                    check=True,
                    capture_output=True,
                )
                verify_schematic_netlist(nets, xml)


if __name__ == "__main__":
    unittest.main()
