"""Pure planning of complete functional regions onto KiCad schematic sheets.

Bounds include the region heading, symbols, text and wires. Planning translates
those rectangles without changing components, connectivity, scale or typography.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..core import CompiledDesign
    from .KiCadSchematicExporter import SchematicExportOptions

Bounds = Tuple[float, float, float, float]
USABLE_BOUNDS: Bounds = (20, 40, 395, 265)
OVERVIEW_BOUNDS: Bounds = (20, 205, 395, 265)
GUTTER = 8.0
TITLE_BLOCK_BOUNDS: Bounds = (230, 245, 410, 287)



def natural_order(value: str) -> tuple:
    """Stable human ordering for continuation and array indices."""
    return tuple((1, int(part)) if part.isdecimal() else (0, part)
                 for part in re.split(r"(\d+)", value))


def _continuation_order(sheets, regions, diagnostics):
    """Keep source-region continuations ordered even on mixed-title pages."""
    def key(sheet):
        title = sheet.title.rsplit(" /", 1)
        continuation = int(title[1]) if len(title) == 2 and title[1].isdigit() else 0
        return sheet.scope, sheet.id != "overview", natural_order(title[0]), continuation, sheet.id
    families = {}
    for index, sheet in enumerate(sheets):
        for placement in sheet.regions:
            region = regions[placement.region_id]
            suffix = region.title.rsplit(" /", 1)
            number = int(suffix[1]) if len(suffix) == 2 and suffix[1].isdigit() else 1
            family = suffix[0] if len(suffix) == 2 and suffix[1].isdigit() else region.title
            families.setdefault((sheet.scope, family), []).append((number, index))
            array = re.fullmatch(r"(.*)\[([0-9, ]+)\](.*)", family)
            if array:
                indices = [int(item.strip()) for item in array[2].split(",")]
                array_family = (sheet.scope, "array", array[1], array[3])
                families.setdefault(array_family, []).append((min(indices), index))
    before = {i: set() for i in range(len(sheets))}
    for entries in families.values():
        for first_number, first in entries:
            for second_number, second in entries:
                if first_number < second_number and first != second:
                    before[second].add(first)
    remaining, ordered = set(before), []
    while remaining:
        eligible = [i for i in remaining if not before[i] & remaining]
        if not eligible:
            diagnostics.append("continuation_order_conflict: mixed sheet assignments impose a cycle; retaining stable title order")
            eligible = list(remaining)
        chosen = min(eligible, key=lambda i: key(sheets[i]))
        ordered.append(sheets[chosen]); remaining.remove(chosen)
    return ordered

def _string(value: Any, name: str, allow_empty: bool = False) -> None:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise ValueError(f"{name} must be {'a' if allow_empty else 'a nonempty'} string")


def _number(value: Any, name: str) -> None:
    try:
        valid = not isinstance(value, bool) and isinstance(value, (float, int)) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{name} must be a finite number")


def _bounds(value: Any, name: str) -> None:
    if not isinstance(value, tuple) or len(value) != 4:
        raise ValueError(f"{name} must contain four coordinates")
    for coordinate in value:
        _number(coordinate, name)
    if value[2] <= value[0] or value[3] <= value[1]:
        raise ValueError(f"{name} must have positive width and height")


def _object(value: Any, fields: set, required: set, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    if set(value) - fields or required - set(value):
        raise ValueError(f"{name} has unknown or missing fields")
    return value


def _array(value: Any, name: str) -> Sequence[Any]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be an array")
    return value


@dataclass(frozen=True)
class SchematicRegion:
    id: str
    title: str
    scope: str
    components: Tuple[str, ...]
    bounds: Bounds
    kind: str = "circuit"

    def __post_init__(self) -> None:
        _string(self.id, "region id")
        _string(self.title, "region title")
        _string(self.scope, "region scope", allow_empty=True)
        if not isinstance(self.components, tuple):
            raise ValueError("region components must be a tuple")
        for component in self.components:
            _string(component, "component path")
        if len(set(self.components)) != len(self.components):
            raise ValueError("region has duplicate component paths")
        _bounds(self.bounds, "region bounds")
        if self.kind not in ("circuit", "mechanical", "empty"):
            raise ValueError("region kind must be circuit, mechanical or empty")
        if self.kind == "empty" and self.components:
            raise ValueError("empty region cannot contain physical components")

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict(
            id=self.id, title=self.title, scope=self.scope, components=list(self.components), bounds=list(self.bounds)
        )
        if self.kind != "circuit":
            result["kind"] = self.kind
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SchematicRegion:
        data = _object(
            value,
            {"id", "title", "scope", "components", "bounds", "kind"},
            {"id", "title", "scope", "components", "bounds"},
            "region",
        )
        return cls(
            data["id"],
            data["title"],
            data["scope"],
            tuple(_array(data["components"], "components")),
            tuple(_array(data["bounds"], "bounds")),
            data.get("kind", "circuit"),
        )  # type: ignore[arg-type]


@dataclass(frozen=True)
class SchematicRegionPlacement:
    region_id: str
    x: float
    y: float

    def __post_init__(self) -> None:
        _string(self.region_id, "placement region_id")
        _number(self.x, "placement x")
        _number(self.y, "placement y")

    def to_dict(self) -> Dict[str, Any]:
        return dict(region_id=self.region_id, x=self.x, y=self.y)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SchematicRegionPlacement:
        data = _object(value, {"region_id", "x", "y"}, {"region_id", "x", "y"}, "placement")
        return cls(data["region_id"], data["x"], data["y"])


# Compatibility with the short name used in the initial architecture discussion.
RegionPlacement = SchematicRegionPlacement


@dataclass(frozen=True)
class SchematicSheet:
    id: str
    title: str
    scope: str
    regions: Tuple[SchematicRegionPlacement, ...]

    def __post_init__(self) -> None:
        _string(self.id, "sheet id")
        _string(self.title, "sheet title")
        _string(self.scope, "sheet scope", allow_empty=True)
        if not isinstance(self.regions, tuple) or not all(
            isinstance(v, SchematicRegionPlacement) for v in self.regions
        ):
            raise ValueError("sheet regions must be a tuple of region placements")
        if not self.regions and self.id != "overview":
            raise ValueError("only an overview sheet may be empty")
        if (self.id == "overview") != (self.title == "Overview"):
            raise ValueError("overview sheet id and title must be overview and Overview together")

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            id=self.id, title=self.title, scope=self.scope, regions=[placement.to_dict() for placement in self.regions]
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SchematicSheet:
        data = _object(value, {"id", "title", "scope", "regions"}, {"id", "title", "scope", "regions"}, "sheet")
        return cls(
            data["id"],
            data["title"],
            data["scope"],
            tuple(SchematicRegionPlacement.from_dict(v) for v in _array(data["regions"], "sheet regions")),
        )


def _rect(region: SchematicRegion, placement: SchematicRegionPlacement) -> Bounds:
    return (
        placement.x,
        placement.y,
        placement.x + region.bounds[2] - region.bounds[0],
        placement.y + region.bounds[3] - region.bounds[1],
    )


def _separated(first: Bounds, second: Bounds) -> bool:
    tolerance = 1e-7
    return (
        first[2] + GUTTER <= second[0] + tolerance
        or second[2] + GUTTER <= first[0] + tolerance
        or first[3] + GUTTER <= second[1] + tolerance
        or second[3] + GUTTER <= first[1] + tolerance
    )


def _outside_title_block(rect: Bounds) -> bool:
    return rect[2] <= TITLE_BLOCK_BOUNDS[0] or rect[3] <= TITLE_BLOCK_BOUNDS[1]


def _inside(rect: Bounds, usable: Bounds) -> bool:
    tolerance = 1e-7
    return (
        rect[0] >= usable[0] - tolerance
        and rect[1] >= usable[1] - tolerance
        and rect[2] <= usable[2] + tolerance
        and rect[3] <= usable[3] + tolerance
    )


def _region_map(regions: Tuple[SchematicRegion, ...]) -> Dict[str, SchematicRegion]:
    result: Dict[str, SchematicRegion] = {}
    components = set()
    for region in regions:
        if not isinstance(region, SchematicRegion):
            raise ValueError("regions must contain SchematicRegion objects")
        if region.id in result:
            raise ValueError(f"duplicate region id: {region.id}")
        for path in region.components:
            identity = (region.scope, path)
            if identity in components:
                raise ValueError(f"component belongs to more than one region: {path}")
            components.add(identity)
        result[region.id] = region
    return result


@dataclass(frozen=True)
class SchematicSheetPlan:
    fingerprint: str
    regions: Tuple[SchematicRegion, ...]
    sheets: Tuple[SchematicSheet, ...]
    diagnostics: Tuple[str, ...] = ()
    overview: bool = True

    def __post_init__(self) -> None:
        _string(self.fingerprint, "plan fingerprint")
        if not isinstance(self.regions, tuple) or not isinstance(self.sheets, tuple):
            raise ValueError("plan regions and sheets must be tuples")
        if not isinstance(self.overview, bool):
            raise ValueError("overview must be a boolean")
        if not isinstance(self.diagnostics, tuple) or not all(isinstance(v, str) for v in self.diagnostics):
            raise ValueError("diagnostics must be a tuple of strings")
        regions = _region_map(self.regions)
        sheet_ids = set()
        covered = set()
        scope_sheets: Dict[str, list] = {}
        for sheet in self.sheets:
            if not isinstance(sheet, SchematicSheet):
                raise ValueError("sheets must contain SchematicSheet objects")
            identity = (sheet.scope, sheet.id)
            if identity in sheet_ids:
                raise ValueError(f"duplicate sheet id in scope {sheet.scope}: {sheet.id}")
            sheet_ids.add(identity)
            scope_sheets.setdefault(sheet.scope, []).append(sheet)
            if sheet.id == "overview" and not self.overview:
                raise ValueError("overview sheet conflicts with overview=False")
            occupied = []
            for placement in sheet.regions:
                if placement.region_id not in regions:
                    raise ValueError(f"unknown placement region: {placement.region_id}")
                region = regions[placement.region_id]
                if region.scope != sheet.scope:
                    raise ValueError(f"region cannot move between board scopes: {region.id}")
                if region.id in covered:
                    raise ValueError(f"region placed more than once: {region.id}")
                covered.add(region.id)
                rectangle = _rect(region, placement)
                usable = OVERVIEW_BOUNDS if sheet.id == "overview" else USABLE_BOUNDS
                if not _inside(rectangle, usable) or not _outside_title_block(rectangle):
                    raise ValueError(f"region outside usable sheet bounds: {region.id}")
                if any(not _separated(rectangle, previous) for previous in occupied):
                    raise ValueError(f"region overlap or insufficient {GUTTER:g} mm gutter: {region.id}")
                occupied.append(rectangle)
        if covered != set(regions):
            raise ValueError(
                "plan must place every region exactly once; missing: " + ", ".join(sorted(set(regions) - covered))
            )
        if self.overview:
            for scope, sheets in scope_sheets.items():
                if (
                    len([sheet for sheet in sheets if sheet.id != "overview"]) > 1
                    and (scope, "overview") not in sheet_ids
                ):
                    raise ValueError(f"multiple content sheets require an overview in scope {scope}")

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            fingerprint=self.fingerprint,
            regions=[region.to_dict() for region in self.regions],
            sheets=[sheet.to_dict() for sheet in self.sheets],
            diagnostics=list(self.diagnostics),
            overview=self.overview,
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SchematicSheetPlan:
        data = _object(
            value,
            {"fingerprint", "regions", "sheets", "diagnostics", "overview"},
            {"fingerprint", "regions", "sheets"},
            "plan",
        )
        return cls(
            data["fingerprint"],
            tuple(SchematicRegion.from_dict(v) for v in _array(data["regions"], "regions")),
            tuple(SchematicSheet.from_dict(v) for v in _array(data["sheets"], "sheets")),
            tuple(_array(data.get("diagnostics", []), "diagnostics")),
            data.get("overview", True),
        )


class SchematicSheetPlanner:
    def plan(self, compiled: CompiledDesign, options: SchematicExportOptions) -> SchematicSheetPlan:
        from .KiCadSchematicExporter import KiCadSchematicExporter

        # Share the exporter's prepared regions and non-rail adjacency weights.
        # A planning preview must be identical to the plan used for export.
        return KiCadSchematicExporter()._plan_compiled(compiled, options)

    @staticmethod
    def _assignments(
        regions: Mapping[str, SchematicRegion], assignments: Optional[Mapping[str, str]]
    ) -> Dict[str, str]:
        if assignments is not None and not isinstance(assignments, Mapping):
            raise ValueError("sheet assignments must be an object")
        titles: Dict[str, list] = {}
        for region in regions.values():
            titles.setdefault(region.title, []).append(region.id)
        result: Dict[str, str] = {}
        for reference, title in (assignments or {}).items():
            _string(reference, "assignment region reference")
            _string(title, "assignment sheet title")
            if reference in regions:
                identity = reference
            elif reference not in titles:
                raise ValueError(f"unknown assignment region: {reference}")
            elif len(titles[reference]) != 1:
                raise ValueError(f"ambiguous assignment region title: {reference}; use a canonical region id")
            else:
                identity = titles[reference][0]
            if identity in result and result[identity] != title:
                raise ValueError(f"conflicting assignments for region {identity}")
            result[identity] = title
        for region in regions.values():
            if region.kind == "mechanical" and region.id not in result:
                result[region.id] = "Overview"
        return result

    @staticmethod
    def _adjacency(
        regions: Mapping[str, SchematicRegion], adjacency: Optional[Mapping[Tuple[str, str], float]]
    ) -> Dict[Tuple[str, str], float]:
        if adjacency is not None and not isinstance(adjacency, Mapping):
            raise ValueError("adjacency must map region-id pairs to weights")
        result: Dict[Tuple[str, str], float] = {}
        for pair, weight in (adjacency or {}).items():
            if not isinstance(pair, tuple) or len(pair) != 2 or not all(v in regions for v in pair):
                raise ValueError(f"unknown or invalid adjacency pair: {pair}")
            _number(weight, "adjacency weight")
            if weight < 0:
                raise ValueError("adjacency weight cannot be negative")
            if pair[0] == pair[1] or weight == 0:
                continue
            key = tuple(sorted(pair))
            if key in result and result[key] != weight:
                raise ValueError(f"conflicting adjacency weights: {pair}")
            result[key] = float(weight)
        return result

    @staticmethod
    def _position(
        region: SchematicRegion, occupied: Sequence[Bounds], usable: Bounds
    ) -> Optional[SchematicRegionPlacement]:
        xs = sorted({usable[0]} | {rect[2] + GUTTER for rect in occupied})
        ys = sorted({usable[1]} | {rect[3] + GUTTER for rect in occupied})
        for y in ys:
            for x in xs:
                candidate = SchematicRegionPlacement(region.id, x, y)
                rectangle = _rect(region, candidate)
                if (
                    _inside(rectangle, usable)
                    and _outside_title_block(rectangle)
                    and all(_separated(rectangle, other) for other in occupied)
                ):
                    return candidate
        return None

    def plan_regions(
        self,
        regions: Sequence[SchematicRegion],
        fingerprint: str,
        *,
        assignments: Optional[Mapping[str, str]] = None,
        requested: Optional[Union[SchematicSheetPlan, Mapping[str, Any]]] = None,
        overview: bool = True,
        adjacency: Optional[Mapping[Tuple[str, str], float]] = None,
    ) -> SchematicSheetPlan:
        _string(fingerprint, "fingerprint")
        if not isinstance(overview, bool):
            raise ValueError("overview must be boolean")
        if not isinstance(regions, Sequence) or not all(isinstance(region, SchematicRegion) for region in regions):
            raise ValueError("regions must be a sequence of SchematicRegion objects")
        prepared = tuple(sorted(regions, key=lambda region: region.id))
        by_id = _region_map(prepared)
        assigned = self._assignments(by_id, assignments)
        edges = self._adjacency(by_id, adjacency)
        if requested is not None:
            adopted = (
                requested if isinstance(requested, SchematicSheetPlan) else SchematicSheetPlan.from_dict(requested)
            )
            if adopted.fingerprint != fingerprint:
                raise ValueError(
                    "stale sheet plan fingerprint; regenerate the plan for this compiled design and geometry"
                )
            supplied = {region.id: region for region in adopted.regions}
            if set(supplied) != set(by_id):
                raise ValueError("requested plan regions differ from prepared regions")
            for identity, region in by_id.items():
                other = supplied[identity]
                if (region.title, region.scope, region.kind, region.bounds, set(region.components)) != (
                    other.title,
                    other.scope,
                    other.kind,
                    other.bounds,
                    set(other.components),
                ):
                    raise ValueError(f"requested region bounds or membership changed: {identity}")
            for sheet in adopted.sheets:
                for placement in sheet.regions:
                    title = assigned.get(placement.region_id)
                    if title is not None and not self._title_matches(sheet.title, title):
                        raise ValueError(f"requested plan conflicts with sheet assignment: {placement.region_id}")
                    if title == "Overview" and sheet.id != "overview":
                        raise ValueError("Overview assignment must use sheet id overview")
            return SchematicSheetPlan(
                fingerprint,
                prepared,
                adopted.sheets,
                self._diagnostics(prepared, adopted.sheets, edges, adopted.diagnostics, measured=adjacency is not None),
                adopted.overview,
            )

        groups: Dict[Tuple[str, Optional[str]], list] = {}
        for region in prepared:
            groups.setdefault((region.scope, assigned.get(region.id)), []).append(region)
        sheets = []
        diagnostics = []
        for (scope, title), members in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1] or "")):
            if title == "Overview" and not overview:
                raise ValueError("Overview assignment requires overview=True")
            usable = OVERVIEW_BOUNDS if title == "Overview" else USABLE_BOUNDS
            pages: list = []
            ordered = sorted(
                members,
                key=lambda r: (
                    -(r.bounds[2] - r.bounds[0]) * (r.bounds[3] - r.bounds[1]),
                    -max(r.bounds[2] - r.bounds[0], r.bounds[3] - r.bounds[1]),
                    r.id,
                ),
            )
            # Keep signal neighbours contiguous in the packing order, rather than
            # letting unrelated large rectangles consume their available space.
            # Adjacency is measured upstream with common rails excluded.
            remaining = list(ordered)
            ordered = []
            while remaining:
                if not ordered:
                    chosen = remaining[0]
                else:
                    previous = ordered[-1]
                    chosen = min(
                        remaining,
                        key=lambda r: (
                            -edges.get(tuple(sorted((previous.id, r.id))), 0),
                            -(previous.title.split(" /")[0] == r.title.split(" /")[0]),
                            remaining.index(r),
                        ),
                    )
                remaining.remove(chosen)
                ordered.append(chosen)
            for region in ordered:
                if self._position(region, (), usable) is None:
                    width = region.bounds[2] - region.bounds[0]
                    height = region.bounds[3] - region.bounds[1]
                    raise ValueError(
                        f"region {region.id} ({width:g} x {height:g} mm) exceeds usable "
                        f"{'overview inset' if title == 'Overview' else 'A3 sheet'}; "
                        "partition it into whole functional continuation regions before planning; no content was cropped"
                    )
                candidates = []
                for index, placements in enumerate(pages):
                    occupied = [_rect(by_id[p.region_id], p) for p in placements]
                    placement = self._position(region, occupied, usable)
                    if placement is not None:
                        colocated = {p.region_id for p in placements}
                        inside = sum(
                            weight
                            for pair, weight in edges.items()
                            if region.id in pair and (set(pair) - {region.id}).issubset(colocated)
                        )
                        placed_elsewhere = {p.region_id for page in pages for p in page} - colocated
                        crossing = sum(
                            weight
                            for pair, weight in edges.items()
                            if region.id in pair and bool((set(pair) - {region.id}) & placed_elsewhere)
                        )
                        family = region.title.split(" /")[0]
                        siblings = sum(by_id[p.region_id].title.split(" /")[0] == family for p in placements)
                        candidates.append(((-inside, -siblings, crossing, placement.y, placement.x, index), index, placement))
                if candidates:
                    _, index, placement = min(candidates, key=lambda candidate: candidate[0])
                    pages[index].append(placement)
                else:
                    if title == "Overview" and pages:
                        raise ValueError(
                            "explicit Overview regions do not fit the reserved lower inset; revise their grouping or geometry"
                        )
                    pages.append([self._position(region, (), usable)])
            # Continuation numbers are local to a functional title. A single
            # Control page must not become /17 because sixteen other pages exist.
            pages.sort(key=lambda placements: min(
                (natural_order(by_id[p.region_id].title), by_id[p.region_id].id) for p in placements))
            bases = []
            for placements in pages:
                if title is not None:
                    bases.append(title)
                else:
                    labels = sorted(set(by_id[p.region_id].title.split(" /")[0] for p in placements))
                    base = " + ".join(labels[:2]) + (" + others" if len(labels) > 2 else "")
                    bases.append(base[:60])
            totals, counts = Counter(bases), Counter()
            for index, placements in enumerate(pages):
                if title == "Overview":
                    sheet_id, sheet_title = "overview", "Overview"
                else:
                    base = bases[index]
                    counts[base] += 1
                    sheet_title = base if totals[base] == 1 else f"{base} /{counts[base]}"
                    token = json.dumps([scope, title, sorted(p.region_id for p in placements)], ensure_ascii=False).encode("utf-8")
                    sheet_id = "sheet_" + hashlib.sha256(token).hexdigest()[:16]
                    if title is not None and counts[base] > 1:
                        diagnostics.append(
                            f"continuation: explicit sheet {title!r} in scope {scope!r} continues as {sheet_title!r}"
                        )
                sheets.append(SchematicSheet(sheet_id, sheet_title, scope, tuple(placements)))
        scopes = sorted({region.scope for region in prepared})
        if not scopes and overview:
            sheets.append(SchematicSheet("overview", "Overview", "", ()))
        for scope in scopes:
            content = [sheet for sheet in sheets if sheet.scope == scope and sheet.id != "overview"]
            if overview and len(content) > 1 and not any(s.scope == scope and s.id == "overview" for s in sheets):
                sheets.append(SchematicSheet("overview", "Overview", scope, ()))
        sheets = _continuation_order(sheets, by_id, diagnostics)
        return SchematicSheetPlan(
            fingerprint,
            prepared,
            tuple(sheets),
            self._diagnostics(prepared, tuple(sheets), edges, tuple(diagnostics), measured=adjacency is not None),
            overview,
        )

    @staticmethod
    def _title_matches(actual: str, assigned: str) -> bool:
        if actual == assigned:
            return True
        prefix = assigned + " /"
        return actual.startswith(prefix) and actual[len(prefix) :].isdigit() and int(actual[len(prefix) :]) >= 1

    @staticmethod
    def _diagnostics(
        regions: Tuple[SchematicRegion, ...],
        sheets: Tuple[SchematicSheet, ...],
        adjacency: Mapping[Tuple[str, str], float],
        initial: Tuple[str, ...],
        *,
        measured: bool,
    ) -> Tuple[str, ...]:
        generated = ("sparse_sheet:", "tiny_sheet:", "cross_sheet_connections:", "region_continuation:")
        result = [note for note in initial if not note.startswith(generated)]
        by_id = {region.id: region for region in regions}
        location = {p.region_id: (sheet.scope, sheet.id) for sheet in sheets for p in sheet.regions}
        for region in regions:
            suffix = region.title.rsplit(" /", 1)
            if len(suffix) == 2 and suffix[1].isdigit() and int(suffix[1]) >= 2:
                result.append(
                    f"region_continuation: prepared region {region.id!r} retains whole functional continuation {region.title!r}"
                )
        for sheet in sheets:
            if sheet.id == "overview":
                continue
            area = sum(
                (by_id[p.region_id].bounds[2] - by_id[p.region_id].bounds[0])
                * (by_id[p.region_id].bounds[3] - by_id[p.region_id].bounds[1])
                for p in sheet.regions
            )
            fraction = area / ((USABLE_BOUNDS[2] - USABLE_BOUNDS[0]) * (USABLE_BOUNDS[3] - USABLE_BOUNDS[1]))
            if fraction < 0.25:
                result.append(
                    f"sparse_sheet: {sheet.title!r} in scope {sheet.scope!r} uses {fraction:.1%} of its usable region area"
                )
            component_count = sum(len(by_id[p.region_id].components) for p in sheet.regions)
            if component_count <= 2:
                result.append(
                    f"tiny_sheet: {sheet.title!r} in scope {sheet.scope!r} contains {component_count} physical components"
                )
        crossing = sum(
            weight
            for pair, weight in adjacency.items()
            if by_id[pair[0]].scope == by_id[pair[1]].scope and location[pair[0]] != location[pair[1]]
        )
        if measured:
            result.append(
                f"cross_sheet_connections: {crossing:g} weighted region connections (not an electrical or visual acceptance result)"
            )
        else:
            result.append("cross_sheet_connections: not measured (no adjacency supplied)")
        return tuple(dict.fromkeys(result))


KiCadSchematicPlanner = SchematicSheetPlanner
