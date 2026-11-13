"""Single-instance symbols for verified packed passive networks.

The physical pin inventory remains authoritative. Branch pairing comes from the
ResistorArray model's a[index]/b[index] exports, never physical pad ordering.
"""

from __future__ import annotations

import re
from typing import Any, Optional, Sequence, Tuple, TYPE_CHECKING
from .KiCadSchematicTypes import SExpr

if TYPE_CHECKING:
    from .KiCadSchematicExporter import PhysicalComponent

from sexpdata import Symbol as S

RESISTOR_ARRAY_CLASSES = {
    "edg.vendor_parts.jlc.JlcResistorArray.JlcResistorArray",
}


def resistor_array_symbol(
    component: PhysicalComponent, class_names: Sequence[str]
) -> Optional[Tuple[SExpr, list[tuple[str, float, float, float]], str]]:
    if not class_names or class_names[-1].removeprefix("PolymorphicBlocks.") not in RESISTOR_ARRAY_CLASSES:
        return None
    pairs: dict[str, dict[str, str]] = {}
    for number, role in component.pins.items():
        match = re.fullmatch(r"([ab])\.(\d+)(?:\.net)?", role)
        if match is None:
            return None
        side, index = match.groups()
        if side in pairs.setdefault(index, {}):
            return None
        pairs[index][side] = number
    if not pairs or any(set(pair) != {"a", "b"} for pair in pairs.values()):
        return None

    # Use inventory and branch pairing in the identity, independent of position.
    import hashlib
    import json

    pin_names = (getattr(component, "mapping", None) or {}).get("pin_names", {})
    identity = {"pairs": pairs, "pin_names": pin_names} if pin_names else pairs
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
    lib_id = "PB:ResistorArray_" + digest
    body: SExpr = [S("symbol"), lib_id.split(":", 1)[1] + "_1_1"]
    positions: list[tuple[str, float, float, float]] = []
    for row, index in enumerate(sorted(pairs, key=int)):
        y = round((row - (len(pairs) - 1) / 2) * 7.62, 4)
        body.append(
            [
                S("rectangle"),
                [S("start"), -2.54, -y + 1.016],
                [S("end"), 2.54, -y - 1.016],
                [S("stroke"), [S("width"), 0.254], [S("type"), S("default")]],
                [S("fill"), [S("type"), S("none")]],
            ]
        )
        for side, x, angle in (("a", -7.62, 0), ("b", 7.62, 180)):
            number = pairs[index][side]
            body.append(
                [
                    S("pin"),
                    S("passive"),
                    S("line"),
                    [S("at"), x, -y, angle],
                    [S("length"), 5.08],
                    [
                        S("name"),
                        "~",
                        [S("effects"), [S("font"), [S("size"), 1.0, 1.0]]],
                    ],
                    [
                        S("number"),
                        number,
                        [S("effects"), [S("font"), [S("size"), 1.0, 1.0]]],
                    ],
                ]
            )
            positions.append((number, x, y, angle))
    definition: SExpr = [
        S("symbol"),
        lib_id,
        [S("pin_names"), [S("offset"), 0]],
        [S("in_bom"), S("yes")],
        [S("on_board"), S("yes")],
        body,
    ]
    return definition, positions, lib_id
