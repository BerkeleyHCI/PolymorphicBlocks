"""Connectivity-driven placement and conservative orthogonal local wiring.

Layout consumes the physical netlist; it never introduces electrical connections.
Failed local routes retain labels and are reported, rather than guessed wires.
"""

from __future__ import annotations

import heapq
import math
from collections import defaultdict
from typing import Any, Dict, List, Sequence, Tuple

GRID = 1.27


def snap(value: float) -> float:
    return round(round(value / GRID) * GRID, 4)


def transform(x: float, y: float, angle: int) -> Tuple[float, float]:
    r = math.radians(angle)
    return round(x * math.cos(r) + y * math.sin(r), 4), round(-x * math.sin(r) + y * math.cos(r), 4)


def pins(view: Any, x: float, y: float, angle: int) -> list:
    result = []
    for number, dx, dy, direction in view.pins:
        tx, ty = transform(dx, dy, angle)
        result.append((number, round(x + tx, 4), round(y + ty, 4), (direction + angle) % 360))
    return result


def graphic_bounds(view: Any, angle: int = 0, include_pins: bool = True) -> Tuple[float, float, float, float]:
    points = []

    def collect(tree):
        if not isinstance(tree, list) or not tree:
            return
        name = str(tree[0])
        if name in ("property", "pin"):
            return
        if name == "circle":
            center = next((v for v in tree if isinstance(v, list) and str(v[0]) == "center"), None)
            radius = next((v[1] for v in tree if isinstance(v, list) and str(v[0]) == "radius"), None)
            if center is not None and radius is not None:
                for dx, dy in ((radius, 0), (-radius, 0), (0, radius), (0, -radius)):
                    points.append(transform(center[1] + dx, -center[2] + dy, angle))
        if name in ("start", "end", "xy", "center") and len(tree) >= 3:
            if isinstance(tree[1], (int, float)) and isinstance(tree[2], (int, float)):
                points.append(transform(float(tree[1]), -float(tree[2]), angle))
        for child in tree:
            collect(child)

    collect(view.definition)
    if include_pins:
        points.extend((transform(p[1], p[2], angle)) for p in view.pins)
    if not points:
        return -5, -5, 5, 5
    return min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)


def ground_rotation(direction: float) -> int:
    """Point ground away from the pin instead of into adjacent pin labels."""
    return int(direction + 270) % 360


def ground_bounds(x: float, y: float, direction: float):
    angle = ground_rotation(direction)
    corners = [transform(dx, dy, angle) for dx in (-2.54, 2.54) for dy in (0, 4.445)]
    return (
        x + min(p[0] for p in corners),
        y + min(p[1] for p in corners),
        x + max(p[0] for p in corners),
        y + max(p[1] for p in corners),
    )


def annotation_position(component, view, x, y, rotation):
    if getattr(component, "annotation", None) is not None:
        return component.annotation[0], component.annotation[1], ""
    xmin, ymin, xmax, ymax = graphic_bounds(view, rotation)
    width = max(len(component.refdes), len(getattr(component, "display_value", "") or component.value)) * 0.8
    if "FET" in view.lib_id or "Q_NMOS" in view.lib_id or "Q_PMOS" in view.lib_id:
        if rotation in (0, 180):
            return x + xmax + 3.81 + width / 2, y - 1.27, ""
        gate = next((p for p in pins(view, x, y, rotation) if p[0] == "1"), None)
        return (x, y + ymin - 6.35, "") if gate and gate[2] > y else (x, y + ymax + 3.81, "")
    terminals = pins(view, x, y, rotation)
    if len(terminals) == 2 and abs(terminals[0][1] - terminals[1][1]) < 0.01:
        return x + xmax + 3.81 + width / 2, y - 1.27, ""
    return x, y + ymax + 12.7, ""


def regroup(components: Sequence[Any], pin_nets: dict) -> None:
    """Co-locate small sibling circuits; IC/control groups stay boundaries."""
    groups = defaultdict(list)
    for c in components:
        groups[c.group].append(c)
    parent = {g: g for g in groups}

    def root(g):
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


def place_group(components: Sequence[Any], views: dict, pin_nets: dict) -> list:
    """Compact graph ordering; simple two-terminal chains get inline orientation."""
    components = sorted(components, key=lambda c: c.path)
    adjacency = {c.path: set() for c in components}
    nets = defaultdict(list)
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
            key=lambda p: ("Resistor" in views[p].lib_id or ":R_" in views[p].lib_id, p),
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
    placed = []
    x = 65.0
    y = 80.0
    row_height = 0.0
    page = []
    pages = []
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
                key=lambda a: desired * next(transform(dx, dy, a)[0] for n, dx, dy, _ in view.pins if n == target_pin),
            )
        xmin, ymin, xmax, ymax = graphic_bounds(view, rotation)
        # Space includes outward labels, annotation block, and local routing lanes.
        width = max(30, xmax - xmin + 20) if chain else max(60, xmax - xmin + 48)
        height = max(52, ymax - ymin + 32)
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
        x += width
        row_height = max(row_height, height)
    if page:
        pages.append(page)
    return pages


def route_local(placed: list, views: dict, pin_nets: dict) -> Tuple[list, dict, list]:
    """Route a same-net tree between pin escapes on a grid, avoiding other copper.

    No crossings or near misses are accepted. All failed endpoints retain a label.
    Router output is independently checked through native KiCad netlist export.
    """
    step = 0.635

    def grid(x, y):
        return round(x / step), round(y / step)

    def point(p):
        return round(p[0] * step, 4), round(p[1] * step, 4)

    obstacles = set()
    occupied = {}
    tracks = defaultdict(dict)
    protected = set()
    endpoints = defaultdict(list)
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
        text_width = max(len(c.refdes), len(getattr(c, "display_value", "") or c.value)) * 0.8
        ax, ay = grid(tx if align else tx - text_width / 2, ty - 1.27)
        bx, by = grid(tx + text_width if align else tx + text_width / 2, ty + 4)
        obstacles.update((ix, iy) for ix in range(ax, bx + 1) for iy in range(ay, by + 1))
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
        for key, _ in entries:
            _, _, ex, ey, direction = escapes[key]
            if net.lower().split(".")[-1] == "gnd":
                bounds = ground_bounds(ex, ey, direction)
            elif len(entries) == 1:
                width = len(net) * 0.8 + 2.54
                if direction == 0:
                    bounds = (ex - width, ey - 1.27, ex - 1.27, ey + 1.27)
                elif direction == 180:
                    bounds = (ex + 1.27, ey - 1.27, ex + width, ey + 1.27)
                elif direction == 270:
                    bounds = (ex - 1.27, ey - width, ex + 1.27, ey - 1.27)
                else:
                    bounds = (ex - 1.27, ey + 1.27, ex + 1.27, ey + width)
            else:
                continue
            ax, ay = grid(bounds[0], bounds[1])
            bx, by = grid(bounds[2], bounds[3])
            obstacles.update((ix, iy) for ix in range(ax, bx + 1) for iy in range(ay, by + 1))
    connected = set()
    for net, entries in sorted(endpoints.items(), key=lambda pair: (len(pair[1]), pair[0])):
        if len(entries) < 2 or net.lower().split(".")[-1] == "gnd":
            continue
        tree = {entries[0][1]}
        connected.add(entries[0][0])
        for key, start in entries[1:]:
            target = min(tree, key=lambda p: abs(p[0] - start[0]) + abs(p[1] - start[1]))
            queue = [(0, 0, start, None)]
            cost = {start: 0}
            previous = {}
            found = None
            expanded = 0
            while queue and expanded < 20000:
                _, distance, current, prior_direction = heapq.heappop(queue)
                if distance != cost.get(current):
                    continue
                if current in tree:
                    found = current
                    break
                expanded += 1
                for direction, (dx, dy) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
                    q = current[0] + dx, current[1] + dy
                    if not (25 <= q[0] <= 625 and 65 <= q[1] <= 425):
                        continue
                    if q in obstacles and q not in tree:
                        continue
                    axis = 0 if dx else 1
                    others = {n: axes for n, axes in tracks.get(q, {}).items() if n != net}
                    if others:
                        if q in protected or any(axis in axes for axes in others.values()):
                            continue
                    # Crossings must pass straight through, never terminate or
                    # turn on another net. No junction is emitted at crossings.
                    if any(n != net for n in tracks.get(current, {})):
                        if prior_direction != direction:
                            continue
                    new_cost = distance + 1 + (3 if prior_direction is not None and prior_direction != direction else 0)
                    if new_cost >= cost.get(q, float("inf")):
                        continue
                    cost[q] = new_cost
                    previous[q] = current
                    heuristic = abs(q[0] - target[0]) + abs(q[1] - target[1])
                    heapq.heappush(queue, (new_cost + heuristic, new_cost, q, direction))
            if found is None:
                failures.append((key, net))
                continue
            path = [found]
            while path[-1] != start:
                path.append(previous[path[-1]])
            path.reverse()
            tree.update(path)
            connected.add(key)
            protected.update((path[0], path[-1]))
            for i, q in enumerate(path):
                occupied[q] = net
                axes = set()
                for neighbor in path[max(0, i - 1) : i] + path[i + 1 : i + 2]:
                    axes.add(0 if neighbor[1] == q[1] else 1)
                tracks[q].setdefault(net, set()).update(axes)
                if len(axes) > 1:
                    protected.add(q)
            compact = [path[0]]
            for i in range(1, len(path) - 1):
                before = path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]
                after = path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]
                if before != after:
                    compact.append(path[i])
            compact.append(path[-1])
            for a, b in zip(compact, compact[1:]):
                if a != b:
                    wires.append((net, point(a), point(b)))
    routed_nets = {net for net, _, _ in wires}
    for key, (_, _, ex, ey, _) in escapes.items():
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
