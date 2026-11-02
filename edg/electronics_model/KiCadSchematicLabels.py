"""Readable injective net labels, retaining the complete PB name in evidence."""

import re
import hashlib


def readable_labels(net_names):
    names = sorted(set(net_names))
    parts = {name: name.split(".") for name in names}
    depth = {name: min(3, len(parts[name])) for name in names}
    while True:
        candidate = {name: ".".join(parts[name][-depth[name] :]) for name in names}
        duplicates = {}
        for name, label in candidate.items():
            duplicates.setdefault(label, []).append(name)
        expand = [
            name for group in duplicates.values() if len(group) > 1 for name in group if depth[name] < len(parts[name])
        ]
        if not expand:
            break
        for name in expand:
            depth[name] += 1
    result = {}
    for name in names:
        label = candidate[name]
        if re.search(r"[\s~{}]", label):
            label = "N_" + name.encode("utf-8").hex()
        result[name] = label
    # Encoded names can collide with a legal PB name. Escape both with a stable
    # digest, never rely on iteration order or a UUID derived from coordinates.
    groups = {}
    for name, label in result.items():
        groups.setdefault(label, []).append(name)
    for group in groups.values():
        if len(group) > 1:
            for name in group:
                result[name] += "_" + hashlib.sha256(name.encode()).hexdigest()
    if len(set(result.values())) != len(result):
        # Cryptographic collision or deliberately crafted names: full hex is injective.
        return {name: "N_" + name.encode("utf-8").hex() for name in names}
    return result
