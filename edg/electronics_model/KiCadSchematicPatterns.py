"""Pure circuit patterns established from declared terminal roles and real nets.

Patterns suggest presentation only. They neither rename nets nor add electrical
connections; ambiguous fan-outs and rings are deliberately left unclassified.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class SchematicPattern:
    kind: str
    components: Tuple[str, ...]
    nets: Tuple[str, ...]

    def to_dict(self) -> dict:
        return dict(
            kind=self.kind, components=list(self.components), nets=list(self.nets)
        )


def terminal_roles(component: Any, pin_nets: Optional[Mapping] = None) -> dict:
    """Use declared PB terminal names; accept parallel pads only with net proof."""
    roles = {}
    for number, name in component.pins.items():
        role = name.removesuffix(".net").split(".")[-1].lower()
        if role in roles:
            if (pin_nets is not None and pin_nets.get((component.path, number)) is not None
                    and pin_nets.get((component.path, number)) == pin_nets.get((component.path, roles[role]))):
                continue
            return {}  # Ambiguous parallel/packed terminals remain unsupported.
        roles[role] = number
    return roles


def amplifier_channels(component: Any) -> dict:
    """Read explicit amplifier terminal roles, including packed/vector channels.

    Physical packed blocks use inpa/inna/outa; other compiled models retain
    inp.0/inn.0/out.0. These are declared terminal names, not net-name guesses.
    Ambiguous duplicate roles invalidate only that channel.
    """
    channels = {}
    ambiguous = set()
    for number, name in sorted(component.pins.items()):
        parts = name.removesuffix(".net").lower().split(".")
        leaf = parts[-1]
        if leaf in ("inp", "inn", "out"):
            role, channel = leaf, ""
        elif len(parts) >= 2 and parts[-2] in ("inp", "inn", "out") and leaf.isdecimal():
            role, channel = parts[-2], leaf
        else:
            match = re.fullmatch(r"(inp|inn|out)([a-z])", leaf)
            if match is None:
                continue
            role, channel = match.groups()
        roles = channels.setdefault(channel, {})
        if role in roles:
            ambiguous.add(channel)
        roles[role] = number
    return {channel: roles for channel, roles in sorted(channels.items())
            if channel not in ambiguous and {"inp", "inn", "out"} <= set(roles)}


def decoupling_associations(
    components: Sequence[Any], pin_nets: Mapping, views: Optional[Mapping] = None
) -> Tuple[SchematicPattern, ...]:
    """Associate typed local bypass wrappers with their unique powered device.

    A common supply does not establish ownership. The compiled DecouplingCapacitor
    ancestor establishes the functional owner's subtree; actual supply and return
    pins then verify the association. Ambiguous owners remain unclassified.
    """
    by_path = {c.path: c for c in components}
    roles = {c.path: terminal_roles(c, pin_nets) for c in components}
    associations = {}
    for cap in sorted(components, key=lambda c: c.path):
        if len(cap.pins) != 2:
            continue
        symbol = (
            views[cap.path].lib_id if views is not None and cap.path in views
            else (getattr(cap, "mapping", None) or {}).get("lib_id", "")
        ).split("_PB_", 1)[0]
        if symbol not in ("Device:C", "Device:C_Polarized"):
            continue
        wrappers = [
            path for path, cls in getattr(cap, "hierarchy", ())
            if cls.removeprefix("PolymorphicBlocks.")
            == "edg.abstract_parts.Capacitor.DecouplingCapacitor"
        ]
        if not wrappers:
            continue
        wrapper = max(wrappers, key=lambda path: len(path.split(".")))
        owner = wrapper.rpartition(".")[0]
        if not owner:
            continue
        cap_nets = {pin_nets.get((cap.path, n)) for n in cap.pins}
        if len(cap_nets) != 2 or None in cap_nets:
            continue
        # Establish the nearest physical-device boundary BEFORE checking role
        # eligibility. An FPGA with repeated/ambiguous supply roles still owns
        # this boundary; a nested memory must not capture the FPGA's outer
        # bypasses merely because it is the only device with simple role names.
        physical = [path for path, device in by_path.items()
                    if (path == owner or path.startswith(owner + ".")) and not path.startswith(wrapper + ".")
                    and len(device.pins) >= 3]
        if not physical:
            continue
        nearest = min(len(path.split(".")) for path in physical)
        boundary = sorted(path for path in physical if len(path.split(".")) == nearest)
        candidates = []
        for path in boundary:
            role = roles[path]
            supplies = {pin_nets.get((path, n)) for r, n in role.items()
                        if r in ("vdd", "vcc", "pwr", "vin", "vp")}
            grounds = {pin_nets.get((path, n)) for r, n in role.items()
                       if r in ("gnd", "vss", "vn")}
            matches = {(supply, ground) for supply in supplies for ground in grounds
                       if supply != ground and {supply, ground} == cap_nets}
            if len(matches) == 1:
                candidates.append((path, next(iter(matches))))
        if len(candidates) != 1:
            continue
        path, nets = candidates[0]
        associations.setdefault((path, nets), []).append(cap.path)
    return tuple(
        SchematicPattern("local_decoupling", (path, *caps), nets)
        for (path, nets), caps in sorted(associations.items())
    )


def discover_patterns(
    components: Sequence[Any], pin_nets: Mapping, views: Optional[Mapping] = None
) -> Tuple[SchematicPattern, ...]:
    """Find unambiguous data chains using explicit DIN/DOUT terminal roles.

    Endpoint degree is measured against *all* provided physical pins. A shared
    power net or a branched data output cannot accidentally become a serial link.
    """
    by_path = {c.path: c for c in components}
    roles = {c.path: terminal_roles(c, pin_nets) for c in components}
    serial = {p for p, r in roles.items() if "din" in r and "dout" in r}
    endpoints = {}
    for key, net in pin_nets.items():
        if key[0] in by_path:
            endpoints.setdefault(net, set()).add(key)
    following = {}
    preceding = {}
    edge_net = {}
    for source in sorted(serial):
        out_key = (source, roles[source]["dout"])
        net = pin_nets.get(out_key)
        peers = endpoints.get(net, set()) - {out_key}
        if len(peers) != 1:
            continue
        target, number = next(iter(peers))
        if target not in serial or target == source or roles[target]["din"] != number:
            continue
        following[source] = target
        preceding[target] = source
        edge_net[source] = net
    patterns = []
    visited = set()
    for start in sorted(serial - set(preceding)):
        chain = [start]
        while chain[-1] in following:
            target = following[chain[-1]]
            if target in chain:
                break
            chain.append(target)
        if len(chain) > 1:
            visited.update(chain)
            patterns.append(
                SchematicPattern(
                    "serial_data_chain",
                    tuple(chain),
                    tuple(edge_net[p] for p in chain[:-1]),
                )
            )

    # Conventional two-terminal symbols establish passive roles. Names such as
    # R1, part strings, and footprint identifiers are never used as evidence.
    def symbol(path):
        if views is not None and path in views:
            return views[path].lib_id.split("_PB_", 1)[0]
        return (getattr(by_path[path], "mapping", None) or {}).get("lib_id", "")

    resistors = {
        p
        for p, c in by_path.items()
        if len(c.pins) == 2 and symbol(p) in ("Device:R", "Device:R_US")
    }
    indicators = {
        p for p, c in by_path.items() if len(c.pins) == 2 and symbol(p) == "Device:LED"
    }
    claimed = set(visited)
    for anchor in sorted(by_path):
        role = roles[anchor]
        if "fb" not in role or "gnd" not in role:
            continue
        feedback = pin_nets.get((anchor, role["fb"]))
        ground = pin_nets.get((anchor, role["gnd"]))
        if feedback is None or ground is None or feedback == ground:
            continue
        entries = endpoints.get(feedback, set())
        branches = sorted({p for p, _ in entries if p in resistors})
        if len(entries) != 3 or len(branches) != 2 or claimed.intersection(branches):
            continue
        other = {}
        for p in branches:
            connections = {pin_nets.get((p, number)) for number in by_path[p].pins}
            other[p] = connections - {feedback}
        lower = [p for p in branches if other[p] == {ground}]
        upper = [
            p
            for p in branches
            if len(other[p]) == 1 and None not in other[p] and ground not in other[p]
        ]
        if len(lower) == len(upper) == 1:
            members = (anchor, upper[0], lower[0])
            patterns.append(
                SchematicPattern(
                    "feedback_divider",
                    members,
                    (next(iter(other[upper[0]])), feedback, ground),
                )
            )
            claimed.update(members)
    for net in sorted(endpoints):
        entries = endpoints[net]
        if len(entries) != 2:
            continue
        paths = {p for p, _ in entries}
        led = paths & indicators
        resistor = paths & resistors
        if len(led) == len(resistor) == 1 and not claimed.intersection(paths):
            members = (next(iter(led)), next(iter(resistor)))
            patterns.append(SchematicPattern("indicator_branch", members, (net,)))
            claimed.update(members)
    inductors = {
        p for p, c in by_path.items() if len(c.pins) == 2 and symbol(p) == "Device:L"
    }
    capacitors = {
        p
        for p, c in by_path.items()
        if len(c.pins) == 2 and symbol(p) in ("Device:C", "Device:C_Polarized")
    }
    for anchor in sorted(by_path):
        role = roles[anchor]
        if "sw" not in role or "gnd" not in role:
            continue
        switch_net = pin_nets.get((anchor, role["sw"]))
        ground = pin_nets.get((anchor, role["gnd"]))
        entries = endpoints.get(switch_net, set())
        coils = sorted({p for p, _ in entries if p in inductors})
        if len(entries) != 2 or len(coils) != 1 or ground is None:
            continue
        coil = coils[0]
        output = {pin_nets.get((coil, n)) for n in by_path[coil].pins} - {switch_net}
        if len(output) != 1 or None in output or ground in output:
            continue
        output_net = next(iter(output))
        caps = sorted(
            p
            for p in capacitors
            if {pin_nets.get((p, n)) for n in by_path[p].pins} == {output_net, ground}
        )
        # Shared rails alone do not justify merging all output capacitors: source
        # siblings identify local support of this converter implementation.
        parent = anchor.rpartition(".")[0]
        caps = [p for p in caps if parent and p.startswith(parent + ".")]
        patterns.append(
            SchematicPattern(
                "converter_output",
                (anchor, coil, *caps),
                (switch_net, output_net, ground),
            )
        )
    # Diode feedback is common in clamp/error amplifiers. The verified symbol
    # identity establishes a two-terminal branch; its polarity remains untouched.
    diodes = {p for p, c in by_path.items() if len(c.pins) == 2 and symbol(p) in (
        "Device:D", "Device:D_Schottky", "Device:D_Zener", "Device:D_Small",
        "Device:D_Schottky_Small", "Device:D_Zener_Small")}
    for anchor in sorted(by_path):
        for channel, role in amplifier_channels(by_path[anchor]).items():
            negative = pin_nets.get((anchor, role["inn"]))
            output = pin_nets.get((anchor, role["out"]))
            if negative is None or output is None or negative == output:
                continue
            feedback = sorted(
                p for p in resistors | capacitors | diodes
                if {pin_nets.get((p, n)) for n in by_path[p].pins} == {negative, output}
            )
            # Require a direct branch for this exact channel. A common negative
            # input or supply does not associate arbitrary incident components.
            if feedback:
                patterns.append(SchematicPattern(
                    "amplifier_feedback", (anchor, *feedback), (negative, output)))
    # Differential sense networks belong together even when their controller
    # is in an independently bounded power-stage region.
    for anchor, role in sorted(roles.items()):
        for positive, negative in (("acp", "acn"), ("srp", "srn")):
            if positive not in role or negative not in role:
                continue
            sense_nets = {pin_nets.get((anchor, role[positive])), pin_nets.get((anchor, role[negative]))}
            if len(sense_nets) != 2 or None in sense_nets:
                continue
            caps = [p for p in capacitors if {pin_nets.get((p, n)) for n in by_path[p].pins} == sense_nets]
            branches = []
            for net in sorted(sense_nets):
                candidates = [p for p in resistors if net in {pin_nets.get((p, n)) for n in by_path[p].pins}]
                if len(candidates) == 1:
                    branches.append(candidates[0])
            if len(caps) == 1 and len(set(branches)) == 2:
                patterns.append(SchematicPattern("differential_sense_filter", tuple(sorted([*branches, caps[0]])), tuple(sorted(sense_nets))))
    from .KiCadSchematicPower import gate_driver_circuits
    patterns.extend(SchematicPattern("gate_driver_stage", (anchor, *members), nets)
                    for anchor, members, nets in gate_driver_circuits(components, pin_nets, views))
    return tuple(patterns) + decoupling_associations(components, pin_nets, views) + hierarchy_circuits(components, pin_nets, views)


def hierarchy_circuits(components, pin_nets, views=None):
    """Keep compiled repeated subcircuits and verified power stages together.

    Hierarchy establishes ownership; actual terminal incidence establishes the
    circuit. No supply-name, reference-prefix or part-number inference is used.
    Repeated siblings require the same compiled class, not just similar names.
    """
    from collections import defaultdict
    by_path = {c.path: c for c in components}
    owners, classes = defaultdict(set), {}
    endpoints = defaultdict(set)
    for c in components:
        for number in c.pins:
            if (net := pin_nets.get((c.path, number))) is not None:
                endpoints[net].add(c.path)
        for path, cls in getattr(c, "hierarchy", ()):
            if path != c.path:
                owners[path].add(c.path)
                classes[path] = cls
    siblings = defaultdict(list)
    for path in owners:
        match = re.fullmatch(r"(.*)\[([^]]+)\]", path)
        if match:
            siblings[match[1], classes[path]].append(path)
    patterns, claimed = [], set()
    for _, paths in sorted(siblings.items()):
        if len(paths) < 2:
            continue
        for owner in sorted(paths):
            members = owners[owner]
            internal = tuple(sorted(n for n, ends in endpoints.items()
                                    if len(ends) > 1 and ends <= members))
            if 3 <= len(members) <= 24 and internal and not claimed.intersection(members):
                patterns.append(SchematicPattern("repeated_subcircuit", tuple(sorted(members)), internal))
                claimed.update(members)
    # A power stage needs declared FET terminals plus a verified inductor, or
    # multiple FETs sharing a declared multi-input controller subtree.
    for owner in sorted(owners, key=lambda p: (-len(p.split(".")), p)):
        members = owners[owner]
        if not 4 <= len(members) <= 64 or claimed.intersection(members):
            continue
        role_sets = {p: {name.removesuffix(".net").split(".")[-1].lower()
                         for name in by_path[p].pins.values()} for p in members}
        fets = {p for p in members if {"gate", "source", "drain"} <= role_sets[p]}
        coils = {p for p in members if views and views[p].lib_id.split("_PB_", 1)[0] == "Device:L"}
        controllers = {p for p in members if len(by_path[p].pins) >= 6 and
                       (role_sets[p] & {"sw", "sw1", "sw2", "gate1", "gate2", "drvhi", "ho"})}
        if not controllers or not (coils or len(fets) >= 2):
            continue
        if len(members) <= 32:
            selected = members
            kind = "power_subcircuit"
        else:
            from .KiCadSchematicPower import power_topology, bridge_kernel
            topology = power_topology(members, by_path, views, pin_nets) if views else None
            selected = fets | coils
            power_nets = {pin_nets.get((p, n)) for p in selected for n, role in by_path[p].pins.items()
                          if role.removesuffix(".net").split(".")[-1].lower() != "gate"}
            grounds = {pin_nets.get((p, n)) for p in controllers for n, role in by_path[p].pins.items()
                       if role.removesuffix(".net").split(".")[-1].lower() in ("gnd", "vss")}
            power_nets -= grounds | {None}
            selected |= {p for p in members if len(by_path[p].pins) == 2 and
                         any(pin_nets.get((p, n)) in power_nets for n in by_path[p].pins)}
            if topology is not None and topology["kind"] == "bridge":
                selected = bridge_kernel(topology, members, by_path, views, pin_nets)
            kind = "power_stage"
        if not 3 <= len(selected) <= 32:
            continue
        nets = tuple(sorted(n for n, ends in endpoints.items() if len(ends & selected) > 1))
        patterns.append(SchematicPattern(kind, tuple(sorted(selected)), nets))
        claimed.update(selected)
    return tuple(patterns)
