"""Ownership-aware routing must survive explicit presentation coordinates."""

import copy
import unittest
from collections import defaultdict

from .KiCadSchematicExporter import PhysicalComponent, SymbolView, node
from .KiCadSchematicLayout import route_local


class DecouplingRoutingTest(unittest.TestCase):
    def fixture(self, count):
        placed, views, wiring, pairs = [], {}, {}, []
        for i in range(count):
            owner = f"rgb.pixel[{i}]"
            device = PhysicalComponent(
                owner + ".device", f"U{i}", "FP", "pixel",
                {"1": "vdd", "2": "gnd", "3": "din", "4": "dout"}, None, "rgb",
            )
            cap = PhysicalComponent(
                owner + ".bypass.cap", f"C{i}", "FP", "100nF",
                {"1": "pos", "2": "neg"}, {"lib_id": "Device:C"}, "rgb",
                hierarchy=((owner + ".bypass", "edg.abstract_parts.Capacitor.DecouplingCapacitor"),),
            )
            x = 35.3 + i * 40.64  # Intentionally not on the routing grid.
            device.annotation = (x, 133.35)
            cap.annotation = (x + 12.7, 59.69)
            placed.extend(((device, x, 110.49, 0), (cap, x + 12.7, 76.2, 0)))
            views[device.path] = SymbolView(
                node("symbol", node("rectangle", node("start", -2.54, 2.54), node("end", 2.54, -2.54))),
                [("1", 0, -5.08, 270), ("2", 0, 5.08, 90),
                 ("3", -5.08, 0, 0), ("4", 5.08, 0, 180)], "Test:Pixel",
            )
            views[cap.path] = SymbolView(
                node("symbol", node("rectangle", node("start", -1.27, 1.27), node("end", 1.27, -1.27))),
                [("1", -3.81, 0, 0), ("2", 3.81, 0, 180)], "Device:C",
            )
            wiring.update({(device.path, "1"): "supply", (device.path, "2"): "gnd",
                           (device.path, "3"): f"data{i}", (device.path, "4"): f"data{i + 1}",
                           (cap.path, "1"): "supply", (cap.path, "2"): "gnd"})
            pairs.append((device.path, cap.path, x))
        return placed, views, wiring, pairs

    def test_explicit_hints_keep_each_cap_branch_local_without_second_bus(self):
        for count in (1, 8):
            placed, views, wiring, pairs = self.fixture(count)
            before = copy.deepcopy((placed, views, wiring))
            wires, escapes, failures = route_local(placed, views, wiring)
            self.assertEqual(failures, [])
            self.assertEqual((placed, views, wiring), before)
            self.assertEqual(set(escapes), set(wiring))
            self.assertTrue(all(net in wiring.values() for net, _, _ in wires))
            for device, cap, x in pairs:
                # Inspect only the owner's narrow channel. A remote capacitor
                # bus cannot satisfy this connectivity check via another pixel.
                graph = defaultdict(set)
                for net, a, b in wires:
                    if net != "supply" or min(a[0], b[0]) < x - 6 or max(a[0], b[0]) > x + 18:
                        continue
                    dx, dy = b[0] - a[0], b[1] - a[1]
                    self.assertTrue(dx == 0 or dy == 0)
                    steps = max(1, round(max(abs(dx), abs(dy)) / 0.635))
                    points = [(round(a[0] + dx * n / steps, 4), round(a[1] + dy * n / steps, 4))
                              for n in range(steps + 1)]
                    for p, q in zip(points, points[1:]):
                        graph[p].add(q)
                        graph[q].add(p)
                start = tuple(escapes[cap, "1"][2:4])
                target = tuple(escapes[device, "1"][2:4])
                todo, reached = [start], set()
                while todo:
                    point = todo.pop()
                    if point not in reached:
                        reached.add(point)
                        todo.extend(graph[point] - reached)
                self.assertIn(target, reached)
            # Upper support area must contain short branches, not a parallel
            # horizontal rail spanning neighboring bypass capacitors.
            for net, a, b in wires:
                if net == "supply" and a[1] == b[1] and a[1] < 95:
                    self.assertLess(abs(a[0] - b[0]), 20)

    def test_conflicting_cap_hints_report_fallback_instead_of_shared_branch(self):
        placed, views, wiring, pairs = self.fixture(2)
        # An authored plan overlays two bypasses. Their identical supply escapes
        # must not become a misleading local branch that appears to serve both.
        cap0 = placed[1]
        cap1 = placed[3]
        placed[3] = (cap1[0], cap0[1], cap0[2], cap0[3])
        cap1[0].annotation = cap0[0].annotation
        _, escapes, failures = route_local(placed, views, wiring)
        self.assertEqual(escapes[cap0[0].path, "1"], escapes[cap1[0].path, "1"])
        self.assertTrue({((cap, "1"), "supply") for _, cap, _ in pairs}.issubset(set(failures)))

    def test_readability_flags_split_or_missing_support_and_never_auto_approves(self):
        import sexpdata
        from .KiCadSchematicReadability import inspect_documents
        from .KiCadSchematicPatterns import decoupling_associations

        placed, views, wiring, _ = self.fixture(1)
        device, cap = [entry[0] for entry in placed]
        patterns = [p.to_dict() for p in decoupling_associations([device, cap], wiring, views)]

        def document(*components):
            return sexpdata.dumps(node("kicad_sch", *[
                node("symbol", node("property", "PBPath", c.path)) for c in components
            ]))

        cases = (
            ({"together.kicad_sch": document(device, cap)}, False),
            ({"device.kicad_sch": document(device), "cap.kicad_sch": document(cap)}, True),
            ({"device.kicad_sch": document(device)}, True),
        )
        for files, expected in cases:
            evidence = inspect_documents(files, [], patterns)
            split = [f for f in evidence["findings"] if f["code"] == "decoupling_split"]
            self.assertEqual(bool(split), expected)
            if expected:
                self.assertEqual(split[0]["objects"], sorted((device.path, cap.path)))
            self.assertEqual(evidence["visual_approval"], "pending")

    def test_input_order_does_not_change_routing_or_pin_escapes(self):
        placed, views, wiring, _ = self.fixture(3)
        actual = route_local(placed, views, wiring)
        reversed_result = route_local(list(reversed(placed)), dict(reversed(list(views.items()))),
                                      dict(reversed(list(wiring.items()))))
        self.assertEqual(actual, reversed_result)


if __name__ == "__main__":
    unittest.main()
