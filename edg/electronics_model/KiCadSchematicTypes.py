"""Internal geometry types shared by native schematic passes.

S-expressions remain heterogeneous at the sexpdata parsing boundary. Physical
identity and routing geometry have concrete types independent of serialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .KiCadSchematicExporter import PhysicalComponent

SExpr = list[Any]
Point = tuple[float, float]
GridPoint = tuple[int, int]
Bounds = tuple[float, float, float, float]
PinKey = tuple[str, str]
PinNets = Mapping[PinKey, str]
Wire = tuple[str, Point, Point]
Placement = tuple["PhysicalComponent", float, float, int]
Placements = Sequence[Placement]
Views = Mapping[str, "SymbolView"]
Escape = tuple[float, float, float, float, float]
RouteResult = tuple[list[Wire], dict[PinKey, Escape], list[tuple[PinKey, str]]]


@dataclass
class SymbolView:
    definition: SExpr
    pins: list[tuple[str, float, float, float]]
    lib_id: str


class PinTextItem(TypedDict):
    identity: str
    text: str
    owner: str
    kind: str
    bounds: Bounds
