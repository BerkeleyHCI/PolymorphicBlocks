"""Shared conservative scene geometry and bounded electrical-label placement.

Moving a label adds a wire from its existing electrical anchor. No pin, existing
wire or net name is changed. Only strict interior perpendicular crossings
without electrical junctions are allowed across unrelated wires.
"""

from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Sequence
from .KiCadSchematicWriter import S, children, node, write_wires
from .KiCadSchematicTypes import SymbolView, Bounds, Point, SExpr, PinTextItem, Placements, Views, PinNets, Wire, PinKey


def text_width(text: object, size: float) -> float:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in str(text)) * size


def text_bounds(
    text: object,
    x: float,
    y: float,
    angle: float = 0,
    size: float = 1.27,
    justify: str = "center",
    outline: bool = False,
) -> Bounds:
    lines = str(text).splitlines() or [""]
    w = max(text_width(line, size) for line in lines)
    h = size * 1.4 * len(lines)
    lo = 0 if justify == "left" else -w if justify == "right" else -w / 2
    if outline:
        lo -= 1.27
        w += 2.54
        h += 1.27
    r = math.radians(angle)
    pts = [
        (x + a * math.cos(r) + b * math.sin(r), y - a * math.sin(r) + b * math.cos(r))
        for a, b in ((lo, -h / 2), (lo + w, -h / 2), (lo + w, h / 2), (lo, h / 2))
    ]
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def label_bounds(
    text: object,
    x: float,
    y: float,
    angle: float = 0,
    size: float = 1.27,
    justify: str = "center",
    outline: bool = False,
    bottom: bool = False,
) -> Bounds:
    """KiCad keeps labels readable at 0/180 and 90/270 degrees.

    Justification remains left/right in the readable text frame. Rotating a
    right-justified 180-degree label as ordinary text mirrors its measured box
    to the wrong side of the anchor, accepting body collisions and clipping.
    """
    readable = angle % 180
    if bottom:
        shift = size * 1.4 * len(str(text).splitlines() or [""]) / 2
        x -= shift * math.sin(math.radians(readable))
        y -= shift * math.cos(math.radians(readable))
    bounds = text_bounds(text, x, y, readable, size, justify, outline)
    if bottom:
        # Native stroke glyphs extend slightly beyond the nominal font ascent.
        # Keep the electrical baseline fixed and reserve an extra stroke width.
        return (
            bounds[0] - (0.1524 if readable == 90 else 0),
            bounds[1] - (0.1524 if readable == 0 else 0),
            bounds[2],
            bounds[3],
        )
    return bounds


def pin_label_bounds(name: str, x: float, y: float, direction: float, outline: bool = True) -> Bounds:
    angle = (180 - int(direction)) % 360
    return label_bounds(name, x, y, angle, 1.27, "left" if angle in (0, 270) else "right", outline)


def overlap(a: Bounds, b: Bounds, margin: float = 0.25) -> bool:
    return min(a[2], b[2]) - max(a[0], b[0]) > -margin and min(a[3], b[3]) - max(a[1], b[1]) > -margin


def segment_box(a: Point, b: Point, box: Bounds, margin: float = 0.15) -> bool:
    return (
        a[0] == b[0]
        and box[0] - margin <= a[0] <= box[2] + margin
        and max(min(a[1], b[1]), box[1] - margin) <= min(max(a[1], b[1]), box[3] + margin)
    ) or (
        a[1] == b[1]
        and box[1] - margin <= a[1] <= box[3] + margin
        and max(min(a[0], b[0]), box[0] - margin) <= min(max(a[0], b[0]), box[2] + margin)
    )


def safe_wire_crossing(a: Point, b: Point, c: Point, d: Point, protected: Iterable[Point] = ()) -> Point | None:
    """Return the strict orthogonal interior crossing, or None for a touch.

    Endpoints, bends, pins, anchors, and junctions are never valid crossings.
    Keeping both segments unsplit at the returned point preserves KiCad nets.
    """
    if a[0] == b[0] and c[1] == d[1]:
        point = (a[0], c[1])
        inside = (
            min(a[1], b[1]) + 0.15 < point[1] < max(a[1], b[1]) - 0.15
            and min(c[0], d[0]) + 0.15 < point[0] < max(c[0], d[0]) - 0.15
        )
    elif a[1] == b[1] and c[0] == d[0]:
        return safe_wire_crossing(c, d, a, b, protected)
    else:
        return None
    if not inside or any(abs(point[0] - p[0]) < 0.15 and abs(point[1] - p[1]) < 0.15 for p in protected):
        return None
    return point


# One conventional schematic grid step leaves distinct nets distinguishable at
# normal sheet scale. Exact native connectivity alone cannot detect near joins.
WIRE_VISUAL_CLEARANCE = 1.27


def wire_visual_conflict(
    a: Point, b: Point, c: Point, d: Point, protected: Iterable[Point] = (), clearance: float = WIRE_VISUAL_CLEARANCE
) -> bool:
    """Reject near joins/parallel buses; permit clear interior crossings."""
    crossing = safe_wire_crossing(a, b, c, d, protected)
    if crossing is not None:
        return any(
            math.hypot(crossing[0] - p[0], crossing[1] - p[1]) < clearance - 0.0001 for p in (a, b, c, d, *protected)
        )
    dx = max(min(a[0], b[0]) - max(c[0], d[0]), min(c[0], d[0]) - max(a[0], b[0]), 0)
    dy = max(min(a[1], b[1]) - max(c[1], d[1]), min(c[1], d[1]) - max(a[1], b[1]), 0)
    return math.hypot(dx, dy) < clearance - 0.0001


def wire_through_text(a: Point, b: Point, rect: Bounds) -> bool:
    x1, y1, x2, y2 = rect
    return (
        abs(a[0] - b[0]) < 0.001
        and x1 + 0.3 < a[0] < x2 - 0.3
        and max(min(a[1], b[1]), y1 + 0.3) < min(max(a[1], b[1]), y2 - 0.3)
    ) or (
        abs(a[1] - b[1]) < 0.001
        and y1 + 0.3 < a[1] < y2 - 0.3
        and max(min(a[0], b[0]), x1 + 0.3) < min(max(a[0], b[0]), x2 - 0.3)
    )


def segments_touch(a: Point, b: Point, c: Point, d: Point) -> bool:
    return segment_box(a, b, (min(c[0], d[0]), min(c[1], d[1]), max(c[0], d[0]), max(c[1], d[1])), 0.01)


@dataclass(frozen=True)
class SceneObject:
    identity: str
    kind: str
    bounds: Bounds
    owner: str = ""


def pin_name_items(definition: SExpr, sx: float, sy: float, rotation: float, owner: str = "") -> list[PinTextItem]:
    """Visible library pin names in sheet coordinates, including actual fonts."""
    options = children(definition, "pin_names")
    if options and any(str(v) == "hide" for v in options[0][1:]):
        return []
    offsets = children(options[0], "offset") if options else []
    offset = offsets[0][1] if offsets else 0.508
    result: list[PinTextItem] = []
    r = math.radians(rotation)
    for body in children(definition, "symbol"):
        for pin in children(body, "pin"):
            if any(str(v) == "hide" for v in pin[1:] if not isinstance(v, list)):
                continue
            names, ats, lengths = children(pin, "name"), children(pin, "at"), children(pin, "length")
            if not names or names[0][1] in ("~", "") or not ats or not lengths:
                continue
            px, py, angle = ats[0][1:4]
            a = math.radians(angle)
            px += (lengths[0][1] + offset) * math.cos(a)
            py += (lengths[0][1] + offset) * math.sin(a)
            x = sx + px * math.cos(r) - py * math.sin(r)
            y = sy - px * math.sin(r) - py * math.cos(r)
            effective = (angle + rotation) % 360
            textangle = 0 if effective in (0, 180) else 90
            justify = "left" if effective in (0, 90) else "right"
            eff = children(names[0], "effects")
            font = children(eff[0], "font") if eff else []
            sizes = children(font[0], "size") if font else []
            size = sizes[0][1] if sizes else 1.27
            number = children(pin, "number")[0][1]
            result.append(
                dict(
                    identity=owner + ":pin:" + str(number),
                    text=str(names[0][1]),
                    owner=owner,
                    kind="pin_name",
                    bounds=text_bounds(names[0][1], x, y, textangle, size, justify),
                )
            )
    return result


def instance_property_at(property_at: SExpr, symbol_at: SExpr) -> SExpr:
    """Convert KiCad's instance-relative field angle into its visible text frame.

    Instance property positions are absolute, but the stored field angle includes
    symbol rotation. KiCad renders equal field/symbol angles horizontally.
    """
    return [property_at[0], property_at[1], property_at[2], (property_at[3] - symbol_at[3]) % 180]


def pin_number_items(definition: SExpr, sx: float, sy: float, rotation: float, owner: str = "") -> list[PinTextItem]:
    """Reserve visible pin-number glyphs above the native readable pin line."""
    options = children(definition, "pin_numbers")
    if options and any(str(v) == "hide" for v in options[0][1:]):
        return []
    result: list[PinTextItem] = []
    r = math.radians(rotation)
    for body in children(definition, "symbol"):
        for pin in children(body, "pin"):
            if any(str(v) == "hide" for v in pin[1:] if not isinstance(v, list)):
                continue
            numbers, ats, lengths = children(pin, "number"), children(pin, "at"), children(pin, "length")
            if not numbers or not ats or not lengths:
                continue
            number = numbers[0]
            px, py, angle = ats[0][1:4]
            a = math.radians(angle)
            px += lengths[0][1] * math.cos(a) / 2
            py += lengths[0][1] * math.sin(a) / 2
            x = sx + px * math.cos(r) - py * math.sin(r)
            y = sy - px * math.sin(r) - py * math.cos(r)
            horizontal = (angle + rotation) % 180 == 0
            effects = children(number, "effects")
            fonts = children(effects[0], "font") if effects else []
            sizes = children(fonts[0], "size") if fonts else []
            size = sizes[0][1] if sizes else 1.27
            # Text baseline is displaced from the pin line; use a conservative
            # readable-frame envelope at all four symbol orientations.
            if horizontal:
                y -= 0.508 + size * 0.7
            else:
                x -= 0.508 + size * 0.7
            result.append(
                dict(
                    identity=owner + ":number:" + str(number[1]),
                    owner=owner,
                    kind="pin_number",
                    text=str(number[1]),
                    bounds=text_bounds(number[1], x, y, 0 if horizontal else 90, size),
                )
            )
    return result


def label_islands(
    placed: Placements, views: Views, pin_nets: PinNets, wires: Sequence[Wire], external_nets: Iterable[str]
) -> set[PinKey]:
    """Choose one label for each connected graphical island needing a name.

    This operates only on generated same-net segments, never re-extracts PB
    connectivity. Junctions are recognized at segment endpoints (KiCad T joins),
    not at unmarked crossings between wire interiors.
    """
    from .KiCadSchematicLayout import pins

    by_net: dict[str, list[tuple[PinKey, Point, Point, float]]] = {}
    for component, x, y, angle in placed:
        for number, px, py, direction in pins(views[component.path], x, y, angle):
            net = pin_nets.get((component.path, number))
            if net is None:
                continue
            r = math.radians(direction)
            escape = (round(px - 5.08 * math.cos(r), 4), round(py + 5.08 * math.sin(r), 4))
            by_net.setdefault(net, []).append(((component.path, number), (px, py), escape, direction))
    selected = set()
    for net, entries in by_net.items():
        segments = [(a, b) for n, a, b in wires if n == net] + [(a, b) for _, a, b, _ in entries]
        parent = list(range(len(segments)))

        def root(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for i, (a, b) in enumerate(segments):
            for j in range(i):
                c, d = segments[j]
                if any(segments_touch(point, point, c, d) for point in (a, b)) or any(
                    segments_touch(point, point, a, b) for point in (c, d)
                ):
                    left, right = root(i), root(j)
                    parent[max(left, right)] = min(left, right)
        islands: dict[int, list[tuple[PinKey, Point, Point, float]]] = {}
        offset = len(segments) - len(entries)
        for i, entry in enumerate(entries):
            islands.setdefault(root(offset + i), []).append(entry)
        if net not in external_nets and len(islands) == 1 and len(entries) > 1:
            continue
        for members in islands.values():
            # Side-facing labels need less displacement than vertical ones.
            selected.add(min(members, key=lambda e: (e[3] % 180 != 0, e[0]))[0])
    return selected


def wire_island_anchors(anchor: Point, net: str, segments: Sequence[Wire], limit: int = 8) -> list[Point]:
    """Nearby vertices of the same *drawn* island, never another net island."""
    same = [(a, b) for name, a, b in segments if name == net]
    connected = {i for i, (a, b) in enumerate(same) if segments_touch(anchor, anchor, a, b)}
    pending = list(sorted(connected))
    while pending:
        i = pending.pop()
        a, b = same[i]
        for j, (c, d) in enumerate(same):
            if j in connected:
                continue
            if any(segments_touch(p, p, c, d) for p in (a, b)) or any(segments_touch(p, p, a, b) for p in (c, d)):
                connected.add(j)
                pending.append(j)
    points = {p for i in connected for p in same[i] if p != anchor}

    def distance(p: Point) -> float:
        return abs(p[0] - anchor[0]) + abs(p[1] - anchor[1])

    ordered = sorted(points, key=lambda p: (distance(p), p))
    # A local pin cluster can occupy all nearby vertices. Include distant
    # vertices of the same existing tree as well; this moves only a label,
    # never draws a new long wire or jumps to a disconnected same-name island.
    near_count = (limit - 1) // 2
    chosen = ordered[:near_count] + sorted(points, key=lambda p: (-distance(p), p))
    result = [anchor]
    for point in chosen:
        if point not in result:
            result.append(point)
        if len(result) >= limit:
            break
    return result


def place_document_labels(doc: SExpr, electrical_segments: Sequence[Wire], identity: str) -> dict[str, Any]:
    """Repair serialized labels against the actual sheet scene, in UUID order.

    The finite search retains the original label on failure, with an explicit
    diagnostic. At most six settling passes let constrained labels benefit from
    later repairs; stable or repeated states stop the search early.
    """
    from .KiCadSchematicLayout import graphic_bounds
    from .KiCadSchematicReadability import text_item

    definitions = {d[1]: d for lib in children(doc, "lib_symbols") for d in children(lib, "symbol")}
    from .KiCadSchematicPlanner import TITLE_BLOCK_BOUNDS

    obstacles = [TITLE_BLOCK_BOUNDS]
    for symbol in children(doc, "symbol"):
        at = children(symbol, "at")[0]
        lib = children(symbol, "lib_id")[0][1]
        if lib in definitions:
            x1, y1, x2, y2 = graphic_bounds(SymbolView(definitions[lib], [], lib), int(at[3]), False)
            obstacles.append((at[1] + x1, at[2] + y1, at[1] + x2, at[2] + y2))
            obstacles.extend(
                item["bounds"]
                for item in pin_name_items(definitions[lib], at[1], at[2], at[3])
                + pin_number_items(definitions[lib], at[1], at[2], at[3])
            )
        for prop in children(symbol, "property"):
            positions, effects = children(prop, "at"), children(prop, "effects")
            if positions and effects:
                field_text = text_item("", prop[2], instance_property_at(positions[0], at), effects[0], "", "field")
                if field_text:
                    obstacles.append(field_text.bounds)
    for item in children(doc, "text"):
        positions, effects = children(item, "at"), children(item, "effects")
        if positions and effects:
            text = text_item("", item[1], positions[0], effects[0], "", "text")
            if text:
                obstacles.append(text.bounds)
    labels = children(doc, "label") + children(doc, "global_label")
    labels.sort(key=lambda label: children(label, "uuid")[0][1])
    unique: dict[tuple[str, str, Point], SExpr] = {}
    duplicates = []
    for label in labels:
        label_at = children(label, "at")[0]
        label_key = (str(label[0]), label[1], (label_at[1], label_at[2]))
        if label_key in unique:
            duplicates.append(label)
        else:
            unique[label_key] = label
    for label in duplicates:
        doc.remove(label)
    labels = list(unique.values())

    def box(label: SExpr) -> Bounds:
        at = children(label, "at")[0]
        effect = children(label, "effects")[0]
        font = children(effect, "font")
        size = children(font[0], "size")[0][1] if font else 1.27
        just = children(effect, "justify")
        terms = {str(x) for x in just[0][1:]} if just else set()
        return label_bounds(
            label[1],
            at[1],
            at[2],
            at[3],
            size,
            "left" if "left" in terms else "right" if "right" in terms else "center",
            str(label[0]) == "global_label",
            bottom="bottom" in terms,
        )

    boxes = {id(label): box(label) for label in labels}
    anchors: dict[int, Point] = {
        id(label): (children(label, "at")[0][1], children(label, "at")[0][2]) for label in labels
    }
    # The electrical net is recovered from the unchanged anchor, never guessed
    # from the shortened display name.
    nets = {}
    for label in labels:
        matches = {n for n, a, b in electrical_segments if segments_touch(anchors[id(label)], anchors[id(label)], a, b)}
        nets[id(label)] = next(iter(matches)) if len(matches) == 1 else None
    regions = []
    for rectangle in children(doc, "rectangle"):
        start, end = children(rectangle, "start"), children(rectangle, "end")
        if start and end:
            x1, y1 = start[0][1:3]
            x2, y2 = end[0][1:3]
            regions.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
    owners = {}
    for key, (x, y) in anchors.items():
        containing = [b for b in regions if b[0] <= x <= b[2] and b[1] <= y <= b[3]]
        if containing:
            owners[key] = min(containing, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))

    def inside_region(key: int, rect: Bounds) -> bool:
        region = owners.get(key)
        return region is None or (
            region[0] + 0.5 <= rect[0]
            and region[1] + 0.5 <= rect[1]
            and rect[2] <= region[2] - 0.5
            and rect[3] <= region[3] - 0.5
        )

    added: dict[int, list[Wire]] = {}
    records: dict[int, dict[str, Any]] = {}

    def placement_state() -> tuple[tuple[str, tuple[float, ...], tuple[str, ...], tuple[Wire, ...]], ...]:
        return tuple(
            (
                children(label, "uuid")[0][1],
                tuple(children(label, "at")[0][1:]),
                tuple(str(v) for j in children(children(label, "effects")[0], "justify") for v in j[1:]),
                tuple(added.get(id(label), ())),
            )
            for label in labels
        )

    previous_state = placement_state()
    seen_states = {previous_state}
    termination = "pass_limit"
    passes_completed = 0
    for repair_pass in range(6):
        for label in labels:
            key = id(label)
            anchor = anchors[key]
            net = nets[key]
            at = children(label, "at")[0]
            if net is None:
                continue
            bounds = boxes[key]
            others = [b for k, b in boxes.items() if k != key]
            conflict_count = sum(overlap(bounds, b) for b in obstacles + others) + int(not inside_region(key, bounds))
            # Keep clear horizontal labels; repair vertical labels first where
            # possible, so dense bottom-edge pins do not form vertical walls.
            text_rect = label_bounds(
                label[1],
                at[1],
                at[2],
                at[3],
                1.27,
                (
                    "left"
                    if any(str(v) == "left" for j in children(children(label, "effects")[0], "justify") for v in j[1:])
                    else "right"
                ),
                bottom=str(label[0]) == "label",
            )
            current_segments = list(electrical_segments) + [
                segment for entries in added.values() for segment in entries
            ]
            wire_conflict = any(wire_through_text(a, b, text_rect) for _, a, b in current_segments)
            outline_conflict = str(label[0]) == "global_label" and any(
                n != net and segment_box(a, b, bounds) for n, a, b in current_segments
            )
            if conflict_count == 0 and not wire_conflict and not outline_conflict and int(at[3]) % 180 == 0:
                continue
            candidates = []
            for route_anchor in wire_island_anchors(anchor, net, electrical_segments):
                for angle, justify in (
                    (0, "left"),
                    (0, "right"),
                    (int(at[3]), "left" if int(at[3]) in (0, 270) else "right"),
                ):
                    # Outer lanes clear long pin-label banks and enclosing
                    # supply rails; all normal scene and electrical gates apply.
                    for offset in (
                        0,
                        1.27,
                        -1.27,
                        2.54,
                        -2.54,
                        3.81,
                        -3.81,
                        5.08,
                        -5.08,
                        7.62,
                        -7.62,
                        10.16,
                        -10.16,
                        15.24,
                        -15.24,
                        20.32,
                        -20.32,
                        30.48,
                        -30.48,
                        40.64,
                        -40.64,
                        50.8,
                        -50.8,
                    ):
                        # One measured outer lane resolves dense connector
                        # label stacks without unbounded or time-based search.
                        outer_lane = math.ceil((text_width(label[1], 1.27) + 5.08) / 2.54) * 2.54
                        for extension in (0, 2.54, 5.08, outer_lane):
                            sign = 1 if justify == "left" else -1
                            target = (round(route_anchor[0] + sign * extension, 4), round(route_anchor[1] + offset, 4))
                            rect = label_bounds(
                                label[1],
                                *target,
                                angle,
                                1.27,
                                justify,
                                str(label[0]) == "global_label",
                                bottom=str(label[0]) == "label",
                            )
                            if (
                                not inside_region(key, rect)
                                or rect[0] < 12
                                or rect[1] < 30
                                or rect[2] > 408
                                or rect[3] > 278
                            ):
                                continue
                            if any(overlap(rect, b) for b in obstacles + others):
                                continue
                            existing = list(electrical_segments) + [
                                seg for k, entries in added.items() if k != key for seg in entries
                            ]
                            text_rect = label_bounds(
                                label[1], *target, angle, 1.27, justify, bottom=str(label[0]) == "label"
                            )
                            if any(wire_through_text(c, d, text_rect) for n, c, d in existing):
                                continue
                            if any(n != net and segment_box(c, d, rect) for n, c, d in existing):
                                continue
                            for bend in ((route_anchor[0], target[1]), (target[0], route_anchor[1])):
                                path = [(a, b) for a, b in ((route_anchor, bend), (bend, target)) if a != b]
                                if net is None and path:
                                    continue
                                if any(segment_box(a, b, ob) for a, b in path for ob in obstacles):
                                    continue
                                if any(
                                    segment_box(a, b, ob)
                                    and not (ob[0] <= route_anchor[0] <= ob[2] and ob[1] <= route_anchor[1] <= ob[3])
                                    for a, b in path
                                    for ob in others
                                ):
                                    continue
                                protected = set(anchors.values()) | {p for _, c, d in existing for p in (c, d)}
                                protected.update(p for a, b in path for p in (a, b))
                                crossings = set()
                                unsafe = False
                                for a, b in path:
                                    for n, c, d in existing:
                                        if n == net:
                                            continue
                                        if wire_visual_conflict(a, b, c, d, protected):
                                            unsafe = True
                                            break
                                        crossing = safe_wire_crossing(a, b, c, d, protected)
                                        if crossing is not None:
                                            crossings.add(crossing)
                                    if unsafe:
                                        break
                                if unsafe:
                                    continue
                                cost = (
                                    len(crossings),
                                    angle % 180 != 0,
                                    abs(route_anchor[0] - anchor[0]) + abs(route_anchor[1] - anchor[1]),
                                    abs(offset) + extension,
                                    len(path),
                                    angle,
                                    justify,
                                    offset,
                                    extension,
                                    bend,
                                )
                                candidates.append((cost, target, angle, justify, path, rect, route_anchor))
                if any(candidate[0][0] == 0 for candidate in candidates):
                    break
            if candidates:
                _, target, angle, justify, path, rect, route_anchor = min(candidates, key=lambda c: c[0])
                at[1:] = [*target, angle]
                effect = children(label, "effects")[0]
                effect[:] = [v for v in effect if not (isinstance(v, list) and v and str(v[0]) == "justify")]
                effect.append(node("justify", S(justify), *([S("bottom")] if str(label[0]) == "label" else [])))
                added[key] = [(net, a, b) for a, b in path]
                boxes[key] = rect
                records[key] = dict(
                    identity=children(label, "uuid")[0][1],
                    name=label[1],
                    anchor=anchor,
                    wire_anchor=route_anchor,
                    at=target,
                    angle=angle,
                    candidates=len(candidates),
                    pass_index=repair_pass,
                )
        passes_completed = repair_pass + 1
        current_state = placement_state()
        if current_state == previous_state:
            termination = "stable"
            break
        if current_state in seen_states:
            termination = "cycle"
            break
        seen_states.add(current_state)
        previous_state = current_state
    conflicts = []
    for label in labels:
        key = id(label)
        bounds = boxes[key]
        at = children(label, "at")[0]
        terms = {str(v) for j in children(children(label, "effects")[0], "justify") for v in j[1:]}
        text_rect = label_bounds(
            label[1],
            at[1],
            at[2],
            at[3],
            1.27,
            "left" if "left" in terms else "right" if "right" in terms else "center",
            bottom="bottom" in terms,
        )
        all_wires = list(electrical_segments) + [seg for entries in added.values() for seg in entries]
        if (
            any(overlap(bounds, b) for b in obstacles + [b for k, b in boxes.items() if k != key])
            or any(wire_through_text(a, b, text_rect) for _, a, b in all_wires)
            or (
                str(label[0]) == "global_label"
                and any(n != nets[key] and segment_box(a, b, bounds) for n, a, b in all_wires)
            )
        ):
            conflicts.append(dict(identity=children(label, "uuid")[0][1], name=label[1], bounds=bounds))
    # Label extensions can introduce T junctions or overlap a portion of an
    # existing route. Rebuild the wire graph with the same writer that splits
    # segments and emits explicit junctions; raw appended tails can appear
    # connected while KiCad exports them as separate nets.
    if any(added.values()):
        final_segments = list(electrical_segments) + [segment for entries in added.values() for segment in entries]
        doc[:] = [
            item for item in doc if not (isinstance(item, list) and item and str(item[0]) in ("wire", "junction"))
        ]
        write_wires(doc, final_segments, identity, "final-label-scene")
    unresolved_anchors = [
        dict(identity=children(label, "uuid")[0][1], name=label[1], anchor=anchors[id(label)])
        for label in labels
        if nets[id(label)] is None
    ]
    return dict(
        sheet=identity,
        unresolved_anchors=unresolved_anchors,
        moves=list(records.values()),
        conflicts=conflicts,
        passes=passes_completed,
        termination=termination,
        deduplicated=len(duplicates),
    )
