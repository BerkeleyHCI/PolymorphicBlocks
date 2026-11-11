"""Fixed-placement search keeps the baseline unless a bounded trial improves it."""

import copy
import unittest
from collections import defaultdict

from .KiCadSchematicExporter import PhysicalComponent, SymbolView, node
from .KiCadSchematicLayout import route_local, tree_distance
from .KiCadSchematicRouting import optimize_fixed_routes, route_metrics


class RoutingOptimizerTest(unittest.TestCase):
    def test_tree_heuristic_matches_nearest_actual_tree_point(self):
        # Inside a sparse U-shaped tree, bounding-box distance is zero but
        # the actual remaining route still has a substantial lower bound.
        targets = {(x, 0) for x in range(41)} | {(0, y) for y in range(41)} | {(40, y) for y in range(41)}
        distance = tree_distance(targets)
        self.assertEqual(distance((20, 30)), 20)
        for x in range(-5, 46, 3):
            for y in range(-5, 46, 3):
                expected = min(abs(x - tx) + abs(y - ty) for tx, ty in targets)
                self.assertEqual(distance((x, y)), expected)
                self.assertEqual(distance((x, y)), expected)  # Cached query.


    def test_union_metrics_are_independent_of_duplicate_and_split_segments(self):
        wires = [("a", (0, 0), (10, 0)), ("a", (10, 0), (10, 10)),
                 ("b", (5, -2), (5, 2))]
        expected = dict(length_mm=24, bends=1, crossings=1, failures=0)
        self.assertEqual(route_metrics(wires, []), expected)
        overlapping = [("a", (0, 0), (5, 0)), ("a", (3, 0), (10, 0)),
                       wires[1], wires[2], wires[2]]
        self.assertEqual(route_metrics(overlapping, []), expected)
        self.assertEqual(route_metrics(list(reversed(overlapping)), []), expected)

    def test_real_routes_shorten_without_changing_fixed_placements_or_net_identity(self):
        placed, views, wiring = [], {}, {}
        for i, (x, y) in enumerate(((127, 63.5), (76.2, 88.9), (76.2, 114.3), (101.6, 114.3))):
            component = PhysicalComponent(str(i), "X" + str(i), "Fixture:Pad", "Pad",
                                          {"1": "p"}, None, "group", annotation=(x + 5, y + 10))
            placed.append((component, x, y, 0))
            views[component.path] = SymbolView(node("symbol"), [("1", 0, 0, 0)], "Fixture:Pad")
            wiring[component.path, "1"] = "signal"
        original = copy.deepcopy((placed, views, wiring))
        baseline = route_local(placed, views, wiring)
        actual, report = optimize_fixed_routes(placed, views, wiring, baseline, route_local)
        self.assertEqual((placed, views, wiring), original)
        self.assertLess(report["after"]["length_mm"], report["before"]["length_mm"])
        self.assertEqual(actual[1], baseline[1])  # Every physical pin escape remains fixed.
        self.assertEqual(actual[2], [])
        self.assertEqual({net for net, _, _ in actual[0]}, {"signal"})
        reverse = (list(reversed(placed)), dict(reversed(list(views.items()))),
                   dict(reversed(list(wiring.items()))))
        reversed_baseline = route_local(*reverse)
        reversed_actual = optimize_fixed_routes(*reverse, reversed_baseline, route_local)
        self.assertEqual(reversed_actual, (actual, report))
        # Exercise both heading-aware searches directly, even when another
        # candidate wins. Reconstruct their grid graph to catch lost/truncated
        # predecessor states or a route that misses an existing tree attachment.
        tight = [(c, 63.5 + i * 6.35, 76.2 + (i % 2) * 6.35, a)
                 for i, (c, _, _, a) in enumerate(placed)]
        tight_baseline = route_local(tight, views, wiring)
        for strategy in ("tree_search", "tree_reverse"):
            wires, escapes, failures = route_local(tight, views, wiring, strategy=strategy)
            self.assertEqual(failures, [])
            self.assertEqual(escapes, tight_baseline[1])
            self.assertEqual((wires, escapes, failures),
                             route_local(list(reversed(tight)), views, wiring, strategy=strategy))
            graph = defaultdict(set)
            for _, a, b in wires:
                start = tuple(round(v / 0.635) for v in a)
                end = tuple(round(v / 0.635) for v in b)
                self.assertTrue(start[0] == end[0] or start[1] == end[1])
                dx = (end[0] > start[0]) - (end[0] < start[0])
                dy = (end[1] > start[1]) - (end[1] < start[1])
                while start != end:
                    next_point = start[0] + dx, start[1] + dy
                    graph[start].add(next_point)
                    graph[next_point].add(start)
                    start = next_point
            endpoints = {tuple(round(v / 0.635) for v in escape[2:4]) for escape in escapes.values()}
            pending, reached = [min(endpoints)], set()
            while pending:
                point = pending.pop()
                if point not in reached:
                    reached.add(point)
                    pending.extend(graph[point] - reached)
            self.assertTrue(endpoints.issubset(reached))

    def test_candidate_gates_reject_new_failures_crossings_length_and_envelope_growth(self):
        baseline = ([("a", (0, 0), (10, 0)), ("a", (10, 0), (10, 10))], {}, [])
        candidates = {
            "new_failure": ([("a", (0, 0), (5, 0))], {}, [(("device", "1"), "a")]),
            "crossing": ([("a", (0, 5), (10, 5)), ("b", (5, 0), (5, 10))], {}, []),
            "longer": ([("a", (0, 0), (10, 0)), ("a", (10, 0), (10, 10)),
                        ("a", (10, 10), (0, 10))], {}, []),
            "outside": ([("a", (-1, 0), (2, 0))], {}, []),
        }
        for reason, candidate in candidates.items():
            with self.subTest(reason=reason):
                calls = []

                def router(*args, strategy):
                    calls.append(strategy)
                    return candidate

                result, report = optimize_fixed_routes([], {}, {}, baseline, router)
                self.assertEqual(result, baseline)
                self.assertEqual(report["selected"], "baseline")
                self.assertEqual(len(calls), report["candidates"] - 1)
                self.assertLessEqual(len(calls), 8)
                self.assertEqual(len(calls), len(set(calls)))
                self.assertTrue(all(not trial["acceptable"] for trial in report["trials"]))

    def test_longer_detour_can_remove_crossing_outside_original_envelope(self):
        baseline = ([("a", (50, 60), (70, 60)), ("b", (60, 50), (60, 70))], {}, [])
        candidate = ([("a", (50, 60), (50, 45)), ("a", (50, 45), (70, 45)),
                      ("a", (70, 45), (70, 60)), ("b", (60, 50), (60, 70))], {}, [])
        actual, report = optimize_fixed_routes([], {}, {}, baseline,
                                               lambda *args, **kwargs: candidate)
        self.assertEqual(actual, candidate)
        self.assertEqual(report["after"]["crossings"], 0)
        self.assertGreater(report["after"]["length_mm"], report["before"]["length_mm"])

    def test_equal_score_keeps_baseline_and_empty_baseline_does_not_search(self):
        baseline = ([("a", (0, 0), (10, 0))], {}, [])
        result, report = optimize_fixed_routes([], {}, {}, baseline, lambda *args, **kwargs: baseline)
        self.assertIs(result, baseline)
        self.assertEqual(report["selected"], "baseline")

        def forbidden(*args, **kwargs):
            self.fail("Empty baseline must not invoke candidate router")

        empty = ([], {}, [])
        self.assertEqual(optimize_fixed_routes([], {}, {}, empty, forbidden)[0], empty)


if __name__ == "__main__":
    unittest.main()
