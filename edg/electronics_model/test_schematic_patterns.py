"""Electrical role patterns and deterministic ordering, independent of net names."""

from __future__ import annotations
from typing import Sequence
from .KiCadSchematicTypes import PinKey
from .KiCadSchematicExporter import PhysicalComponent, SymbolView

import unittest

from .KiCadSchematicPatterns import discover_patterns, terminal_roles, decoupling_associations
from .KiCadSchematicLayout import place_group
from .KiCadSchematicExporter import generic


def led(path: str) -> PhysicalComponent:
    return PhysicalComponent(
        path,
        "D1",
        "Test:LED",
        "LED",
        {"4": "dout", "2": "din", "1": "gnd", "3": "vdd"},
        None,
        "chain",
    )


def nets(parts: Sequence[PhysicalComponent]) -> dict[PinKey, str]:
    result = {}
    for i, c in enumerate(parts):
        result[c.path, "1"] = "arbitrary_common_return"
        result[c.path, "3"] = "arbitrary_common_supply"
        result[c.path, "2"] = "input" if i == 0 else "n" + str(i - 1)
        result[c.path, "4"] = "output" if i == len(parts) - 1 else "n" + str(i)
    return result


class SchematicPatternsTest(unittest.TestCase):
    def decoupling_fixture(
        self, count: int = 8, prefix: str = "array"
    ) -> tuple[list[PhysicalComponent], list[PhysicalComponent], dict[PinKey, str]]:
        devices = [led(f"{prefix}.pixel[{i}].implementation.device") for i in range(count)]
        wiring = nets(devices)
        caps: list[PhysicalComponent] = []
        for i, device in enumerate(devices):
            owner = f"{prefix}.pixel[{i}]"
            cap = PhysicalComponent(
                owner + ".bypass.wrapper.cap",
                f"C{i}",
                "FP",
                "100nF",
                {"1": "pos", "2": "neg"},
                {"lib_id": "Device:C"},
                "caps",
            )
            cap.hierarchy = (
                (owner, "edg.parts.human_interface.Neopixel.Sk6812Mini_E"),
                (owner + ".bypass", "edg.abstract_parts.Capacitor.DecouplingCapacitor"),
            )
            wiring[cap.path, "1"] = "arbitrary_common_supply"
            wiring[cap.path, "2"] = "arbitrary_common_return"
            caps.append(cap)
        return devices, caps, wiring

    def test_nested_decoupling_owner_single_and_repeated(self) -> None:
        from .KiCadSchematicLayout import regroup, split_group

        for count in (1, 8):
            devices, caps, wiring = self.decoupling_fixture(count)
            parts = devices + caps
            patterns = decoupling_associations(parts, wiring)
            self.assertEqual(len(patterns), count)
            self.assertEqual([p.components for p in patterns], [(d.path, c.path) for d, c in zip(devices, caps)])
            self.assertEqual(patterns, decoupling_associations(list(reversed(parts)), wiring))
            regroup(parts, wiring)
            self.assertTrue(all(c.group == d.group for c, d in zip(caps, devices)))
            views = {c.path: generic(c) for c in parts}
            for cap in caps:
                views[cap.path] = SymbolView(
                    generic(cap).definition, [("1", 0, -2.54, 270), ("2", 0, 2.54, 90)], "Device:C"
                )
            pages = place_group(parts, views, wiring)
            for device, cap in zip(devices, caps):
                containing = [page for page in pages if any(e[0] is device for e in page)]
                self.assertEqual(len(containing), 1)
                self.assertTrue(any(e[0] is cap for e in containing[0]))
            pair = [(devices[0], 0, 0, 0), (caps[0], 0, 30, 0)]
            self.assertIsNone(split_group(pair, views, wiring))

    def test_two_arrays_sharing_rails_do_not_share_cap_ownership(self) -> None:
        a, ca, wa = self.decoupling_fixture(2, "first")
        b, cb, wb = self.decoupling_fixture(2, "second")
        patterns = decoupling_associations(a + b + ca + cb, {**wa, **wb})
        self.assertEqual({p.components for p in patterns}, {(d.path, c.path) for d, c in zip(a + b, ca + cb)})

    def test_decoupling_requires_typed_owner_and_both_matching_rails(self) -> None:
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

    def test_outer_bypass_cannot_fall_through_ambiguous_fpga_to_nested_memory(self) -> None:
        fpga = PhysicalComponent(
            "fpga.ic", "U1", "FP", "FPGA", {"1": "vdd.0", "2": "vdd.1", "3": "gnd.0", "4": "gnd.1"}, None, "fpga"
        )
        memory = PhysicalComponent(
            "fpga.mem.ic", "U2", "FP", "memory", {"1": "vcc", "2": "gnd", "3": "clk"}, None, "memory"
        )
        self.assertEqual(terminal_roles(fpga), {})
        caps: list[PhysicalComponent] = []
        wiring = {
            (fpga.path, "1"): "rail",
            (fpga.path, "2"): "rail",
            (fpga.path, "3"): "return",
            (fpga.path, "4"): "return",
            (memory.path, "1"): "rail",
            (memory.path, "2"): "return",
            (memory.path, "3"): "clock",
        }
        for wrapper in ("fpga.vio_cap0", "fpga.vio_cap1", "fpga.vpp_cap", "fpga.mem.vcc_cap"):
            cap = PhysicalComponent(
                wrapper + ".cap",
                "C" + str(len(caps)),
                "FP",
                "100n",
                {"1": "pos", "2": "neg"},
                {"lib_id": "Device:C"},
                "capacitors",
            )
            cap.hierarchy = ((wrapper, "edg.abstract_parts.Capacitor.DecouplingCapacitor"),)
            wiring[cap.path, "1"], wiring[cap.path, "2"] = "rail", "return"
            caps.append(cap)
        parts = [fpga, memory, *caps]
        expected = [(memory.path, caps[-1].path)]
        patterns = decoupling_associations(parts, wiring)
        self.assertEqual([p.components for p in patterns], expected)
        self.assertEqual(patterns, decoupling_associations(list(reversed(parts)), wiring))
        # If the direct owner's supplies become independently verifiable, the
        # outer bypasses belong to that owner, while memory retains its own cap.
        fpga.pins = {"1": "vdd", "3": "gnd", "4": "clk"}
        wiring[fpga.path, "4"] = "fpga_clock"
        patterns = decoupling_associations(parts, wiring)
        self.assertEqual(
            {p.components for p in patterns}, {(fpga.path, *(c.path for c in caps[:-1])), (memory.path, caps[-1].path)}
        )

    def test_footprint_owner_at_exact_wrapper_parent_blocks_nested_memory(self) -> None:
        owner = PhysicalComponent(
            "fpga", "U1", "FP", "FPGA", {"1": "vdd.0", "2": "vdd.1", "3": "gnd.0", "4": "gnd.1"}, None, "fpga"
        )
        owner.hierarchy = (("fpga", "Test.FootprintWrapper"),)
        memory = PhysicalComponent(
            "fpga.mem.ic", "U2", "FP", "memory", {"1": "vcc", "2": "gnd", "3": "clk"}, None, "memory"
        )
        outer = PhysicalComponent(
            "fpga.bypass.cap", "C1", "FP", "100n", {"1": "pos", "2": "neg"}, {"lib_id": "Device:C"}, "outer"
        )
        outer.hierarchy = (
            ("fpga", "Test.FootprintWrapper"),
            ("fpga.bypass", "edg.abstract_parts.Capacitor.DecouplingCapacitor"),
        )
        local = PhysicalComponent(
            "fpga.mem.bypass.cap", "C2", "FP", "100n", {"1": "pos", "2": "neg"}, {"lib_id": "Device:C"}, "local"
        )
        local.hierarchy = (("fpga.mem.bypass", "edg.abstract_parts.Capacitor.DecouplingCapacitor"),)
        wiring = {
            (owner.path, "1"): "rail",
            (owner.path, "2"): "rail",
            (owner.path, "3"): "return",
            (owner.path, "4"): "return",
            (memory.path, "1"): "rail",
            (memory.path, "2"): "return",
            (memory.path, "3"): "clock",
        }
        for cap in (outer, local):
            wiring[cap.path, "1"], wiring[cap.path, "2"] = "rail", "return"
        parts = [owner, memory, outer, local]
        patterns = decoupling_associations(parts, wiring)
        self.assertEqual([p.components for p in patterns], [(memory.path, local.path)])
        owner.pins = {"1": "vdd", "3": "gnd", "4": "clk"}
        wiring[owner.path, "4"] = "fpga_clock"
        patterns = decoupling_associations(parts, wiring)
        self.assertEqual({p.components for p in patterns}, {(owner.path, outer.path), (memory.path, local.path)})

    def test_chain_follows_physical_pins_and_is_permutation_invariant(self) -> None:
        parts = [led("led[2].ic"), led("led[0].ic"), led("led[10].ic")]
        actual = discover_patterns(parts, nets(parts))
        self.assertEqual(
            actual,
            discover_patterns(list(reversed(parts)), dict(reversed(list(nets(parts).items())))),
        )
        self.assertEqual(actual[0].components, tuple(c.path for c in parts))
        self.assertEqual(actual[0].nets, ("n0", "n1"))

    def test_branch_and_ring_do_not_invent_a_serial_order(self) -> None:
        parts = [led("a"), led("b"), led("c")]
        wiring = nets(parts)
        wiring["c", "2"] = "n0"  # DIN fanout is not a serial connection.
        self.assertEqual(discover_patterns(parts, wiring), ())
        wiring = nets(parts)
        wiring["a", "2"] = wiring["c", "4"]
        self.assertEqual(discover_patterns(parts, wiring), ())

    def test_anonymous_or_ambiguous_roles_are_not_guessed(self) -> None:
        c = led("a")
        c.pins = {"1": "ports.1", "2": "ports.2", "3": "ports.3", "4": "ports.4"}
        self.assertEqual(discover_patterns([c], {}), ())
        c.pins = {"1": "a.din", "2": "b.din"}
        self.assertEqual(terminal_roles(c), {})

    def test_feedback_divider_uses_symbol_and_terminal_roles(self) -> None:
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
        # Parallel exposed/ground pads must not hide an otherwise exact FB role.
        ic.pins["4"] = "gnd"
        wiring[ic.path, "4"] = "return"
        p = discover_patterns([lo, ic, hi], wiring)[0]
        self.assertEqual(p.kind, "feedback_divider")
        self.assertEqual(p.components, (ic.path, hi.path, lo.path))
        from .KiCadSchematicLayout import regroup

        regroup([lo, ic, hi], wiring)
        self.assertEqual({c.group for c in (lo, ic, hi)}, {"reg"})
        hi.mapping = None
        self.assertEqual(discover_patterns([lo, ic, hi], wiring), ())

    def test_converter_support_requires_switch_role_and_local_output_cap(self) -> None:
        ic = PhysicalComponent("buck.ic", "U1", "FP", "IC", {"1": "sw", "2": "gnd"}, None, "buck")
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
        remote = PhysicalComponent("other.cap", "C2", "FP", "C", dict(cap.pins), dict(cap.mapping or {}), "other")
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

    def test_fields_avoid_long_vertical_label_without_moving_source_override(self) -> None:
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
        view = SymbolView(generic(c).definition, [("1", 0, 10, 90), ("2", 10, 0, 180)], "Test:TP")
        x, y, _ = annotation_position(c, view, 100, 100, 0)
        box = annotation_bounds(c, x, y, 0)
        for other in annotation_obstacles(c, view, 100, 100, 0):
            self.assertFalse(
                min(box[2], other[2]) > max(box[0], other[0]) and min(box[3], other[3]) > max(box[1], other[1])
            )
        self.assertEqual(annotation_position(c, view, 100, 100, 0), (x, y, ""))
        c.annotation = (100, 120)
        self.assertEqual(annotation_position(c, view, 100, 100, 0), (100, 120, ""))

    def test_rotated_instance_multiline_fields_remain_native_horizontal(self) -> None:
        from .KiCadSchematicLayout import annotation_bounds

        c = led("a")
        c.display_value = "a long manufacturer identifier with several words"
        c.descriptions = ("external load terminal",)
        a = annotation_bounds(c, 0, 0, 0)
        b = annotation_bounds(c, 0, 0, 90)
        self.assertLess(b[0], b[2])
        self.assertEqual(b, a)
        self.assertGreater(b[2] - b[0], b[3] - b[1])

    def test_amplifier_feedback_uses_explicit_negative_input(self) -> None:
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
        self.assertEqual(discover_patterns([resistor, ic], wiring)[0].kind, "amplifier_feedback")
        wiring[resistor.path, "2"] = "signal"
        self.assertEqual(discover_patterns([resistor, ic], wiring), ())

    def test_packed_amplifier_channels_require_matching_explicit_roles(self) -> None:
        from .KiCadSchematicPatterns import amplifier_channels

        for names in (
            {"1": "outa", "2": "inna", "3": "inpa", "5": "inpb", "6": "innb", "7": "outb"},
            {"1": "out.0", "2": "inn.0", "3": "inp.0", "5": "inp.1", "6": "inn.1", "7": "out.1"},
        ):
            amp = PhysicalComponent("packed.ic", "U1", "FP", "dual", names, None, "packed")
            feedback = [
                PhysicalComponent(
                    "support." + name, ref, "FP", "part", {"1": "a", "2": "b"}, {"lib_id": symbol}, "support"
                )
                for name, ref, symbol in (
                    ("diode", "D1", "Device:D"),
                    ("resistor", "R1", "Device:R"),
                    ("wrong_channel", "R2", "Device:R"),
                )
            ]
            diode, resistor, wrong = feedback
            wiring = {
                (amp.path, "1"): "out0",
                (amp.path, "2"): "neg0",
                (amp.path, "3"): "signal0",
                (amp.path, "7"): "out1",
                (amp.path, "6"): "neg1",
                (amp.path, "5"): "signal1",
                (diode.path, "1"): "out0",
                (diode.path, "2"): "neg0",
                (resistor.path, "1"): "out1",
                (resistor.path, "2"): "neg1",
                (wrong.path, "1"): "out0",
                (wrong.path, "2"): "neg1",
            }
            self.assertEqual(len(amplifier_channels(amp)), 2)
            patterns = [p for p in discover_patterns([amp, *feedback], wiring) if p.kind == "amplifier_feedback"]
            self.assertEqual({p.components for p in patterns}, {(amp.path, diode.path), (amp.path, resistor.path)})
            self.assertEqual(
                patterns,
                [p for p in discover_patterns([*reversed(feedback), amp], wiring) if p.kind == "amplifier_feedback"],
            )
            # A duplicate explicit negative role invalidates its own channel.
            amp.pins["9"] = amp.pins["2"]
            self.assertEqual(len(amplifier_channels(amp)), 1)
            remaining = [p for p in discover_patterns([amp, *feedback], wiring) if p.kind == "amplifier_feedback"]
            self.assertEqual([p.components for p in remaining], [(amp.path, resistor.path)])

    def test_unknown_diode_symbol_does_not_establish_feedback(self) -> None:
        amp = PhysicalComponent("amp.ic", "U1", "FP", "amp", {"1": "outa", "2": "inna", "3": "inpa"}, None, "amp")
        branch = PhysicalComponent("amp.diode", "D1", "FP", "diode", {"1": "a", "2": "b"}, None, "amp")
        wiring = {
            (amp.path, "1"): "output",
            (amp.path, "2"): "negative",
            (amp.path, "3"): "signal",
            (branch.path, "1"): "output",
            (branch.path, "2"): "negative",
        }
        self.assertEqual(discover_patterns([amp, branch], wiring), ())

    def test_atomic_split_keeps_channel_bypass_together(self) -> None:
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
        split = split_group(placed, views, wiring)
        assert split is not None
        left, right = split
        self.assertEqual([e[0].path for e in left], ["ch[0].ic", "ch[0].cap"])
        self.assertEqual([e[0].path for e in right], ["ch[1].ic"])

    def test_serial_layout_follows_chain_and_retains_every_component(self) -> None:
        parts = [led("ch[2].ic"), led("ch[0].ic"), led("ch[1].ic")]
        views = {c.path: generic(c) for c in parts}
        # Capacitor uses a verified symbol identity, never the C reference prefix.
        cap = PhysicalComponent("ch[0].cap", "C1", "Test:C", "1u", {"1": "pos", "2": "neg"}, None, "chain")
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
        self.assertEqual([c.path for c, _, _, _ in flat if c is not cap], [c.path for c in parts[:3]])
        self.assertEqual(sorted(c.path for c, _, _, _ in flat), sorted(c.path for c in parts))
        ch = next(e for e in flat if e[0].path == "ch[0].ic")
        cp = next(e for e in flat if e[0] is cap)
        self.assertEqual(ch[1], cp[1])
        self.assertGreater(cp[2], ch[2])
        self.assertEqual(pages, place_group(list(reversed(parts)), views, wiring))


if __name__ == "__main__":
    unittest.main()
