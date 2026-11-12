"""Connectivity-driven placement and conservative orthogonal local wiring.

Layout consumes the physical netlist; it never introduces electrical connections.
Failed local routes retain labels and are reported, rather than guessed wires.
"""

from __future__ import annotations

import bisect
import heapq
import math
import textwrap
from collections import defaultdict
from typing import Any, Optional, Sequence, Tuple, TYPE_CHECKING, Callable, Iterable, Mapping, cast, Union
from .KiCadSchematicTypes import (
    Bounds,
    Point,
    GridPoint,
    PinKey,
    PinNets,
    Placement,
    Placements,
    Views,
    Wire,
    RouteResult,
    Escape,
    SExpr,
)

if TYPE_CHECKING:
    from .KiCadSchematicExporter import PhysicalComponent, SymbolView

RouteState = Union[GridPoint, tuple[GridPoint, Optional[int]]]

from .KiCadSchematicScene import pin_label_bounds, pin_name_items, pin_number_items
from .KiCadSchematicPatterns import decoupling_associations, discover_patterns, terminal_roles

GRID = 1.27


def tree_distance(targets: Iterable[GridPoint]) -> Callable[[GridPoint], float]:
    """Cached exact Manhattan distance to a route tree, an admissible A* bound."""
    raw_columns: defaultdict[int, list[int]] = defaultdict(list)
    for x, y in targets:
        raw_columns[x].append(y)
    columns = {x: sorted(set(ys)) for x, ys in raw_columns.items()}
    xs = sorted(columns)
    cache: dict[GridPoint, float] = {}

    def distance(point: GridPoint) -> float:
        if point in cache:
            return cache[point]
        x, y = point
        right = bisect.bisect_left(xs, x)
        left = right - 1
        best = float("inf")
        while left >= 0 or right < len(xs):
            dl = abs(xs[left] - x) if left >= 0 else float("inf")
            dr = abs(xs[right] - x) if right < len(xs) else float("inf")
            if min(dl, dr) >= best:
                break
            if dl <= dr:
                cx = xs[left]
                left -= 1
            else:
                cx = xs[right]
                right += 1
            ys = columns[cx]
            index = bisect.bisect_left(ys, y)
            for i in (index - 1, index):
                if 0 <= i < len(ys):
                    best = min(best, abs(cx - x) + abs(ys[i] - y))
        cache[point] = best
        return best

    return distance


def snap(value: float) -> float:
    return round(round(value / GRID) * GRID, 4)


def transform(x: float, y: float, angle: int) -> Tuple[float, float]:
    r = math.radians(angle)
    return round(x * math.cos(r) + y * math.sin(r), 4), round(-x * math.sin(r) + y * math.cos(r), 4)


def pins(view: SymbolView, x: float, y: float, angle: int) -> list[tuple[str, float, float, float]]:
    result = []
    for number, dx, dy, direction in view.pins:
        tx, ty = transform(dx, dy, angle)
        result.append((number, round(x + tx, 4), round(y + ty, 4), (direction + angle) % 360))
    return result


def _arc_extrema(start: Point, mid: Point, end: Point) -> Iterable[Point]:
    """Yield circle extrema on the sweep from start to end through mid."""
    # Solve for the circle center relative to start using the two perpendicular bisectors.
    mx, my = mid[0] - start[0], mid[1] - start[1]
    ex, ey = end[0] - start[0], end[1] - start[1]
    cross = mx * ey - my * ex
    if cross == 0:  # Repeated or collinear points have no unique circle.
        return
    m_squared, e_squared = mx * mx + my * my, ex * ex + ey * ey
    cx = (m_squared * ey - e_squared * my) / (2 * cross)
    cy = (mx * e_squared - ex * m_squared) / (2 * cross)
    radius = math.hypot(cx, cy)
    # The endpoint chord divides the circle into two arcs. Keep its midpoint's side.
    for x, y in ((cx - radius, cy), (cx + radius, cy), (cx, cy - radius), (cx, cy + radius)):
        if (x * ey - y * ex) * cross >= 0:
            yield start[0] + x, start[1] + y


def graphic_bounds(view: SymbolView, angle: int = 0, include_pins: bool = True) -> Tuple[float, float, float, float]:
    points: list[Point] = []

    def collect(tree: object) -> None:
        if not isinstance(tree, list) or not tree:
            return
        name = str(tree[0])
        if name in ("property", "pin"):
            return
        if name == "arc":
            arc = {
                str(v[0]): (v[1], v[2])
                for v in tree
                if isinstance(v, list) and len(v) >= 3 and str(v[0]) in ("start", "mid", "end")
            }
            if {"start", "mid", "end"} <= arc.keys():
                for x, y in _arc_extrema(arc["start"], arc["mid"], arc["end"]):
                    points.append(transform(x, -y, angle))
        if name == "circle":
            center = next((v for v in tree if isinstance(v, list) and str(v[0]) == "center"), None)
            radius = next(
                (v[1] for v in tree if isinstance(v, list) and str(v[0]) == "radius"),
                None,
            )
            if center is not None and radius is not None:
                for dx, dy in ((radius, 0), (-radius, 0), (0, radius), (0, -radius)):
                    points.append(transform(center[1] + dx, -center[2] + dy, angle))
        if name in ("start", "mid", "end", "xy", "center") and len(tree) >= 3:
            if isinstance(tree[1], (int, float)) and isinstance(tree[2], (int, float)):
                points.append(transform(float(tree[1]), -float(tree[2]), angle))
        for child in tree:
            collect(child)

    collect(view.definition)
    if include_pins:
        points.extend((transform(p[1], p[2], angle)) for p in view.pins)
    if not points:
        return -5, -5, 5, 5
    return (
        min(p[0] for p in points),
        min(p[1] for p in points),
        max(p[0] for p in points),
        max(p[1] for p in points),
    )


def ground_rotation(direction: float) -> int:
    """Point ground away from the pin instead of into adjacent pin labels."""
    return int(direction + 270) % 360


def ground_bounds(x: float, y: float, direction: float, label: str = "") -> Bounds:
    angle = ground_rotation(direction)
    corners = [transform(dx, dy, angle) for dx in (-2.54, 2.54) for dy in (0, 4.445)]
    bounds = (
        x + min(p[0] for p in corners),
        y + min(p[1] for p in corners),
        x + max(p[0] for p in corners),
        y + max(p[1] for p in corners),
    )
    if label:
        from .KiCadSchematicScene import text_bounds

        lx, ly = ground_label_position(x, y, direction)
        text = text_bounds(label, lx, ly, size=1.27)
        bounds = (min(bounds[0], text[0]), min(bounds[1], text[1]), max(bounds[2], text[2]), max(bounds[3], text[3]))
    return bounds


def ground_label_position(x: float, y: float, direction: float) -> Point:
    """Keep distinct return identities horizontal below the ground glyph."""
    bounds = ground_bounds(x, y, direction)
    return round((bounds[0] + bounds[2]) / 2, 4), round(bounds[3] + 2.54, 4)


def annotation_bounds(component: PhysicalComponent, x: float, y: float, rotation: int) -> Bounds:
    """Visible field bounds matching serialized instance-relative text angles.

    Exported Reference/Value angles equal the symbol rotation modulo 180, so
    native KiCad renders these fields horizontally for every symbol orientation.
    """
    from .KiCadSchematicScene import text_bounds

    visible = getattr(component, "display_value", "") or component.value
    value = "\n".join(textwrap.wrap(visible, 30)) if visible != component.value else visible
    boxes = [text_bounds(component.refdes, x, y, size=1.27), text_bounds(value, x, y + 2.54, size=1.27)]
    count = 0
    for description in getattr(component, "descriptions", ()):
        for line in textwrap.wrap(description, 42):
            boxes.append(text_bounds(line, x, y + 10 + count * 2.54, size=1.1))
            count += 1
    # Reserve stroke clearance beyond the font envelope.
    return (
        min(b[0] for b in boxes) - 0.3,
        min(b[1] for b in boxes) - 0.3,
        max(b[2] for b in boxes) + 0.3,
        max(b[3] for b in boxes) + 0.3,
    )


def annotation_obstacles(
    component: PhysicalComponent, view: SymbolView, x: float, y: float, rotation: int
) -> list[Bounds]:
    """Own symbol and pin outward corridors, including long external labels."""
    xmin, ymin, xmax, ymax = graphic_bounds(view, rotation)
    result = [(x + xmin, y + ymin, x + xmax, y + ymax)]
    labels = getattr(component, "net_labels", {})
    for number, px, py, direction in pins(view, x, y, rotation):
        r = math.radians(direction)
        ex, ey = px - 5.08 * math.cos(r), py + 5.08 * math.sin(r)
        result.append((min(px, ex) - 0.8, min(py, ey) - 0.8, max(px, ex) + 0.8, max(py, ey) + 0.8))
        ground_label = getattr(component, "ground_net_labels", {}).get(number, "")
        name = labels.get(number, "") or ground_label
        if not name:
            continue
        if ground_label or name.lower().split(".")[-1] == "gnd":
            result.append(ground_bounds(ex, ey, direction, ground_label))
            continue
        result.append(pin_label_bounds(name, ex, ey, direction))

    return result


def annotation_position(
    component: PhysicalComponent, view: SymbolView, x: float, y: float, rotation: int
) -> tuple[float, float, str]:
    if component.annotation is not None:
        return component.annotation[0], component.annotation[1], ""
    # Score locally so translation cannot change a floating-point tie.
    origin_x, origin_y = x, y
    x = y = 0.0
    xmin, ymin, xmax, ymax = graphic_bounds(view, rotation)
    local = annotation_bounds(component, 0, 0, rotation)
    half_width = (local[2] - local[0]) / 2
    half_height = (local[3] - local[1]) / 2
    # Existing preferred placement remains first; repair examines a finite list
    # of side/corner positions, never a time-dependent unconstrained search.
    preferred = (x, y + ymax + 12.7)
    terminals = pins(view, x, y, rotation)
    if ("FET" in view.lib_id or "Q_NMOS" in view.lib_id or "Q_PMOS" in view.lib_id) and rotation in (0, 180):
        preferred = (x + xmax + 3.81 + half_width, y - 1.27)
    elif len(terminals) == 2 and abs(terminals[0][1] - terminals[1][1]) < 0.01:
        preferred = (x + xmax + 3.81 + half_width, y - 1.27)
    candidates = [preferred]
    for margin in (3.81, 8.89, 15.24):
        left, right = x + xmin - margin - half_width, x + xmax + margin + half_width
        top, bottom = y + ymin - margin - half_height, y + ymax + margin + half_height
        candidates.extend(
            (
                (right, y),
                (left, y),
                (x, top),
                (x, bottom),
                (right, top),
                (left, top),
                (right, bottom),
                (left, bottom),
            )
        )
    obstacles = annotation_obstacles(component, view, x, y, rotation)

    def score(candidate: Point) -> tuple[float, float]:
        box = annotation_bounds(component, *candidate, rotation)
        overlap = sum(
            max(0, min(box[2], b[2]) - max(box[0], b[0])) * max(0, min(box[3], b[3]) - max(box[1], b[1]))
            for b in obstacles
        )
        return overlap, abs(candidate[0] - preferred[0]) + abs(candidate[1] - preferred[1])

    chosen = min(enumerate(candidates), key=lambda pair: (*score(pair[1]), pair[0]))[1]
    return chosen[0] + origin_x, chosen[1] + origin_y, ""


def freeze_annotations(placed: Placements, views: Views) -> list[Placement]:
    """Resolve fields once for routing, measurement, and final serialization.

    Copies retain placement evidence without leaking generated coordinates into
    source components, which may subsequently be split and placed again.
    """
    from copy import copy

    result = []
    for component, x, y, rotation in placed:
        resolved = copy(component)
        ax, ay, _ = annotation_position(component, views[component.path], x, y, rotation)
        resolved.annotation = (ax, ay)
        result.append((resolved, x, y, rotation))
    return result


def regroup(components: Sequence[PhysicalComponent], pin_nets: PinNets, views: Optional[Views] = None) -> None:
    """Co-locate small sibling circuits; IC/control groups stay boundaries."""
    original_groups = {c.path: c.group for c in components}
    groups = defaultdict(list)
    for c in components:
        groups[c.group].append(c)
    parent = {g: g for g in groups}

    def root(g: str) -> str:
        while parent[g] != g:
            g = parent[g]
        return g

    by_net = defaultdict(set)
    by_path = {c.path: c for c in components}
    for (path, _), net in pin_nets.items():
        by_net[net].add(path)
    for net, paths in sorted(by_net.items()):
        if len(paths) > 8 or any(
            word.startswith("pwr") or word in ("gnd", "v3v3", "vbus", "vusb", "vbat", "power")
            for word in net.lower().split(".")
        ):
            continue
        candidates = sorted(
            {
                root(by_path[p].group)
                for p in paths
                if p in by_path and max([len(c.pins) for c in groups[by_path[p].group]] + [0]) <= 6
            }
        )
        if len(candidates) < 2:
            continue
        for g in candidates[1:]:
            parent[root(g)] = root(candidates[0])
    for c in components:
        c.group = root(c.group)
    # Explicit feedback terminal + conventional resistor symbols justify a
    # complete local divider region, even across nested PB implementation blocks.
    model = getattr(components[0], "circuit_model", None) if components else None
    patterns = model.patterns if model is not None else discover_patterns(components, pin_nets, views)
    for pattern in patterns:
        if pattern.kind in (
            "feedback_divider",
            "indicator_branch",
            "converter_output",
            "gate_driver_stage",
            "amplifier_feedback",
            "local_decoupling",
        ):
            owner = original_groups[pattern.components[0]]
            for path in pattern.components:
                by_path[path].group = owner


def place_group(
    components: Sequence[PhysicalComponent], views: Views, pin_nets: PinNets, *, optimize_orientations: bool = True
) -> list[list[Placement]]:
    """Place whole functional atoms; retain established inline serial chains."""
    from .KiCadSchematicPlacement import functional_atoms, place_functional

    _, patterns = functional_atoms(components, pin_nets, views)
    nonserial = [p for p in patterns if p.kind != "serial_data_chain"]
    authored = any(p.kind == "authored_circuit" for p in patterns)
    chains = [p for p in patterns if p.kind == "serial_data_chain"]
    circuits = {
        circuit.id: circuit
        for c in components
        if (circuit := getattr(c, "functional_circuit", None)) is not None and circuit.provenance == "explicit"
    }
    # A declared repeated channel without ordered stages selects the proven
    # inline chain template, including its locally owned bypass capacitors.
    # Ordered stages remain authoritative and use functional placement.
    inline_authored = (
        authored
        and bool(circuits)
        and all(
            circuit.template == "repeated_channel"
            and not circuit.stages
            and any(set(chain.components) <= set(circuit.components) for chain in chains)
            for circuit in circuits.values()
        )
    )
    if inline_authored or (not authored and (chains or (all(len(c.pins) == 2 for c in components) and not nonserial))):
        return _place_group_legacy(components, views, pin_nets)
    return place_functional(components, views, pin_nets, optimize_orientations=optimize_orientations)


def _place_group_legacy(
    components: Sequence[PhysicalComponent], views: Views, pin_nets: PinNets
) -> list[list[Placement]]:
    """Compact graph ordering; simple two-terminal chains get inline orientation."""
    components = sorted(components, key=lambda c: c.path)
    adjacency: dict[str, set[str]] = {c.path: set() for c in components}
    nets: defaultdict[str, list[PinKey]] = defaultdict(list)
    for c in components:
        for pin in c.pins:
            net = pin_nets.get((c.path, pin))
            if net is not None:
                nets[net].append((c.path, pin))
    edge_pins = {}
    for net, endpoints in nets.items():
        paths = sorted({p for p, _ in endpoints})
        if len(paths) == 2:
            a, b = paths
            adjacency[a].add(b)
            adjacency[b].add(a)
            edge_pins[(a, b)] = next(pin for p, pin in endpoints if p == a)
            edge_pins[(b, a)] = next(pin for p, pin in endpoints if p == b)
    by_path = {c.path: c for c in components}
    chain = (
        bool(components) and all(len(c.pins) == 2 for c in components) and all(len(v) <= 2 for v in adjacency.values())
    )
    order = []
    if chain:
        todo = sorted(
            (p for p in adjacency if len(adjacency[p]) == 1),
            key=lambda p: (
                "Resistor" in views[p].lib_id or ":R_" in views[p].lib_id,
                p,
            ),
        )
        if todo:
            current = todo[0]
            while current not in order:
                order.append(current)
                following = sorted(adjacency[current] - set(order))
                if not following:
                    break
                current = following[0]
        chain = len(order) == len(components)
    if not chain:
        order = []
        remaining = set(by_path)
        while remaining:
            start = max(remaining, key=lambda p: (len(by_path[p].pins), len(adjacency[p]), p))
            queue = [start]
            while queue:
                current = queue.pop(0)
                if current not in remaining:
                    continue
                remaining.remove(current)
                order.append(current)
                queue.extend(sorted(adjacency[current] & remaining))
    # Serial order follows verified DIN/DOUT connections, not lexical paths.
    patterns = discover_patterns(components, pin_nets, views)
    serial_order = [p for pattern in patterns if pattern.kind == "serial_data_chain" for p in pattern.components]
    serial_members = set(serial_order)
    supports: defaultdict[str, list[str]] = defaultdict(list)
    for pattern in patterns:
        if pattern.kind == "local_decoupling":
            supports[pattern.components[0]].extend(pattern.components[1:])
    support_members = {p for values in supports.values() for p in values}
    order = serial_order + [p for p in order if p not in serial_members | support_members]
    x = 65.0
    y = 80.0
    row_height = 0.0
    page: list[Placement] = []
    pages: list[list[Placement]] = []
    for i, path in enumerate(order):
        component = by_path[path]
        view = views[path]
        rotation = 0
        if chain and len(order) > 1:
            target = order[i + 1] if i + 1 < len(order) else order[i - 1]
            target_pin = edge_pins[(path, target)]
            desired = 1 if i + 1 < len(order) else -1
            rotation = max(
                (0, 90, 180, 270),
                key=lambda a: (
                    desired * next(transform(dx, dy, a)[0] for n, dx, dy, _ in view.pins if n == target_pin)
                ),
            )
        if path in serial_members:
            # Use actual physical pin geometry to put DOUT to the right of DIN.
            roles = terminal_roles(component)
            rotation = max(
                (0, 90, 180, 270),
                key=lambda a: (
                    next(transform(dx, dy, a)[0] for n, dx, dy, _ in view.pins if n == roles["dout"])
                    - next(transform(dx, dy, a)[0] for n, dx, dy, _ in view.pins if n == roles["din"]),
                    -a,
                ),
            )
        xmin, ymin, xmax, ymax = graphic_bounds(view, rotation)
        # Space includes outward labels, annotation block, and local routing lanes.
        width = max(30, xmax - xmin + 20) if chain else max(60, xmax - xmin + 48)
        height = max(52, ymax - ymin + 32)
        tx, ty, _ = annotation_position(component, view, 0, 0, rotation)
        fx1, fy1, fx2, fy2 = annotation_bounds(component, tx, ty, rotation)
        width = max(width, max(xmax, fx2) - min(xmin, fx1) + 10)
        height = max(height, max(ymax, fy2) - min(ymin, fy1) + 10)
        if supports[path]:
            height += 38 + 30 * (len(supports[path]) - 1)
            width = max(width, 60)
        if width > 340 or height > 205:
            raise ValueError("symbol exceeds page bounds: " + path)
        if x + width / 2 > 390:
            x = 65
            y += row_height
            row_height = 0
        if y + height / 2 > 265:
            pages.append(page)
            page = []
            x = 65
            y = 80
            row_height = 0
        page.append((component, snap(x), snap(y), rotation))
        for index, support in enumerate(sorted(supports[path])):
            page.append((by_path[support], snap(x), snap(y + ymax + 30 + index * 30), 90))
        x += width
        row_height = max(row_height, height)
    if page:
        pages.append(page)
    return pages


class _NearForeignCache:
    """Monotonic exact cache of the eight-neighbor visual-clearance rule.

    A source track forbids its own axes in neighboring cells; protected source
    points forbid both axes. The source cell itself is intentionally excluded:
    exact perpendicular interior crossings use the existing track rule.
    """

    def __init__(self, tracks: defaultdict[GridPoint, dict[str, set[int]]], protected: set[GridPoint]) -> None:
        self.tracks = tracks
        self.protected = protected
        self.owners: tuple[defaultdict[GridPoint, set[str]], defaultdict[GridPoint, set[str]]] = (
            defaultdict(set),
            defaultdict(set),
        )
        for point, nets in tracks.items():
            for net, axes in nets.items():
                self._reserve(point, net, axes)

    def _reserve(self, point: GridPoint, net: str, axes: Iterable[int]) -> None:
        axes = (0, 1) if point in self.protected else axes
        x, y = point
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) != point:
                    for axis in axes:
                        self.owners[axis][nx, ny].add(net)

    def add_track(self, point: GridPoint, net: str, axes: Iterable[int]) -> None:
        existing = self.tracks[point].setdefault(net, set())
        existing.update(axes)
        self._reserve(point, net, existing)

    def protect(self, points: Iterable[GridPoint]) -> None:
        for point in points:
            if point in self.protected:
                continue
            self.protected.add(point)
            for net, axes in self.tracks.get(point, {}).items():
                self._reserve(point, net, axes)

    def blocked(self, point: GridPoint, axis: int, net: str) -> bool:
        owners = self.owners[axis].get(point)
        return owners is not None and bool(owners) and (len(owners) > 1 or net not in owners)


def _pin_lengths(definition: SExpr) -> dict[str, float]:
    """Read the resolved embedded symbol's actual library pin-leg lengths."""
    result: dict[str, float] = {}

    def visit(tree: object) -> None:
        if not isinstance(tree, list) or not tree:
            return
        if str(tree[0]) == "pin":
            number = next((v[1] for v in tree if isinstance(v, list) and v and str(v[0]) == "number"), None)
            length = next((v[1] for v in tree if isinstance(v, list) and v and str(v[0]) == "length"), None)
            if number is not None and length is not None:
                result[str(number)] = float(length)
        for child in tree:
            visit(child)

    visit(definition)
    return result


def route_local(placed: Placements, views: Views, pin_nets: PinNets, *, strategy: str = "baseline") -> RouteResult:
    """Route a same-net tree between pin escapes on a grid, avoiding other copper.

    Crossings remain straight and junction-free; crossing-averse trials penalize
    them explicitly. All failed endpoints retain a label.
    Router output is independently checked through native KiCad netlist export.
    """
    step = 0.635

    def grid(x: float, y: float) -> GridPoint:
        return round(x / step), round(y / step)

    def point(p: GridPoint) -> Point:
        return round(p[0] * step, 4), round(p[1] * step, 4)

    obstacles: set[GridPoint] = set()
    label_obstacles: defaultdict[GridPoint, set[str]] = defaultdict(set)
    occupied = {}
    tracks: defaultdict[GridPoint, dict[str, set[int]]] = defaultdict(dict)
    protected: set[GridPoint] = set()
    fixed_clearance: defaultdict[GridPoint, set[str]] = defaultdict(set)
    pin_necks = set()
    endpoints: defaultdict[str, list[tuple[PinKey, GridPoint]]] = defaultdict(list)
    escapes = {}
    wires = []
    failures = []
    for c, x, y, rotation in placed:
        xmin, ymin, xmax, ymax = graphic_bounds(views[c.path], rotation, include_pins=False)
        # Pin contacts remain outside the actual symbol graphics.
        a, b = grid(x + xmin, y + ymin)
        d, e = grid(x + xmax, y + ymax)
        if a <= d and b <= e:
            obstacles.update((ix, iy) for ix in range(a, d + 1) for iy in range(b, e + 1))
        tx, ty, align = annotation_position(c, views[c.path], x, y, rotation)
        field_box = annotation_bounds(c, tx, ty, rotation)
        ax, ay = grid(field_box[0], field_box[1])
        bx, by = grid(field_box[2], field_box[3])
        obstacles.update((ix, iy) for ix in range(ax, bx + 1) for iy in range(ay, by + 1))
        for item in pin_name_items(views[c.path].definition, x, y, rotation, c.path) + pin_number_items(
            views[c.path].definition, x, y, rotation, c.path
        ):
            lo_x, lo_y, hi_x, hi_y = item["bounds"]
            # Only grid points actually inside the text box are obstacles.
            obstacles.update(
                (ix, iy)
                for ix in range(math.ceil(lo_x / step), math.floor(hi_x / step) + 1)
                for iy in range(math.ceil(lo_y / step), math.floor(hi_y / step) + 1)
            )
        pin_lengths = _pin_lengths(views[c.path].definition)
        for number, px, py, direction in pins(views[c.path], x, y, rotation):
            key = c.path, number
            net = pin_nets.get(key)
            if net is None:
                continue
            r = math.radians(direction)
            ex = round(px - 5.08 * math.cos(r), 4)
            ey = round(py + 5.08 * math.sin(r), 4)
            escape = grid(ex, ey)
            escapes[key] = (px, py, ex, ey, direction)
            endpoints[net].append((key, escape))
            # Reserve true-coordinate stub geometry, including its off-grid
            # transition, by a full 1.27 mm. Rounded grid occupancy alone lets
            # distinct buses approach within 0.635 mm and look joined.
            from .KiCadSchematicScene import WIRE_VISUAL_CLEARANCE

            gx, gy = point(escape)
            # Routes join fixed stubs only at outward escape anchors. Reserve
            # the entire inward neck, including the red library pin leg, even
            # from the SAME net. Otherwise a path may backtrack through its pin
            # and hide against the symbol body while the visible stub hangs bare.
            inward = (round(math.cos(r)), -round(math.sin(r)))
            length = pin_lengths.get(number, 0.0)
            body = (px + length * inward[0], py + length * inward[1])
            lo_x, hi_x = sorted((gx, body[0]))
            lo_y, hi_y = sorted((gy, body[1]))
            for ix in range(math.floor((lo_x - 1.27) / step), math.ceil((hi_x + 1.27) / step) + 1):
                for iy in range(math.floor((lo_y - 1.27) / step), math.ceil((hi_y + 1.27) / step) + 1):
                    qx, qy = point((ix, iy))
                    along = (qx - gx) * inward[0] + (qy - gy) * inward[1]
                    across = abs((qx - gx) * inward[1] - (qy - gy) * inward[0])
                    extent = (body[0] - gx) * inward[0] + (body[1] - gy) * inward[1]
                    if 0.0001 < along <= extent + 0.0001 and across < 1.27 - 0.0001:
                        pin_necks.add((ix, iy))
            for first, last in (((px, py), (ex, ey)), ((ex, ey), (gx, ey)), ((gx, ey), (gx, gy))):
                lo_x, hi_x = sorted((first[0], last[0]))
                lo_y, hi_y = sorted((first[1], last[1]))
                margin = WIRE_VISUAL_CLEARANCE
                for ix in range(math.floor((lo_x - margin) / step), math.ceil((hi_x + margin) / step) + 1):
                    for iy in range(math.floor((lo_y - margin) / step), math.ceil((hi_y + margin) / step) + 1):
                        qx, qy = point((ix, iy))
                        distance = math.hypot(max(lo_x - qx, qx - hi_x, 0), max(lo_y - qy, qy - hi_y, 0))
                        if distance < margin - 0.0001:
                            fixed_clearance[ix, iy].add(net)
            # Reserve the entire escape stub from unrelated nets.
            start = grid(px, py)
            protected.update((start, escape))
            axis = 0 if start[1] == escape[1] else 1
            for ix in range(min(start[0], escape[0]), max(start[0], escape[0]) + 1):
                for iy in range(min(start[1], escape[1]), max(start[1], escape[1]) + 1):
                    occupied[(ix, iy)] = net
                    tracks[(ix, iy)].setdefault(net, set()).add(axis)
    # Ground glyphs and external net-label text are real graphical obstacles,
    # even though they are not physical components in the compiled netlist.
    for net, entries in endpoints.items():
        # Repeated physical pins on one IC still need one external island
        # label. Reserve its canonical side-facing anchor before a foreign
        # pin bus can trap it; final label_islands uses this same ordering.
        single_component = len({key[0] for key, _ in entries}) == 1
        label_key = min(entries, key=lambda entry: (escapes[entry[0]][4] % 180 != 0, entry[0]))[0]
        for key, _ in entries:
            _, _, ex, ey, direction = escapes[key]
            if net.lower().split(".")[-1] == "gnd":
                component = next(c for c, _, _, _ in placed if c.path == key[0])
                label = getattr(component, "ground_net_labels", {}).get(key[1], "")
                bounds = ground_bounds(ex, ey, direction, label)
            elif len(entries) == 1 or (single_component and key == label_key):
                component = next(c for c, _, _, _ in placed if c.path == key[0])
                name = getattr(component, "net_labels", {}).get(key[1], net)
                bounds = pin_label_bounds(name, ex, ey, direction)

            else:
                continue
            ax, ay = grid(bounds[0], bounds[1])
            bx, by = grid(bounds[2], bounds[3])
            for ix in range(ax, bx + 1):
                for iy in range(ay, by + 1):
                    if single_component and len(entries) > 1 and net.lower().split(".")[-1] != "gnd":
                        # Its own tree may reach the label terminal; unrelated
                        # nets must leave the full outline clear.
                        label_obstacles[(ix, iy)].add(net)
                    else:
                        obstacles.add((ix, iy))
    # Preserve verified functional ownership even for explicitly positioned
    # circuits: bypass branches terminate at their own device's supply escape,
    # never at a neighbouring capacitor simply because it is geometrically near.
    local_targets: dict[PinKey, tuple[PinKey, GridPoint]] = {}
    components = [c for c, _, _, _ in placed]
    for association in decoupling_associations(components, pin_nets, views):
        device, *capacitors = association.components
        supply, _ = association.nets
        device_entries = [(key, pos) for key, pos in endpoints[supply] if key[0] == device]
        if len(device_entries) != 1:
            continue
        for key, pos in endpoints[supply]:
            if key[0] in capacitors:
                local_targets[key] = device_entries[0]

    def net_order(pair: tuple[str, list[tuple[PinKey, GridPoint]]]) -> tuple[float, int, str] | tuple[int, str]:
        net, entries = pair
        if strategy == "short_first":
            xs, ys = zip(*(p for _, p in entries))
            return (max(xs) - min(xs) + max(ys) - min(ys), len(entries), net)
        return (len(entries), net)

    near_cache = _NearForeignCache(tracks, protected)
    escape_anchors = {anchor for entries in endpoints.values() for _, anchor in entries}
    connected = set()
    for net, entries in sorted(endpoints.items(), key=net_order):
        if len(entries) < 2 or net.lower().split(".")[-1] == "gnd":
            continue
        # Build the device backbone first; attach each local bypass directly
        # to its verified owner. Sorting also removes input traversal dependence.
        entries = sorted(entries, key=lambda entry: (entry[0] in local_targets, entry[0]))
        if strategy in ("x", "y", "reverse", "tree_reverse"):
            anchors = [entry for entry in entries if entry[0] not in local_targets]
            supports = [entry for entry in entries if entry[0] in local_targets]
            if strategy in ("reverse", "tree_reverse"):
                anchors.reverse()
            else:
                axis = 0 if strategy == "x" else 1
                anchors.sort(key=lambda entry: (entry[1][axis], entry[1][1 - axis], entry[0]))
            entries = anchors + supports
        tree = {entries[0][1]}
        connected.add(entries[0][0])
        for key, start in entries[1:]:
            targets = {local_targets[key][1]} if key in local_targets else tree
            target = min(targets, key=lambda p: (abs(p[0] - start[0]) + abs(p[1] - start[1]), p))
            own_stub = set()
            if key in local_targets:
                px, py, _, _, _ = escapes[key]
                pin = grid(px, py)
                own_stub = {
                    (ix, iy)
                    for ix in range(min(pin[0], start[0]), max(pin[0], start[0]) + 1)
                    for iy in range(min(pin[1], start[1]), max(pin[1], start[1]) + 1)
                } - {start}
            direction_search = strategy in ("tree_search", "tree_reverse", "crossing_averse")
            # Distance to the actual tree stays informative inside its bounding
            # box, avoiding budget exhaustion on sparse U-shaped route trees.
            distance_to_tree = tree_distance(targets) if direction_search else None
            start_state: RouteState = (start, None) if direction_search else start
            queue: list[tuple[float, int, GridPoint, Optional[int]]] = [(0, 0, start, None)]
            cost: dict[RouteState, int] = {start_state: 0}
            previous: dict[RouteState, RouteState] = {}
            found: Optional[RouteState] = None
            expanded = 0
            while queue and expanded < 20000:
                _, distance, current, prior_direction = heapq.heappop(queue)
                state: RouteState = (current, prior_direction) if direction_search else current
                if distance != cost.get(state):
                    continue
                if current in targets:
                    found = state
                    break
                expanded += 1
                for direction, (dx, dy) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
                    q = current[0] + dx, current[1] + dy
                    if not (25 <= q[0] <= 625 and 65 <= q[1] <= 425):
                        continue
                    if (
                        q in obstacles or any(owner != net for owner in label_obstacles.get(q, ()))
                    ) and q not in targets:
                        continue
                    if q in own_stub or (q in pin_necks and q not in escape_anchors):
                        continue
                    if any(owner != net for owner in fixed_clearance.get(q, ())):
                        continue
                    axis = 0 if dx else 1
                    # A one-cell gap is electrically separate but visually
                    # ambiguous beside a foreign bus, endpoint or bend. Keep
                    # parallel tracks at least two 0.635 mm cells apart. A
                    # strict perpendicular interior crossing remains legal.
                    if near_cache.blocked(q, axis, net):
                        continue
                    others = {n: axes for n, axes in tracks.get(q, {}).items() if n != net}
                    if others:
                        if q in protected or any(axis in axes for axes in others.values()):
                            continue
                    # Crossings must pass straight through, never terminate or
                    # turn on another net. No junction is emitted at crossings.
                    if any(n != net for n in tracks.get(current, {})):
                        if prior_direction != direction:
                            continue
                    new_cost = (
                        distance
                        + 1
                        + (24 if others and strategy == "crossing_averse" else 0)
                        + (3 if prior_direction is not None and prior_direction != direction else 0)
                    )
                    next_state: RouteState = (q, direction) if direction_search else q
                    if new_cost >= cost.get(next_state, float("inf")):
                        continue
                    cost[next_state] = new_cost
                    previous[next_state] = state
                    if distance_to_tree is not None:
                        heuristic = distance_to_tree(q)
                    else:
                        heuristic = abs(q[0] - target[0]) + abs(q[1] - target[1])
                    heapq.heappush(queue, (new_cost + heuristic, new_cost, q, direction))
            if found is None:
                failures.append((key, net))
                continue
            state_path = [found]
            while state_path[-1] != start_state:
                state_path.append(previous[state_path[-1]])
            state_path.reverse()
            if direction_search:
                path = [cast(tuple[GridPoint, Optional[int]], item)[0] for item in state_path]
            else:
                path = [cast(GridPoint, item) for item in state_path]
            if key in local_targets:
                direct = abs(start[0] - target[0]) + abs(start[1] - target[1])
                other_caps = {pos for other, pos in entries if other != key and other in local_targets}
                # Conflicting hints must not turn a local bypass into a remote
                # loop or a chain through another bypass endpoint.
                if len(path) - 1 > 2 * direct + 16 or other_caps.intersection(path):
                    failures.append((key, net))
                    continue
            tree.update(path)
            connected.add(key)
            near_cache.protect((path[0], path[-1]))
            for i, q in enumerate(path):
                occupied[q] = net
                axes = set()
                for neighbor in path[max(0, i - 1) : i] + path[i + 1 : i + 2]:
                    axes.add(0 if neighbor[1] == q[1] else 1)
                near_cache.add_track(q, net, axes)
                if len(axes) > 1:
                    near_cache.protect((q,))
            compact = [path[0]]
            for i in range(1, len(path) - 1):
                before = path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]
                after = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
                if before != after:
                    compact.append(path[i])
            compact.append(path[-1])
            for first_point, last_point in zip(compact, compact[1:]):
                if first_point != last_point:
                    wires.append((net, point(first_point), point(last_point)))
    routed_nets = {net for net, _, _ in wires}
    for key, (_, _, ex, ey, _) in sorted(escapes.items()):
        net = pin_nets[key]
        if net not in routed_nets:
            continue
        gx, gy = point(grid(ex, ey))
        # Real library pins need not lie on the routing grid. Preserve the exact
        # electrical contact with short orthogonal transitions to the search grid.
        if ex != gx:
            wires.append((net, (ex, ey), (gx, ey)))
        if ey != gy:
            wires.append((net, (gx, ey), (gx, gy)))
    return wires, escapes, failures


def split_group(placed: Placements, views: Views, pin_nets: PinNets) -> Optional[tuple[Placements, Placements]]:
    """Cut complete functional atoms, minimizing signal-net page boundaries."""
    from .KiCadSchematicPlacement import functional_atoms, signal_nets, atom_bounds

    components = [entry[0] for entry in placed]
    atoms, _ = functional_atoms(components, pin_nets, views)
    paths = [c.path for c in components]
    endpoints = signal_nets(components, pin_nets)
    choices = []
    for cut in range(1, len(placed)):
        left, right = set(paths[:cut]), set(paths[cut:])
        if any(set(atom) & left and set(atom) & right for atom in atoms):
            continue
        crossing = sum(bool(ends & left) and bool(ends & right) for ends in endpoints.values())
        a, b = atom_bounds(placed[:cut], views), atom_bounds(placed[cut:], views)
        area_a, area_b = (a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])
        choices.append(((crossing, abs(area_a - area_b), abs(2 * cut - len(placed)), tuple(sorted(left))), cut))
    if not choices:
        return None
    _, cut = min(choices)
    return placed[:cut], placed[cut:]
