"""Presentation-only system overviews backed by compiled cross-sheet nets.

Diagram connectors are graphics, never electrical wires. Direction is an explicit
source annotation; shared-net witnesses establish association, not signal flow.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
import re
import textwrap
from typing import Any, Mapping, Tuple

GRID = 1.27
CARD_W, CARD_H = 83.82, 27.94


def _text(value, name, limit=None):
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or (limit is not None and len(value) > limit)
    ):
        raise ValueError(f"{name} must be nonempty text" + (f" of at most {limit} characters" if limit else ""))


def _object(value, fields, required):
    if not isinstance(value, Mapping) or set(value) - set(fields) or set(required) - set(value):
        raise ValueError("overview object has unknown or missing fields")
    return value


@dataclass(frozen=True)
class SchematicOverviewBlock:
    sheet: str
    title: str
    summary: str
    column: int
    row: int

    def __post_init__(self):
        _text(self.sheet, "overview sheet")
        _text(self.title, "overview title", 48)
        _text(self.summary, "overview summary", 96)
        for value in (self.column, self.row):
            if type(value) is not int or not 0 <= value <= 3:
                raise ValueError("overview column and row must be integers from 0 to 3")

    def to_dict(self):
        return dict(sheet=self.sheet, title=self.title, summary=self.summary, column=self.column, row=self.row)

    @classmethod
    def from_dict(cls, value):
        return cls(
            **_object(
                value, ("sheet", "title", "summary", "column", "row"), ("sheet", "title", "summary", "column", "row")
            )
        )


@dataclass(frozen=True)
class SchematicOverviewLink:
    source: str
    target: str
    label: str
    nets: Tuple[str, ...]
    directed: bool = False

    def __post_init__(self):
        _text(self.source, "overview link source")
        _text(self.target, "overview link target")
        _text(self.label, "overview link label", 48)
        if (
            not isinstance(self.nets, tuple)
            or not self.nets
            or not all(isinstance(n, str) for n in self.nets)
            or len(set(self.nets)) != len(self.nets)
        ):
            raise ValueError("overview link nets must be a nonempty tuple without duplicates")
        for net in self.nets:
            _text(net, "overview link net")
        if not isinstance(self.directed, bool):
            raise ValueError("overview directed must be boolean")

    def to_dict(self):
        return dict(
            source=self.source, target=self.target, label=self.label, nets=list(self.nets), directed=self.directed
        )

    @classmethod
    def from_dict(cls, value):
        data = dict(
            _object(value, ("source", "target", "label", "nets", "directed"), ("source", "target", "label", "nets"))
        )
        if not isinstance(data["nets"], (list, tuple)):
            raise ValueError("overview link nets must be an array")
        data["nets"] = tuple(data["nets"])
        return cls(**data)


@dataclass(frozen=True)
class SchematicOverview:
    blocks: Tuple[SchematicOverviewBlock, ...] = ()
    links: Tuple[SchematicOverviewLink, ...] = ()

    def __post_init__(self):
        if (
            not isinstance(self.blocks, tuple)
            or len(self.blocks) > 16
            or not all(isinstance(v, SchematicOverviewBlock) for v in self.blocks)
        ):
            raise ValueError("overview blocks must be a tuple of at most 16 blocks")
        if (
            not isinstance(self.links, tuple)
            or len(self.links) > 8
            or not all(isinstance(v, SchematicOverviewLink) for v in self.links)
        ):
            raise ValueError("overview links must be a tuple of at most 8 links")

    def to_dict(self):
        return dict(blocks=[v.to_dict() for v in self.blocks], links=[v.to_dict() for v in self.links])

    @classmethod
    def from_dict(cls, value):
        data = _object(value, ("blocks", "links"), ())
        if any(not isinstance(data.get(k, []), (list, tuple)) for k in ("blocks", "links")):
            raise ValueError("overview blocks and links must be arrays")
        return cls(
            tuple(SchematicOverviewBlock.from_dict(v) for v in data.get("blocks", [])),
            tuple(SchematicOverviewLink.from_dict(v) for v in data.get("links", [])),
        )


def _ground(net):
    return any(p in ("gnd", "ground") for p in re.split(r"[.\[\]]", net.lower()))


def _route(start, end, rectangles, occupied):
    def grid(p):
        return tuple(round(v / GRID) for v in p)

    start, end = grid(start), grid(end)
    blocked = set(occupied)
    for x1, y1, x2, y2 in rectangles:
        for x in range(math.floor(x1 / GRID), math.ceil(x2 / GRID) + 1):
            for y in range(math.floor(y1 / GRID), math.ceil(y2 / GRID) + 1):
                blocked.add((x, y))
    blocked.discard(start)
    blocked.discard(end)
    queue = [(0, 0, start, -1)]
    best = {(start, -1): 0}
    previous = {}
    goal = None
    while queue:
        _, cost, point, direction = heapq.heappop(queue)
        key = (point, direction)
        if best.get(key) != cost:
            continue
        if point == end:
            goal = key
            break
        for d, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
            nxt = point[0] + dx, point[1] + dy
            if not (14 <= nxt[0] <= 314 and 36 <= nxt[1] <= 150) or nxt in blocked:
                continue
            nc = cost + 1 + (0.3 if direction not in (-1, d) else 0)
            nk = (nxt, d)
            if nc < best.get(nk, math.inf):
                best[nk] = nc
                previous[nk] = key
                heapq.heappush(queue, (nc + abs(nxt[0] - end[0]) + abs(nxt[1] - end[1]), nc, nxt, d))
    if goal is None:
        return [], set()
    points = []
    while True:
        points.append(goal[0])
        if goal not in previous:
            break
        goal = previous[goal]
    points.reverse()
    compact = [points[0]]
    for i in range(1, len(points) - 1):
        if (points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]) != (
            points[i + 1][0] - points[i][0],
            points[i + 1][1] - points[i][1],
        ):
            compact.append(points[i])
    if len(points) > 1:
        compact.append(points[-1])
    return [[round(x * GRID, 4), round(y * GRID, 4)] for x, y in compact], set(points)


def _segment_cells(a, b):
    a, b = [tuple(round(v / GRID) for v in p) for p in (a, b)]
    return {
        (x, y) for x in range(min(a[0], b[0]), max(a[0], b[0]) + 1) for y in range(min(a[1], b[1]), max(a[1], b[1]) + 1)
    }


def _intersects(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def _tag_box(p):
    return (p[0] - 0.5, p[1] - 1.4, p[0] + 3.8, p[1] + 1.4)


def _position_tags(nodes, links, diagnostics):
    # Reserve all strokes and arrowheads before placing any text. Label IDs are
    # graphical annotations, so they must never sit on another relationship.
    obstacles = [(x1 - 0.8, y1 - 0.8, x2 + 0.8, y2 + 0.8) for x1, y1, x2, y2 in (n["bounds"] for n in nodes)]
    for link in links:
        for a, b in zip(link["path"], link["path"][1:]):
            obstacles.append(
                (min(a[0], b[0]) - 0.65, min(a[1], b[1]) - 0.65, max(a[0], b[0]) + 0.65, max(a[1], b[1]) + 0.65)
            )
        if link["directed"] and link["path"]:
            a, b = link["path"][-2:]
            obstacles.append(
                (min(a[0], b[0]) - 1.1, min(a[1], b[1]) - 1.1, max(a[0], b[0]) + 1.1, max(a[1], b[1]) + 1.1)
            )
    for link in links:
        candidates = []
        for a, b in zip(link["path"], link["path"][1:]):
            length = math.dist(a, b)
            if length < GRID:
                continue
            steps = max(1, round(length / GRID))
            for step in sorted(range(steps + 1), key=lambda i: (abs(i - steps / 2), i)):
                x = a[0] + (b[0] - a[0]) * step / steps
                y = a[1] + (b[1] - a[1]) * step / steps
                for side in (-1, 1):
                    candidates.append(
                        (x - 1.65, y + side * 3.81) if a[1] == b[1] else (x + side * 3.81 - (3.8 if side < 0 else 0), y)
                    )
        tag = None
        for candidate in candidates:
            box = _tag_box(candidate)
            if (
                18 <= box[0]
                and box[2] <= 396
                and 47 <= box[1]
                and box[3] <= 190
                and not any(_intersects(box, o) for o in obstacles)
            ):
                tag = [round(v, 4) for v in candidate]
                obstacles.append(box)
                break
        link["tag"] = tag
        if tag is None and link["path"]:
            link["path"] = []
            link["status"] = "legend_only"
            diagnostics.append(link["id"] + ": no clear diagram tag position; relationship retained in connection key")


def build_overviews(boards, plan, custom=None):
    custom = custom or SchematicOverview()
    if not isinstance(custom, SchematicOverview):
        raise ValueError("overview must be a SchematicOverview")
    all_sheets = [s for s in plan.sheets if s.id != "overview"]

    def resolve(selector):
        found = [s for s in all_sheets if s.id == selector]
        if not found:
            found = [s for s in all_sheets if s.title == selector]
        if len(found) != 1:
            raise ValueError("unknown or ambiguous overview sheet: " + selector)
        return found[0]

    blocks = {}
    for block in custom.blocks:
        sheet = resolve(block.sheet)
        if sheet.id in blocks:
            raise ValueError("duplicate overview block: " + block.sheet)
        blocks[sheet.id] = block
    links = []
    pairs = set()
    for link in custom.links:
        source, target = resolve(link.source), resolve(link.target)
        if source.scope != target.scope or source.id == target.id:
            raise ValueError("overview links must join different sheets in one board scope")
        pair = tuple(sorted((source.id, target.id)))
        if pair in pairs:
            raise ValueError("duplicate overview relationship")
        pairs.add(pair)
        links.append((source, target, link))
    result = dict(schema=1, fingerprint=plan.fingerprint, boards=[])
    for board in boards:
        sheets = [s for s in all_sheets if s.scope == board.scope]
        sheet_of = {p.region_id: s.id for s in sheets for p in s.regions}
        available = {}
        for net, regions in sorted(board.net_regions.items()):
            if _ground(net):
                continue
            pages = sorted({sheet_of[r] for r in regions if r in sheet_of})
            for i, a in enumerate(pages):
                for b in pages[i + 1 :]:
                    available.setdefault((a, b), []).append(net)
        used = set()
        nodes = []
        overview_present = any(s.id == "overview" and s.scope == board.scope for s in plan.sheets)
        mode = "diagram" if len(sheets) <= 16 else "directory"
        for sheet in sheets:
            if sheet.id in blocks:
                block = blocks[sheet.id]
                if (block.column, block.row) in used:
                    raise ValueError("overview blocks occupy the same grid cell")
                used.add((block.column, block.row))
        for index, sheet in enumerate(sheets):
            block = blocks.get(sheet.id)
            if block and mode != "diagram":
                raise ValueError("custom overview diagrams support at most 16 sheets per scope")
            if block:
                column, row = block.column, block.row
            else:
                free = next(
                    ((c, r) for r in range(4) for c in range(4) if (c, r) not in used), (index // 10, index % 10)
                )
                column, row = free
                used.add(free)
            groups = [board.regions[p.region_id].spec.title for p in sheet.regions]
            # Region continuation indices describe packing fragments, not circuit
            # sheet numbers. Only the actual sheet title names a continuation.
            summary_groups = list(dict.fromkeys(re.sub(r" /\d+$", "", group) for group in groups))
            summary = "; ".join(summary_groups)
            if len(summary) > 96:
                summary = summary[:76].rsplit(";", 1)[0] + f"; {len(groups)} circuit regions"
            x, y = round(20.32 + column * 96.52, 4), round(49.53 + row * 36.83, 4)
            nodes.append(
                dict(
                    sheet_id=sheet.id,
                    sheet_title=sheet.title,
                    title=block.title
                    if block
                    else (
                        re.sub(r"^\d+[. ]+", "", sheet.title)[:45] + "..."
                        if len(re.sub(r"^\d+[. ]+", "", sheet.title)) > 48
                        else re.sub(r"^\d+[. ]+", "", sheet.title)
                    ),
                    summary=block.summary if block else summary[:96],
                    column=column,
                    row=row,
                    page=sheets.index(sheet) + (2 if overview_present else 1),
                    components=sum(len(board.regions[p.region_id].spec.components) for p in sheet.regions),
                    regions=groups,
                    section=groups[0].split(" /")[0] if groups else sheet.title,
                    bounds=[x, y, round(x + CARD_W, 4), round(y + CARD_H, 4)],
                )
            )
        directory_pages = []
        if mode == "directory":
            if len(nodes) > 40:
                # The serializer inserts Contents pages above forty children.
                # Record the real document owning each circuit link, and its
                # legacy measured bounds there, rather than claiming those links
                # exist on the overview root. Keep that pagination unbounded.
                for index, item in enumerate(nodes):
                    bucket, slot = divmod(index, 40)
                    x, y = 20 + (slot // 10) * 90, 50 + (slot % 10) * 14
                    item["column"], item["row"] = divmod(slot, 10)
                    item["bounds"] = [x, y, x + 80, y + 8]
                    item["directory_document"] = board.prefix + f"_contents_{bucket + 1}.kicad_sch"
                for bucket in range((len(nodes) + 39) // 40):
                    members = nodes[bucket * 40:(bucket + 1) * 40]
                    x, y = 20 + (bucket // 10) * 90, 50 + (bucket % 10) * 14
                    directory_pages.append(dict(
                        index=bucket, title=f"Contents {bucket + 1}",
                        filename=board.prefix + f"_contents_{bucket + 1}.kicad_sch",
                        page=len(sheets) + bucket + 2, sheets=len(members),
                        components=sum(n["components"] for n in members),
                        bounds=[x, y, x + 80, y + 8],
                    ))
            else:
                # Group navigation by actual source-owned functional titles.
                directory_nodes = sorted(nodes, key=lambda n: (n["section"], n["sheet_title"], n["sheet_id"]))
                for index, item in enumerate(directory_nodes):
                    column, row = divmod(index, 10)
                    x, y = round(20.32 + column * 96.52, 4), round(52.07 + row * 12.7, 4)
                    item["column"], item["row"] = column, row
                    item["bounds"] = [x, y, round(x + CARD_W, 4), round(y + 12, 4)]
                    item["directory_document"] = board.prefix + ".kicad_sch"
        selected = []
        explicit = [(a, b, l) for a, b, l in links if a.scope == board.scope]
        if explicit and mode != "diagram":
            raise ValueError("overview connections require at most 16 sheets")
        if explicit:
            for a, b, link in explicit:
                witness = available.get(tuple(sorted((a.id, b.id))), [])
                if not set(link.nets).issubset(witness):
                    raise ValueError("overview net does not connect both sheets: " + link.label)
                selected.append(
                    dict(
                        source=a.id,
                        target=b.id,
                        label=link.label,
                        nets=list(link.nets),
                        directed=link.directed,
                        origin="authored",
                    )
                )
        elif mode == "diagram":
            parent = {s.id: s.id for s in sheets}

            def root(a):
                while parent[a] != a:
                    a = parent[a]
                return a

            for (a, b), nets in sorted(available.items(), key=lambda item: (-len(item[1]), item[0])):
                if len(selected) == 8:
                    break
                if root(a) == root(b):
                    continue
                parent[root(a)] = root(b)
                selected.append(
                    dict(
                        source=a,
                        target=b,
                        label=(nets[0][:45] + "..." if len(nets[0]) > 48 else nets[0])
                        if len(nets) == 1
                        else f"{len(nets)} shared nets",
                        nets=nets,
                        directed=False,
                        origin="compiled",
                    )
                )
        by_id = {n["sheet_id"]: n for n in nodes}
        ports = {}
        for index, link in enumerate(selected):
            a, b = by_id[link["source"]], by_id[link["target"]]
            side_a, side_b = ("right", "left") if a["column"] < b["column"] else ("left", "right")
            if a["column"] == b["column"]:
                side_a, side_b = ("bottom", "top") if a["row"] < b["row"] else ("top", "bottom")
            link["_sides"] = (side_a, side_b)
            for n, side in ((a, side_a), (b, side_b)):
                ports.setdefault((n["sheet_id"], side), []).append(index)
        reserved = set()
        diagnostics = []
        for index, link in enumerate(selected):
            ends = []
            stubs = []
            for identity, side in zip((link["source"], link["target"]), link.pop("_sides")):
                n = by_id[identity]
                x1, y1, x2, y2 = n["bounds"]
                order = ports[(identity, side)]
                offset = (order.index(index) - (len(order) - 1) / 2) * 3.81
                if side in ("left", "right"):
                    p = (x1 if side == "left" else x2, round((y1 + y2) / 2 + offset, 4))
                    d = (-1, 0) if side == "left" else (1, 0)
                else:
                    p = (round((x1 + x2) / 2 + offset, 4), y1 if side == "top" else y2)
                    d = (0, -1) if side == "top" else (0, 1)
                p = tuple(round(round(v / GRID) * GRID, 4) for v in p)
                ends.append(list(p))
                stubs.append([round(p[0] + d[0] * 3.81, 4), round(p[1] + d[1] * 3.81, 4)])
            link["_ends"] = ends
            link["_stubs"] = stubs
            for a, b in zip(ends, stubs):
                reserved.update(_segment_cells(a, b))
        occupied = set()
        for index, link in enumerate(selected):
            ends = link.pop("_ends")
            stubs = link.pop("_stubs")
            path, cells = _route(stubs[0], stubs[1], [n["bounds"] for n in nodes], occupied | reserved)
            link["id"] = "L" + str(index + 1)
            link["endpoints"] = [
                dict(sheet_id=identity, sheet_title=by_id[identity]["sheet_title"],
                     page=by_id[identity]["page"])
                for identity in (link["source"], link["target"])
            ]
            link["path"] = [ends[0], *path, ends[1]] if path else []
            link["status"] = "drawn" if path else "legend_only"
            if path:
                occupied.update(cells)
            else:
                diagnostics.append(link["id"] + ": diagram route unavailable; relationship retained in connection key")
        _position_tags(nodes, selected, diagnostics)
        mechanical = sum(len(d.spec.components) for d in board.regions.values() if d.spec.kind == "mechanical")
        overview_sheet = next((s for s in plan.sheets if s.scope == board.scope and s.id == "overview"), None)
        overview_bounds = []
        if overview_sheet:
            for location in overview_sheet.regions:
                r = board.regions[location.region_id].spec
                overview_bounds.append(
                    [
                        location.x,
                        location.y,
                        location.x + r.bounds[2] - r.bounds[0],
                        location.y + r.bounds[3] - r.bounds[1],
                    ]
                )
        result["boards"].append(
            dict(
                scope=board.scope,
                root=board.prefix + ".kicad_sch",
                mode=mode,
                overview_present=overview_present,
                mechanical_area_bounds=overview_bounds,
                components=sum(len(d.spec.components) for d in board.regions.values()),
                mechanical_components=mechanical,
                circuit_sheets=len(sheets),
                nodes=nodes,
                directory_layout="paginated" if directory_pages else "grouped" if mode == "directory" else None,
                directory_pages=directory_pages,
                connections=selected,
                diagnostics=diagnostics,
                omitted_connection_pairs=max(0, len(available) - len(selected)),
                total_shared_pairs=len(available),
                shared_connections=[dict(source=a, target=b, nets=nets) for (a, b), nets in sorted(available.items())],
            )
        )
    return result


def render_overview(doc, board, data, options):
    # Import only when rendering, so the option models stay independent of the writer.
    from .KiCadSchematicExporter import node, children, effects, uid, S

    def text(role, value, x, y, size=1.27):
        doc.append(
            node(
                "text",
                value,
                node("at", round(x, 4), round(y, 4), 0),
                node("effects", node("font", node("size", size, size)), node("justify", S("left"))),
                node("uuid", uid(board.prefix, "overview", role)),
            )
        )

    text("title", options.design_name + " / SYSTEM OVERVIEW", 20, 33, 2.54)
    text(
        "subtitle",
        f"{data['components']} physical components  /  {data['circuit_sheets']} circuit sheets  /  Open a functional card for circuit detail",
        20,
        40,
        1.27,
    )
    if data["mode"] == "directory":
        text(
            "directory", "SHEET DIRECTORY — complete connectivity is shown on the detailed circuit sheets", 20, 46, 1.1
        )
        actual = {children(sheet, "uuid")[0][1]: sheet for sheet in children(doc, "sheet")}
        if data.get("directory_layout") == "paginated":
            for item in data["directory_pages"]:
                identity = uid(board.prefix, "contents", str(item["index"]))
                sheet = actual.get(identity)
                if sheet is None:
                    continue
                x, y, right, bottom = item["bounds"]
                for prop in children(sheet, "property"):
                    prop[-1] = effects(hide=True)
                text("directory-" + identity + "-title", item["title"], x + 2, y + 2, 1.1)
                text("directory-" + identity + "-count",
                     f"Page {item['page']} / {item['sheets']} sheets / {item['components']} components",
                     x + 2, y + 5.5, 1.1)
            return
        for item in data["nodes"]:
            identity = uid(board.prefix, item["sheet_id"])
            sheet = actual.get(identity)
            if sheet is None:
                continue
            x, y, right, bottom = item["bounds"]
            children(sheet, "at")[0][1:] = [x, y]
            children(sheet, "size")[0][1:] = [right - x, bottom - y]
            for prop in children(sheet, "property"):
                prop[-1] = effects(hide=True)
            section = item["section"]
            section = section if len(section) <= 48 else section[:45] + "..."
            display = item["title"]
            display = display if len(display) <= 48 else display[:45] + "..."
            text("directory-" + identity + "-section", section, x + 2, y + 2.5, 1.1)
            text("directory-" + identity + "-title", display, x + 2, y + 6, 1.1)
            text("directory-" + identity + "-count", f"Sheet {item['page']} / {item['components']} components", x + 2, y + 9.5, 1.1)
        return
    key_only = sum(link["status"] != "drawn" for link in data["connections"])
    text(
        "coverage",
        f"{len(data['connections'])} selected relationships / {data['total_shared_pairs']} shared sheet pairs / {key_only} key-only routes. Detail sheets define complete wiring.",
        20,
        46,
        1.27,
    )
    actual = {children(s, "uuid")[0][1]: s for s in children(doc, "sheet")}
    for n in data["nodes"]:
        identity = uid(board.prefix, n["sheet_id"])
        sheet = actual.get(identity)
        if sheet is None:
            continue
        x, y, x2, y2 = n["bounds"]
        children(sheet, "at")[0][1:] = [x, y]
        children(sheet, "size")[0][1:] = [CARD_W, CARD_H]
        children(children(sheet, "stroke")[0], "width")[0][1] = 0.35
        for prop in children(sheet, "property"):
            if prop[1] == "Sheetname":
                prop[-1] = effects(hide=True)
            children(prop, "at")[0][1:] = [x + 3.81, y + 4.445, 0]
        for i, line in enumerate(textwrap.wrap(n["title"], 38)):
            text(n["sheet_id"] + "-title-" + str(i), line, x + 3.81, y + 4.445 + i * 4.0, 2.0)
        for i, line in enumerate(textwrap.wrap(n["summary"], 56)):
            text(n["sheet_id"] + "-summary-" + str(i), line, x + 3.81, y + 13.0 + i * 3.1, 1.4)
        text(n["sheet_id"] + "-count", f"Sheet {n['page']}  /  {n['components']} components", x + 3.81, y + 23.5, 1.4)
    for index, link in enumerate(data["connections"]):
        path = link["path"]

        def line(role, pts):
            doc.append(
                node(
                    "polyline",
                    node("pts", *[node("xy", *p) for p in pts]),
                    node("stroke", node("width", 0.25), node("type", S("default"))),
                    node("fill", node("type", S("none"))),
                    node("uuid", uid(board.prefix, "overview", link["id"], role)),
                )
            )

        if path:
            line("relationship", path)
            p = link["tag"]
            text(link["id"] + "-tag", link["id"], p[0], p[1], 1.27)
            if link["directed"]:
                a, b = path[-2:]
                dx = b[0] - a[0]
                dy = b[1] - a[1]
                length = math.hypot(dx, dy)
                dx /= length
                dy /= length
                line(
                    "arrow",
                    [[b[0] - dx * 1.8 - dy, b[1] - dy * 1.8 + dx], b, [b[0] - dx * 1.8 + dy, b[1] - dy * 1.8 - dx]],
                )
        # Two bounded lines fit between the last card row and the mechanical
        # inset at y=205. Page identities remain useful even with no drawn route
        # or with long, repeated, or source-authored card titles.
        source, target = link["endpoints"]
        relation = "→" if link["directed"] else "↔"
        label = f"{link['id']}  Sheet {source['page']} {relation} Sheet {target['page']}"
        if not path:
            label += " (key only)"
        x, y = 20.32 + (index % 4) * 96.52, 191.0 + (index // 4) * 6.35
        text(link["id"] + "-key", label, x, y, 1.27)
        text(link["id"] + "-key-label", link["label"], x, y + 2.54, 1.27)
    text(
        "legend",
        "Functional relationships only; arrow direction is source-authored. See detail sheets for complete electrical connectivity.",
        20,
        204,
        1.0,
    )
    # Keep explanatory notes outside every physical region in the overview inset.
    occupied_right = max((b[2] for b in data["mechanical_area_bounds"]), default=20)
    note_x = max(20, occupied_right + 10)
    if note_x + 105 <= 395:
        text("mechanical-title", "MECHANICAL REFERENCES", note_x, 212, 1.65)
        text(
            "mechanical-count",
            f"{data['mechanical_components']} reference footprints in compiled scope",
            note_x,
            218,
            1.4,
        )
        text("mechanical-help", "Reference symbols identify mechanical parts.", note_x, 224, 1.27)
        text("mechanical-pins", "They have no modeled electrical pins.", note_x, 230, 1.27)
        text("workflow", "PB Python  >  compile  >  regenerate", note_x, 239, 1.4)
