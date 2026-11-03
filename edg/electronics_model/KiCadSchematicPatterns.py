"""Pure circuit patterns established from declared terminal roles and real nets.

Patterns suggest presentation only. They neither rename nets nor add electrical
connections; ambiguous fan-outs and rings are deliberately left unclassified.
"""

from __future__ import annotations

from dataclasses import dataclass
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


def terminal_roles(component: Any) -> dict:
    """Use only unique explicit PB terminal names, not component/net prefixes."""
    roles = {}
    for number, name in component.pins.items():
        role = name.removesuffix(".net").split(".")[-1].lower()
        if role in roles:
            return {}  # Parallel/packed terminals need a more specific pattern.
        roles[role] = number
    return roles


def decoupling_associations(
    components: Sequence[Any], pin_nets: Mapping, views: Optional[Mapping] = None
) -> Tuple[SchematicPattern, ...]:
    """Associate typed local bypass wrappers with their unique powered device.

    A common supply does not establish ownership. The compiled DecouplingCapacitor
    ancestor establishes the functional owner's subtree; actual supply and return
    pins then verify the association. Ambiguous owners remain unclassified.
    """
    by_path = {c.path: c for c in components}
    roles = {c.path: terminal_roles(c) for c in components}
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
        candidates = []
        for path, role in roles.items():
            if not path.startswith(owner + ".") or path.startswith(wrapper + "."):
                continue
            if len(by_path[path].pins) < 3:
                continue
            supplies = {pin_nets.get((path, n)) for r, n in role.items()
                        if r in ("vdd", "vcc", "pwr", "vin")}
            grounds = {pin_nets.get((path, n)) for r, n in role.items()
                       if r in ("gnd", "vss")}
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
    roles = {c.path: terminal_roles(c) for c in components}
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
    for anchor in sorted(by_path):
        role = roles[anchor]
        if not {"inp", "inn", "out"}.issubset(role):
            continue
        negative = pin_nets.get((anchor, role["inn"]))
        output = pin_nets.get((anchor, role["out"]))
        if negative is None or output is None or negative == output:
            continue
        feedback = sorted(
            p
            for p in resistors | capacitors
            if {pin_nets.get((p, n)) for n in by_path[p].pins} == {negative, output}
        )
        # A verified direct feedback branch is sufficient; arbitrary shared
        # analog supply rails or semantic net-name guesses are never considered.
        if feedback:
            patterns.append(
                SchematicPattern(
                    "amplifier_feedback", (anchor, *feedback), (negative, output)
                )
            )
    return tuple(patterns) + decoupling_associations(components, pin_nets, views)
