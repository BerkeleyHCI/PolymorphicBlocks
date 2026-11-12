"""Deterministic placement of verified functional atoms, without electrical edits.

Electrical roles come from discovered patterns. Bounded candidate search uses
pin geometry and occupied bounds; the normal router subsequently proves whether
those geometric estimates admit actual routes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Collection, Mapping, Optional, Sequence
from .KiCadSchematicTypes import Bounds, Point, PinNets, Wire, Placement, Placements, Views, RouteResult

if TYPE_CHECKING:
    from .KiCadSchematicExporter import PhysicalComponent, SymbolView
    from .KiCadSchematicCircuits import SchematicCircuit
from .KiCadSchematicPatterns import SchematicPattern


from collections import defaultdict
import hashlib
import json
import os
import re

from .KiCadSchematicPatterns import discover_patterns, terminal_roles


def functional_atoms(
    components: Sequence[PhysicalComponent], pin_nets: PinNets, views: Views
) -> tuple[tuple[tuple[str, ...], ...], tuple[SchematicPattern, ...]]:
    """Merge overlapping support patterns; serial links remain cuttable edges."""
    paths = {c.path for c in components}
    parent = {p: p for p in paths}

    def root(p: str) -> str:
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    # The exporter builds the shared model once from the complete board scope.
    # Filtering here retains its ownership decisions instead of rediscovering
    # patterns from a smaller group, where ambiguous owners can look unique.
    model = next(
        (getattr(c, "circuit_model", None) for c in components if getattr(c, "circuit_model", None) is not None), None
    )
    patterns: Sequence[SchematicPattern] = (
        list(p for p in model.patterns if set(p.components) <= paths)
        if model
        else list(discover_patterns(components, pin_nets, views))
    )
    if model:
        # Explicit ownership is a boundary, even when an automatic power or
        # repeated-subtree pattern was discovered across it on the full board.
        protected = [set(c.components) for c in model.circuits if c.provenance == "explicit"]
        patterns = [
            p
            for p in patterns
            if p.kind == "serial_data_chain"
            or not any(set(p.components) & owned and not set(p.components) <= owned for owned in protected)
        ]
        from .KiCadSchematicPatterns import SchematicPattern

        for circuit in model.circuits:
            if circuit.provenance == "explicit" and set(circuit.components) <= paths:
                patterns.append(SchematicPattern("authored_circuit", circuit.components, circuit.primary_nets))
    by_path = {c.path: c for c in components}
    bounded: list[SchematicPattern] = []
    continuation_sections: list[set[str]] = []
    for pattern in patterns:
        if pattern.kind in ("repeated_subcircuit", "power_subcircuit", "power_stage", "authored_circuit"):
            entries = _circuit_template(pattern.components, by_path, views, pin_nets)
            bounds = packing_bounds(entries, views, pin_nets)
            if bounds[2] - bounds[0] + 17.78 > 340 or bounds[3] - bounds[1] + 17.78 > 205:
                # A complex repeated channel may contain several independent
                # compiled support subcircuits. Preserve those authored child
                # boundaries instead of either clipping or splitting by role.
                owner = os.path.commonprefix([p.split(".") for p in pattern.components])
                children = defaultdict(list)
                for path in pattern.components:
                    suffix = path.split(".")[len(owner) :]
                    children[suffix[0] if suffix else path].append(path)
                sections = [paths for paths in children.values() if len(paths) > 1]
                direct = [paths[0] for paths in children.values() if len(paths) == 1]
                if direct:
                    sections.append(direct)
                circuit = _authored_circuit(pattern.components, by_path)
                if circuit is not None and circuit.stages:
                    sections = [list(stage.components) for stage in circuit.stages]
                    rest = sorted(set(pattern.components) - {p for section in sections for p in section})
                    if rest:
                        sections.append(rest)
                if len(sections) > 1:
                    continuation_sections.extend(set(section) for section in sections)
                    for section_paths in sections:
                        bounded.append(type(pattern)("functional_section", tuple(sorted(section_paths)), pattern.nets))
                    for path in pattern.components:
                        by_path[path].functional_continuation = dict(
                            owner=".".join(owner),
                            reason="measured whole circuit exceeds A3",
                            sections=[sorted(paths) for paths in sections],
                        )
                    continue
        bounded.append(pattern)
    # A smaller discovered support pattern cannot rejoin a deliberate measured
    # continuation, including a whole repeated-subtree or power-stage pattern.
    patterns = tuple(
        p
        for p in bounded
        if p.kind == "functional_section"
        or not any(
            set(p.components) & section and not set(p.components) <= section for section in continuation_sections
        )
    )
    boundaries = [
        set(p.components)
        for p in patterns
        if p.kind
        in ("repeated_subcircuit", "power_subcircuit", "power_stage", "functional_section", "authored_circuit")
    ]
    for pattern in patterns:
        if pattern.kind not in (
            "repeated_subcircuit",
            "power_subcircuit",
            "power_stage",
            "functional_section",
            "authored_circuit",
        ) and any(
            set(pattern.components) & boundary and not set(pattern.components) <= boundary for boundary in boundaries
        ):
            # Keep the support branch intact without rejoining a controller
            # already owned by an explicit power-stage continuation.
            if pattern.kind == "feedback_divider":
                support = set(pattern.components[1:])
                if not any(support & boundary for boundary in boundaries):
                    members = sorted(support & paths)
                    for path in members[1:]:
                        a, b = root(members[0]), root(path)
                        parent[max(a, b)] = min(a, b)
            continue  # A support pattern cannot reunite an explicit continuation.
        if pattern.kind == "serial_data_chain":
            continue
        members = sorted(set(pattern.components) & paths)
        for path in members[1:]:
            a, b = root(members[0]), root(path)
            parent[max(a, b)] = min(a, b)
    groups = defaultdict(set)
    for path in sorted(paths):
        groups[root(path)].add(path)
    return tuple(tuple(sorted(group)) for _, group in sorted(groups.items())), patterns


def signal_nets(components: Sequence[PhysicalComponent], pin_nets: PinNets) -> dict[str, set[str]]:
    """Exclude actual declared supply terminals, rather than guessing net names."""
    rails = set()
    for c in components:
        for role, number in terminal_roles(c).items():
            if role in ("gnd", "vss", "vdd", "vcc", "pwr", "vin", "vout", "pwr_in", "pwr_out", "vp", "vn"):
                net = pin_nets.get((c.path, number))
                if net is not None:
                    rails.add(net)
    endpoints = defaultdict(set)
    for c in components:
        for number in c.pins:
            net = pin_nets.get((c.path, number))
            if net is not None and net not in rails:
                endpoints[net].add(c.path)
    return endpoints


def channel_signature(
    atom: tuple[str, ...],
    by_path: Mapping[str, PhysicalComponent],
    pin_nets: PinNets,
    views: Views,
    patterns: Sequence[SchematicPattern],
) -> Optional[str]:
    """Recognize repeated compiled circuits conservatively, without net names.

    Matching requires compiled class evidence, identical relative implementation
    paths, physical pin inventories and net-incidence structure. A visual
    resemblance or an array-like path alone never establishes equivalence.
    """
    if not atom or not all(getattr(by_path[path], "hierarchy", ()) for path in atom):
        return None
    prefix = os.path.commonprefix([path.split(".")[:-1] for path in atom])
    members = sorted(atom, key=lambda path: path.split(".")[len(prefix) :])
    indices = {path: i for i, path in enumerate(members)}
    components = []
    nets = defaultdict(list)
    for path in members:
        c = by_path[path]
        components.append(
            (
                path.split(".")[len(prefix) :],
                [cls for _, cls in c.hierarchy],
                sorted(c.pins.items()),
                views[path].lib_id.split("_PB_", 1)[0] if not views[path].lib_id.startswith("PB:") else "generic",
            )
        )
        for number in sorted(c.pins):
            net = pin_nets.get((path, number))
            if net is not None:
                nets[net].append((indices[path], number))
    kinds = sorted(p.kind for p in patterns if set(p.components) <= set(atom))
    signature = (components, sorted(tuple(value) for value in nets.values()), kinds)
    return hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()[:16]


def _union(boxes: Sequence[Bounds]) -> Bounds:
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def _overlap(a: Bounds, b: Bounds, margin: float = 1.27) -> bool:
    return min(a[2], b[2]) + margin > max(a[0], b[0]) and min(a[3], b[3]) + margin > max(a[1], b[1])


def component_boxes(entry: Placement, views: Views) -> list[Bounds]:
    from .KiCadSchematicLayout import graphic_bounds, annotation_bounds, annotation_position

    c, x, y, angle = entry
    a, b, d, e = graphic_bounds(views[c.path], angle)
    tx, ty, _ = annotation_position(c, views[c.path], x, y, angle)
    return [(x + a, y + b, x + d, y + e), annotation_bounds(c, tx, ty, angle)]


def pin_escapes(entries: Placements, views: Views, pin_nets: PinNets) -> list[tuple[str, Point, Point, str, str]]:
    """Use the exact immutable 5.08 mm pin escapes emitted by the exporter."""
    from .KiCadSchematicLayout import pin_escape, pins

    result = []
    for c, x, y, angle in entries:
        for number, px, py, direction in pins(views[c.path], x, y, angle):
            net = pin_nets.get((c.path, number))
            if net is None:
                continue
            ex, ey = pin_escape(px, py, direction)
            result.append((net, (px, py), (ex, ey), c.path, number))
    return result


def escape_conflicts(entries: Placements, views: Views, pin_nets: PinNets) -> int:
    """Reject cross-net escape touching, including identical escape endpoints.

    The downstream router reserves escapes but cannot repair a short introduced
    before routing. Same-net contacts, including parallel physical pins, remain
    legal. Nonconnected crossings are also conservatively kept apart here.
    """
    from .KiCadSchematicScene import segments_touch, segment_box, pin_name_items, pin_number_items

    escapes = pin_escapes(entries, views, pin_nets)
    glyphs = [
        (c.path, item["bounds"])
        for c, x, y, angle in entries
        for item in (
            pin_name_items(views[c.path].definition, x, y, angle)
            + pin_number_items(views[c.path].definition, x, y, angle)
        )
    ]
    text_conflicts = sum(
        owner != other and segment_box(a, b, box) for _, a, b, owner, _ in escapes for other, box in glyphs
    )
    return text_conflicts + sum(
        net != other and segments_touch(a, b, c, d)
        for i, (net, a, b, _, _) in enumerate(escapes)
        for other, c, d, _, _ in escapes[i + 1 :]
    )


def atom_bounds(entries: Placements, views: Views) -> Bounds:
    return _union([box for entry in entries for box in component_boxes(entry, views)])


def packing_bounds(entries: Placements, views: Views, pin_nets: PinNets) -> Bounds:
    """Measure bodies, fields, escapes and labels that leave this atom.

    Only external-net and singleton labels reserve packing corridors. Internal
    loop nets are handled by local routing; reserving their hypothetical label
    walls inside a template would artificially explode complete circuits.
    """
    import copy
    from .KiCadSchematicLayout import annotation_obstacles

    members = {c.path for c, _, _, _ in entries}
    endpoints = defaultdict(list)
    for (path, number), net in pin_nets.items():
        endpoints[net].append((path, number))
    outside = {net for net, pins in endpoints.items() if len(pins) == 1 or any(path not in members for path, _ in pins)}
    boxes = [box for entry in entries for box in component_boxes(entry, views)]
    for c, x, y, angle in entries:
        measured = copy.copy(c)
        labels = getattr(c, "net_labels", {})
        measured.net_labels = {
            number: labels.get(number, label_net)
            for number in c.pins
            if (label_net := pin_nets.get((c.path, number))) is not None and label_net in outside
        }
        # annotation_obstacles shares the exporter's pin-label/ground bounds,
        # while keeping actual pin escapes even when their net is internal.
        boxes.extend(annotation_obstacles(measured, views[c.path], x, y, angle))
    return _union(boxes)


def _rotation_for_pin(view: SymbolView, number: str, desired: Point) -> int:
    from .KiCadSchematicLayout import transform

    pin = next((p for p in view.pins if p[0] == number), None)
    if pin is None:
        return 0
    return max((0, 90, 180, 270), key=lambda a: (sum(u * v for u, v in zip(transform(pin[1], pin[2], a), desired)), -a))


def _horizontal(view: SymbolView) -> int:
    from .KiCadSchematicLayout import transform

    if len(view.pins) != 2:
        return 0
    return max(
        (0, 90, 180, 270),
        key=lambda a: (abs(transform(view.pins[0][1] - view.pins[1][1], view.pins[0][2] - view.pins[1][2], a)[0]), -a),
    )


def _authored_circuit(members: Collection[str], by_path: Mapping[str, PhysicalComponent]) -> Optional[SchematicCircuit]:
    circuits: list[Optional[SchematicCircuit]] = [getattr(by_path[p], "functional_circuit", None) for p in members]
    return next(
        (c for c in circuits if c is not None and c.provenance == "explicit" and set(c.components) == set(members)),
        None,
    )


def _staged_template(
    members: Collection[str], by_path: Mapping[str, PhysicalComponent], views: Views, pin_nets: PinNets
) -> Optional[list[Placement]]:
    """Measured left-to-right authored stages, never inferred signal arrows.

    Boundary roles guide rotation only; net and physical pad identities remain
    unchanged. Components omitted from ordered stages form a support column.
    """
    from .KiCadSchematicLayout import snap, transform

    circuit = _authored_circuit(members, by_path)
    if circuit is None or not circuit.stages:
        return None
    stages = [tuple(stage.components) for stage in circuit.stages]
    unassigned = tuple(sorted(set(members) - {p for stage in stages for p in stage}))
    if unassigned:
        stages.append(unassigned)
    entries, x = [], 0.0
    desired = {"input": (-1, 0), "output": (1, 0), "supply": (0, -1), "return": (0, 1)}
    for stage in stages:
        column, y = [], 0.0
        for path in stage:
            roles = [b for b in circuit.boundaries if b.component == path and b.role in desired]

            def orientation_score(angle: int) -> tuple[float, int]:
                result = 0.0
                for boundary in roles:
                    pin = next(p for p in views[path].pins if p[0] == boundary.pin)
                    position = transform(pin[1], pin[2], angle)
                    result += sum(a * b for a, b in zip(position, desired[boundary.role]))
                return result, -angle

            angle = max((0, 90, 180, 270), key=orientation_score) if roles else 0
            box = packing_bounds([(by_path[path], 0, 0, angle)], views, pin_nets)
            column.append((by_path[path], snap(x - box[0]), snap(y - box[1]), angle))
            y += box[3] - box[1] + 15.24
        if column:
            entries.extend(column)
            x = packing_bounds(column, views, pin_nets)[2] + 20.32
    # Preserve measured stage order even when it exceeds A3: functional_atoms
    # must see the oversized bounds and create explicit stage continuations.
    # A shelf fallback here would silently erase the authored flow just to fit.
    if entries and _score(entries, views, pin_nets)[:2] == (0, 0):
        return entries
    return None


def _circuit_template(
    members: Collection[str], by_path: Mapping[str, PhysicalComponent], views: Views, pin_nets: PinNets
) -> list[Placement]:
    """Measured shelf placement around an owner, preserving complete channels.

    Try three fixed widths. Unlike the old unclaimed-member horizontal strip,
    support parts wrap within their circuit, before sheet packing is considered.
    """
    from .KiCadSchematicLayout import snap
    from .KiCadSchematicPower import power_template

    circuit = _authored_circuit(members, by_path)
    requested = circuit.template if circuit is not None else "auto"
    # Ordered stages explicitly describe flow and take geometric precedence.
    # A typed template still requires its compiled topology during validation.
    authored = _staged_template(members, by_path, views, pin_nets)
    if authored is not None:
        return authored
    # Generic and signal/support families must not silently become converters
    # just because a recognized power topology happens to lie in their members.
    if requested in ("auto", "buck", "four_switch_bridge"):
        power = power_template(members, by_path, views, pin_nets)
        if power is not None:
            return power
    if requested == "series_path":
        from .KiCadSchematicLayout import _place_group_legacy

        pages = _place_group_legacy([by_path[p] for p in members], views, pin_nets)
        if len(pages) == 1 and _candidate_valid(pages[0], views, pin_nets):
            return pages[0]
    anchor = min(members, key=lambda p: (-len(by_path[p].pins), p))
    signals = signal_nets([by_path[p] for p in members], pin_nets)

    def stage_part(path: str) -> bool:
        roles = {v.removesuffix(".net").split(".")[-1].lower() for v in by_path[path].pins.values()}
        return {"gate", "source", "drain"} <= roles or views[path].lib_id.split("_PB_", 1)[0] == "Device:L"

    def angle_for(path: str) -> int:
        if views[path].lib_id.split("_PB_", 1)[0] == "Device:L":
            return _horizontal(views[path])
        if stage_part(path):
            source = [p for p in views[path].pins if by_path[path].pins.get(p[0], "").removesuffix(".net") == "source"]
            drain = [p for p in views[path].pins if by_path[path].pins.get(p[0], "").removesuffix(".net") == "drain"]
            if source and drain:
                return 90 if abs(source[0][2] - drain[0][2]) > abs(source[0][1] - drain[0][1]) else 0
        return 0

    remaining = set(members) - {anchor}
    ordered, prior = [], {anchor}
    while remaining:
        path = min(
            remaining,
            key=lambda p: (not stage_part(p), -sum(p in ends and bool(prior & ends) for ends in signals.values()), p),
        )
        ordered.append(path)
        remaining.remove(path)
        prior = {path}
    trials = []
    for shelf_width in (160.02, 220.98, 281.94):
        owner = (by_path[anchor], 0.0, 0.0, angle_for(anchor))
        owner_box = atom_bounds([owner], views)
        start_x = owner_box[2] + 15.24 if len(by_path[anchor].pins) >= 6 else owner_box[0]
        start_y = owner_box[1] if len(by_path[anchor].pins) >= 6 else owner_box[3] + 15.24
        entries = [owner]
        x, y, row_height = start_x, start_y, 0.0
        for path in ordered:
            c = by_path[path]
            angle = angle_for(path)
            box = atom_bounds([(c, 0, 0, angle)], views)
            width, height = box[2] - box[0], box[3] - box[1]
            if x > start_x and x + width > start_x + shelf_width:
                x, y, row_height = start_x, y + row_height + 15.24, 0.0
            entry = (c, snap(x - box[0]), snap(y - box[1]), angle)
            entries.append(entry)
            x += width + 15.24
            row_height = max(row_height, height)
        bounds = packing_bounds(entries, views, pin_nets)
        width, height = bounds[2] - bounds[0] + 17.78, bounds[3] - bounds[1] + 17.78
        if width <= 340 and height <= 205 and _score(entries, views, pin_nets)[:2] == (0, 0):
            trials.append((round(width * height, 4), entries))
    if trials:
        return min(trials, key=lambda t: t[0])[1]
    # Let the normal measured-bounds gate report an oversized complete atom;
    # never silently split a verified channel or shrink its typography.
    return entries


def _template(
    members: Sequence[str],
    patterns: Sequence[SchematicPattern],
    by_path: Mapping[str, PhysicalComponent],
    views: Views,
    pin_nets: PinNets,
) -> list[Placement]:
    """Finite layout templates for already validated electrical patterns."""
    from .KiCadSchematicLayout import graphic_bounds, snap

    local = [p for p in patterns if p.kind != "serial_data_chain" and set(p.components) <= set(members)]
    if any(
        p.kind
        in (
            "repeated_subcircuit",
            "power_subcircuit",
            "power_stage",
            "functional_section",
            "gate_driver_stage",
            "authored_circuit",
        )
        for p in local
    ):
        return _circuit_template(members, by_path, views, pin_nets)
    bypasses = [p for p in local if p.kind == "local_decoupling"]
    if (
        sum(len(p.components) - 1 for p in bypasses) >= 2
        and len({p.components[0] for p in bypasses}) == 1
        and set(members) == {path for p in bypasses for path in p.components}
    ):
        # Parallel supply pads can legitimately own many capacitors. Use the
        # measured, wrapped bank beside the IC instead of a vertical stack
        # that grows below an already tall MCU.
        return _circuit_template(members, by_path, views, pin_nets)
    priority = {
        "converter_output": 0,
        "amplifier_feedback": 1,
        "feedback_divider": 2,
        "indicator_branch": 3,
        "local_decoupling": 4,
    }
    local.sort(key=lambda p: (priority.get(p.kind, 9), p.components))
    anchor = local[0].components[0] if local else members[0]
    entries = {anchor: (by_path[anchor], 0.0, 0.0, 0)}
    feedback_count = 0
    for pattern in local:
        owner = pattern.components[0]
        if owner not in entries:
            entries[owner] = (by_path[owner], 0.0, 0.0, 0)
        _, ox, oy, oa = entries[owner]
        owner_box = atom_bounds([entries[owner]], views)
        right = owner_box[2]
        if pattern.kind == "feedback_divider":
            # The feedback junction is between a vertical upper/lower pair.
            _, hi, lo = pattern.components
            x = right + 20.32
            for path, y, toward in ((hi, oy - 12.7, (0, 1)), (lo, oy + 17.78, (0, -1))):
                number = next(n for n in by_path[path].pins if pin_nets.get((path, n)) == pattern.nets[1])
                angle = _rotation_for_pin(views[path], number, toward)
                entries.setdefault(path, (by_path[path], snap(x), snap(y), angle))
        elif pattern.kind == "amplifier_feedback":
            for path in pattern.components[1:]:
                # Distinct packed channels keep separate branches; parallel
                # feedback components are never placed over the same location.
                if path not in entries:
                    entries[path] = (
                        by_path[path],
                        snap(ox + feedback_count * 25.4),
                        snap(oy - 30.48),
                        _horizontal(views[path]),
                    )
                    feedback_count += 1
        elif pattern.kind == "converter_output":
            for i, path in enumerate(pattern.components[1:]):
                x = right + 25.4 + i * 30.48
                angle = _horizontal(views[path]) if i == 0 else (_horizontal(views[path]) + 90) % 360
                entries.setdefault(path, (by_path[path], snap(x), snap(oy + (0 if i == 0 else 15.24)), angle))
        elif pattern.kind == "indicator_branch":
            shared = pattern.nets[0]
            owner_pin = next(number for number in by_path[owner].pins if pin_nets.get((owner, number)) == shared)
            owner_angle = _rotation_for_pin(views[owner], owner_pin, (1, 0))
            entries[owner] = (by_path[owner], ox, oy, owner_angle)
            right = atom_bounds([entries[owner]], views)[2]
            for path in pattern.components[1:]:
                target_pin = next(number for number in by_path[path].pins if pin_nets.get((path, number)) == shared)
                angle = _rotation_for_pin(views[path], target_pin, (-1, 0))
                entries.setdefault(path, (by_path[path], snap(right + 25.4), oy, angle))
        elif pattern.kind == "local_decoupling":
            ymax = graphic_bounds(views[owner], oa)[3]
            for i, path in enumerate(pattern.components[1:]):
                # Bypass ownership remains visible and consistent across arrays.
                entries.setdefault(path, (by_path[path], ox, snap(oy + ymax + 30.48 + i * 30.48), 90))
    for i, path in enumerate(sorted(set(members) - set(entries))):
        entries[path] = (by_path[path], 60.96 + i * 40.64, 0.0, 0)
    # If long values or unusual symbols collide, spread the new member locally.
    accepted: list[Placement] = []
    for path in [anchor] + sorted(set(entries) - {anchor}):
        entry = entries[path]
        # Keep a support on its template's intended side of the owner. Moving
        # every collision downward can push a feedback branch through the IC
        # and below its own bypass when a larger rail-pin envelope is measured.
        _, ax, ay, _ = entries[anchor]
        _, ex, ey, _ = entry
        if ey < ay:
            spread = (0.0, -5.08)
        elif ey > ay:
            spread = (0.0, 5.08)
        else:
            spread = (-5.08 if ex < ax else 5.08, 0.0)
        for attempt in range(32):
            boxes = component_boxes(entry, views)
            if not any(
                _overlap(a, b) for prior in accepted for a in boxes for b in component_boxes(prior, views)
            ) and not escape_conflicts(accepted + [entry], views, pin_nets):
                break
            c, x, y, angle = entry
            entry = (c, snap(x + spread[0]), snap(y + spread[1]), angle)
        else:
            raise ValueError(
                "cannot separate symbol fields or cross-net pin escapes in functional atom: " + ", ".join(members)
            )
        accepted.append(entry)
    return accepted


def _score(entries: Placements, views: Views, pin_nets: PinNets) -> tuple[int, int, float, float]:
    from .KiCadSchematicLayout import pins

    boxes = [component_boxes(e, views) for e in entries]
    collisions = sum(
        _overlap(a, b) for i, first in enumerate(boxes) for second in boxes[i + 1 :] for a in first for b in second
    )
    terminals = defaultdict(list)
    for c, x, y, angle in entries:
        for number, px, py, _ in pins(views[c.path], x, y, angle):
            net = pin_nets.get((c.path, number))
            if net is not None:
                terminals[net].append((px, py))
    # A Manhattan bounding tree is only an estimate, never a routing guarantee.
    length = sum(
        max(x for x, y in pts) - min(x for x, y in pts) + max(y for x, y in pts) - min(y for x, y in pts)
        for pts in terminals.values()
        if len(pts) > 1
    )
    a, b, d, e = atom_bounds(entries, views)
    return escape_conflicts(entries, views, pin_nets), collisions, round(length, 4), round((d - a) * (e - b), 4)


def _optimize(
    entries: Placements, views: Views, pin_nets: PinNets, locked: Collection[str], *, rotations: bool = True
) -> tuple[list[Placement], int, list[list[Placement]]]:
    """At most two passes of 32 orthogonal candidate transforms per atom."""
    from .KiCadSchematicLayout import snap

    best = list(entries)
    score = _score(best, views, pin_nets)
    count = 0
    finalists: list[list[Placement]] = []
    if len(best) == 1:
        return best, count, finalists
    for _ in range(2):
        trials = 0
        # Stable path order removes traversal dependence. Owners and dedicated
        # bypass positions are retained; only unclaimed support transforms move.
        for index in sorted(range(len(best)), key=lambda i: best[i][0].path):
            c, x, y, angle = best[index]
            if c.path in locked:
                continue
            candidates = [(x, y, a) for a in (0, 90, 180, 270) if a != angle] if rotations else []
            candidates += [
                (snap(x + dx), snap(y + dy), angle)
                for dx, dy in (
                    (-2.54, 0),
                    (2.54, 0),
                    (0, -2.54),
                    (0, 2.54),
                    (-5.08, 0),
                    (5.08, 0),
                    (0, -5.08),
                    (0, 5.08),
                )
            ]
            for tx, ty, ta in candidates:
                if trials >= 32:
                    break
                trials += 1
                count += 1
                candidate = list(best)
                candidate[index] = (c, tx, ty, ta)
                candidate_score = _score(candidate, views, pin_nets)
                if candidate_score < score:
                    best, score = candidate, candidate_score
                    finalists.append(candidate)
            if trials >= 32:
                break
    return best, count, finalists[-3:]


def _candidate_valid(entries: Placements, views: Views, pin_nets: PinNets) -> bool:
    if not entries or _score(entries, views, pin_nets)[:2] != (0, 0):
        return False
    a, b, c, d = packing_bounds(entries, views, pin_nets)
    return c - a + 17.78 <= 340 and d - b + 17.78 <= 205


def _whole_candidates(
    baseline: list[Placement],
    finalists: Sequence[list[Placement]],
    views: Views,
    pin_nets: PinNets,
    locked: Collection[str],
) -> list[tuple[str, list[Placement]]]:
    """At most eight stable proposals, baseline included, before routing.

    Spacing changes apply to the whole unlocked support arrangement. They expose
    alternatives that a distance-only sequence of single-part moves cannot find.
    The conventional circuit orientation itself is never mirrored or reversed.
    """
    from .KiCadSchematicLayout import snap

    proposals = [("template", baseline)]
    proposals.extend(("local_" + str(i + 1), candidate) for i, candidate in enumerate(finalists))
    cx = sum(x for _, x, _, _ in baseline) / len(baseline)
    cy = sum(y for _, _, y, _ in baseline) / len(baseline)
    for name, sx, sy in (("wide", 1.15, 1.0), ("tall", 1.0, 1.15), ("compact_x", 0.9, 1.0), ("compact_y", 1.0, 0.9)):
        candidate = [
            (
                c,
                x if c.path in locked else snap(cx + (x - cx) * sx),
                y if c.path in locked else snap(cy + (y - cy) * sy),
                angle,
            )
            for c, x, y, angle in baseline
        ]
        proposals.append((name, candidate))
    seen, result = set(), []
    for name, candidate in proposals:
        key = tuple((c.path, x, y, angle) for c, x, y, angle in candidate)
        if key in seen:
            continue
        seen.add(key)
        if name == "template" or _candidate_valid(candidate, views, pin_nets):
            result.append((name, candidate))
        if len(result) == 8:
            break
    return result


def _stage_intrusions(entries: Placements, wires: Sequence[Wire], views: Views, pin_nets: PinNets) -> int:
    """Count routes crossing authored stages unrelated to their endpoints.

    A region includes its support wiring space, beyond individual symbol bodies
    already protected by the router. This keeps another stage's signal from
    visually threading through the middle of a coherent local circuit.
    """
    from .KiCadSchematicScene import segment_box

    by_path = {entry[0].path: entry for entry in entries}
    stages, seen = [], set()
    for component, _, _, _ in entries:
        circuit = getattr(component, "functional_circuit", None)
        if circuit is None or circuit.id in seen:
            continue
        seen.add(circuit.id)
        for stage in circuit.stages:
            members = set(stage.components) & set(by_path)
            if len(members) >= 2:
                bounds = atom_bounds([by_path[p] for p in sorted(members)], views)
                related = {net for (path, _), net in pin_nets.items() if path in members}
                stages.append((bounds, related))
    return sum(net not in related and segment_box(a, b, bounds) for net, a, b in wires for bounds, related in stages)


def _choose_routes(
    baseline: list[Placement],
    candidates: Sequence[tuple[str, list[Placement]]],
    views: Views,
    pin_nets: PinNets,
    *,
    max_candidates: int = 3,
) -> tuple[list[Placement], dict[str, Any]]:
    """Route a baseline and at most three shortlisted complete arrangements.

    Each candidate uses its own deterministic page translation. Failed endpoint
    identities are checked against the original baseline, never a moving target.
    """
    from .KiCadSchematicLayout import route_local, snap
    from .KiCadSchematicRouting import route_metrics

    primary = set()
    for c, _, _, _ in baseline:
        circuit = getattr(c, "functional_circuit", None)
        if circuit is not None:
            primary.update(circuit.primary_nets)

    def evaluate(entries: Placements) -> tuple[RouteResult, dict[str, Any]]:
        a, b, c, d = packing_bounds(entries, views, pin_nets)
        dx, dy = snap(25.4 - a + 8.89), snap(60.96 - b + 8.89)
        placed = [(component, round(x + dx, 4), round(y + dy, 4), angle) for component, x, y, angle in entries]
        route = route_local(placed, views, pin_nets)
        metric: dict[str, Any] = dict(route_metrics(route[0], route[2]))
        metric["primary_fallbacks"] = sum(net in primary for _, net in route[2])
        metric["unrelated_intrusions"] = _stage_intrusions(placed, route[0], views, pin_nets)
        metric["area_mm2"] = round((c - a) * (d - b), 4)
        metric["outside_page"] = any(
            not (15 <= p[0] <= 400 and 35 <= p[1] <= 275) for _, a, b in route[0] for p in (a, b)
        )
        return route, metric

    def score(metric: Mapping[str, Any]) -> tuple[float, ...]:
        return (
            metric["primary_fallbacks"],
            metric["crossings"],
            metric["unrelated_intrusions"],
            metric["bends"],
            metric["length_mm"],
            metric["area_mm2"],
        )

    shortlisted = sorted(candidates[1:], key=lambda item: _score(item[1], views, pin_nets))[:max_candidates]
    if not shortlisted:
        return baseline, dict(selected="template", route_trials=0, candidates=len(candidates), trials=[])
    original, before = evaluate(baseline)
    selected, best, best_name = baseline, before, "template"
    trials = []
    for name, candidate in shortlisted:
        route, metric = evaluate(candidate)
        acceptable = (
            set(route[2]) <= set(original[2])
            and not metric["outside_page"]
            and metric["crossings"] <= before["crossings"]
            and _candidate_valid(candidate, views, pin_nets)
        )
        chosen = acceptable and score(metric) < score(best)
        trials.append(
            dict(
                candidate=name,
                metrics=metric,
                acceptable=acceptable,
                selected=chosen,
                reason=(
                    "improved routed score"
                    if chosen
                    else (
                        "invalid or new fallback/crossing/page violation"
                        if not acceptable
                        else "baseline or earlier candidate scores better"
                    )
                ),
            )
        )
        if chosen:
            selected, best, best_name = candidate, metric, name
    return selected, dict(
        selected=best_name,
        route_trials=1 + len(shortlisted),
        candidates=len(candidates),
        before=before,
        after=best,
        trials=trials,
    )


def _route_guard(
    baseline: list[Placement], candidate: list[Placement], views: Views, pin_nets: PinNets
) -> tuple[list[Placement], dict[str, Any]]:
    """Compatibility helper for callers evaluating a single finalist."""
    if baseline == candidate:
        return baseline, {"selected": "template", "route_trials": 0}
    selected, evidence = _choose_routes(baseline, [("template", baseline), ("optimized", candidate)], views, pin_nets)
    evidence["accepted"] = selected != baseline
    evidence["trial"] = evidence["trials"][0]["metrics"] if evidence["trials"] else evidence.get("before")
    return selected, evidence


def place_functional(
    components: Sequence[PhysicalComponent], views: Views, pin_nets: PinNets, *, optimize_orientations: bool = True
) -> list[list[Placement]]:
    """Pack complete measured functional atoms before splitting across pages."""
    from .KiCadSchematicLayout import snap

    components = sorted(components, key=lambda c: c.path)
    by_path = {c.path: c for c in components}
    atoms, patterns = functional_atoms(components, pin_nets, views)
    net_paths = signal_nets(components, pin_nets)
    families = {atom: channel_signature(atom, by_path, pin_nets, views, patterns) for atom in atoms}
    family_counts: dict[Optional[str], int] = defaultdict(int)
    for family in families.values():
        if family is not None:
            family_counts[family] += 1
    # Strong connectivity orders complete atoms. Stable pattern kind provides
    # repeated channels with the same template, without inferred signal arrows.
    # Repeated compiled channels have a semantic ordinal. Connectivity degree
    # must not move a terminal channel ahead of channel zero.
    from .KiCadSchematicPlanner import natural_order

    repeated = {}
    for pattern in patterns:
        if pattern.kind == "repeated_subcircuit":
            owner = ".".join(os.path.commonprefix([p.split(".") for p in pattern.components]))
            for atom in atoms:
                if set(pattern.components) <= set(atom):
                    repeated[atom] = (re.sub(r"\[[^]]+\]", "[]", owner), natural_order(owner))
    remaining = set(atoms)
    order: list[tuple[str, ...]] = []
    while remaining:
        prior = set(order[-1]) if order else set()

        def affinity(atom: tuple[str, ...]) -> tuple[int, int, tuple[str, ...]]:
            shared = sum(bool(set(atom) & ends) and bool(prior & ends) for ends in net_paths.values())
            degree = sum(bool(set(atom) & ends) and bool(ends - set(atom)) for ends in net_paths.values())
            return (-shared, -degree, atom)

        eligible = [
            atom
            for atom in remaining
            if atom not in repeated
            or not any(
                other in repeated and repeated[other][0] == repeated[atom][0] and repeated[other][1] < repeated[atom][1]
                for other in remaining
            )
        ]
        selected = min(eligible, key=affinity)
        remaining.remove(selected)
        order.append(selected)
    pages: list[list[Placement]] = []
    page: list[Placement] = []
    x, y, row_height = 25.4, 60.96, 0.0
    for atom in order:
        entries = _template(atom, patterns, by_path, views, pin_nets)
        locked = {p.components[0] for p in patterns if p.kind != "serial_data_chain" and set(p.components) <= set(atom)}
        locked.update(path for p in patterns if p.kind == "local_decoupling" for path in p.components)
        baseline = entries
        entries, candidates, finalists = _optimize(
            entries, views, pin_nets, locked, rotations=not optimize_orientations
        )
        # Route a fixed shortlist, not only the single best distance estimate.
        # A slightly worse geometric estimate may have much clearer real wires.
        proposals = _whole_candidates(baseline, finalists, views, pin_nets, locked)
        entries, routing = _choose_routes(baseline, proposals, views, pin_nets)
        local_transforms = candidates
        candidates = len(proposals)
        bounds = packing_bounds(entries, views, pin_nets)
        width, height = bounds[2] - bounds[0] + 17.78, bounds[3] - bounds[1] + 17.78
        if width > 340 or height > 205:
            raise ValueError("indivisible functional atom exceeds page bounds: " + ", ".join(atom))
        if page and x + width > 390:
            x, y, row_height = 25.4, y + row_height, 0.0
        if page and y + height > 265:
            pages.append(page)
            page = []
            x, y, row_height = 25.4, 60.96, 0.0
        dx, dy = x - bounds[0] + 8.89, y - bounds[1] + 8.89
        for c, px, py, angle in entries:
            c.placement_evidence = {
                "atom": list(atom),
                "candidates": candidates,
                "local_transforms": local_transforms,
                "requested_template": getattr(getattr(c, "functional_circuit", None), "template", "auto"),
                "patterns": sorted({p.kind for p in patterns if set(p.components) <= set(atom)}),
                "routing": routing,
                "functional_continuation": getattr(c, "functional_continuation", None),
                "repeated_family": families[atom],
                "matching_channels": family_counts.get(families[atom], 0),
            }
            page.append((c, snap(px + dx), snap(py + dy), angle))
        x += width
        row_height = max(row_height, height)
    if page:
        pages.append(page)
    return pages
