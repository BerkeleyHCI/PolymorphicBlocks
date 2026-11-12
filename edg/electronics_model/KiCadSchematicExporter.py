"""Deterministic, one-way schematic views of compiled PB physical connectivity."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import shutil
import tempfile
import textwrap
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, TYPE_CHECKING, cast

import sexpdata
from .KiCadSchematicWriter import (
    S as S,
    children as children,
    effects as effects,
    node as node,
    uid as uid,
    write_wires,
)
from .KiCadSymbolRegistry import infer_symbol
from .KiCadSchematicRoles import infer_pin_names, infer_description
from .KiCadCompositeSymbols import resistor_array_symbol
from .KiCadSchematicTypes import SymbolView as SymbolView
from .KiCadSchematicTypes import SExpr, Bounds, Point, PinKey, Wire, Placement, Placements, Views, PinNets, RouteResult

if TYPE_CHECKING:
    from .KiCadSchematicCircuits import SchematicCircuit, SchematicCircuitModel
    from _hashlib import HASH
    from ..core.Range import Range

from ..core import CompiledDesign
from .NetlistGenerator import NetlistTransform, NetBlock
from .KiCadSchematicPlanner import (
    SchematicRegion,
    SchematicRegionPlacement,
    SchematicSheet,
    SchematicSheetPlan,
    SchematicSheetPlanner,
    region_fits_page,
)
from .KiCadSchematicPresentation import SchematicPresentation
from .KiCadSchematicOverview import SchematicOverview, build_overviews, render_overview
from .KiCadSchematicScene import pin_label_bounds, text_width
from .KiCadSchematicLayout import (
    annotation_position,
    annotation_bounds,
    freeze_annotations,
    ground_bounds,
    ground_label_position,
    ground_rotation,
    graphic_bounds,
    pins as positioned_pins,
    place_group,
    regroup,
    route_local,
    split_group,
)

NOTICE = "GENERATED FROM POLYMORPHICBLOCKS PYTHON — SOURCE OF TRUTH"
INSTRUCTIONS = "Edit the PB Python source and regenerate. Schematic edits will be overwritten."
VERSION = "8"


@dataclass(frozen=True)
class SchematicPlacement:
    """Optional Python-owned functional schematic placement, in millimetres."""

    group: str
    x: float
    y: float
    rotation: int = 0
    flip_horizontal: bool = False
    annotation: Optional[Tuple[float, float]] = None
    lock_rotation: bool = True

    def __post_init__(self) -> None:
        if type(self.lock_rotation) is not bool:
            raise ValueError("lock_rotation must be a boolean")


@dataclass(frozen=True)
class SchematicExportOptions:
    design_name: str
    source: str = ""
    symbol_library_dirs: Tuple[str, ...] = ()
    kicad_major: int = 9
    placements: Mapping[str, SchematicPlacement] = field(default_factory=dict)
    sheet_assignments: Mapping[str, str] = field(default_factory=dict)
    sheet_plan: Optional[SchematicSheetPlan] = None
    overview: Optional[SchematicOverview] = None
    presentation: Optional[SchematicPresentation] = None
    ground_style: str = "bars"
    optimize_routes: bool = True
    optimize_orientations: bool = True
    orientation_mode: str = "half_turn"

    def __post_init__(self) -> None:
        if self.orientation_mode not in ("half_turn", "passive_quarter_turn"):
            raise ValueError("orientation_mode must be half_turn or passive_quarter_turn")
        if type(self.optimize_orientations) is not bool:
            raise ValueError("optimize_orientations must be a boolean")
        if type(self.optimize_routes) is not bool:
            raise ValueError("optimize_routes must be a boolean")
        if self.ground_style not in ("bars", "triangle"):
            raise ValueError("ground_style must be bars or triangle")


def ground_symbol(resolver: SymbolResolver, style: str) -> SExpr:
    """Change only ground graphics, retaining the original power-net semantics.

    Do not substitute Earth/GNDREF: those are different electrical net names in
    some supported KiCad versions. Both styles fit the router's ground bounds.
    """
    definition = copy.deepcopy(resolver.load("power:GND"))
    if style == "bars":
        body = next(body for body in children(definition, "symbol") if body[1].endswith("_0_1"))
        body[:] = body[:2]
        for a, b in (
            ((0, 0), (0, -1.27)),
            ((-1.27, -1.27), (1.27, -1.27)),
            ((-0.635, -1.905), (0.635, -1.905)),
            ((-0.127, -2.54), (0.127, -2.54)),
        ):
            body.append(
                node(
                    "polyline",
                    node("pts", node("xy", *a), node("xy", *b)),
                    node("stroke", node("width", 0), node("type", S("default"))),
                    node("fill", node("type", S("none"))),
                )
            )
    return definition


@dataclass(frozen=True)
class SchematicDiagnostic:
    component: str
    reason: str


@dataclass
class SchematicExport:
    files: Dict[str, str]
    diagnostics: List[SchematicDiagnostic]

    def write(self, directory: Path) -> None:
        """Stage all files first; clean only stale files owned by our previous manifest."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        old = directory / "manifest.json"
        previous = json.loads(old.read_text(encoding="utf-8")).get("files", []) if old.exists() else []
        for name in list(self.files) + previous:
            if Path(name).name != name or name in (".", ".."):
                raise ValueError("unsafe generated filename")
        # Roll back ordinary I/O failures, not process termination or power loss.
        # Keep recovery files if rollback itself fails.
        stage = Path(tempfile.mkdtemp(prefix=".schematic-recovery-", dir=directory))
        changed: List[str] = []
        retain_recovery = False
        try:
            incoming, backup = stage / "incoming", stage / "backup"
            incoming.mkdir()
            backup.mkdir()
            for name, content in self.files.items():
                (incoming / name).write_text(content, encoding="utf-8")
            for name in sorted(set(self.files) | set(previous)):
                destination = directory / name
                if destination.is_symlink() or destination.exists():
                    if destination.is_dir() and not destination.is_symlink():
                        raise ValueError("generated file destination is a directory: " + name)
                    shutil.copy2(destination, backup / name, follow_symlinks=False)
            try:
                for name in sorted(n for n in self.files if n != "manifest.json"):
                    os.replace(incoming / name, directory / name)
                    changed.append(name)
                for name in sorted(set(previous) - set(self.files)):
                    destination = directory / name
                    if destination.exists() or destination.is_symlink():
                        destination.unlink()
                        changed.append(name)
                # Publish ownership only after replacements and cleanup succeed.
                if "manifest.json" in self.files:
                    os.replace(incoming / "manifest.json", directory / "manifest.json")
                    changed.append("manifest.json")
            except BaseException as error:
                failures = []
                for name in reversed(changed):
                    try:
                        saved = backup / name
                        if saved.exists() or saved.is_symlink():
                            os.replace(saved, directory / name)
                        else:
                            (directory / name).unlink(missing_ok=True)
                    except OSError as rollback_error:
                        failures.append(f"{name}: {rollback_error}")
                if failures:
                    retain_recovery = True
                    raise RuntimeError(
                        f"schematic write failed and rollback was incomplete; recovery files retained at {stage}: "
                        + "; ".join(failures)
                    ) from error
                raise
        finally:
            if not retain_recovery:
                shutil.rmtree(stage, ignore_errors=True)


@dataclass
class PhysicalComponent:
    path: str
    refdes: str
    footprint: str
    value: str
    pins: Dict[str, str]
    mapping: Optional[dict[str, Any]]
    group: str
    display_value: str = ""
    annotation: Optional[Tuple[float, float]] = None
    descriptions: Tuple[str, ...] = ()
    net_labels: Mapping[str, str] = field(default_factory=dict)
    hierarchy: Tuple[Tuple[str, str], ...] = ()
    ground_net_labels: Mapping[str, str] = field(default_factory=dict)
    symbol_coverage: Dict[str, Any] = field(default_factory=dict)
    # These are attached by later passes, not constructor/dataclass fields.
    if TYPE_CHECKING:
        presentation_pin_roles: dict[str, str] = field(init=False)
        circuit_model: SchematicCircuitModel = field(init=False)
        functional_circuit: Optional[SchematicCircuit] = field(init=False)
        placement_evidence: dict[str, Any] = field(init=False)
        functional_continuation: dict[str, Any] = field(init=False)


class SymbolResolver:
    def __init__(self, directories: Sequence[str]) -> None:
        self.directories = directories
        self.libraries: Dict[str, dict[str, SExpr]] = {}

    def load(self, lib_id: str, stack: Tuple[str, ...] = ()) -> SExpr:
        if lib_id in stack:
            raise ValueError("cyclic symbol inheritance")
        library, symbol = lib_id.split(":", 1)
        if library not in self.libraries:
            filename = next(
                (
                    Path(d, library + ".kicad_sym")
                    for d in self.directories
                    if Path(d, library + ".kicad_sym").is_file()
                ),
                None,
            )
            if filename is None:
                raise FileNotFoundError(lib_id)
            tree = sexpdata.loads(filename.read_text(encoding="utf-8"))
            self.libraries[library] = {v[1]: v for v in children(tree, "symbol")}
        result = copy.deepcopy(self.libraries[library][symbol])
        parent = children(result, "extends")
        if parent:
            base = self.load(library + ":" + parent[0][1], stack + (lib_id,))
            overridden = {v[1] for v in children(result, "property")}
            inherited = [
                v for v in base[2:] if not (isinstance(v, list) and v and v[0] == S("property") and v[1] in overridden)
            ]
            result = result[:2] + inherited + [v for v in result[2:] if v not in parent]
        result[1] = lib_id
        for sub in children(result, "symbol"):
            suffix = re.search(r"_(\d+_\d+)$", sub[1])
            if suffix:
                sub[1] = symbol + "_" + suffix[1]
        return result

    def resolve(self, component: PhysicalComponent) -> SymbolView:
        mapping = component.mapping
        if mapping is None:
            raise LookupError("no schematic symbol mapping")
        definition = self.load(mapping["lib_id"])
        pins = []
        observed = set()
        for sub in children(definition, "symbol"):
            match = re.search(r"_(\d+)_(\d+)$", sub[1])
            if match and int(match[1]) > 1:
                raise LookupError("multi-unit symbol unsupported")
            if match and int(match[2]) > 1:
                continue  # alternate body style
            for pin in children(sub, "pin"):
                number = str(children(pin, "number")[0][1])
                if number not in mapping["pinning"]:
                    if mapping.get("_omit_unmodeled"):
                        sub.remove(pin)
                        continue
                    raise ValueError("unmapped library pin " + number)
                observed.add(number)
                physical = mapping["pinning"][number]
                if physical not in component.pins:
                    raise ValueError("symbol maps to unknown physical pin " + physical)
                children(pin, "number")[0][1] = physical
                at = children(pin, "at")[0]
                pins.append((physical, float(at[1]), -float(at[2]), float(at[3])))
        if observed != set(mapping["pinning"]) or set(component.pins) != set(mapping["pinning"].values()):
            raise ValueError("symbol mapping must cover the modeled physical pins exactly")
        if len({p[0] for p in pins}) != len(pins):
            raise LookupError("stacked or repeated symbol pins unsupported")
        export_id = mapping["lib_id"] + "_PB_" + uid(json.dumps(mapping, sort_keys=True))[:8]
        definition[1] = export_id
        # Vendor libraries may target KiCad10; these library flags are not part
        # of the KiCad9 embedded-symbol grammar and do not affect our pin graph.
        definition[:] = [
            v
            for v in definition
            if not (
                isinstance(v, list)
                and v
                and str(v[0])
                in (
                    "in_pos_files",
                    "duplicate_pin_numbers_are_jumpers",
                    "embedded_fonts",
                )
            )
        ]
        for sub in children(definition, "symbol"):
            match = re.search(r"_(\d+_\d+)$", sub[1])
            if match:
                sub[1] = export_id.split(":", 1)[1] + "_" + match[1]
        # Remove alternate bodies excluded from the selected pin geometry.
        definition[:] = [
            v
            for v in definition
            if not (isinstance(v, list) and v and v[0] == S("symbol") and re.search(r"_\d+_[2-9]$", str(v[1])))
        ]
        return SymbolView(definition, pins, export_id)


def generic(component: PhysicalComponent) -> SymbolView:
    """Functional IC view when no exact library definition is available.

    Pin numbers and electrical inventory remain the PB physical mapping. Only
    graphical grouping uses logical roles; no missing vendor pins are invented.
    """
    lib_id = "PB:" + uid(component.path)
    sides: dict[str, list[tuple[str, str]]] = {"left": [], "right": [], "top": [], "bottom": []}
    declared_names = (component.mapping or {}).get("pin_names", {})
    declared_roles = getattr(component, "presentation_pin_roles", {})
    display_pins = {number: declared_names.get(number, name) for number, name in component.pins.items()}
    for number, name in sorted(display_pins.items()):
        role = name.removesuffix(".net").lower()
        if number in declared_roles:
            side = {
                "input": "left",
                "output": "right",
                "supply": "top",
                "return": "bottom",
                "control": "left",
                "feedback": "left",
                "bidirectional": "right",
            }[declared_roles[number]]
        elif role in ("gnd", "vss", "com"):
            side = "bottom"
        elif role in ("pwr", "vdd", "vcc", "vs", "vddio"):
            side = "top"
        elif role.startswith(("out", "vout", "bat", "chrg", "alrt", "alert", "int", "dout")) or re.fullmatch(
            r"(?:gate|sw|boot|cboot|bst|btst|hidrv|lodrv|tgup|tgdn|gh|gl)\d*", role
        ):
            # Declared gate-drive/switch ports face the adjacent power stage.
            # This changes graphics only, never pin numbers or connectivity.
            side = "right"
        else:
            side = "left"
        sides[side].append((number, name.removesuffix(".net")))
    if len(display_pins) == 2:
        entries = sorted(display_pins.items())
        sides = {"left": [entries[0]], "right": [entries[1]], "top": [], "bottom": []}
    if len(sides["left"]) > 8 and not sides["right"]:
        midpoint = (len(sides["left"]) + 1) // 2
        sides["right"] = sides["left"][midpoint:]
        sides["left"] = sides["left"][:midpoint]
    rows = max(len(sides["left"]), len(sides["right"]), 2)
    # Dense fallback ICs must leave room for native global-label outlines and
    # pin text. Physical pin inventory is unchanged; only the drawing grows.
    side_pitch = 3.81
    rail_pitch = 5.08
    rail_name_depth = max([text_width(name, 1.27) for _, name in sides["top"] + sides["bottom"]] + [0])
    half_height = (rows + 1) * side_pitch / 2 + max(0, rail_name_depth + 2.54 - side_pitch)
    half_width = max(
        10.16,
        max([text_width(v.removesuffix(".net"), 1.27) for v in display_pins.values()] + [1]) + 5.08,
        max(len(sides["top"]), len(sides["bottom"])) * rail_pitch / 2 + 2.54,
    )
    body = node(
        "symbol",
        lib_id.split(":")[1] + "_0_1",
        node(
            "rectangle",
            node("start", -half_width, half_height),
            node("end", half_width, -half_height),
            node("stroke", node("width", 0), node("type", S("default"))),
            node("fill", node("type", S("background"))),
        ),
    )
    positions: list[tuple[str, float, float, float]] = []
    for side, entries in sides.items():
        for i, (number, name) in enumerate(entries):
            offset = (i - (len(entries) - 1) / 2) * (side_pitch if side in ("left", "right") else rail_pitch)
            if side == "left":
                x, y, angle = -half_width - 2.54, offset, 0
            elif side == "right":
                x, y, angle = half_width + 2.54, offset, 180
            elif side == "top":
                x, y, angle = offset, -half_height - 2.54, 270
            else:
                x, y, angle = offset, half_height + 2.54, 90
            body.append(
                node(
                    "pin",
                    S("passive"),
                    S("line"),
                    node("at", x, -y, angle),
                    node("length", 2.54),
                    node("name", name, effects()),
                    node("number", number, effects()),
                )
            )
            positions.append((number, x, y, angle))
    return SymbolView(
        node("symbol", lib_id, node("in_bom", S("yes")), node("on_board", S("yes")), body),
        positions,
        lib_id,
    )


@dataclass
class _RegionDrawing:
    spec: SchematicRegion
    placed: list[Placement]
    wires: list[Wire]
    failed_routes: list[tuple[PinKey, str]]
    routing: dict[str, Any] = field(default_factory=dict)
    heading_positions: tuple[tuple[str, float, float, float], ...] = ()
    heading_boxes: tuple[Bounds, ...] = ()
    route_snapshot: Optional[RouteResult] = None
    source_annotations: dict[str, Optional[Point]] = field(default_factory=dict)


@dataclass
class _PreparedBoard:
    scope: str
    prefix: str
    root_id: str
    views: dict[str, SymbolView]
    pin_nets: dict[PinKey, str]
    names: dict[str, str]
    regions: dict[str, _RegionDrawing]
    net_regions: dict[str, set[str]] = field(default_factory=dict)
    circuit_model: Optional[SchematicCircuitModel] = None


class KiCadSchematicExporter:
    _wires = staticmethod(write_wires)

    def prepare_regions(
        self, compiled: CompiledDesign, options: SchematicExportOptions
    ) -> tuple[tuple[SchematicRegion, ...], str]:
        """Prepare the same measured regions consumed by planning and rendering."""
        boards, fingerprint, _, _ = self._prepare_boards(compiled, options)
        return tuple(d.spec for b in boards for d in b.regions.values()), fingerprint

    def _prepare_boards(
        self, compiled: CompiledDesign, options: SchematicExportOptions
    ) -> tuple[list[_PreparedBoard], str, SymbolResolver, list[SchematicDiagnostic]]:
        boards, fingerprint, resolver, diagnostics, prefix = self._prepare_legacy_boards(compiled, options)
        boards, fingerprint = self._prepare_led_bucks(boards, fingerprint, prefix, resolver, diagnostics, options)
        if not options.optimize_orientations or options.orientation_mode == "half_turn":
            return boards, fingerprint, resolver, diagnostics
        from .KiCadSchematicOrientation import (
            optimize_passive_orientations,
            orientation_metrics,
            passive_orientation_rank,
            orientation_conflict_identities,
        )
        from .KiCadSchematicRouting import optimize_fixed_routes, route_metrics

        # Provisional scene checks do not adopt a plan whose fingerprint belongs
        # to the eventual quarter-turn geometry. The public serializer validates
        # that requested plan only after the geometry has been selected.
        provisional = replace(options, sheet_plan=None, overview=None)
        baseline_bundle = self._serialize_prepared(boards, fingerprint, resolver, list(diagnostics), provisional)
        candidate_boards, changed_scopes = [], set()
        for board in boards:
            candidate_board = copy.copy(board)
            candidate_board.regions = dict(board.regions)
            candidate_boards.append(candidate_board)
            for identity, drawing in board.regions.items():
                if drawing.route_snapshot is None:
                    continue
                strategy = drawing.routing.get("selected", "baseline")
                router = lambda items, views, nets, strategy=strategy: route_local(
                    items, views, nets, strategy=strategy
                )
                locked = {
                    c.path
                    for c, _, _, _ in drawing.placed
                    if (hint := options.placements.get(c.path)) is not None and hint.lock_rotation
                }
                placed, route, evidence = optimize_passive_orientations(
                    drawing.placed,
                    board.views,
                    board.pin_nets,
                    router,
                    locked=locked,
                    baseline=drawing.route_snapshot,
                    source_annotations=drawing.source_annotations,
                    region_bounds=lambda items, result: self._region_bounds(
                        items, board.views, board.pin_nets, board.names, result[0], drawing.spec.title
                    ),
                )
                selected = copy.copy(drawing)
                selected.routing = copy.deepcopy(drawing.routing)
                selected.routing["passive_orientation"] = evidence
                candidate_board.regions[identity] = selected
                if not evidence["changed"]:
                    evidence["accepted"] = False
                    continue
                final_route, order_evidence = (
                    optimize_fixed_routes(placed, board.views, board.pin_nets, route, route_local)
                    if options.optimize_routes
                    else (route, None)
                )
                final_metric = orientation_metrics(placed, board.views, board.pin_nets, final_route)
                old_metric = orientation_metrics(drawing.placed, board.views, board.pin_nets, drawing.route_snapshot)
                old_conflicts = orientation_conflict_identities(
                    drawing.placed, board.views, board.pin_nets, drawing.route_snapshot
                )
                final_conflicts = orientation_conflict_identities(placed, board.views, board.pin_nets, final_route)
                bounds, headings, heading_boxes = self._region_geometry(
                    placed, board.views, board.pin_nets, board.names, final_route[0], drawing.spec.title
                )
                w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
                valid = (
                    set(final_route[2]) <= set(drawing.failed_routes)
                    and final_conflicts["escape"] <= old_conflicts["escape"]
                    and final_conflicts["visual_clearance"] <= old_conflicts["visual_clearance"]
                    and final_metric["visual_conflicts"] <= old_metric["visual_conflicts"]
                    and passive_orientation_rank(final_metric) < passive_orientation_rank(old_metric)
                    and region_fits_page(w, h)
                )
                if not valid:
                    self._rollback_passive(selected, drawing, "final routing or page-fit guard")
                    continue
                selected.placed, selected.wires, selected.failed_routes = placed, final_route[0], final_route[2]
                selected.route_snapshot = final_route
                selected.spec = replace(drawing.spec, bounds=bounds)
                selected.heading_positions, selected.heading_boxes = headings, heading_boxes
                evidence.update(accepted=True, after=final_metric)
                selected.routing["after"] = route_metrics(final_route[0], final_route[2])
                if order_evidence is not None:
                    selected.routing["passive_route_order"] = order_evidence
                    if order_evidence["selected"] != "baseline":
                        selected.routing["selected"] = order_evidence["selected"]
                changed_scopes.add(board.scope)
        if changed_scopes:
            candidate_fingerprint = self._prepared_fingerprint(prefix, candidate_boards, options)
            try:
                candidate_bundle = self._serialize_prepared(
                    candidate_boards, candidate_fingerprint, resolver, list(diagnostics), provisional
                )
                old_issues = self._passive_scene_issues(baseline_bundle)
                new_issues = self._passive_scene_issues(candidate_bundle)
                rejected = {
                    scope
                    for scope in changed_scopes
                    if any(
                        severity > old_issues.get(scope, {}).get(key, 0) + 1e-7
                        for key, severity in new_issues.get(scope, {}).items()
                    )
                }
            except ValueError as error:
                rejected = set(changed_scopes)
                scene_reason = "serialized candidate could not be planned: " + str(error)
            else:
                scene_reason = "new blocking serialized scene finding"
            for old_board, new_board in zip(boards, candidate_boards):
                if old_board.scope in rejected:
                    for identity, new_drawing in new_board.regions.items():
                        if new_drawing.routing.get("passive_orientation", {}).get("accepted"):
                            self._rollback_passive(new_drawing, old_board.regions[identity], scene_reason)
        fingerprint = self._prepared_fingerprint(prefix, candidate_boards, options)
        return candidate_boards, fingerprint, resolver, diagnostics

    def _prepare_led_bucks(
        self,
        boards: list[_PreparedBoard],
        fingerprint: str,
        prefix: HASH,
        resolver: SymbolResolver,
        diagnostics: Sequence[SchematicDiagnostic],
        options: SchematicExportOptions,
    ) -> tuple[list[_PreparedBoard], str]:
        """Bounded converter proposals, followed by a cached serialized-scene gate."""
        from .KiCadSchematicPower import led_buck_topology, compare_led_buck_variants
        from .KiCadSchematicRouting import optimize_fixed_routes, route_metrics
        from .KiCadSchematicOrientation import orientation_metrics, passive_orientation_rank

        bundle = None
        provisional = replace(options, sheet_plan=None, overview=None)
        for board in boards:
            for identity, drawing in list(board.regions.items()):
                by_path = {c.path: c for c, _, _, _ in drawing.placed}
                topology, reason = led_buck_topology(tuple(sorted(by_path)), by_path, board.views, board.pin_nets)
                if topology is None and reason is None:
                    continue
                if any(c.path in options.placements for c in by_path.values()):
                    drawing.routing["led_buck"] = dict(
                        accepted=False, reason="authored placements take precedence", route_trials=0, trials=[]
                    )
                    continue
                if topology is None:
                    drawing.routing["led_buck"] = dict(accepted=False, reason=reason, route_trials=0, trials=[])
                    continue
                if bundle is None:
                    bundle = self._serialize_prepared(boards, fingerprint, resolver, list(diagnostics), provisional)
                strategy = drawing.routing.get("selected", "baseline")
                router = lambda items, views, nets, strategy=strategy: route_local(
                    items, views, nets, strategy=strategy
                )
                placed, route, evidence = compare_led_buck_variants(
                    drawing.placed,
                    board.views,
                    board.pin_nets,
                    cast(RouteResult, drawing.route_snapshot),
                    router,
                    source_annotations=drawing.source_annotations,
                    region_bounds=lambda items, result: self._region_bounds(
                        items, board.views, board.pin_nets, board.names, result[0], drawing.spec.title
                    ),
                )
                assert evidence is not None  # topology was verified above
                drawing.routing["led_buck"] = evidence
                if not evidence["accepted"]:
                    continue
                final_route, order = (
                    optimize_fixed_routes(placed, board.views, board.pin_nets, route, route_local)
                    if options.optimize_routes
                    else (route, None)
                )
                metric = orientation_metrics(placed, board.views, board.pin_nets, final_route)
                if (
                    not set(final_route[2]) <= set(drawing.failed_routes)
                    or metric["visual_conflicts"] > evidence["before"]["visual_conflicts"]
                    or passive_orientation_rank(metric) >= passive_orientation_rank(evidence["before"])
                ):
                    final_route, order, metric = route, None, evidence["after"]
                bounds, headings, heading_boxes = self._region_geometry(
                    placed, board.views, board.pin_nets, board.names, final_route[0], drawing.spec.title
                )
                content_bounds = bounds
                old_width = drawing.spec.bounds[2] - drawing.spec.bounds[0]
                old_height = drawing.spec.bounds[3] - drawing.spec.bounds[1]
                if bounds[2] - bounds[0] <= old_width and bounds[3] - bounds[1] <= old_height:
                    # A local improvement must not disturb unrelated circuits'
                    # established packing. Retain the incumbent's measured cell
                    # size as explicit whitespace when the new content fits.
                    # Its origin follows the newly measured content, so no pins,
                    # wires or authored field coordinates need translating.
                    bounds = (bounds[0], bounds[1], bounds[0] + old_width, bounds[1] + old_height)
                selected = copy.copy(drawing)
                selected.routing = copy.deepcopy(drawing.routing)
                selected.routing["led_buck"].update(
                    after=metric, route_order=order, content_bounds=content_bounds, reserved_bounds=bounds
                )
                selected.routing["after"] = route_metrics(final_route[0], final_route[2])
                # "baseline" in the additional search means its supplied
                # incumbent, which may already use tree_search or another
                # strategy. Preserve that strategy for subsequent quarter turns.
                selected.routing["selected"] = (
                    order["selected"] if order and order["selected"] != "baseline" else strategy
                )
                selected.placed, selected.wires, selected.failed_routes = placed, final_route[0], final_route[2]
                selected.route_snapshot = final_route
                selected.spec = replace(drawing.spec, bounds=bounds)
                selected.heading_positions, selected.heading_boxes = headings, heading_boxes
                board.regions[identity] = selected
                candidate_fingerprint = self._prepared_fingerprint(prefix, boards, options)
                rejection = None
                try:
                    candidate_bundle = self._serialize_prepared(
                        boards, candidate_fingerprint, resolver, list(diagnostics), provisional
                    )
                    old = self._passive_scene_issues(bundle).get(board.scope, {})
                    new = self._passive_scene_issues(candidate_bundle).get(board.scope, {})
                    scene_changes = [
                        dict(identity=list(key), before=old.get(key, 0), after=value)
                        for key, value in sorted(new.items())
                        if value > old.get(key, 0) + 1e-6
                    ]
                    before_pages = sum(
                        name.endswith(".kicad_sch") and name.startswith(board.prefix) for name in bundle.files
                    )
                    after_pages = sum(
                        name.endswith(".kicad_sch") and name.startswith(board.prefix) for name in candidate_bundle.files
                    )
                    selected.routing["led_buck"]["scene_gate"] = dict(
                        before_findings=len(old),
                        after_findings=len(new),
                        new_or_worsened=scene_changes,
                        before_sheets=before_pages,
                        after_sheets=after_pages,
                    )
                    if after_pages > before_pages:
                        rejection = "increased schematic sheet fragmentation"
                    elif scene_changes:
                        rejection = "new or worsened blocking serialized scene finding"
                except ValueError as error:
                    rejection = "serialized candidate could not be planned: " + str(error)
                if rejection:
                    board.regions[identity] = drawing
                    evidence.update(
                        accepted=False, rollback_reason=rejection, attempted_after=metric, after=evidence["before"]
                    )
                    evidence["scene_gate"] = selected.routing["led_buck"].get("scene_gate")
                else:
                    bundle, fingerprint = candidate_bundle, candidate_fingerprint
        return boards, fingerprint

    @staticmethod
    def _rollback_passive(candidate: _RegionDrawing, baseline: _RegionDrawing, reason: str) -> None:
        evidence = candidate.routing["passive_orientation"]
        evidence.update(
            accepted=False,
            rollback_reason=reason,
            final_rotations={c.path: angle for c, _, _, angle in baseline.placed},
        )
        evidence["attempted_after"] = evidence["after"]
        evidence["after"] = evidence["before"]
        candidate.placed, candidate.wires, candidate.failed_routes = (
            baseline.placed,
            baseline.wires,
            baseline.failed_routes,
        )
        candidate.route_snapshot, candidate.spec = baseline.route_snapshot, baseline.spec
        candidate.heading_positions, candidate.heading_boxes = baseline.heading_positions, baseline.heading_boxes
        candidate.routing = copy.deepcopy(baseline.routing)
        candidate.routing["passive_orientation"] = evidence

    @staticmethod
    def _passive_scene_issues(bundle: SchematicExport) -> dict[str, dict[tuple[str, ...], float]]:
        """Compare actual serialized contacts, including existing bad labels.

        A label UUID alone cannot distinguish its old overlap from a new body
        contact. Stable collider identities and overlap area detect both new
        contacts and worsening existing ones. Wire indices are not identities.
        """
        from .KiCadSchematicReadability import text_item, SceneText
        from .KiCadSchematicScene import pin_name_items, pin_number_items, instance_property_at

        manifest = json.loads(bundle.files["manifest.json"])
        scopes = {Path(b["root"]).stem: b["scope"] for b in manifest["boards"]}
        result: dict[str, dict[tuple[str, ...], float]] = {}
        sheet_scopes: dict[str, str] = {}

        def scope_for(filename: str) -> str:
            return str(next(scope for prefix, scope in scopes.items() if filename.startswith(prefix)))

        def area(a: Bounds, b: Bounds) -> float:
            return max(0, min(a[2], b[2]) - max(a[0], b[0]) + 0.25) * max(0, min(a[3], b[3]) - max(a[1], b[1]) + 0.25)

        for filename, content in bundle.files.items():
            if filename.endswith(".kicad_sch"):
                doc = sexpdata.loads(content)
                scope = scope_for(filename)
                sheet_scopes[children(doc, "uuid")[0][1]] = scope
                issues = result.setdefault(scope, {})
                definitions = {d[1]: d for lib in children(doc, "lib_symbols") for d in children(lib, "symbol")}
                texts: list[SceneText] = []
                bodies: list[tuple[str, Bounds]] = []
                for symbol in children(doc, "symbol"):
                    at = children(symbol, "at")[0]
                    props = {p[1]: p for p in children(symbol, "property")}
                    owner = props["PBPath"][2] if "PBPath" in props else children(symbol, "uuid")[0][1]
                    lib_id = children(symbol, "lib_id")[0][1]
                    definition = definitions.get(lib_id)
                    if definition is not None:
                        x1, y1, x2, y2 = graphic_bounds(SymbolView(definition, [], lib_id), int(at[3]), False)
                        bodies.append((owner, (at[1] + x1, at[2] + y1, at[1] + x2, at[2] + y2)))
                        texts.extend(
                            SceneText(**item)
                            for item in (
                                pin_name_items(definition, at[1], at[2], at[3], owner)
                                + pin_number_items(definition, at[1], at[2], at[3], owner)
                            )
                        )
                    for name, prop in props.items():
                        positions, effects_nodes = children(prop, "at"), children(prop, "effects")
                        if positions and effects_nodes:
                            field_text = text_item(
                                owner + ":" + name,
                                prop[2],
                                instance_property_at(positions[0], at),
                                effects_nodes[0],
                                owner,
                                "field",
                            )
                            if field_text is not None:
                                texts.append(field_text)
                for kind in ("text", "label", "global_label"):
                    for item in children(doc, kind):
                        positions, effects_nodes = children(item, "at"), children(item, "effects")
                        if positions and effects_nodes:
                            text = text_item(
                                children(item, "uuid")[0][1], item[1], positions[0], effects_nodes[0], "", kind
                            )
                            if text is not None:
                                texts.append(text)
                for index, text in enumerate(texts):
                    for owner, box in bodies:
                        # Pin text is intentionally inside its own symbol.
                        if text.owner == owner and text.kind.startswith("pin_"):
                            continue
                        severity = area(text.bounds, box)
                        if severity:
                            key: tuple[str, ...] = ("text_body_contact", text.identity, owner)
                            issues[key] = max(issues.get(key, 0), severity)
                    for other in texts[index + 1 :]:
                        severity = area(text.bounds, other.bounds)
                        if severity:
                            key = ("text_contact", *sorted((text.identity, other.identity)))
                            issues[key] = max(issues.get(key, 0), severity)
                    # Quantify crossings too: an already affected text UUID
                    # must not whitelist another or longer wire through it.
                    spans: dict[tuple[int, float], list[tuple[float, float]]] = {}
                    for wire in children(doc, "wire"):
                        points = [tuple(p[1:3]) for pts in children(wire, "pts") for p in children(pts, "xy")]
                        if len(points) != 2:
                            continue
                        a, b = points
                        x1, y1, x2, y2 = text.bounds
                        axis = 1 if a[0] == b[0] else 0
                        fixed = a[1 - axis]
                        low, high = (y1 + 0.3, y2 - 0.3) if axis else (x1 + 0.3, x2 - 0.3)
                        inside = x1 + 0.3 < fixed < x2 - 0.3 if axis else y1 + 0.3 < fixed < y2 - 0.3
                        lo, hi = max(min(a[axis], b[axis]), low), min(max(a[axis], b[axis]), high)
                        if inside and hi > lo:
                            spans.setdefault((axis, fixed), []).append((lo, hi))
                    length = 0.0
                    for intervals in spans.values():
                        merged: list[tuple[float, float]] = []
                        for lo, hi in sorted(intervals):
                            if merged and lo <= merged[-1][1]:
                                merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
                            else:
                                merged.append((lo, hi))
                        length += sum(hi - lo for lo, hi in merged)
                    if length:
                        issues["text_wire_contact", text.identity] = length
        for entry in json.loads(bundle.files["layout.json"])["label_placement"]:
            issues = result.setdefault(sheet_scopes[entry["sheet"]], {})
            issues.update({("label_collision", item["identity"]): 1 for item in entry["conflicts"]})
            issues.update({("unresolved_anchor", item["identity"]): 1 for item in entry["unresolved_anchors"]})
        for finding in json.loads(bundle.files["readability.json"])["findings"]:
            if finding["code"] not in ("text_collision", "text_outside_page", "wire_through_text"):
                continue
            objects = tuple(o for o in finding["objects"] if not o.startswith("wire:"))
            result.setdefault(scope_for(finding["sheet"]), {})[(finding["code"],) + objects] = 1
        return result

    def _prepare_legacy_boards(
        self, compiled: CompiledDesign, options: SchematicExportOptions
    ) -> tuple[list[_PreparedBoard], str, SymbolResolver, list[SchematicDiagnostic], HASH]:
        presentation = options.presentation or SchematicPresentation()
        if not isinstance(presentation, SchematicPresentation):
            raise ValueError("presentation must be a SchematicPresentation")
        presentation = SchematicPresentation.from_dict(presentation.to_dict())
        if options.overview is not None and not isinstance(options.overview, SchematicOverview):
            raise ValueError("overview must be a SchematicOverview")
        if compiled.errors:
            raise ValueError("cannot export a design with compilation errors")
        scopes = NetlistTransform(compiled).run()
        # Hash canonical solved physical state, not compiler source-location metadata:
        # the latter contains machine-specific Python paths and line numbers.
        digest = hashlib.sha256(VERSION.encode())
        digest.update(options.source.encode("utf-8"))
        for scope, netlist in sorted(scopes.items(), key=lambda entry: str(entry[0])):
            resolved: dict[str, Any] = {
                "scope": str(scope),
                "blocks": [
                    list(b[:4])
                    + [
                        str(b.full_path),
                        [cls.target.name for cls in b.path_classes],
                        compiled.get_value(b.full_path.to_tuple() + ("fp_pinning",)),
                        compiled.get_value(b.full_path.to_tuple() + ("sch_symbol",))
                        or compiled.get_value(b.full_path.to_tuple() + ("sch_symbol_default",)),
                    ]
                    for b in sorted(netlist.blocks, key=lambda b: str(b.full_path))
                ],
                "nets": [(n.name, sorted((str(p.block_path), p.pin_name) for p in n.pins)) for n in netlist.nets],
            }
            digest.update(json.dumps(resolved, sort_keys=True, ensure_ascii=False).encode("utf-8"))
        fingerprint = digest.hexdigest()
        directories = list(options.symbol_library_dirs)
        env = os.environ.get(f"KICAD{options.kicad_major}_SYMBOL_DIR")
        if env:
            directories.append(env)
        resolver = SymbolResolver(directories)
        boards = []
        all_hints = set(options.placements)
        known_paths = {str(b.full_path) for n in scopes.values() for b in n.blocks}
        if all_hints - known_paths:
            raise ValueError(
                "schematic placement references missing components: " + str(sorted(all_hints - known_paths))
            )
        presentation.validate(
            {
                str(b.full_path): dict(
                    (number, port)
                    for number, port in (
                        v.split("=", 1)
                        for v in cast(list[str], compiled.get_value(b.full_path.to_tuple() + ("fp_pinning",)))
                    )
                )
                for n in scopes.values()
                for b in n.blocks
            }
        )
        used_groups = set()
        diagnostics: List[SchematicDiagnostic] = []
        for scope, netlist in scopes.items():
            scope_name = str(scope)
            prefix = "board_" + uid(options.design_name, scope_name)
            root_id = uid(prefix, "root")
            components = []
            blocks_by_path = {str(block.full_path): block for block in netlist.blocks}
            classes_by_path = {
                path: [c.target.name for c in block.path_classes] for path, block in blocks_by_path.items()
            }
            for block in netlist.blocks:
                path = str(block.full_path)
                raw = cast(list[str], compiled.get_value(block.full_path.to_tuple() + ("fp_pinning",)))
                pins = {number: port for number, port in (v.split("=", 1) for v in raw)}
                mapping_raw = cast(Optional[str], compiled.get_value(block.full_path.to_tuple() + ("sch_symbol",)))
                mapping_source = "explicit"
                if mapping_raw is None:
                    mapping_raw = cast(
                        Optional[str], compiled.get_value(block.full_path.to_tuple() + ("sch_symbol_default",))
                    )
                    mapping_source = "footprint_default" if mapping_raw else "registry"
                relative = block.full_path.blocks[len(scope.blocks) :]
                group = relative[0] if relative else "Board-level components"
                if not pins and ("MountingHole" in block.footprint or "ToolingHole" in block.footprint):
                    group = "Mechanical notes"
                components.append(
                    PhysicalComponent(
                        path,
                        block.refdes,
                        block.footprint,
                        block.value,
                        pins,
                        json.loads(mapping_raw) if mapping_raw else None,
                        group,
                    )
                )
                component = components[-1]
                component.hierarchy = tuple(
                    (".".join(block.full_path.blocks[: i + 1]), cls.target.name)
                    for i, cls in enumerate(block.path_classes)
                )
                component.display_value = self._display_value(compiled, block, component.mapping)
                component.symbol_coverage = dict(
                    component=path,
                    refdes=component.refdes,
                    compiled_class=block.path_classes[-1].target.name if block.path_classes else "",
                    mapping_source=mapping_source,
                )
                if component.mapping is None:
                    component.mapping = infer_symbol(
                        component, classes_by_path[path], block.part, resolver, component.symbol_coverage
                    )
            for component in components:
                entry = presentation.components.get(component.path, {})
                component.presentation_pin_roles = {
                    boundary["pin"]: boundary["role"]
                    for circuit in presentation.circuits
                    for boundary in circuit.get("boundaries", ())
                    if boundary["component"] == component.path
                }
                if entry.get("display_value"):
                    component.display_value = entry["display_value"]
                classes = classes_by_path[component.path]
                physical_block = blocks_by_path[component.path]
                connector_length = compiled.get_value(physical_block.full_path.to_tuple() + ("length",))
                inferred_names = infer_pin_names(component, classes, connector_length)
                if inferred_names:
                    component.mapping = dict(component.mapping or {})
                    component.mapping["pin_names"] = dict(inferred_names, **component.mapping.get("pin_names", {}))
                description = infer_description(component, classes, connector_length)
                component.descriptions = presentation.descriptions(component.path) or (
                    (description,) if description else ()
                )
                if entry.get("pin_names"):
                    component.mapping = dict(component.mapping or {})
                    component.mapping["pin_names"] = dict(
                        (component.mapping or {}).get("pin_names", {}),
                        **entry["pin_names"],
                    )
            views = {}
            for component in components:
                composite = resistor_array_symbol(component, classes_by_path[component.path])
                if composite is not None:
                    views[component.path] = SymbolView(*composite)
                    component.symbol_coverage.update(
                        status="resolved", category="composite", lib_id=views[component.path].lib_id
                    )
                    continue
                try:
                    if not (component.mapping or {}).get("lib_id"):
                        raise LookupError("no schematic symbol mapping")
                    views[component.path] = resolver.resolve(component)
                    component.symbol_coverage.update(
                        status="resolved", category="library_symbol", lib_id=(component.mapping or {})["lib_id"]
                    )
                except (LookupError, FileNotFoundError) as error:
                    coverage = component.symbol_coverage
                    category = (
                        "missing_library"
                        if isinstance(error, FileNotFoundError)
                        else (
                            "unsupported_multi_unit"
                            if str(error) == "multi-unit symbol unsupported"
                            else (
                                "unsupported_symbol"
                                if str(error) == "stacked or repeated symbol pins unsupported"
                                else "missing_symbol" if isinstance(error, KeyError) else "missing_mapping"
                            )
                        )
                    )
                    # Registry lookup may already have identified an unavailable
                    # library before returning None. Preserve that exact reason.
                    coverage.update(
                        status="fallback",
                        category=coverage.get("category", category),
                        reason=coverage.get("reason", str(error)),
                    )
                    if (component.mapping or {}).get("lib_id"):
                        coverage["lib_id"] = (component.mapping or {})["lib_id"]
                    diagnostics.append(SchematicDiagnostic(component.path, str(coverage["reason"])))
                    views[component.path] = generic(component)
            for component in components:
                view = views[component.path]
                for body in children(view.definition, "symbol"):
                    for pin in children(body, "pin"):
                        number = str(children(pin, "number")[0][1])
                        name = (component.mapping or {}).get("pin_names", {}).get(number)
                        if name:
                            children(pin, "name")[0][1] = name
                hint = options.placements.get(component.path)
                if hint:
                    component.annotation = hint.annotation
                    if hint.flip_horizontal:
                        view = views[component.path]
                        definition = copy.deepcopy(view.definition)

                        def reflect(tree: object) -> None:
                            if isinstance(tree, list) and tree:
                                if (
                                    str(tree[0]) in ("at", "start", "mid", "end", "xy", "center")
                                    and len(tree) >= 3
                                    and isinstance(tree[1], (float, int))
                                ):
                                    tree[1] = -tree[1]
                                    if str(tree[0]) == "at" and len(tree) >= 4:
                                        tree[3] = (180 - tree[3]) % 360
                                for child in tree:
                                    reflect(child)

                        reflect(definition)
                        reflected_id = view.lib_id + "_reflected"
                        definition[1] = reflected_id
                        for body in children(definition, "symbol"):
                            match = re.search(r"_(\d+_\d+)$", body[1])
                            if match:
                                body[1] = reflected_id.split(":", 1)[1] + "_" + match[1]
                        views[component.path] = SymbolView(
                            definition,
                            [(n, -x, y, (180 - angle) % 360) for n, x, y, angle in view.pins],
                            reflected_id,
                        )
            pin_nets = {(str(p.block_path), p.pin_name): n.name for n in netlist.nets for p in n.pins}
            from .KiCadSchematicCircuits import build_circuits

            circuit_model = build_circuits(components, pin_nets, views, presentation)
            for diagnostic in circuit_model.diagnostics:
                diagnostics.append(SchematicDiagnostic(scope_name, str(diagnostic)))
            by_component = {path: circuit for circuit in circuit_model.circuits for path in circuit.components}
            for component in components:
                component.circuit_model = circuit_model
                component.functional_circuit = by_component.get(component.path)
            from .KiCadSchematicLabels import readable_labels

            names = readable_labels(n.name for n in netlist.nets)
            ground_nets = {n.name for n in netlist.nets if n.name.lower().split(".")[-1] == "gnd"}
            for component in components:
                component.ground_net_labels = (
                    {
                        number: names[net]
                        for number in component.pins
                        if (net := pin_nets.get((component.path, number))) in ground_nets
                    }
                    if len(ground_nets) > 1
                    else {}
                )
                component.net_labels = {
                    number: names[pin_nets[(component.path, number)]]
                    for number in component.pins
                    if (component.path, number) in pin_nets
                }
            regroup(components, pin_nets, views)
            for component in components:
                circuit = component.functional_circuit
                if circuit is not None and circuit.provenance == "explicit":
                    component.group = circuit.title
                hint = options.placements.get(component.path)
                if hint:
                    if hint.rotation not in (0, 90, 180, 270):
                        raise ValueError("schematic rotation must be orthogonal")
                    if not all(math.isfinite(v) for v in (hint.x, hint.y)):
                        raise ValueError("schematic coordinates must be finite")
                    if hint.annotation and not all(math.isfinite(v) for v in hint.annotation):
                        raise ValueError("schematic annotations must be finite")
                    component.group = hint.group

            for component in components:
                selector = component.group
                if selector in presentation.groups:
                    component.group = presentation.groups[selector]
                    used_groups.add(selector)
            board = _PreparedBoard(scope_name, prefix, root_id, views, pin_nets, names, {})
            board.circuit_model = circuit_model
            for group in sorted({c.group for c in components}):
                members = [c for c in components if c.group == group]
                hints = [options.placements.get(c.path) for c in members]
                hinted = any(hints)
                if hinted:
                    if not all(hints):
                        raise ValueError("all members of hinted group require placements: " + group)
                    batches: list[list[Placement]] = [
                        [(c, h.x, h.y, h.rotation) for c, h in zip(members, cast(list[SchematicPlacement], hints))]
                    ]
                elif group == "Mechanical notes":
                    batches = [[(c, 40 + (i % 9) * 35, 220 + (i // 9) * 25, 0) for i, c in enumerate(members)]]
                else:
                    batches = place_group(members, views, pin_nets, optimize_orientations=options.optimize_orientations)
                pending = list(batches)
                part = 0
                while pending:
                    source_placed = pending.pop(0)
                    placed = freeze_annotations(source_placed, views)
                    baseline = route_local(placed, views, pin_nets)
                    orientation = None
                    bridge_comparison = None
                    if options.optimize_orientations:
                        from .KiCadSchematicOrientation import optimize_orientations

                        rotation_locks = {
                            c.path
                            for c, _, _, _ in source_placed
                            if (hint := options.placements.get(c.path)) is not None and hint.lock_rotation
                        }
                        placed, baseline, orientation = optimize_orientations(
                            source_placed,
                            views,
                            pin_nets,
                            route_local,
                            locked=rotation_locks,
                            baseline=baseline,
                            region_bounds=lambda items, route: self._region_bounds(
                                items, views, pin_nets, names, route[0], group
                            ),
                        )
                    if options.optimize_orientations and not hinted:
                        from .KiCadSchematicPower import compare_bridge_variants

                        placed, baseline, bridge_comparison = compare_bridge_variants(
                            placed,
                            views,
                            pin_nets,
                            baseline,
                            route_local,
                            region_bounds=lambda items, route: self._region_bounds(
                                items, views, pin_nets, names, route[0], group
                            ),
                            source_annotations={c.path: getattr(c, "annotation", None) for c, _, _, _ in source_placed},
                        )
                    from .KiCadSchematicRouting import optimize_fixed_routes, route_metrics

                    if options.optimize_routes:
                        routed, routing = optimize_fixed_routes(placed, views, pin_nets, baseline, route_local)
                    else:
                        routed = baseline
                        metric = route_metrics(baseline[0], baseline[2])
                        routing = dict(before=metric, after=metric, selected="baseline", candidates=1)
                    if orientation is not None:
                        routing["orientation"] = orientation
                    if bridge_comparison is not None:
                        routing["bridge_comparison"] = bridge_comparison
                    wires, _, failed = routed
                    # Measure the selected route so detours reserve their actual packing area.
                    bounds = self._region_bounds(placed, views, pin_nets, names, wires, group)
                    width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
                    if routed is not baseline and not region_fits_page(width, height):
                        original = self._region_bounds(placed, views, pin_nets, names, baseline[0], group)
                        original_width, original_height = original[2] - original[0], original[3] - original[1]
                        if region_fits_page(original_width, original_height):
                            routing["rejected_for_page_fit"] = routing["selected"]
                            routing["selected"] = "baseline"
                            routing["after"] = routing["before"]
                            routed = baseline
                            wires, _, failed = baseline
                            bounds, width, height = original, original_width, original_height
                    if not region_fits_page(width, height) and len(placed) > 1 and not hinted:
                        subsets = split_group(placed, views, pin_nets)
                        if subsets is None:
                            raise ValueError(
                                f"indivisible functional region exceeds A3: {group} ({width:.1f} x {height:.1f} mm); components: "
                                + ", ".join(c.path for c, _, _, _ in placed)
                            )
                        # Repacking must resolve automatic fields afresh at the
                        # new placement, not retain this rejected region's fields.
                        originals = {c.path: c for c, _, _, _ in source_placed}
                        for subset in subsets:
                            pending.extend(
                                place_group(
                                    [originals[c.path] for c, _, _, _ in subset],
                                    views,
                                    pin_nets,
                                    optimize_orientations=options.optimize_orientations,
                                )
                            )
                        diagnostics.append(
                            SchematicDiagnostic(
                                group,
                                "continuation: measured circuit region requires functional continuation",
                            )
                        )
                        continue
                    if not region_fits_page(width, height):
                        raise ValueError(
                            f"region {group!r} ({width:.1f} x {height:.1f} mm) exceeds A3; revise presentation without shrinking text"
                        )
                    part += 1
                    title = group if part == 1 else group + " /" + str(part)
                    # Identify the actual repeated-channel indices on this sheet.
                    match = re.fullmatch(r"(.+)\[0\]", group)
                    if match and not hinted:
                        prefix = (scope_name + "." if scope_name != "(root)" else "") + match.group(1)
                        indices = set()
                        for component, _, _, _ in placed:
                            item = re.match(re.escape(prefix) + r"\[(\d+)\](?:\.|$)", component.path)
                            if item:
                                indices.add(int(item.group(1)))
                        if indices:
                            title = match.group(1) + "[" + ",".join(str(i) for i in sorted(indices)) + "]"

                    identity = json.dumps(
                        [scope_name, group, part],
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    spec = SchematicRegion(
                        identity,
                        title,
                        scope_name,
                        tuple(c.path for c, _, _, _ in placed),
                        bounds,
                        kind=(
                            "mechanical"
                            if group == "Mechanical notes" and all(not c.pins for c in members)
                            else "circuit"
                        ),
                    )
                    rendered_heading = self._region_heading_lines(title, placed)
                    if len(rendered_heading) == len(textwrap.wrap(title, 42) or [""]):
                        # Retain existing automatic geometry even when the final
                        # channel/continuation title differs from its group key.
                        headings = tuple(
                            (line, size, bounds[0] + 3, bounds[1] + 3 + i * 2.54)
                            for i, (line, size) in enumerate(rendered_heading)
                        )
                        heading_boxes: tuple[Bounds, ...] = (
                            (bounds[0], bounds[1], bounds[2], bounds[1] + 5 + 2.54 * len(rendered_heading)),
                        )
                    else:
                        _, headings, heading_boxes = self._region_geometry(
                            placed,
                            views,
                            pin_nets,
                            names,
                            wires,
                            title,
                        )
                    board.regions[identity] = _RegionDrawing(
                        spec,
                        placed,
                        wires,
                        failed,
                        routing,
                        headings,
                        heading_boxes,
                        routed,
                        {c.path: c.annotation for c, _, _, _ in source_placed},
                    )
            if not board.regions:
                spec = SchematicRegion(
                    scope_name + "::Empty design",
                    "Empty design",
                    scope_name,
                    (),
                    (0, 0, 50, 10),
                    kind="empty",
                )
                board.regions[spec.id] = _RegionDrawing(spec, [], [], [])
            rendered = [c.path for drawing in board.regions.values() for c, _, _, _ in drawing.placed]
            if (
                len(rendered) != len(components)
                or set(rendered) != {c.path for c in components}
                or len(set(rendered)) != len(rendered)
            ):
                raise ValueError("prepared schematic regions must contain each physical component exactly once")
            for identity, drawing in board.regions.items():
                for c, _, _, _ in drawing.placed:
                    for pin_number in c.pins:
                        net = pin_nets.get((c.path, pin_number))
                        if net is not None:
                            board.net_regions.setdefault(net, set()).add(identity)
            boards.append(board)
        if set(presentation.groups) - used_groups:
            raise ValueError(
                "presentation references unknown groups: " + str(sorted(set(presentation.groups) - used_groups))
            )
        digest.update(json.dumps(presentation.to_dict(), sort_keys=True, ensure_ascii=False).encode("utf-8"))
        return boards, self._prepared_fingerprint(digest, boards, options), resolver, diagnostics, digest

    @staticmethod
    def _prepared_fingerprint(prefix: HASH, boards: Sequence[_PreparedBoard], options: SchematicExportOptions) -> str:
        digest = prefix.copy()
        # Bind plans to solved electrical state AND actual symbol/layout geometry.
        # Library, hint or source changes cannot silently reuse an old packing plan.
        geometry = [
            dict(
                scope=b.scope,
                regions=[d.spec.to_dict() for d in b.regions.values()],
                placed=[
                    (c.path, x, y, a, c.annotation, c.display_value)
                    for d in b.regions.values()
                    for c, x, y, a in d.placed
                ],
                symbols={k: sexpdata.dumps(v.definition) for k, v in sorted(b.views.items())},
            )
            for b in boards
        ]
        digest.update(
            json.dumps(
                options.overview.to_dict() if options.overview is not None else None,
                sort_keys=True,
                ensure_ascii=False,
            ).encode("utf-8")
        )
        digest.update(json.dumps(geometry, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        return digest.hexdigest()

    @staticmethod
    def _region_heading_lines(title: str, placed: Placements) -> list[tuple[str, float]]:
        lines = [(line, 1.5) for line in (textwrap.wrap(title, 42) or [""])]
        members = {c.path: c for c, _, _, _ in placed}
        circuits = {
            circuit.id: circuit
            for c in members.values()
            if (circuit := cast("Optional[SchematicCircuit]", getattr(c, "functional_circuit", None))) is not None
            and circuit.provenance == "explicit"
        }
        for circuit in sorted(circuits.values(), key=lambda c: c.id):
            lines.extend((line, 1.1) for line in textwrap.wrap(circuit.summary, 52))
            for boundary in circuit.boundaries:
                if boundary.component in members:
                    component = members[boundary.component]
                    label = component.net_labels.get(boundary.pin, "unconnected")
                    note = f"{boundary.name}: {component.refdes}.{boundary.pin} [{label}]"
                    lines.extend((line, 1.1) for line in textwrap.wrap(note, 52))
        return lines

    @staticmethod
    def _region_bounds(
        placed: Placements,
        views: Views,
        pin_nets: PinNets,
        names: Mapping[str, str],
        wires: Sequence[Wire],
        title: str = "",
    ) -> Bounds:
        return KiCadSchematicExporter._region_geometry(
            placed,
            views,
            pin_nets,
            names,
            wires,
            title,
        )[0]

    @staticmethod
    def _region_geometry(
        placed: Placements,
        views: Views,
        pin_nets: PinNets,
        names: Mapping[str, str],
        wires: Sequence[Wire],
        title: str = "",
    ) -> tuple[Bounds, tuple[tuple[str, float, float, float], ...], tuple[Bounds, ...]]:
        """Measure circuit and explanatory notes with one shared layout.

        Ordinary headings retain their historical geometry. When authored notes
        would overflow the usable A3 height, a measured right-hand column may
        preserve the complete circuit without shrinking or dropping any text.
        """
        points: list[Point] = []
        for c, x, y, angle in placed:
            xmin, ymin, xmax, ymax = graphic_bounds(views[c.path], angle)
            points.extend(((x + xmin, y + ymin), (x + xmax, y + ymax)))
            tx, ty, align = annotation_position(c, views[c.path], x, y, angle)
            ax1, ay1, ax2, ay2 = annotation_bounds(c, tx, ty, angle)
            points.extend(((ax1, ay1), (ax2, ay2)))
            connector_labels = []
            for number, px, py, direction in positioned_pins(views[c.path], x, y, angle):
                net = pin_nets.get((c.path, number))
                if net is None:
                    continue
                r = math.radians(direction)
                ex, ey = (
                    round(px - 5.08 * math.cos(r), 4),
                    round(py + 5.08 * math.sin(r), 4),
                )
                if net.lower().split(".")[-1] == "gnd":
                    gx1, gy1, gx2, gy2 = ground_bounds(
                        ex,
                        ey,
                        direction,
                        c.ground_net_labels.get(number, ""),
                    )
                    points.extend(((gx1, gy1), (gx2, gy2)))
                    continue
                bounds = pin_label_bounds(names[net], ex, ey, direction)
                points.extend(((bounds[0], bounds[1]), (bounds[2], bounds[3])))
                if views[c.path].lib_id.startswith("Connector") and direction in (0, 180):
                    connector_labels.append((direction, bounds, names[net]))
            # Dense connector pin rows can mix local text and outlined global
            # labels. Reserve an outer lane only when their measured boxes
            # conflict, so the final scene can stagger them without clipping.
            from .KiCadSchematicScene import overlap

            for direction, bounds, name in connector_labels:
                if any(
                    other_direction == direction and other_bounds != bounds and overlap(bounds, other_bounds)
                    for other_direction, other_bounds, _ in connector_labels
                ):
                    extra = math.ceil((text_width(name, 1.27) + 5.08) / 2.54) * 2.54
                    side = bounds[0] - extra if direction == 0 else bounds[2] + extra
                    points.append((side, bounds[1]))
        for _, a, b in wires:
            points.extend((a, b))
        if not points:
            return (0, 0, 50, 10), (), ()
        measured = KiCadSchematicExporter._region_heading_lines(title + " /999", placed)
        rendered = KiCadSchematicExporter._region_heading_lines(title, placed)
        title_count = len(textwrap.wrap(title, 42) or [""])
        measured_title_count = len(textwrap.wrap(title + " /999", 42) or [""])
        notes = rendered[title_count:]
        xmin = min(p[0] for p in points) - 3
        bottom = max(p[1] for p in points) + 3

        def top_layout(
            lines: Sequence[tuple[str, float]], reserved: Sequence[tuple[str, float]], header_gap: float = 6
        ) -> tuple[Bounds, tuple[tuple[str, float, float, float], ...], tuple[Bounds, ...]]:
            ymin = min(p[1] for p in points) - (header_gap + len(reserved) * 2.54)
            xmax = max(max(p[0] for p in points) + 3, xmin + max(text_width(line, size) for line, size in reserved) + 6)
            bounds: Bounds = (round(xmin, 4), round(ymin, 4), round(xmax, 4), round(bottom, 4))
            headings = tuple((line, size, xmin + 3, ymin + 3 + i * 2.54) for i, (line, size) in enumerate(lines))
            boxes = ((xmin, ymin, xmax, ymin + 5 + 2.54 * len(lines)),)
            return bounds, headings, boxes

        def fits(bounds: Bounds) -> bool:
            width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
            return region_fits_page(width, height)

        top = top_layout(rendered, measured)
        if not notes or fits(top[0]):
            return top
        # Keep the original title above the circuit. The notes occupy their own
        # obstacle column with measured padding and the same font/line spacing.
        for header_gap in (6, 4.73, 3):
            body = top_layout(rendered[:title_count], measured[:measured_title_count], header_gap)
            body_bounds, body_headings, body_boxes = body
            # Compact only whitespace; keep at least one grid of clearance
            # below the title glyphs, above the measured circuit content.
            if max(y + size / 2 for _, size, _, y in body_headings) > min(p[1] for p in points) - 1.27:
                continue
            column_x = body_bounds[2] + 5.08
            column_width = max(text_width(line, size) for line, size in notes) + 6
            column_bottom = body_bounds[1] + 6 + len(notes) * 2.54
            side_bounds = (body_bounds[0], body_bounds[1], column_x + column_width, max(body_bounds[3], column_bottom))
            if not fits(side_bounds):
                continue
            note_positions = tuple(
                (line, size, column_x + 3, body_bounds[1] + 3 + i * 2.54) for i, (line, size) in enumerate(notes)
            )
            note_box = (column_x, body_bounds[1], column_x + column_width, column_bottom)
            return (
                cast(Bounds, tuple(round(v, 4) for v in side_bounds)),
                body_headings + note_positions,
                body_boxes + (note_box,),
            )
        return top

    def _plan_compiled(self, compiled: CompiledDesign, options: SchematicExportOptions) -> SchematicSheetPlan:
        boards, fingerprint, _, _ = self._prepare_boards(compiled, options)
        return self._plan_prepared(boards, fingerprint, options)

    @staticmethod
    def _plan_prepared(
        boards: Sequence[_PreparedBoard], fingerprint: str, options: SchematicExportOptions
    ) -> SchematicSheetPlan:
        regions = tuple(d.spec for b in boards for d in b.regions.values())
        adjacency: dict[tuple[str, str], float] = {}
        for b in boards:
            for net, identities in b.net_regions.items():
                if KiCadSchematicExporter._is_backbone(net) or len(identities) > 8:
                    continue
                for a in sorted(identities):
                    for other in sorted(identities):
                        if a < other:
                            adjacency[(a, other)] = adjacency.get((a, other), 0) + 1
        return SchematicSheetPlanner().plan_regions(
            regions,
            fingerprint,
            assignments=options.sheet_assignments,
            requested=options.sheet_plan,
            adjacency=adjacency,
        )

    def overview(self, compiled: CompiledDesign, options: SchematicExportOptions) -> dict[str, Any]:
        """Preview the same compiled, witnessed functional overview emitted by export."""
        boards, fingerprint, _, _ = self._prepare_boards(compiled, options)
        plan = self._plan_prepared(boards, fingerprint, options)
        return build_overviews(boards, plan, options.overview)

    def layout(self, compiled: CompiledDesign, options: SchematicExportOptions) -> dict[str, Any]:
        """Return deterministic native layout evidence from the exported artifact."""
        return cast(dict[str, Any], json.loads(self.export(compiled, options).files["layout.json"]))

    def readability(self, compiled: CompiledDesign, options: SchematicExportOptions) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(self.export(compiled, options).files["readability.json"]))

    def export(self, compiled: CompiledDesign, options: SchematicExportOptions) -> SchematicExport:
        boards, fingerprint, resolver, diagnostics = self._prepare_boards(compiled, options)
        return self._serialize_prepared(boards, fingerprint, resolver, list(diagnostics), options)

    def _serialize_prepared(
        self,
        boards: Sequence[_PreparedBoard],
        fingerprint: str,
        resolver: SymbolResolver,
        diagnostics: list[SchematicDiagnostic],
        options: SchematicExportOptions,
    ) -> SchematicExport:
        plan = self._plan_prepared(boards, fingerprint, options)
        overview_data = build_overviews(boards, plan, options.overview)
        files = {}
        board_records = []
        label_evidence = []
        for board in boards:
            sheets = [s for s in plan.sheets if s.scope == board.scope]
            if not sheets:
                raise ValueError("sheet plan omitted board scope: " + board.scope)
            overview = next((s for s in sheets if s.id == "overview"), None)
            content = [s for s in sheets if s.id != "overview"]
            root_sheet = overview or (content[0] if len(content) == 1 else None)
            if root_sheet is None:
                raise ValueError("multiple sheets require an overview")
            root_title = root_sheet.title if board.scope in ("", "(root)") else board.scope + " / " + root_sheet.title
            root = self._document(board.root_id, options, fingerprint, root_title)
            root.append(node("sheet_instances", node("path", "/", node("page", "1"))))
            root_filename = board.prefix + ".kicad_sch"
            board_records.append(dict(scope=board.scope, root=root_filename))
            index_docs = {}
            net_pages: dict[str, set[str]] = {}
            for sheet in sheets:
                for location in sheet.regions:
                    drawing = board.regions[location.region_id]
                    for c, _, _, _ in drawing.placed:
                        for pin in c.pins:
                            net = board.pin_nets.get((c.path, pin))
                            if net is not None:
                                net_pages.setdefault(net, set()).add(sheet.id)
            for number, sheet in enumerate(sheets):
                is_root = sheet.id == root_sheet.id
                sheet_id = board.root_id if is_root else uid(board.prefix, sheet.id)
                parent_path = "/" + board.root_id
                child_index = content.index(sheet) if not is_root else -1
                if not is_root and len(content) > 40:
                    bucket = child_index // 40
                    index_id = uid(board.prefix, "contents", str(bucket))
                    parent_path += "/" + index_id
                    if bucket not in index_docs:
                        index_docs[bucket] = self._document(index_id, options, fingerprint, f"Contents {bucket + 1}")
                        index_docs[bucket].append(node("lib_symbols"))
                instance_path = "/" + board.root_id if is_root else parent_path + "/" + sheet_id
                doc = root if is_root else self._document(sheet_id, options, fingerprint, sheet.title)
                definitions = {}
                for location in sheet.regions:
                    for c, _, _, _ in board.regions[location.region_id].placed:
                        definitions[board.views[c.path].lib_id] = board.views[c.path].definition
                try:
                    ground = ground_symbol(resolver, options.ground_style)
                    definitions["power:GND"] = ground
                except (LookupError, FileNotFoundError):
                    ground = None
                doc.append(node("lib_symbols", *[definitions[k] for k in sorted(definitions)]))
                ground_positions: set[Point] = set()
                sheet_segments = []
                for location in sheet.regions:
                    sheet_segments.extend(
                        self._render_region(
                            doc,
                            board,
                            board.regions[location.region_id],
                            location,
                            sheet_id,
                            instance_path,
                            net_pages,
                            ground,
                            ground_positions,
                            diagnostics,
                        )
                    )
                self._inter_region_wires(doc, board, sheet, sheet_id, sheet_segments)
                from .KiCadSchematicScene import place_document_labels

                evidence = place_document_labels(doc, sheet_segments, sheet_id)
                label_evidence.append(evidence)
                for unknown in evidence["unresolved_anchors"]:
                    diagnostics.append(
                        SchematicDiagnostic(
                            unknown["identity"], "label anchor missing or ambiguous on sheet " + sheet.title
                        )
                    )
                for conflict in evidence["conflicts"]:
                    diagnostics.append(
                        SchematicDiagnostic(
                            conflict["identity"],
                            "label collision on sheet " + sheet.title + ": " + json.dumps(conflict, sort_keys=True),
                        )
                    )
                if is_root:
                    continue
                filename = board.prefix + "_" + uid(sheet.id)[:12] + ".kicad_sch"
                files[filename] = sexpdata.dumps(doc) + "\n"
                parent_doc = index_docs[child_index // 40] if len(content) > 40 else root
                slot = child_index % 40
                self._sheet_link(
                    parent_doc,
                    board.prefix,
                    sheet_id,
                    parent_path,
                    sheet.title,
                    filename,
                    20 + (slot // 10) * 90,
                    50 + (slot % 10) * 14,
                    child_index + 2,
                )
            for bucket, index_doc in sorted(index_docs.items()):
                index_id = uid(board.prefix, "contents", str(bucket))
                filename = board.prefix + "_contents_" + str(bucket + 1) + ".kicad_sch"
                files[filename] = sexpdata.dumps(index_doc) + "\n"
                self._sheet_link(
                    root,
                    board.prefix,
                    index_id,
                    "/" + board.root_id,
                    f"Contents {bucket + 1}",
                    filename,
                    20 + (bucket // 10) * 90,
                    50 + (bucket % 10) * 14,
                    len(sheets) + bucket + 1,
                )
            if overview:
                render_overview(
                    root,
                    board,
                    next(d for d in overview_data["boards"] if d["scope"] == board.scope),
                    options,
                )
            files[root_filename] = sexpdata.dumps(root) + "\n"
        files["net-labels.json"] = json.dumps({b.scope: b.names for b in boards}, indent=2, ensure_ascii=False) + "\n"
        files["overview.json"] = json.dumps(overview_data, indent=2, ensure_ascii=False) + "\n"
        files["sheet-plan.json"] = json.dumps(plan.to_dict(), indent=2, ensure_ascii=False) + "\n"
        from .KiCadSchematicReadability import inspect_documents

        patterns: list[dict[str, Any]] = []
        for board in boards:
            patterns.extend(
                dict(scope=board.scope, **p.to_dict())
                for p in cast("SchematicCircuitModel", board.circuit_model).patterns
            )
        files["circuit-model.json"] = (
            json.dumps(
                dict(
                    schema=1,
                    boards=[
                        dict(scope=b.scope, **cast("SchematicCircuitModel", b.circuit_model).to_dict()) for b in boards
                    ],
                ),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        readability = inspect_documents(files, diagnostics, patterns)
        files["readability.json"] = json.dumps(readability, indent=2, ensure_ascii=False) + "\n"
        files["routing.json"] = (
            json.dumps(
                dict(
                    schema=1,
                    optimize_routes=options.optimize_routes,
                    metric_scope="Local routed wires only; excludes fixed pin stubs and inter-region links",
                    regions=[
                        dict(scope=b.scope, region=d.spec.title, **d.routing)
                        for b in boards
                        for d in b.regions.values()
                        if d.routing
                    ],
                ),
                indent=2,
            )
            + "\n"
        )
        placement_records = [
            dict(
                scope=b.scope,
                region=d.spec.title,
                components=[dict(path=c.path, **getattr(c, "placement_evidence", {})) for c, _, _, _ in d.placed],
            )
            for b in boards
            for d in b.regions.values()
        ]
        atom_evidence = {
            (b.scope, tuple(getattr(c, "placement_evidence", {}).get("atom", [c.path]))): getattr(
                c, "placement_evidence", {}
            )
            for b in boards
            for d in b.regions.values()
            for c, _, _, _ in d.placed
        }
        layout = dict(
            schema=1,
            exporter_version=VERSION,
            patterns=patterns,
            regions=placement_records,
            label_placement=label_evidence,
            summary=dict(
                label_conflicts=sum(len(e["conflicts"]) for e in label_evidence),
                label_moves=sum(len(e["moves"]) for e in label_evidence),
                route_fallbacks=sum(len(d.failed_routes) for b in boards for d in b.regions.values()),
                regions=len(plan.regions),
                sheets=len(plan.sheets),
                atomic_groups=len(
                    {
                        tuple(getattr(c, "placement_evidence", {}).get("atom", [c.path]))
                        for b in boards
                        for d in b.regions.values()
                        for c, _, _, _ in d.placed
                    }
                ),
                search_candidates=sum(e.get("candidates", 0) for e in atom_evidence.values()),
            ),
        )
        files["layout.json"] = json.dumps(layout, indent=2, ensure_ascii=False) + "\n"
        manifest = dict(
            exporter_version=VERSION,
            source=options.source,
            design=options.design_name,
            fingerprint=fingerprint,
            boards=board_records,
            files=sorted(list(files) + ["manifest.json"]),
            planning=dict(
                regions=len(plan.regions),
                sheets=len(plan.sheets),
                total_documents=sum(n.endswith(".kicad_sch") for n in files),
                diagnostics=list(plan.diagnostics),
            ),
            diagnostics=[vars(d) for d in diagnostics],
            symbol_coverage=[
                dict(component.symbol_coverage, scope=board.scope)
                for board in boards
                for component in sorted(
                    {c.path: c for drawing in board.regions.values() for c, _, _, _ in drawing.placed}.values(),
                    key=lambda c: c.path,
                )
            ],
        )
        files["manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        return SchematicExport(files, diagnostics)

    @staticmethod
    def _is_backbone(net: str) -> bool:
        return any(
            word.startswith("pwr") or word in ("gnd", "v3v3", "vbus", "vusb", "vbat", "vcell", "power")
            for word in net.lower().split(".")
        )

    @staticmethod
    def _sheet_link(
        doc: SExpr,
        prefix: str,
        identity: str,
        parent_path: str,
        title: str,
        filename: str,
        x: float,
        y: float,
        page: int,
    ) -> None:
        doc.append(
            node(
                "sheet",
                node("at", x, y),
                node("size", 80, 8),
                node("stroke", node("width", 0), node("type", S("default"))),
                node("fill", node("color", 0, 0, 0, 0)),
                node("uuid", identity),
                node(
                    "property",
                    "Sheetname",
                    title,
                    node("at", x, y - 2, 0),
                    node(
                        "effects",
                        node("font", node("size", 1.27, 1.27)),
                        node("justify", S("left")),
                    ),
                ),
                node(
                    "property",
                    "Sheetfile",
                    filename,
                    node("at", x, y + 10, 0),
                    effects(hide=True),
                ),
                node(
                    "instances",
                    node(
                        "project",
                        prefix,
                        node("path", parent_path, node("page", str(page))),
                    ),
                ),
            )
        )

    def _render_region(
        self,
        doc: SExpr,
        board: _PreparedBoard,
        drawing: _RegionDrawing,
        location: SchematicRegionPlacement,
        sheet_id: str,
        instance_path: str,
        net_pages: Mapping[str, set[str]],
        ground_definition: SExpr | None,
        ground_positions: set[Point],
        diagnostics: list[SchematicDiagnostic],
    ) -> list[Wire]:
        bounds = drawing.spec.bounds
        dx, dy = location.x - bounds[0], location.y - bounds[1]

        def move(p: Point) -> Point:
            return (round(p[0] + dx, 4), round(p[1] + dy, 4))

        headings = drawing.heading_positions or tuple(
            (line, size, bounds[0] + 3, bounds[1] + 3 + i * 2.54)
            for i, (line, size) in enumerate(self._region_heading_lines(drawing.spec.title, drawing.placed))
        )
        for line_number, (line, size, hx, hy) in enumerate(headings):
            doc.append(
                node(
                    "text",
                    line,
                    node("at", *move((hx, hy)), 0),
                    node(
                        "effects",
                        node("font", node("size", size, size)),
                        node("justify", S("left")),
                    ),
                    node(
                        "uuid",
                        uid(board.prefix, drawing.spec.id, "title", str(line_number)),
                    ),
                )
            )
        doc.append(
            node(
                "rectangle",
                node("start", location.x, location.y),
                node(
                    "end",
                    round(location.x + bounds[2] - bounds[0], 4),
                    round(location.y + bounds[3] - bounds[1], 4),
                ),
                node("stroke", node("width", 0.15), node("type", S("default"))),
                node("fill", node("type", S("none"))),
                node("uuid", uid(board.prefix, drawing.spec.id, "border")),
            )
        )
        if not drawing.placed:
            doc.append(
                node(
                    "text",
                    "No physical components in compiled design",
                    node("at", location.x + 3, location.y + 7, 0),
                    node("effects", node("font", node("size", 1.1, 1.1)), node("justify", S("left"))),
                    node("uuid", uid(board.prefix, "empty")),
                )
            )
        views = board.views
        pin_nets = board.pin_nets
        names = board.names
        local_wires = [(net, move(a), move(b)) for net, a, b in drawing.wires]
        for failed_pin, failed_net in drawing.failed_routes:
            diagnostics.append(SchematicDiagnostic(failed_pin[0], "local wire route retained net label: " + failed_net))
        all_segments = list(local_wires)
        from .KiCadSchematicScene import label_islands

        selected_labels = label_islands(
            drawing.placed,
            views,
            pin_nets,
            drawing.wires,
            {net for net, regions in board.net_regions.items() if len(regions) > 1},
        )
        for original, x, y, rotation in drawing.placed:
            x, y = move((x, y))
            component = replace(
                original,
                annotation=move(original.annotation) if original.annotation else None,
            )
            view = views[component.path]
            instance_id = uid(board.prefix, component.path, "symbol")
            instance = node(
                "symbol",
                node("lib_id", view.lib_id),
                node("at", x, y, rotation),
                node("unit", 1),
                node("in_bom", S("yes")),
                node("on_board", S("yes")),
                node("dnp", S("no")),
                node("uuid", instance_id),
            )
            display_value = component.display_value or component.value
            px, py, align = annotation_position(component, view, x, y, rotation)
            for i, (key, value) in enumerate(
                (
                    ("Reference", component.refdes),
                    ("Value", component.value),
                    ("Footprint", component.footprint),
                    ("PBPath", component.path),
                )
            ):
                instance.append(
                    node(
                        "property",
                        key,
                        value,
                        node("at", px, py + i * 2.54, rotation % 180),
                        node(
                            "effects",
                            node("font", node("size", 1.27, 1.27)),
                            *([node("justify", S(align))] if align else []),
                            *([S("hide")] if i > 1 or (i == 1 and display_value != component.value) else []),
                        ),
                    )
                )
            if display_value != component.value:
                instance.append(
                    node(
                        "property",
                        "PBDisplayValue",
                        "\n".join(textwrap.wrap(display_value, 30)),
                        node("at", px, py + 2.54, rotation % 180),
                        node(
                            "effects",
                            node("font", node("size", 1.27, 1.27)),
                            *([node("justify", S(align))] if align else []),
                        ),
                    )
                )
            description_line = 0
            for description in component.descriptions:
                for line in textwrap.wrap(description, 42):
                    doc.append(
                        node(
                            "text",
                            line,
                            node("at", px, py + 10 + description_line * 2.54, 0),
                            effects(1.1),
                            node(
                                "uuid",
                                uid(instance_id, "description", str(description_line)),
                            ),
                        )
                    )
                    description_line += 1
            instance.append(
                node(
                    "instances",
                    node(
                        "project",
                        board.prefix,
                        node(
                            "path",
                            instance_path,
                            node("reference", component.refdes),
                            node("unit", 1),
                        ),
                    ),
                )
            )
            for number, px, py, angle in positioned_pins(view, x, y, rotation):
                instance.append(node("pin", number, node("uuid", uid(instance_id, number))))
                net = pin_nets.get((component.path, number))
                if net is None:
                    continue
                r = math.radians(angle)
                lx = round(px - 5.08 * math.cos(r), 4)
                ly = round(py + 5.08 * math.sin(r), 4)
                all_segments.append((net, (px, py), (lx, ly)))
                if (component.path, number) not in selected_labels and net.lower().split(".")[-1] != "gnd":
                    continue
                if net.lower().split(".")[-1] == "gnd" and ground_definition is not None:
                    if (lx, ly) not in ground_positions:
                        ground_positions.add((lx, ly))
                        gid = uid(sheet_id, str(lx), str(ly), "ground")
                        ref = "#PWR" + gid.replace("-", "")[:10]
                        doc.append(
                            node(
                                "symbol",
                                node("lib_id", "power:GND"),
                                node("at", lx, ly, ground_rotation(angle)),
                                node("unit", 1),
                                node("in_bom", S("no")),
                                node("on_board", S("yes")),
                                node("dnp", S("no")),
                                node("uuid", gid),
                                node(
                                    "property",
                                    "Reference",
                                    ref,
                                    node("at", lx, ly, 0),
                                    effects(hide=True),
                                ),
                                node(
                                    "property",
                                    "Value",
                                    names[net],
                                    node("at", lx, ly + 5.08, 0),
                                    effects(hide=True),
                                ),
                                node("pin", "1", node("uuid", uid(gid, "pin"))),
                                node(
                                    "instances",
                                    node(
                                        "project",
                                        board.prefix,
                                        node(
                                            "path",
                                            instance_path,
                                            node("reference", ref),
                                            node("unit", 1),
                                        ),
                                    ),
                                ),
                            )
                        )
                        ground_label = component.ground_net_labels.get(number)
                        if ground_label:
                            gx, gy = ground_label_position(lx, ly, angle)
                            doc.append(
                                node(
                                    "text",
                                    ground_label,
                                    node("at", gx, gy, 0),
                                    effects(),
                                    node("uuid", uid(gid, "return-identity")),
                                )
                            )
                    continue
                kind = "global_label" if len(net_pages[net]) > 1 else "label"
                a = (180 - int(angle)) % 360
                eff = effects()
                eff.append(
                    node(
                        "justify", S("left" if a in (0, 270) else "right"), *([S("bottom")] if kind == "label" else [])
                    )
                )
                label = node(
                    kind,
                    names[net],
                    node("at", lx, ly, a),
                    eff,
                    node("uuid", uid(instance_id, number, "label")),
                )
                if kind == "global_label":
                    label.append(node("shape", S("bidirectional")))
                    label.append(
                        node(
                            "property",
                            "Intersheetrefs",
                            "${INTERSHEET_REFS}",
                            node("at", lx, ly, 0),
                            effects(hide=True),
                        )
                    )
                doc.append(label)
            doc.append(instance)
        write_wires(doc, all_segments, sheet_id, drawing.spec.id)
        return all_segments

    @staticmethod
    def _inter_region_wires(
        doc: SExpr, board: _PreparedBoard, sheet: SchematicSheet, sheet_id: str, segments: list[Wire]
    ) -> None:
        """Add only short, straight, unobstructed same-net sheet connections.

        Region interfaces keep their labels. No search through other circuits is
        attempted; distant or obstructed interfaces remain labeled connections.
        """
        terminals: dict[str, list[tuple[str, Point]]] = {}
        boxes: list[tuple[str | None, Bounds]] = []
        for location in sheet.regions:
            drawing = board.regions[location.region_id]
            bounds = drawing.spec.bounds
            dx, dy = location.x - bounds[0], location.y - bounds[1]
            heading_boxes = drawing.heading_boxes or (
                (
                    bounds[0],
                    bounds[1],
                    bounds[2],
                    bounds[1]
                    + 5
                    + 2.54 * len(KiCadSchematicExporter._region_heading_lines(drawing.spec.title, drawing.placed)),
                ),
            )
            boxes.extend((None, (x1 + dx, y1 + dy, x2 + dx, y2 + dy)) for x1, y1, x2, y2 in heading_boxes)
            for original, x, y, angle in drawing.placed:
                x, y = round(x + dx, 4), round(y + dy, 4)
                c = replace(
                    original,
                    annotation=(
                        (
                            original.annotation[0] + dx,
                            original.annotation[1] + dy,
                        )
                        if original.annotation
                        else None
                    ),
                )
                view = board.views[c.path]
                min_x, min_y, max_x, max_y = graphic_bounds(view, angle)
                boxes.append((None, (x + min_x, y + min_y, x + max_x, y + max_y)))
                tx, ty, align = annotation_position(c, view, x, y, angle)
                visible = c.display_value or c.value
                lines = (textwrap.wrap(visible, 30) if visible != c.value else visible.splitlines()) or [""]
                width = max([len(c.refdes)] + [len(line) for line in lines]) * 1.27 + 2
                boxes.append(
                    (
                        None,
                        (
                            tx if align else tx - width / 2,
                            ty - 1.5 - len(lines) * 1.27,
                            tx + width if align else tx + width / 2,
                            ty + 3.81 + len(lines) * 1.27,
                        ),
                    )
                )
                for number, px, py, direction in positioned_pins(view, x, y, angle):
                    net = board.pin_nets.get((c.path, number))
                    if net is None:
                        continue
                    r = math.radians(direction)
                    ex = round(px - 5.08 * math.cos(r), 4)
                    ey = round(py + 5.08 * math.sin(r), 4)
                    if net.lower().split(".")[-1] == "gnd":
                        boxes.append((None, ground_bounds(ex, ey, direction, c.ground_net_labels.get(number, ""))))
                        continue
                    rect = pin_label_bounds(board.names[net], ex, ey, direction)
                    boxes.append((net, rect))
                    terminals.setdefault(net, []).append((location.region_id, (ex, ey)))

        def crosses_box(a: Point, b: Point, rect: Bounds) -> bool:
            return (
                a[0] == b[0]
                and rect[0] <= a[0] <= rect[2]
                and max(min(a[1], b[1]), rect[1]) <= min(max(a[1], b[1]), rect[3])
            ) or (
                a[1] == b[1]
                and rect[1] <= a[1] <= rect[3]
                and max(min(a[0], b[0]), rect[0]) <= min(max(a[0], b[0]), rect[2])
            )

        def crosses_segment(a: Point, b: Point, c: Point, d: Point) -> bool:
            return crosses_box(
                a,
                b,
                (min(c[0], d[0]), min(c[1], d[1]), max(c[0], d[0]), max(c[1], d[1])),
            )

        candidates = []
        for net, entries in terminals.items():
            for index, (ra, a) in enumerate(entries):
                for rb, b in entries[index + 1 :]:
                    length = abs(a[0] - b[0]) + abs(a[1] - b[1])
                    if ra != rb and 0 < length <= 50 and (a[0] == b[0] or a[1] == b[1]):
                        candidates.append((length, net, ra, rb, a, b))
        joined: dict[str, dict[str, str]] = {}
        for _, net, ra, rb, a, b in sorted(candidates):
            parent = joined.setdefault(net, {})

            def root(identity: str) -> str:
                while identity in parent:
                    identity = parent[identity]
                return identity

            if root(ra) == root(rb):
                continue
            if any(kind != net and crosses_box(a, b, rect) for kind, rect in boxes):
                continue
            if any(other != net and crosses_segment(a, b, c, d) for other, c, d in segments):
                continue
            parent[root(rb)] = root(ra)
            doc.append(
                node(
                    "wire",
                    node("pts", node("xy", *a), node("xy", *b)),
                    node("stroke", node("width", 0), node("type", S("default"))),
                    node(
                        "uuid",
                        uid(sheet_id, net, ra, rb, str(a), str(b), "region-wire"),
                    ),
                )
            )
            for point in (a, b):
                doc.append(
                    node(
                        "junction",
                        node("at", *point),
                        node("diameter", 0),
                        node("color", 0, 0, 0, 0),
                        node("uuid", uid(sheet_id, net, str(point), "region-junction")),
                    )
                )
            segments.append((net, a, b))

    @staticmethod
    def _display_value(compiled: CompiledDesign, block: NetBlock, mapping: Mapping[str, Any] | None = None) -> str:
        classes = [c.target.name.rsplit(".", 1)[-1].lower() for c in block.path_classes]
        leaf = classes[-1] if classes else ""
        quantities = []
        declared = (mapping or {}).get("lib_id", "")
        if declared in ("Device:C", "Device:C_Polarized"):
            quantities = [("actual_capacitance", "F")]
        elif declared == "Device:R":
            quantities = [("actual_resistance", "Ω")]
        elif declared == "Device:L":
            quantities = [("actual_inductance", "H")]
        elif "crystal" in leaf or "oscillator" in leaf:
            quantities = [("actual_frequency", "Hz")]
        elif "resistor" in leaf:
            quantities = [("actual_resistance", "Ω")]
        elif "capacitor" in leaf:
            quantities = [("actual_capacitance", "F")]
        elif "inductor" in leaf:
            quantities = [("actual_inductance", "H")]
        for parameter, unit in quantities:
            value = compiled.get_value(block.full_path.to_tuple() + (parameter,))
            if value is None:
                value = compiled.get_value(block.full_path.to_tuple() + (parameter.removeprefix("actual_"),))
            if hasattr(value, "lower") and hasattr(value, "upper"):
                interval = cast("Range", value)
                nominal = (interval.lower + interval.upper) / 2
            elif isinstance(value, (float, int)):
                nominal = value
            else:
                continue
            if math.isfinite(nominal):
                for scale, prefix in (
                    (1e9, "G"),
                    (1e6, "M"),
                    (1e3, "k"),
                    (1, ""),
                    (1e-3, "m"),
                    (1e-6, "µ"),
                    (1e-9, "n"),
                    (1e-12, "p"),
                ):
                    if abs(nominal) >= scale * (1 - 1e-10):
                        return f"{nominal / scale:.3g}{prefix}{unit}"
                return "0" + unit
        color = compiled.get_value(block.full_path.to_tuple() + ("actual_color",))
        if isinstance(color, str) and color:
            return color + " LED"
        if block.part:
            return block.part.split(" (")[0]
        return block.value if len(block.value) <= 48 else "\n".join(textwrap.wrap(block.value, 30))

    @staticmethod
    def _document(identity: str, options: SchematicExportOptions, fingerprint: str, group: str) -> SExpr:
        return node(
            "kicad_sch",
            node("version", 20250114),
            node("generator", "polymorphicblocks"),
            node("uuid", identity),
            node("paper", "A3"),
            node(
                "title_block",
                node("title", options.design_name + " / " + group),
                node("comment", 1, options.source),
                node("comment", 2, fingerprint),
            ),
            node(
                "text",
                NOTICE,
                node("at", 20, 15, 0),
                node(
                    "effects",
                    node("font", node("size", 2, 2)),
                    node("justify", S("left")),
                ),
                node("uuid", uid(identity, "notice")),
            ),
            node(
                "text",
                INSTRUCTIONS,
                node("at", 20, 22, 0),
                node(
                    "effects",
                    node("font", node("size", 1.27, 1.27)),
                    node("justify", S("left")),
                ),
                node("uuid", uid(identity, "instructions")),
            ),
        )
