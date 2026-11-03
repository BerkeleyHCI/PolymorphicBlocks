"""Conservative scene inspection. Machine evidence never grants visual approval."""

from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import math
import unicodedata
import sexpdata


def children(tree, name):
    return [v for v in tree if isinstance(v, list) and v and str(v[0]) == name]


def text_width(text, size):
    return sum((2 if unicodedata.east_asian_width(c) in ("W", "F") else 1) for c in text) * size * 0.8


@dataclass(frozen=True)
class SceneText:
    identity: str
    text: str
    bounds: tuple
    owner: str
    kind: str


def text_item(identity, text, at, effect, owner, kind):
    if any(str(v) == "hide" for v in effect[1:]):
        return None
    font = children(effect, "font")
    size = children(font[0], "size")[0][1] if font and children(font[0], "size") else 1.27
    lines = str(text).splitlines() or [""]
    w = max(text_width(line, size) for line in lines)
    h = size * 1.4 * len(lines)
    justify = children(effect, "justify")
    terms = {str(v) for v in justify[0][1:]} if justify else set()
    x, y = float(at[1]), float(at[2])
    angle = float(at[3]) if len(at) > 3 else 0
    lo = 0 if "left" in terms else -w if "right" in terms else -w / 2
    corners = [(lo, -h / 2), (lo + w, -h / 2), (lo + w, h / 2), (lo, h / 2)]
    r = math.radians(angle)
    pts = [(x + a * math.cos(r) + b * math.sin(r), y - a * math.sin(r) + b * math.cos(r)) for a, b in corners]
    return SceneText(
        identity,
        str(text),
        (
            min(a for a, b in pts),
            min(b for a, b in pts),
            max(a for a, b in pts),
            max(b for a, b in pts),
        ),
        owner,
        kind,
    )


def inspect_documents(files, diagnostics, patterns=()):
    findings = []
    scenes = []
    component_sheets = {}

    def finding(code, sheet, objects, detail):
        identity = hashlib.sha256((code + "|" + sheet + "|" + "|".join(sorted(objects))).encode()).hexdigest()[:20]
        findings.append(
            dict(
                id=identity,
                code=code,
                sheet=sheet,
                objects=sorted(objects),
                detail=detail,
            )
        )

    for filename, content in sorted(files.items()):
        if not filename.endswith(".kicad_sch"):
            continue
        doc = sexpdata.loads(content)
        texts = []
        for i, item in enumerate(children(doc, "text") + children(doc, "label") + children(doc, "global_label")):
            at = children(item, "at")
            ef = children(item, "effects")
            if at and ef:
                ids = children(item, "uuid")
                t = text_item(
                    str(ids[0][1]) if ids else str(i),
                    item[1],
                    at[0],
                    ef[0],
                    "",
                    str(item[0]),
                )
                if t:
                    texts.append(t)
        definitions = {d[1]: d for container in children(doc, "lib_symbols") for d in children(container, "symbol")}
        wires = [
            (tuple(p[1:3]) for p in children(pts, "xy"))
            for wire in children(doc, "wire")
            for pts in children(wire, "pts")
        ]
        wires = [tuple(wire) for wire in wires]
        for symbol in children(doc, "symbol"):
            props = children(symbol, "property")
            owner = next((p[2] for p in props if p[1] == "PBPath"), "")
            if owner:
                component_sheets[owner] = filename
            for p in props:
                at = children(p, "at")
                ef = children(p, "effects")
                if at and ef:
                    t = text_item(owner + ":" + str(p[1]), p[2], at[0], ef[0], owner, "field")
                    if t:
                        texts.append(t)
            lib = children(symbol, "lib_id")
            ats = children(symbol, "at")
            if lib and ats and lib[0][1] in definitions:
                definition = definitions[lib[0][1]]
                name_options = children(definition, "pin_names")
                hide_names = name_options and any(str(v) == "hide" for v in name_options[0][1:])
                if not hide_names:
                    sx, sy, rotation = ats[0][1:4]
                    r = math.radians(rotation)
                    for body in children(definition, "symbol"):
                        for pin in children(body, "pin"):
                            names = children(pin, "name")
                            pat = children(pin, "at")
                            lengths = children(pin, "length")
                            if not names or names[0][1] in ("~", "") or not pat or not lengths:
                                continue
                            px, py, angle = pat[0][1:4]
                            a = math.radians(angle)
                            px += (lengths[0][1] + 0.508) * math.cos(a)
                            py += (lengths[0][1] + 0.508) * math.sin(a)
                            # Library Y is up; sheet Y is down, before instance rotation.
                            x = sx + px * math.cos(r) - py * math.sin(r)
                            y = sy - px * math.sin(r) - py * math.cos(r)
                            number = children(pin, "number")[0][1]
                            effective = (angle + rotation) % 360
                            # Pin-name text remains readable at 0/90 degrees.
                            textangle = 0 if effective in (0, 180) else 90
                            justify = "left" if effective in (0, 90) else "right"
                            ef = [
                                sexpdata.Symbol("effects"),
                                [
                                    sexpdata.Symbol("font"),
                                    [sexpdata.Symbol("size"), 1.27, 1.27],
                                ],
                                [sexpdata.Symbol("justify"), sexpdata.Symbol(justify)],
                            ]
                            t = text_item(
                                owner + ":pin:" + str(number),
                                names[0][1],
                                ["at", x, y, textangle],
                                ef,
                                owner,
                                "pin_name",
                            )
                            if t:
                                texts.append(t)
        for i, a in enumerate(texts):
            x1, y1, x2, y2 = a.bounds
            if x1 < 10 or y1 < 8 or x2 > 410 or y2 > 287:
                finding(
                    "text_outside_page",
                    filename,
                    [a.identity],
                    "Text bounds extend outside page margins",
                )
            for b in texts[i + 1 :]:
                if a.owner and a.owner == b.owner and a.kind != "pin_name" and b.kind != "pin_name":
                    continue
                u1, v1, u2, v2 = b.bounds
                if min(x2, u2) - max(x1, u1) > 0.3 and min(y2, v2) - max(y1, v1) > 0.3:
                    finding(
                        "text_collision",
                        filename,
                        [a.identity, b.identity],
                        "Visible text bounds overlap",
                    )
        for text in texts:
            x1, y1, x2, y2 = text.bounds
            for index, wire in enumerate(wires):
                if len(wire) != 2:
                    continue
                (ax, ay), (bx, by) = wire
                # Only orthogonal wire interiors qualify; legal wire crossings are unrelated.
                crosses = (
                    ax == bx and x1 + 0.3 < ax < x2 - 0.3 and min(ay, by) < y2 - 0.3 and max(ay, by) > y1 + 0.3
                ) or (ay == by and y1 + 0.3 < ay < y2 - 0.3 and min(ax, bx) < x2 - 0.3 and max(ax, bx) > x1 + 0.3)
                if crosses:
                    finding(
                        "wire_through_text",
                        filename,
                        [text.identity, "wire:" + str(index)],
                        "Wire intersects visible text bounds",
                    )
        scenes.append(dict(sheet=filename, texts=[asdict(t) for t in texts]))
    for pattern in patterns:
        if pattern["kind"] == "local_decoupling":
            members = pattern["components"]
            sheets = {component_sheets.get(path) for path in members}
            if None in sheets or len(sheets) != 1:
                finding("decoupling_split", "", members,
                        "A verified device and its local bypass capacitors are not on one sheet")
    for d in diagnostics:
        reason = d.reason
        if reason == "no schematic symbol mapping" or reason.startswith("local wire"):
            finding(
                "symbol_fallback" if reason == "no schematic symbol mapping" else "local_wire_fallback",
                "",
                [d.component],
                reason,
            )
    return dict(
        schema=1,
        visual_approval="pending",
        status="findings" if findings else "no_machine_findings",
        findings=findings,
        patterns=list(patterns),
        scenes=scenes,
        limitations=[
            "Text bounds are conservative stroke-font estimates.",
            "Machine evidence cannot establish circuit meaning or visual acceptance.",
        ],
    )
