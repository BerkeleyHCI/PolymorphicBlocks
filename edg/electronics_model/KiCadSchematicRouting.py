"""Bounded fixed-placement routing search; electrical identities are immutable."""
from collections import defaultdict


def route_metrics(wires, failures):
    """Measure union length, geometric corners and distinct cross-net crossings.

    Measurements cover local routed wires, excluding pin stubs and inter-region
    links, which are fixed by the caller. Collinear overlaps count only once.
    """
    lines = defaultdict(list)
    ends = defaultdict(set)
    for net, a, b in wires:
        axis = 0 if a[1] == b[1] else 1
        fixed = a[1 - axis]
        lo, hi = sorted((a[axis], b[axis]))
        if lo == hi:
            continue
        lines[net, axis, fixed].append((lo, hi))
        ends[net, a].add(axis)
        ends[net, b].add(axis)
    segments = []
    for (net, axis, fixed), spans in sorted(lines.items()):
        merged = []
        for lo, hi in sorted(spans):
            if merged and lo <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
            else:
                merged.append((lo, hi))
        segments.extend((net, axis, fixed, lo, hi) for lo, hi in merged)
    crossings = set()
    corners = set()
    for i, (net, axis, fixed, lo, hi) in enumerate(segments):
        for other, other_axis, other_fixed, other_lo, other_hi in segments[i + 1:]:
            if axis == other_axis:
                continue
            if lo <= other_fixed <= hi and other_lo <= fixed <= other_hi:
                xy = (other_fixed, fixed) if axis == 0 else (fixed, other_fixed)
                if net != other:
                    crossings.add((tuple(sorted((net, other))), xy))
                elif other_fixed in (lo, hi) and fixed in (other_lo, other_hi):
                    corners.add((net, xy))
    return dict(length_mm=round(sum(hi - lo for _, _, _, lo, hi in segments), 4),
                bends=len(corners), crossings=len(crossings), failures=len(failures))


def optimize_fixed_routes(placed, views, pin_nets, baseline, router):
    """Evaluate a fixed set of orders; ties retain the earlier candidate.

    Never accept new fallback endpoints, more crossings, longer routes, or routes
    outside the baseline envelope. The caller retains baseline packing bounds.
    """
    before = route_metrics(baseline[0], baseline[2])
    best, score, selected = baseline, _score(before), "baseline"
    points = [p for _, a, b in baseline[0] for p in (a, b)]
    if not points:
        return best, dict(before=before, after=before, selected=selected, candidates=1)
    bounds = (min(p[0] for p in points), min(p[1] for p in points),
              max(p[0] for p in points), max(p[1] for p in points))
    evaluated = []
    for strategy in ("x", "y", "reverse", "short_first", "tree_search", "tree_reverse"):
        candidate = router(placed, views, pin_nets, strategy=strategy)
        metric = route_metrics(candidate[0], candidate[2])
        acceptable = (
            set(candidate[2]) <= set(baseline[2])
            and metric["crossings"] <= before["crossings"]
            and metric["length_mm"] <= before["length_mm"]
            and all(bounds[0] <= p[0] <= bounds[2] and bounds[1] <= p[1] <= bounds[3]
                    for _, a, b in candidate[0] for p in (a, b))
        )
        evaluated.append(dict(strategy=strategy, metrics=metric, acceptable=acceptable))
        if acceptable and _score(metric) < score:
            best, score, selected = candidate, _score(metric), strategy
    return best, dict(before=before, after=route_metrics(best[0], best[2]),
                      selected=selected, candidates=1 + len(evaluated), trials=evaluated)


def _score(metrics):
    return (metrics["failures"], metrics["crossings"],
            round(metrics["length_mm"] + 2.54 * metrics["bends"], 4),
            metrics["bends"], metrics["length_mm"])
