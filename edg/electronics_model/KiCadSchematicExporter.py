"""Deterministic, one-way schematic views of compiled PB physical connectivity."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import tempfile
import textwrap
import uuid
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import sexpdata

from ..core import CompiledDesign
from .NetlistGenerator import NetlistTransform
from .KiCadSchematicPlanner import (
    SchematicRegion,
    SchematicSheetPlan,
    SchematicSheetPlanner,
)
from .KiCadSchematicPresentation import SchematicPresentation
from .KiCadSchematicOverview import SchematicOverview, build_overviews, render_overview
from .KiCadSchematicLayout import (
    annotation_position,
    annotation_bounds,
    ground_bounds,
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
VERSION = "5"
S = sexpdata.Symbol


def node(name: str, *args: Any) -> List[Any]:
    return [S(name), *args]


def children(tree: list, name: str) -> list:
    return [v for v in tree if isinstance(v, list) and v and v[0] == S(name)]


def uid(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps(parts, ensure_ascii=False)))


def effects(size: float = 1.27, hide: bool = False) -> list:
    return node(
        "effects",
        node("font", node("size", size, size)),
        *([S("hide")] if hide else []),
    )


@dataclass(frozen=True)
class SchematicPlacement:
    """Optional Python-owned functional schematic placement, in millimetres."""

    group: str
    x: float
    y: float
    rotation: int = 0
    flip_horizontal: bool = False
    annotation: Optional[Tuple[float, float]] = None


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
        with tempfile.TemporaryDirectory(dir=directory) as stage:
            for name, content in self.files.items():
                Path(stage, name).write_text(content, encoding="utf-8")
            for name in sorted(self.files, key=lambda n: n == "manifest.json"):
                os.replace(Path(stage, name), directory / name)
        for name in previous:
            if name not in self.files:
                (directory / name).unlink(missing_ok=True)


@dataclass
class PhysicalComponent:
    path: str
    refdes: str
    footprint: str
    value: str
    pins: Dict[str, str]
    mapping: Optional[dict]
    group: str
    display_value: str = ""
    annotation: Optional[Tuple[float, float]] = None
    descriptions: Tuple[str, ...] = ()
    net_labels: Mapping[str, str] = field(default_factory=dict)


@dataclass
class SymbolView:
    definition: list
    pins: List[Tuple[str, float, float, float]]
    lib_id: str


class SymbolResolver:
    def __init__(self, directories: Sequence[str]):
        self.directories = directories
        self.libraries: Dict[str, dict] = {}

    def load(self, lib_id: str, stack: Tuple[str, ...] = ()) -> list:
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
    sides = {"left": [], "right": [], "top": [], "bottom": []}
    declared_names = (component.mapping or {}).get("pin_names", {})
    display_pins = {number: declared_names.get(number, name) for number, name in component.pins.items()}
    for number, name in sorted(display_pins.items()):
        role = name.removesuffix(".net").lower()
        if role in ("gnd", "vss", "com"):
            side = "bottom"
        elif role in ("pwr", "vdd", "vcc", "vs", "vddio"):
            side = "top"
        elif role.startswith(("out", "vout", "bat", "chrg", "alrt", "alert", "int", "dout")):
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
    half_height = (rows + 1) * 1.27
    half_width = max(
        10.16,
        max([len(v.removesuffix(".net")) for v in display_pins.values()] + [1]) * 0.8 + 5.08,
        max(len(sides["top"]), len(sides["bottom"])) * 1.27 + 2.54,
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
    positions = []
    for side, entries in sides.items():
        for i, (number, name) in enumerate(entries):
            offset = (i - (len(entries) - 1) / 2) * 2.54
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
    placed: list
    wires: list
    failed_routes: list


@dataclass
class _PreparedBoard:
    scope: str
    prefix: str
    root_id: str
    views: dict
    pin_nets: dict
    names: dict
    regions: dict
    net_regions: dict = field(default_factory=dict)


class KiCadSchematicExporter:
    def prepare_regions(self, compiled: CompiledDesign, options: SchematicExportOptions):
        """Prepare the same measured regions consumed by planning and rendering."""
        boards, fingerprint, _, _ = self._prepare_boards(compiled, options)
        return tuple(d.spec for b in boards for d in b.regions.values()), fingerprint

    def _prepare_boards(self, compiled: CompiledDesign, options: SchematicExportOptions):
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
            resolved = {
                "scope": str(scope),
                "blocks": [
                    list(b[:4])
                    + [
                        str(b.full_path),
                        compiled.get_value(b.full_path.to_tuple() + ("fp_pinning",)),
                        compiled.get_value(b.full_path.to_tuple() + ("sch_symbol",)),
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
                    v.split("=", 1) for v in compiled.get_value(b.full_path.to_tuple() + ("fp_pinning",))
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
            for block in netlist.blocks:
                path = str(block.full_path)
                raw = compiled.get_value(block.full_path.to_tuple() + ("fp_pinning",))
                pins = dict(v.split("=", 1) for v in raw)
                mapping_raw = compiled.get_value(block.full_path.to_tuple() + ("sch_symbol",))
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
                component.display_value = self._display_value(compiled, block)
                if component.mapping is None:
                    try:
                        from .KiCadSymbolRegistry import infer_symbol

                        classes = [c.target.name for c in block.path_classes]
                        component.mapping = infer_symbol(component, classes, block.part, resolver)
                    except ImportError:
                        pass
            for component in components:
                entry = presentation.components.get(component.path, {})
                if entry.get("display_value"):
                    component.display_value = entry["display_value"]
                from .KiCadSchematicRoles import infer_pin_names, infer_description

                classes = [
                    c.target.name
                    for c in next(b for b in netlist.blocks if str(b.full_path) == component.path).path_classes
                ]
                physical_block = next(b for b in netlist.blocks if str(b.full_path) == component.path)
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
            from .KiCadCompositeSymbols import resistor_array_symbol

            classes_by_path = {str(b.full_path): [c.target.name for c in b.path_classes] for b in netlist.blocks}
            views = {}
            for component in components:
                composite = resistor_array_symbol(component, classes_by_path[component.path])
                if composite is not None:
                    views[component.path] = SymbolView(*composite)
                    continue
                try:
                    if not (component.mapping or {}).get("lib_id"):
                        raise LookupError("no schematic symbol mapping")
                    views[component.path] = resolver.resolve(component)
                except (LookupError, FileNotFoundError) as error:
                    diagnostics.append(SchematicDiagnostic(component.path, str(error)))
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

                        def reflect(tree):
                            if isinstance(tree, list) and tree:
                                if (
                                    str(tree[0]) in ("at", "start", "end", "xy", "center")
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
            from .KiCadSchematicLabels import readable_labels

            names = readable_labels(n.name for n in netlist.nets)
            for component in components:
                component.net_labels = {
                    number: names[pin_nets[(component.path, number)]]
                    for number in component.pins
                    if (component.path, number) in pin_nets
                }
            regroup(components, pin_nets, views)
            for component in components:
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
            for group in sorted({c.group for c in components}):
                members = [c for c in components if c.group == group]
                hints = [options.placements.get(c.path) for c in members]
                hinted = any(hints)
                if hinted:
                    if not all(hints):
                        raise ValueError("all members of hinted group require placements: " + group)
                    batches = [[(c, h.x, h.y, h.rotation) for c, h in zip(members, hints)]]
                elif group == "Mechanical notes":
                    batches = [[(c, 40 + (i % 9) * 35, 220 + (i // 9) * 25, 0) for i, c in enumerate(members)]]
                else:
                    batches = place_group(members, views, pin_nets)
                pending = list(batches)
                part = 0
                while pending:
                    placed = pending.pop(0)
                    wires, _, failed = route_local(placed, views, pin_nets)
                    bounds = self._region_bounds(placed, views, pin_nets, names, wires, group)
                    width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
                    if (
                        (width > 375 or height > 225 or (width > 210 and height > 205))
                        and len(placed) > 1
                        and not hinted
                    ):
                        subsets = split_group(placed, views, pin_nets)
                        if subsets is None:
                            raise ValueError("indivisible functional region exceeds A3: " + group)
                        for subset in subsets:
                            pending.extend(place_group([c for c, _, _, _ in subset], views, pin_nets))
                        diagnostics.append(
                            SchematicDiagnostic(
                                group,
                                "continuation: measured circuit region requires functional continuation",
                            )
                        )
                        continue
                    if width > 375 or height > 225 or (width > 210 and height > 205):
                        raise ValueError(
                            f"region {group!r} ({width:.1f} x {height:.1f} mm) exceeds A3; revise presentation without shrinking text"
                        )
                    part += 1
                    title = group if part == 1 else group + " /" + str(part)
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
                        kind="mechanical"
                        if group == "Mechanical notes" and all(not c.pins for c in members)
                        else "circuit",
                    )
                    board.regions[identity] = _RegionDrawing(spec, placed, wires, failed)
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
                    for pin in c.pins:
                        net = pin_nets.get((c.path, pin))
                        if net is not None:
                            board.net_regions.setdefault(net, set()).add(identity)
            boards.append(board)
        if set(presentation.groups) - used_groups:
            raise ValueError(
                "presentation references unknown groups: " + str(sorted(set(presentation.groups) - used_groups))
            )
        digest.update(json.dumps(presentation.to_dict(), sort_keys=True, ensure_ascii=False).encode("utf-8"))
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
        return boards, digest.hexdigest(), resolver, diagnostics

    @staticmethod
    def _region_bounds(placed, views, pin_nets, names, wires, title=""):
        points = []
        for c, x, y, angle in placed:
            xmin, ymin, xmax, ymax = graphic_bounds(views[c.path], angle)
            points.extend(((x + xmin, y + ymin), (x + xmax, y + ymax)))
            tx, ty, align = annotation_position(c, views[c.path], x, y, angle)
            ax1, ay1, ax2, ay2 = annotation_bounds(c, tx, ty, angle)
            points.extend(((ax1, ay1), (ax2, ay2)))
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
                    gx1, gy1, gx2, gy2 = ground_bounds(ex, ey, direction)
                    points.extend(((gx1, gy1), (gx2, gy2)))
                    continue
                length = len(names[net]) * 1.27 + 3
                if direction == 0:
                    bounds = (ex - length, ey - 1.5, ex, ey + 1.5)
                elif direction == 180:
                    bounds = (ex, ey - 1.5, ex + length, ey + 1.5)
                elif direction == 270:
                    bounds = (ex - 1.5, ey - length, ex + 1.5, ey)
                else:
                    bounds = (ex - 1.5, ey, ex + 1.5, ey + length)
                points.extend(((bounds[0], bounds[1]), (bounds[2], bounds[3])))
        for _, a, b in wires:
            points.extend((a, b))
        if not points:
            return (0, 0, 50, 10)
        heading = textwrap.wrap(title + " /999", 42) or [""]
        xmin = min(p[0] for p in points) - 3
        ymin = min(p[1] for p in points) - (6 + len(heading) * 2.54)
        xmax = max(
            max(p[0] for p in points) + 3,
            xmin + max(len(line) for line in heading) * 1.2 + 6,
        )
        return (
            round(xmin, 4),
            round(ymin, 4),
            round(xmax, 4),
            round(max(p[1] for p in points) + 3, 4),
        )

    def _plan_compiled(self, compiled, options):
        boards, fingerprint, _, _ = self._prepare_boards(compiled, options)
        return self._plan_prepared(boards, fingerprint, options)

    @staticmethod
    def _plan_prepared(boards, fingerprint, options):
        regions = tuple(d.spec for b in boards for d in b.regions.values())
        adjacency = {}
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

    def overview(self, compiled: CompiledDesign, options: SchematicExportOptions) -> dict:
        """Preview the same compiled, witnessed functional overview emitted by export."""
        boards, fingerprint, _, _ = self._prepare_boards(compiled, options)
        plan = self._plan_prepared(boards, fingerprint, options)
        return build_overviews(boards, plan, options.overview)

    def readability(self, compiled: CompiledDesign, options: SchematicExportOptions) -> dict:
        return json.loads(self.export(compiled, options).files["readability.json"])

    def export(self, compiled: CompiledDesign, options: SchematicExportOptions) -> SchematicExport:
        boards, fingerprint, resolver, diagnostics = self._prepare_boards(compiled, options)
        plan = self._plan_prepared(boards, fingerprint, options)
        overview_data = build_overviews(boards, plan, options.overview)
        files = {}
        board_records = []
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
            net_pages = {}
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
                    ground = resolver.load("power:GND")
                    definitions["power:GND"] = ground
                except (LookupError, FileNotFoundError):
                    ground = None
                doc.append(node("lib_symbols", *[definitions[k] for k in sorted(definitions)]))
                ground_positions = set()
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
        from .KiCadSchematicPatterns import discover_patterns

        patterns = []
        for board in boards:
            components = [c for d in board.regions.values() for c, _, _, _ in d.placed]
            patterns.extend(
                dict(scope=board.scope, **p.to_dict())
                for p in discover_patterns(components, board.pin_nets, board.views)
            )
        readability = inspect_documents(files, diagnostics, patterns)
        files["readability.json"] = json.dumps(readability, indent=2, ensure_ascii=False) + "\n"
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
        )
        files["manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        return SchematicExport(files, diagnostics)

    @staticmethod
    def _is_backbone(net):
        return any(
            word.startswith("pwr") or word in ("gnd", "v3v3", "vbus", "vusb", "vbat", "vcell", "power")
            for word in net.lower().split(".")
        )

    @staticmethod
    def _sheet_link(doc, prefix, identity, parent_path, title, filename, x, y, page):
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
        doc,
        board,
        drawing,
        location,
        sheet_id,
        instance_path,
        net_pages,
        ground_definition,
        ground_positions,
        diagnostics,
    ):
        bounds = drawing.spec.bounds
        dx, dy = location.x - bounds[0], location.y - bounds[1]

        def move(p):
            return (round(p[0] + dx, 4), round(p[1] + dy, 4))

        for line_number, line in enumerate(textwrap.wrap(drawing.spec.title, 42) or [""]):
            doc.append(
                node(
                    "text",
                    line,
                    node("at", location.x + 3, location.y + 3 + line_number * 2.54, 0),
                    node(
                        "effects",
                        node("font", node("size", 1.5, 1.5)),
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
        for key, net in drawing.failed_routes:
            diagnostics.append(SchematicDiagnostic(key[0], "local wire route retained net label: " + net))
        routed_nets = {net for net, _, _ in local_wires}
        all_segments = list(local_wires)
        labeled_nets = set()
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
                if (
                    net in routed_nets
                    and len(board.net_regions[net]) == 1
                    and not any(n == net for _, n in drawing.failed_routes)
                ):
                    continue
                if (
                    net in routed_nets
                    and net in labeled_nets
                    and not any(k == (component.path, number) for k, _ in drawing.failed_routes)
                ):
                    continue
                labeled_nets.add(net)
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
                    continue
                kind = "global_label" if len(net_pages[net]) > 1 else "label"
                a = (180 - int(angle)) % 360
                eff = effects()
                eff.append(node("justify", S("left" if a in (0, 270) else "right")))
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
        self._wires(doc, all_segments, sheet_id, drawing.spec.id)
        return all_segments

    @staticmethod
    def _inter_region_wires(doc, board, sheet, sheet_id, segments):
        """Add only short, straight, unobstructed same-net sheet connections.

        Region interfaces keep their labels. No search through other circuits is
        attempted; distant or obstructed interfaces remain labeled connections.
        """
        terminals = {}
        boxes = []
        for location in sheet.regions:
            drawing = board.regions[location.region_id]
            bounds = drawing.spec.bounds
            dx, dy = location.x - bounds[0], location.y - bounds[1]
            boxes.append(
                (
                    None,
                    (
                        location.x,
                        location.y,
                        location.x + bounds[2] - bounds[0],
                        location.y + 5 + 2.54 * len(textwrap.wrap(drawing.spec.title, 42)),
                    ),
                )
            )
            for original, x, y, angle in drawing.placed:
                x, y = round(x + dx, 4), round(y + dy, 4)
                c = replace(
                    original,
                    annotation=(
                        original.annotation[0] + dx,
                        original.annotation[1] + dy,
                    )
                    if original.annotation
                    else None,
                )
                view = board.views[c.path]
                a, b, d, e = graphic_bounds(view, angle)
                boxes.append((None, (x + a, y + b, x + d, y + e)))
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
                        boxes.append((None, ground_bounds(ex, ey, direction)))
                        continue
                    length = len(board.names[net]) * 1.27 + 3
                    if direction == 0:
                        rect = (ex - length, ey - 1.5, ex, ey + 1.5)
                    elif direction == 180:
                        rect = (ex, ey - 1.5, ex + length, ey + 1.5)
                    elif direction == 270:
                        rect = (ex - 1.5, ey - length, ex + 1.5, ey)
                    else:
                        rect = (ex - 1.5, ey, ex + 1.5, ey + length)
                    boxes.append((net, rect))
                    terminals.setdefault(net, []).append((location.region_id, (ex, ey)))

        def crosses_box(a, b, rect):
            return (
                a[0] == b[0]
                and rect[0] <= a[0] <= rect[2]
                and max(min(a[1], b[1]), rect[1]) <= min(max(a[1], b[1]), rect[3])
            ) or (
                a[1] == b[1]
                and rect[1] <= a[1] <= rect[3]
                and max(min(a[0], b[0]), rect[0]) <= min(max(a[0], b[0]), rect[2])
            )

        def crosses_segment(a, b, c, d):
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
        joined = {}
        for _, net, ra, rb, a, b in sorted(candidates):
            parent = joined.setdefault(net, {})

            def root(identity):
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
    def _wires(doc, all_segments, sheet_id, region_id):
        for net in sorted({n for n, _, _ in all_segments}):
            segments = [(a, b) for n, a, b in all_segments if n == net and a != b]
            candidates = {p for pair in segments for p in pair}
            edges = set()
            for a, b in segments:
                cuts = [
                    p
                    for p in candidates
                    if (a[0] == b[0] == p[0] and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))
                    or (a[1] == b[1] == p[1] and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]))
                ]
                cuts.sort()
                edges.update((u, v) for u, v in zip(cuts, cuts[1:]) if u != v)
            degrees = {}
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

    @staticmethod
    def _display_value(compiled, block) -> str:
        classes = [c.target.name.rsplit(".", 1)[-1].lower() for c in block.path_classes]
        leaf = classes[-1] if classes else ""
        quantities = []
        if "crystal" in leaf or "oscillator" in leaf:
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
                nominal = (value.lower + value.upper) / 2
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
    def _document(identity: str, options: SchematicExportOptions, fingerprint: str, group: str) -> list:
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
