"""Shared, deterministic circuit presentation backed by physical connectivity.

This model describes existing compiled terminals only. Authored flow and function
are presentation intent; they never redefine electrical topology.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Collection, Mapping, Optional, Sequence
from .KiCadSchematicTypes import PinNets, Views

if TYPE_CHECKING:
    from .KiCadSchematicExporter import PhysicalComponent
    from .KiCadSchematicPresentation import SchematicPresentation


from collections import defaultdict
from dataclasses import dataclass
import hashlib
from typing import Tuple

from .KiCadSchematicPatterns import SchematicPattern, discover_patterns, terminal_roles

BOUNDARY_ROLES = frozenset(("input", "output", "supply", "return", "control", "feedback", "bidirectional"))
TEMPLATES = frozenset(
    (
        "auto",
        "generic",
        "buck",
        "four_switch_bridge",
        "gate_driver",
        "repeated_channel",
        "connector_protection",
        "mcu_support",
        "series_path",
        "controller_support",
    )
)
SUPPLY_ROLES = frozenset(("gnd", "vss", "pgnd", "vdd", "vcc", "pwr", "vin", "vout", "pwr_in", "pwr_out", "vp", "vn"))


def _text(value: object, what: str) -> None:
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > 240:
        raise ValueError(what + " must be trimmed nonempty text of at most 240 characters")


def _paths(value: object, what: str) -> None:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError(what + " must be a nonempty array")
    for item in value:
        _text(item, what)
    if len(set(value)) != len(value):
        raise ValueError(what + " contains duplicate component paths")


def validate_circuit_entries(
    entries: Sequence[Mapping[str, Any]], inventories: Optional[Mapping[str, Mapping[str, str]]] = None
) -> None:
    """Validate input syntax and, when available, exact physical references."""
    ids, ownership = set(), {}
    for entry in entries:
        if (
            not isinstance(entry, Mapping)
            or set(entry) - {"id", "title", "summary", "components", "template", "stages", "boundaries"}
            or not {"id", "title", "summary", "components"} <= set(entry)
        ):
            raise ValueError("circuit has unknown or missing fields")
        for key in ("id", "title", "summary"):
            _text(entry[key], "circuit " + key)
        identity = entry["id"]
        if identity in ids:
            raise ValueError("duplicate circuit id: " + identity)
        ids.add(identity)
        _paths(entry["components"], "circuit components")
        members = set(entry["components"])
        for path in members:
            if path in ownership:
                raise ValueError("component belongs to conflicting circuits: " + path)
            ownership[path] = identity
            if inventories is not None and path not in inventories:
                raise ValueError("circuit references missing component: " + path)
        template = entry.get("template", "auto")
        if not isinstance(template, str) or template not in TEMPLATES:
            raise ValueError("unsupported circuit template: " + str(template))
        stages = entry.get("stages", [])
        boundaries = entry.get("boundaries", [])
        if not isinstance(stages, (list, tuple)) or not isinstance(boundaries, (list, tuple)):
            raise ValueError("circuit stages and boundaries must be arrays")
        stage_ids: set[str] = set()
        stage_members: set[str] = set()
        for stage in stages:
            if not isinstance(stage, Mapping) or set(stage) != {"id", "components"}:
                raise ValueError("circuit stage requires id and components")
            _text(stage["id"], "stage id")
            _paths(stage["components"], "stage components")
            if stage["id"] in stage_ids:
                raise ValueError("duplicate stage id: " + stage["id"])
            stage_ids.add(stage["id"])
            if not set(stage["components"]) <= members:
                raise ValueError("stage components must belong to their circuit: " + identity)
            if stage_members & set(stage["components"]):
                raise ValueError("component belongs to conflicting stages: " + identity)
            stage_members.update(stage["components"])
        boundary_keys = set()
        for boundary in boundaries:
            if not isinstance(boundary, Mapping) or set(boundary) != {"component", "pin", "name", "role"}:
                raise ValueError("circuit boundary requires component, pin, name and role")
            for key in ("component", "pin", "name", "role"):
                _text(boundary[key], "boundary " + key)
            if boundary["role"] not in BOUNDARY_ROLES:
                raise ValueError("unsupported boundary role: " + boundary["role"])
            path, pin = boundary["component"], boundary["pin"]
            if path not in members:
                raise ValueError("boundary component must belong to its circuit: " + path)
            if (path, pin) in boundary_keys:
                raise ValueError("duplicate circuit boundary terminal: " + path + ":" + pin)
            boundary_keys.add((path, pin))
            if inventories is not None and pin not in inventories[path]:
                raise ValueError("circuit boundary references unknown physical pin: " + path + ":" + pin)


@dataclass(frozen=True)
class CircuitStage:
    id: str
    components: Tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return dict(id=self.id, components=list(self.components))


@dataclass(frozen=True)
class CircuitBoundary:
    component: str
    pin: str
    name: str
    role: str
    net: str

    def to_dict(self) -> dict[str, Any]:
        return dict(component=self.component, pin=self.pin, name=self.name, role=self.role, net=self.net)


@dataclass(frozen=True)
class SchematicCircuit:
    id: str
    title: str
    summary: str
    components: Tuple[str, ...]
    template: str = "auto"
    stages: Tuple[CircuitStage, ...] = ()
    boundaries: Tuple[CircuitBoundary, ...] = ()
    patterns: Tuple[SchematicPattern, ...] = ()
    provenance: str = "automatic"

    @property
    def primary_nets(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {b.net for b in self.boundaries if b.role in ("input", "output", "bidirectional")}
                | {n for p in self.patterns if p.kind == "serial_data_chain" for n in p.nets}
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return dict(
            id=self.id,
            title=self.title,
            summary=self.summary,
            components=list(self.components),
            template=self.template,
            stages=[s.to_dict() for s in self.stages],
            boundaries=[b.to_dict() for b in self.boundaries],
            patterns=[p.to_dict() for p in self.patterns],
            primary_nets=list(self.primary_nets),
            provenance=self.provenance,
        )


@dataclass(frozen=True)
class SchematicCircuitModel:
    circuits: Tuple[SchematicCircuit, ...]
    patterns: Tuple[SchematicPattern, ...]
    diagnostics: Tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return dict(
            schema=1,
            circuits=[c.to_dict() for c in self.circuits],
            patterns=[p.to_dict() for p in self.patterns],
            diagnostics=list(self.diagnostics),
        )


def _rails(components: Sequence[PhysicalComponent], pin_nets: PinNets) -> set[str]:
    return {
        pin_nets[c.path, number]
        for c in components
        for role, number in terminal_roles(c, pin_nets).items()
        if role in SUPPLY_ROLES and (c.path, number) in pin_nets
    }


def _validate_template(
    entry: Mapping[str, Any],
    members: Collection[str],
    by_path: Mapping[str, PhysicalComponent],
    pin_nets: PinNets,
    views: Views,
    patterns: Sequence[SchematicPattern],
) -> None:
    template = entry.get("template", "auto")
    if template in ("auto", "generic"):
        return
    kinds = {p.kind for p in patterns if set(p.components) <= set(members)}
    valid = False
    if template in ("buck", "four_switch_bridge"):
        from .KiCadSchematicPower import power_topology

        topology = power_topology(members, by_path, views, pin_nets) if views else None
        valid = topology is not None and topology["kind"] == {"buck": "buck", "four_switch_bridge": "bridge"}[template]
    elif template == "gate_driver":
        valid = "gate_driver_stage" in kinds
    elif template == "repeated_channel":
        valid = bool(kinds & {"repeated_subcircuit", "serial_data_chain"})
    elif template == "series_path":
        valid = bool(kinds & {"indicator_branch", "serial_data_chain"})
    elif template in ("controller_support", "mcu_support"):
        valid = "local_decoupling" in kinds and any(len(by_path[p].pins) >= 8 for p in members)
    elif template == "connector_protection":
        # A protection template must establish its series stages explicitly.
        # Merely sharing a rail or a connector-like name is insufficient.
        symbol = {p: views[p].lib_id.split("_PB_", 1)[0] for p in members} if views else {}
        connectors = {p for p, sid in symbol.items() if sid.startswith(("Connector_Generic:Conn_", "Connector:Conn_"))}
        diodes = {
            p for p, sid in symbol.items() if sid in ("Device:D", "Device:D_Zener", "Device:D_TVS", "Device:D_Schottky")
        }
        returns = {
            pin_nets[p, number]
            for p in members
            for role, number in terminal_roles(by_path[p], pin_nets).items()
            if role in ("gnd", "vss", "pgnd", "vn") and (p, number) in pin_nets
        }
        terminal_nets = {p: {pin_nets[p, pin] for pin in by_path[p].pins if (p, pin) in pin_nets} for p in members}
        rails = _rails([by_path[p] for p in members], pin_nets)
        valid = len(entry.get("stages", ())) >= 2 and any(
            len(terminal_nets[d]) == 2
            and bool(terminal_nets[d] & returns)
            and bool((terminal_nets[d] - rails - returns) & terminal_nets[c])
            for d in diodes
            for c in connectors
        )
    if not valid:
        raise ValueError(
            "circuit template lacks required compiled connectivity evidence: " + entry["id"] + " (" + template + ")"
        )


def build_circuits(
    components: Sequence[PhysicalComponent],
    pin_nets: PinNets,
    views: Views,
    presentation: SchematicPresentation,
    *,
    scope_by_path: Optional[Mapping[str, str]] = None,
) -> SchematicCircuitModel:
    """Discover once, then overlay source-owned circuit boundaries and intent.

    Called per board scope: disjoint authored circuits are skipped and a partial
    intersection is an error. Optional scope metadata also permits full-design
    callers to reject a circuit spanning independent board scopes.
    """
    by_path = {c.path: c for c in components}
    patterns = tuple(
        sorted(discover_patterns(components, pin_nets, views), key=lambda p: (p.kind, p.components, p.nets))
    )
    circuits, diagnostics, claimed = [], [], set()
    rails = _rails(components, pin_nets)
    endpoints = defaultdict(set)
    for (path, pin), net in pin_nets.items():
        if path in by_path:
            endpoints[net].add(path)
    # Syntax/global physical references were checked by presentation.validate;
    # repeat syntax here so direct model clients receive the same strictness.
    validate_circuit_entries(presentation.circuits)
    authored_titles = set()
    for entry in sorted(presentation.circuits, key=lambda e: e["id"]):
        members = set(entry["components"])
        if not members & set(by_path):
            continue
        if members - set(by_path):
            raise ValueError("circuit crosses board scope or references missing components: " + entry["id"])
        if scope_by_path is not None and len({scope_by_path[p] for p in members}) != 1:
            raise ValueError("circuit crosses independent board scopes: " + entry["id"])
        if entry["title"] in authored_titles:
            raise ValueError("duplicate circuit title within board scope: " + entry["title"])
        authored_titles.add(entry["title"])
        validate_circuit_entries([entry], {p: c.pins for p, c in by_path.items()})
        boundary = []
        for item in entry.get("boundaries", ()):
            key = item["component"], item["pin"]
            if key not in pin_nets:
                raise ValueError("circuit boundary has no compiled net: " + ":".join(key))
            boundary.append(CircuitBoundary(**item, net=pin_nets[key]))
        stages = tuple(CircuitStage(s["id"], tuple(s["components"])) for s in entry.get("stages", ()))
        for first, second in zip(stages, stages[1:]):
            first_nets = {n for n, ends in endpoints.items() if ends & set(first.components)}
            second_nets = {n for n, ends in endpoints.items() if ends & set(second.components)}
            authored_flow = {b.net for b in boundary if b.role in ("input", "output", "bidirectional")}
            if not ((first_nets & second_nets) - rails or first_nets & second_nets & authored_flow):
                raise ValueError(
                    "ordered circuit stages lack a non-supply connection: "
                    + entry["id"]
                    + ":"
                    + first.id
                    + " -> "
                    + second.id
                )
        local_patterns = tuple(p for p in patterns if set(p.components) <= members)
        _validate_template(entry, tuple(sorted(members)), by_path, pin_nets, views, local_patterns)
        circuits.append(
            SchematicCircuit(
                entry["id"],
                entry["title"],
                entry["summary"],
                tuple(sorted(members)),
                entry.get("template", "auto"),
                stages,
                tuple(boundary),
                local_patterns,
                "explicit",
            )
        )
        claimed.update(members)
    # Merge verified support ownership only. A serial chain records order but
    # remains cuttable between complete locally supported channels.
    remaining = set(by_path) - claimed
    parent = {p: p for p in remaining}

    def root(p: str) -> str:
        while parent[p] != p:
            p = parent[p]
        return p

    for pattern in patterns:
        members = set(pattern.components)
        if pattern.kind == "serial_data_chain" or not members <= remaining:
            continue
        for p in sorted(members)[1:]:
            a, b = root(min(members)), root(p)
            parent[max(a, b)] = min(a, b)
    groups = defaultdict(set)
    for path in sorted(remaining):
        groups[root(path)].add(path)
    for _, group in sorted(groups.items()):
        automatic_members = tuple(sorted(group))
        local = tuple(p for p in patterns if set(p.components) <= group)
        identity = "auto_" + hashlib.sha256("\0".join(automatic_members).encode()).hexdigest()[:16]
        kinds = sorted({p.kind for p in local})
        title = " / ".join(k.replace("_", " ") for k in kinds) if kinds else automatic_members[0]
        # No automatic summary makes a functional claim beyond its evidence.
        boundary = []
        for path in automatic_members:
            roles = terminal_roles(by_path[path], pin_nets)
            by_number = {number: role for role, number in roles.items()}
            for pin in sorted(by_path[path].pins):
                boundary_net = pin_nets.get((path, pin))
                if boundary_net is None or not endpoints[boundary_net] - group:
                    continue
                declared = by_number.get(pin)
                role = (
                    "return"
                    if declared in ("gnd", "vss", "pgnd", "vn")
                    else "supply" if declared in SUPPLY_ROLES else "bidirectional"
                )
                boundary.append(CircuitBoundary(path, pin, by_path[path].pins[pin], role, boundary_net))
        circuits.append(
            SchematicCircuit(identity, title, "", automatic_members, boundaries=tuple(boundary), patterns=local)
        )
    associated = {p for pattern in patterns if pattern.kind == "local_decoupling" for p in pattern.components[1:]}
    for c in sorted(components, key=lambda c: c.path):
        if c.path not in associated and any(
            cls.endswith(".DecouplingCapacitor") for _, cls in getattr(c, "hierarchy", ())
        ):
            diagnostics.append("Unassigned bypass ownership: " + c.path + "; shared rails do not establish an owner")
    return SchematicCircuitModel(tuple(sorted(circuits, key=lambda c: c.id)), patterns, tuple(diagnostics))
