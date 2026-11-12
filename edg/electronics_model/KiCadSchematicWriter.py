"""KiCad schematic S-expression construction and electrical wire serialization."""

import json
import uuid
from typing import Any, Sequence

import sexpdata

from .KiCadSchematicTypes import Point, SExpr, Wire

S = sexpdata.Symbol


def node(name: str, *args: Any) -> SExpr:
    return [S(name), *args]


def children(tree: SExpr, name: str) -> list[SExpr]:
    return [v for v in tree if isinstance(v, list) and v and v[0] == S(name)]


def uid(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(parts, ensure_ascii=False)))


def effects(size: float = 1.27, hide: bool = False) -> SExpr:
    return node(
        "effects",
        node("font", node("size", size, size)),
        *([S("hide")] if hide else []),
    )


def write_wires(doc: SExpr, all_segments: Sequence[Wire], sheet_id: str, region_id: str) -> None:
    """Split orthogonal wires at endpoints and emit junctions with stable identities."""
    for net in sorted({n for n, _, _ in all_segments}):
        segments = [(a, b) for n, a, b in all_segments if n == net and a != b]
        candidates = {p for pair in segments for p in pair}
        edges: set[tuple[Point, Point]] = set()
        for a, b in segments:
            cuts = [
                p
                for p in candidates
                if (a[0] == b[0] == p[0] and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))
                or (a[1] == b[1] == p[1] and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]))
            ]
            cuts.sort()
            edges.update((u, v) for u, v in zip(cuts, cuts[1:]) if u != v)
        degrees: dict[Point, int] = {}
        for a, b in sorted(edges):
            for p in (a, b):
                degrees[p] = degrees.get(p, 0) + 1
            doc.append(
                node(
                    "wire",
                    node("pts", node("xy", *a), node("xy", *b)),
                    node("stroke", node("width", 0), node("type", S("default"))),
                    node(
                        "uuid",
                        uid(sheet_id, region_id, net, str(a), str(b), "wire"),
                    ),
                )
            )
        for p, degree in sorted(degrees.items()):
            if degree >= 3:
                doc.append(
                    node(
                        "junction",
                        node("at", *p),
                        node("diameter", 0),
                        node("color", 0, 0, 0, 0),
                        node(
                            "uuid",
                            uid(sheet_id, region_id, net, str(p), "junction"),
                        ),
                    )
                )
