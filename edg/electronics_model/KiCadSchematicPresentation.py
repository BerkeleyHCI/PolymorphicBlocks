"""Source-owned presentation descriptions, independent of electrical identity."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Any
import copy


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 240:
        raise ValueError(name + " must be nonempty text of at most 240 characters")
    return value.strip()


@dataclass(frozen=True)
class SchematicPresentation:
    components: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    interfaces: tuple = ()
    groups: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict) or set(value) - {
            "schema",
            "components",
            "interfaces",
            "groups",
        }:
            raise ValueError("unknown presentation fields")
        if type(value.get("schema", 1)) is not int or value.get("schema", 1) != 1:
            raise ValueError("unsupported presentation schema")
        components = value.get("components", {})
        groups = value.get("groups", {})
        interfaces = value.get("interfaces", [])
        if (
            not isinstance(components, dict)
            or not isinstance(groups, dict)
            or not isinstance(interfaces, (list, tuple))
        ):
            raise ValueError("invalid presentation collections")
        for path, entry in components.items():
            _text(path, "component path")
            if not isinstance(entry, dict) or set(entry) - {
                "description",
                "pin_names",
                "display_value",
            }:
                raise ValueError("unknown component presentation fields")
            for key in ("description", "display_value"):
                if key in entry:
                    _text(entry[key], key)
            pins = entry.get("pin_names", {})
            if not isinstance(pins, dict):
                raise ValueError("pin_names must be an object")
            for number, name in pins.items():
                _text(number, "physical pin")
                _text(name, "pin name")
        for entry in interfaces:
            if (
                not isinstance(entry, dict)
                or set(entry) - {"component", "pin", "name", "description"}
                or not {"component", "name"} <= set(entry)
            ):
                raise ValueError("unknown or missing interface presentation fields")
            for key, item in entry.items():
                _text(item, key)
        for selector, title in groups.items():
            _text(selector, "group selector")
            _text(title, "group title")
        return cls(
            copy.deepcopy(components),
            tuple(copy.deepcopy(interfaces)),
            copy.deepcopy(groups),
        )

    def to_dict(self):
        return dict(
            schema=1,
            components=copy.deepcopy(dict(self.components)),
            interfaces=copy.deepcopy(list(self.interfaces)),
            groups=dict(self.groups),
        )

    def validate(self, inventories):
        known = set(inventories)
        requested = set(self.components) | {i["component"] for i in self.interfaces}
        if requested - known:
            raise ValueError("presentation references missing components: " + str(sorted(requested - known)))
        for path, entry in self.components.items():
            if set(entry.get("pin_names", {})) - set(inventories[path]):
                raise ValueError("presentation references unknown physical pins: " + path)
        for entry in self.interfaces:
            if "pin" in entry and entry["pin"] not in inventories[entry["component"]]:
                raise ValueError("interface references unknown physical pin: " + entry["component"])

    def descriptions(self, path):
        result = []
        entry = self.components.get(path, {})
        if entry.get("description"):
            result.append(entry["description"])
        for interface in self.interfaces:
            if interface["component"] == path:
                prefix = "Pin " + interface["pin"] + ": " if "pin" in interface else ""
                result.append(
                    prefix
                    + interface["name"]
                    + (": " + interface["description"] if interface.get("description") else "")
                )
        return tuple(result)
