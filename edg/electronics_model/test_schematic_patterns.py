"""Electrical role patterns and deterministic ordering, independent of net names."""

import unittest

from .KiCadSchematicPatterns import discover_patterns, terminal_roles, decoupling_associations
from .KiCadSchematicLayout import place_group
from .KiCadSchematicExporter import generic, PhysicalComponent, SymbolView


def led(path):
    return PhysicalComponent(
        path,
        "D1",
        "Test:LED",
        "LED",
        {"4": "dout", "2": "din", "1": "gnd", "3": "vdd"},
        None,
        "chain",
    )


def nets(parts):
    result = {}
    for i, c in enumerate(parts):
        result[c.path, "1"] = "arbitrary_common_return"
        result[c.path, "3"] = "arbitrary_common_supply"
        result[c.path, "2"] = "input" if i == 0 else "n" + str(i - 1)
        result[c.path, "4"] = "output" if i == len(parts) - 1 else "n" + str(i)
    return result


class SchematicPatternsTest(unittest.TestCase):
    def decoupling_fixture(self, count=8, prefix="array"):
        devices = [led(f"{prefix}.pixel[{i}].implementation.device") for i in range(count)]
        wiring = nets(devices)
        caps = []
        for i, device in enumerate(devices):
            owner = f"{prefix}.pixel[{i}]"
            cap = PhysicalComponent(
                owner + ".bypass.wrapper.cap", f"C{i}", "FP", "100nF",
                {"1": "pos", "2": "neg"}, {"lib_id": "Device:C"}, "caps",
            )
            cap.hierarchy = ((owner, "edg.parts.human_interface.Neopixel.Sk6812Mini_E"),
                             (owner + ".bypass", "edg.abstract_parts.Capacitor.DecouplingCapacitor"))
            wiring[cap.path, "1"] = "arbitrary_common_supply"
            wiring[cap.path, "2"] = "arbitrary_common_return"
            caps.append(cap)
        return devices, caps, wiring

    def test_nested_decoupling_owner_single_and_repeated(self):
        from .KiCadSchematicLayout import regroup, split_group

        for count in (1, 8):
            devices, caps, wiring = self.decoupling_fixture(count)
            parts = devices + caps
            patterns = decoupling_associations(parts, wiring)
            self.assertEqual(len(patterns), count)
            self.assertEqual([p.components for p in patterns],
                             [(d.path, c.path) for d, c in zip(devices, caps)])
            self.assertEqual(patterns, decoupling_associations(list(reversed(parts)), wiring))
            regroup(parts, wiring)
            self.assertTrue(all(c.group == d.group for c, d in zip(caps, devices)))
            views = {c.path: generic(c) for c in parts}
            for cap in caps:
                views[cap.path] = SymbolView(generic(cap).definition,
                    [("1", 0, -2.54, 270), ("2", 0, 2.54, 90)], "Device:C")
            pages = place_group(parts, views, wiring)
            for device, cap in zip(devices, caps):
                containing = [page for page in pages if any(e[0] is device for e in page)]
                self.assertEqual(len(containing), 1)
                self.assertTrue(any(e[0] is cap for e in containing[0]))
            pair = [(devices[0], 0, 0, 0), (caps[0], 0, 30, 0)]
            self.assertIsNone(split_group(pair, views, wiring))

    def test_two_arrays_sharing_rails_do_not_share_cap_ownership(self):
        a, ca, wa = self.decoupling_fixture(2, "first")
        b, cb, wb = self.decoupling_fixture(2, "second")
        patterns = decoupling_associations(a + b + ca + cb, {**wa, **wb})
        self.assertEqual({p.components for p in patterns},
                         {(d.path, c.path) for d, c in zip(a + b, ca + cb)})

    def test_decoupling_requires_typed_owner_and_both_matching_rails(self):
        devices, caps, wiring = self.decoupling_fixture(1)
        parts = devices + caps
        cap = caps[0]
        original = cap.hierarchy
        cap.hierarchy = ()
        self.assertEqual(decoupling_associations(parts, wiring), ())
        cap.hierarchy = original
        wiring[cap.path, "2"] = "different_return"
        self.assertEqual(decoupling_associations(parts, wiring), ())
        wiring[cap.path, "2"] = "arbitrary_common_return"
        duplicate = led("array.pixel[0].other.device")
        wiring.update(nets([duplicate]))
        self.assertEqual(decoupling_associations(parts + [duplicate], wiring), ())

    def test_chain_follows_physical_pins_and_is_permutation_invariant(self):
        parts = [led("led[2].ic"), led("led[0].ic"), led("led[10].ic")]
        actual = discover_patterns(parts, nets(parts))
        self.assertEqual(
            actual,
            discover_patterns(
                list(reversed(parts)), dict(reversed(list(nets(parts).items())))
            ),
        )
        self.assertEqual(actual[0].components, tuple(c.path for c in parts))
        self.assertEqual(actual[0].nets, ("n0", "n1"))

    def test_branch_and_ring_do_not_invent_a_serial_order(self):
        parts = [led("a"), led("b"), led("c")]
        wiring = nets(parts)
        wiring["c", "2"] = "n0"  # DIN fanout is not a serial connection.
        self.assertEqual(discover_patterns(parts, wiring), ())
        wiring = nets(parts)
        wiring["a", "2"] = wiring["c", "4"]
        self.assertEqual(discover_patterns(parts, wiring), ())

    def test_anonymous_or_ambiguous_roles_are_not_guessed(self):
        c = led("a")
        c.pins = {"1": "ports.1", "2": "ports.2", "3": "ports.3", "4": "ports.4"}
        self.assertEqual(discover_patterns([c], {}), ())
        c.pins = {"1": "a.din", "2": "b.din"}
        self.assertEqual(terminal_roles(c), {})

    def test_feedback_divider_uses_symbol_and_terminal_roles(self):
        ic = PhysicalComponent(
            "reg.ic",
            "U1",
            "Test:IC",
            "reg",
            {"1": "fb", "2": "gnd", "3": "vin"},
            None,
            "reg",
        )
        hi = PhysicalComponent(
            "reg.fb.top",
            "R1",
            "Test:R",
            "10k",
            {"1": "a", "2": "b"},
            {"lib_id": "Device:R"},
            "top",
        )
        lo = PhysicalComponent(
            "reg.fb.bottom",
            "R2",
            "Test:R",
            "1k",
            {"1": "a", "2": "b"},
            {"lib_id": "Device:R"},
            "bottom",
        )
        wiring = {
            (ic.path, "1"): "feedback",
            (ic.path, "2"): "return",
            (ic.path, "3"): "input",
            (hi.path, "1"): "output",
            (hi.path, "2"): "feedback",
            (lo.path, "1"): "feedback",
            (lo.path, "2"): "return",
        }
        p = discover_patterns([lo, ic, hi], wiring)[0]
        self.assertEqual(p.kind, "feedback_divider")
        self.assertEqual(p.components, (ic.path, hi.path, lo.path))
        from .KiCadSchematicLayout import regroup

        regroup([lo, ic, hi], wiring)
        self.assertEqual({c.group for c in (lo, ic, hi)}, {"reg"})
        hi.mapping = None
        self.assertEqual(discover_patterns([lo, ic, hi], wiring), ())

    def test_converter_support_requires_switch_role_and_local_output_cap(self):
        ic = PhysicalComponent(
            "buck.ic", "U1", "FP", "IC", {"1": "sw", "2": "gnd"}, None, "buck"
        )
        coil = PhysicalComponent(
            "buck.coil",
            "L1",
            "FP",
            "L",
            {"1": "a", "2": "b"},
            {"lib_id": "Device:L"},
            "coil",
        )
        cap = PhysicalComponent(
            "buck.cap",
            "C1",
            "FP",
            "C",
            {"1": "pos", "2": "neg"},
            {"lib_id": "Device:C"},
            "cap",
        )
        remote = PhysicalComponent(
            "other.cap", "C2", "FP", "C", dict(cap.pins), dict(cap.mapping), "other"
        )
        wiring = {
            (ic.path, "1"): "switch",
            (ic.path, "2"): "return",
            (coil.path, "1"): "switch",
            (coil.path, "2"): "rail",
        }
        for c in (cap, remote):
            wiring[c.path, "1"] = "rail"
            wiring[c.path, "2"] = "return"
        pattern = discover_patterns([remote, cap, coil, ic], wiring)[0]
        self.assertEqual(pattern.kind, "converter_output")
        self.assertEqual(pattern.components, (ic.path, coil.path, cap.path))
        ic.pins["1"] = "ports.1"
        self.assertEqual(discover_patterns([remote, cap, coil, ic], wiring), ())

    def test_fields_avoid_long_vertical_label_without_moving_source_override(self):
        from .KiCadSchematicLayout import (
            annotation_position,
            annotation_bounds,
            annotation_obstacles,
        )

        c = led("testpoint")
        c.net_labels = {
            "1": "regulator.feedback.really_long_voltage_testpoint",
            "2": "GND",
        }
        view = SymbolView(
            generic(c).definition, [("1", 0, 10, 90), ("2", 10, 0, 180)], "Test:TP"
        )
        x, y, _ = annotation_position(c, view, 100, 100, 0)
        box = annotation_bounds(c, x, y, 0)
        for other in annotation_obstacles(c, view, 100, 100, 0):
            self.assertFalse(
                min(box[2], other[2]) > max(box[0], other[0])
                and min(box[3], other[3]) > max(box[1], other[1])
            )
        self.assertEqual(annotation_position(c, view, 100, 100, 0), (x, y, ""))
        c.annotation = (100, 120)
        self.assertEqual(annotation_position(c, view, 100, 100, 0), (100, 120, ""))

    def test_rotated_multiline_fields_have_vertical_glyph_bounds(self):
        from .KiCadSchematicLayout import annotation_bounds

        c = led("a")
        c.display_value = "a long manufacturer identifier with several words"
        c.descriptions = ["external load terminal"]
        a = annotation_bounds(c, 0, 0, 0)
        b = annotation_bounds(c, 0, 0, 90)
        self.assertLess(b[0], b[2])
        self.assertGreater(b[3] - b[1], a[3] - a[1])

    def test_amplifier_feedback_uses_explicit_negative_input(self):
        ic = PhysicalComponent(
            "amp.ic",
            "U1",
            "FP",
            "amp",
            {"1": "out", "2": "inp", "3": "inn"},
            None,
            "amp",
        )
        resistor = PhysicalComponent(
            "amp.feedback",
            "R1",
            "FP",
            "R",
            {"1": "a", "2": "b"},
            {"lib_id": "Device:R"},
            "feedback",
        )
        wiring = {
            (ic.path, "1"): "output",
            (ic.path, "2"): "signal",
            (ic.path, "3"): "negative",
            (resistor.path, "1"): "output",
            (resistor.path, "2"): "negative",
        }
        self.assertEqual(
            discover_patterns([resistor, ic], wiring)[0].kind, "amplifier_feedback"
        )
        wiring[resistor.path, "2"] = "signal"
        self.assertEqual(discover_patterns([resistor, ic], wiring), ())

    def test_atomic_split_keeps_channel_bypass_together(self):
        from .KiCadSchematicLayout import split_group

        parts = [led("ch[0].ic"), led("ch[1].ic")]
        caps = [
            PhysicalComponent(
                "ch[0].cap",
                "C1",
                "Test:C",
                "1u",
                {"1": "pos", "2": "neg"},
                None,
                "chain",
            )
        ]
        caps[0].hierarchy = (("ch[0].cap", "edg.abstract_parts.Capacitor.DecouplingCapacitor"),)
        views = {c.path: generic(c) for c in parts + caps}
        views[caps[0].path].lib_id = "Device:C"
        placed = [(parts[0], 10, 10, 0), (caps[0], 10, 40, 0), (parts[1], 80, 10, 0)]
        wiring = nets(parts)
        wiring[caps[0].path, "1"] = "arbitrary_common_supply"
        wiring[caps[0].path, "2"] = "arbitrary_common_return"
        left, right = split_group(placed, views, wiring)
        self.assertEqual([e[0].path for e in left], ["ch[0].ic", "ch[0].cap"])
        self.assertEqual([e[0].path for e in right], ["ch[1].ic"])

    def test_serial_layout_follows_chain_and_retains_every_component(self):
        parts = [led("ch[2].ic"), led("ch[0].ic"), led("ch[1].ic")]
        views = {c.path: generic(c) for c in parts}
        # Capacitor uses a verified symbol identity, never the C reference prefix.
        cap = PhysicalComponent(
            "ch[0].cap", "C1", "Test:C", "1u", {"1": "pos", "2": "neg"}, None, "chain"
        )
        cap.hierarchy = (("ch[0].cap", "edg.abstract_parts.Capacitor.DecouplingCapacitor"),)
        parts.append(cap)
        views[cap.path] = SymbolView(
            views[parts[0].path].definition,
            [("1", 0, -2.54, 270), ("2", 0, 2.54, 90)],
            "Device:C",
        )
        wiring = nets(parts[:3])
        wiring[cap.path, "1"] = "arbitrary_common_supply"
        wiring[cap.path, "2"] = "arbitrary_common_return"
        pages = place_group(parts, views, wiring)
        flat = [entry for page in pages for entry in page]
        self.assertEqual(
            [c.path for c, _, _, _ in flat if c is not cap], [c.path for c in parts[:3]]
        )
        self.assertEqual(
            sorted(c.path for c, _, _, _ in flat), sorted(c.path for c in parts)
        )
        ch = next(e for e in flat if e[0].path == "ch[0].ic")
        cp = next(e for e in flat if e[0] is cap)
        self.assertEqual(ch[1], cp[1])
        self.assertGreater(cp[2], ch[2])
        self.assertEqual(pages, place_group(list(reversed(parts)), views, wiring))


if __name__ == "__main__":
    unittest.main()
