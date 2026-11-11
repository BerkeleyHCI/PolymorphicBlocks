"""Bounded deterministic orientation trials with immutable physical pin identities."""
from collections import defaultdict

from .KiCadSchematicLayout import freeze_annotations, pins
from .KiCadSchematicPlacement import packing_bounds, component_boxes, _overlap, _score as geometry_score, _stage_intrusions
from .KiCadSchematicRouting import route_metrics
from .KiCadSchematicScene import wire_visual_conflict, pin_name_items, pin_number_items


def _segments(route, pin_nets):
    result = list(route[0])
    for key, (px, py, ex, ey, _) in route[1].items():
        net = pin_nets.get(key)
        if net is not None:
            result.append((net, (px, py), (ex, ey)))
    return result


def _visual_conflicts(segments):
    # Spatial buckets avoid an all-wire quadratic scan on large IC regions.
    buckets, pairs = defaultdict(list), set()
    for i, (_, a, b) in enumerate(segments):
        for x in range(int((min(a[0], b[0])-1.27)//10.16), int((max(a[0], b[0])+1.27)//10.16)+1):
            for y in range(int((min(a[1], b[1])-1.27)//10.16), int((max(a[1], b[1])+1.27)//10.16)+1):
                for j in buckets[x,y]:
                    pairs.add((j,i))
                buckets[x,y].append(i)
    return sum(segments[i][0] != segments[j][0] and
               wire_visual_conflict(*segments[i][1:], *segments[j][1:]) for i,j in pairs)


def orientation_metrics(placed, views, pin_nets, route):
    segments = _segments(route, pin_nets)
    metric = route_metrics(segments, route[2])
    primary = {net for c,_,_,_ in placed
               for net in getattr(getattr(c, 'functional_circuit', None), 'primary_nets', ())}
    # Verified internal power paths matter even when authored boundary roles
    # classify the external terminals as supplies rather than signal inputs.
    from .KiCadSchematicPower import topology_primary_endpoints
    topology_endpoints = topology_primary_endpoints([c for c,_,_,_ in placed], pin_nets, views)
    primary.update(topology_endpoints)
    # A labeled bulk-bank branch does not sever the converter's main visible
    # path. Count core physical endpoints on a verified converter net, while
    # retaining authored net-level semantics outside that unique topology.
    primary_failures = [(key,net) for key,net in route[2] if net in primary
                        and (net not in topology_endpoints or key in topology_endpoints[net])]
    metric['primary_fallbacks'] = len(primary_failures)
    metric['noncore_converter_fallbacks'] = sum(net in topology_endpoints and key not in topology_endpoints[net]
                                               for key,net in route[2])
    metric['primary_fallback_scope'] = ('Core physical endpoints of uniquely verified converter nets; '
                                       'authored net-level primary paths elsewhere. Bulk/bypass bank endpoints excluded.')
    metric['unrelated_intrusions'] = _stage_intrusions(placed, route[0], views, pin_nets)
    terminals = defaultdict(list)
    for c,x,y,angle in placed:
        for number,px,py,_ in pins(views[c.path],x,y,angle):
            if (c.path,number) in pin_nets:
                terminals[pin_nets[c.path,number]].append((px,py))
    lower = sum(max(x for x,y in pts)-min(x for x,y in pts)+max(y for x,y in pts)-min(y for x,y in pts)
                for pts in terminals.values() if len(pts)>1)
    metric['detour_mm'] = round(max(0,metric['length_mm']-lower),4)
    metric['visual_conflicts'] = _visual_conflicts(segments)
    return metric


def _rank(metric):
    return tuple(metric[key] for key in ('primary_fallbacks','crossings','unrelated_intrusions',
                                         'bends','detour_mm','length_mm'))


def _geometry(placed, views, pin_nets):
    score = geometry_score(placed, views, pin_nets)
    a,b,c,d = packing_bounds(placed, views, pin_nets)
    width,height = c-a,d-b
    boxes = []
    for entry in placed:
        component,x,y,angle = entry
        measured = component_boxes(entry,views)
        measured += [item['bounds'] for item in (
            pin_name_items(views[component.path].definition,x,y,angle)
            + pin_number_items(views[component.path].definition,x,y,angle))]
        boxes.extend((component.path,index,box) for index,box in enumerate(measured))
    contacts = sorted((a,ai,b,bi) for i,(a,ai,first) in enumerate(boxes)
                      for b,bi,second in boxes[i+1:] if a!=b and _overlap(first,second))
    return dict(collision_pairs=contacts, escape_conflicts=score[0], collisions=score[1],
                clipped=width>375 or height>225 or (width>210 and height>205))


def optimize_orientations(source_placed, views, pin_nets, router, *, locked=(),
                          baseline=None, region_bounds=None):
    """Try each unlocked PB path once per sweep, at most two complete sweeps.

    The incumbent route is cached. Each geometrically viable trial invokes only
    the baseline router; its pin-neck and text/ground/label masks remain active.
    Route-order optimization belongs to the caller and runs only after selection.
    Automatic fields are recomputed from source objects for each orientation;
    explicitly authored annotations retain their coordinates.
    """
    current = list(source_placed)
    placed = freeze_annotations(current, views)
    route = baseline if baseline is not None else router(placed,views,pin_nets)
    before = metric = orientation_metrics(placed,views,pin_nets,route)
    original_failures = set(route[2])
    geometry = _geometry(placed,views,pin_nets)
    locked = set(locked)
    eligibility = [dict(path=c.path, eligible=c.path not in locked,
                        reason='explicit rotation lock' if c.path in locked else '180 degree trial')
                   for c,_,_,_ in sorted(current,key=lambda e:e[0].path)]
    trials, route_calls, sweeps = [], 0, 0
    for sweep in range(2):
        improved = False
        sweeps += 1
        for index in sorted(range(len(current)),key=lambda i:current[i][0].path):
            c,x,y,angle = current[index]
            if c.path in locked:
                continue
            candidate = list(current)
            candidate[index] = c,x,y,(angle+180)%360
            trial_placed = freeze_annotations(candidate,views)
            trial_geometry = _geometry(trial_placed,views,pin_nets)
            reason = next((key for key in ('escape_conflicts','collisions')
                           if trial_geometry[key]>geometry[key]), None)
            if not set(trial_geometry.get('collision_pairs',())) <= set(geometry.get('collision_pairs',())):
                reason = 'new symbol, field or pin text collision'
            if trial_geometry['clipped']:
                reason = 'page overflow'
            trial = dict(sweep=sweep+1,path=c.path,from_rotation=angle,
                         to_rotation=(angle+180)%360,selected=False,geometry=trial_geometry)
            if reason is None:
                trial_route = router(trial_placed,views,pin_nets)
                route_calls += 1
                trial_metric = orientation_metrics(trial_placed,views,pin_nets,trial_route)
                trial['metrics'] = trial_metric
                if region_bounds is not None:
                    a,b,cx,d = region_bounds(trial_placed, trial_route)
                    width,height = cx-a,d-b
                    trial_geometry['clipped'] = width>375 or height>225 or (width>210 and height>205)
                if trial_geometry['clipped']:
                    reason = 'routed region page overflow'
                elif not set(trial_route[2]) <= original_failures:
                    reason = 'new failed endpoints'
                elif trial_metric['visual_conflicts']>metric['visual_conflicts']:
                    reason = 'inadequate visual wire clearance'
                elif _rank(trial_metric)>=_rank(metric):
                    reason = 'incumbent scores better or ties'
                else:
                    current,placed,route,metric,geometry = candidate,trial_placed,trial_route,trial_metric,trial_geometry
                    trial['selected'] = True
                    improved = True
                    reason = 'improved routed score'
            trial['reason'] = reason
            trials.append(trial)
        if not improved:
            break
    return placed,route,dict(eligibility=eligibility,trials=trials,sweeps=sweeps,
        route_trials=route_calls,before=before,after=metric,
        selected_rotations={c.path:angle for c,_,_,angle in placed},
        metric_scope='Union of local routed wires and fixed pin stubs; detour uses Manhattan bounding lower bound. Primary fallbacks count core physical endpoints on uniquely verified converter paths, excluding bulk/bypass bank endpoints; authored primary nets elsewhere retain net-level semantics. Final repaired label tails are checked downstream by the shared scene.')


_PASSIVE_QUARTER_TURN_SYMBOLS = frozenset((
    'Device:R', 'Device:R_US', 'Device:C', 'Device:C_Polarized', 'Device:L',
))


def passive_orientation_rank(metric):
    """Balanced wire cost after electrical visibility and crossing priorities."""
    return (metric['primary_fallbacks'], metric['crossings'], metric['unrelated_intrusions'],
            round(metric['length_mm'] + 2.54 * metric['bends'], 4))


def _passive_quarter_turn_eligibility(component, view, locked):
    if component.path in locked:
        return False, 'explicit rotation lock'
    # Resolver-derived IDs carry a pin-map suffix. Reference prefixes,
    # footprint names and two-pin generic boxes do not establish a passive.
    lib_id = view.lib_id.rsplit('_PB_', 1)[0]
    if lib_id not in _PASSIVE_QUARTER_TURN_SYMBOLS:
        return False, 'not a verified resistor, capacitor or inductor symbol'
    if len({(x, y) for _, x, y, _ in view.pins}) != 2:
        return False, 'symbol does not have two distinct terminal attachment positions'
    return True, 'verified two-terminal passive'


def _escape_conflict_identities(placed, views, pin_nets):
    """Physical endpoint identities distinguish replacement escape conflicts."""
    from .KiCadSchematicPlacement import pin_escapes
    from .KiCadSchematicScene import segments_touch, segment_box
    escapes = pin_escapes(placed, views, pin_nets)
    glyphs = [(c.path, item['identity'], item['bounds']) for c, x, y, angle in placed
              for item in (pin_name_items(views[c.path].definition, x, y, angle, c.path)
                           + pin_number_items(views[c.path].definition, x, y, angle, c.path))]
    conflicts = set()
    for index, (net, a, b, owner, number) in enumerate(escapes):
        key = owner, number
        for other_owner, identity, box in glyphs:
            if owner != other_owner and segment_box(a, b, box):
                conflicts.add(('pin_text', key, identity))
        for other_net, c, d, other_owner, other_number in escapes[index+1:]:
            if net != other_net and segments_touch(a, b, c, d):
                conflicts.add(('escape_pair', *sorted((key, (other_owner, other_number)))))
    return frozenset(conflicts)


def _visual_clearance_conflict_identities(route, pin_nets):
    """Canonical wire-union contacts, independent of collinear segmentation.

    Coordinates distinguish a new bad location on an already affected net pair.
    Existing count-based clearance checks remain active independently.
    """
    lines = defaultdict(list)
    for net, a, b in _segments(route, pin_nets):
        if a == b:
            continue
        axis = 0 if a[1] == b[1] else 1
        fixed = a[1-axis]
        lines[net, axis, fixed].append(tuple(sorted((a[axis], b[axis]))))
    segments = []
    for (net, axis, fixed), intervals in sorted(lines.items()):
        merged = []
        for lo, hi in sorted(intervals):
            if merged and lo <= merged[-1][1]:
                merged[-1] = merged[-1][0], max(hi, merged[-1][1])
            else:
                merged.append((lo, hi))
        for lo, hi in merged:
            a, b = ((lo, fixed), (hi, fixed)) if axis == 0 else ((fixed, lo), (fixed, hi))
            segments.append((net, a, b))
    buckets, pairs = defaultdict(list), set()
    for index, (_, a, b) in enumerate(segments):
        for x in range(int((min(a[0], b[0])-1.27)//10.16), int((max(a[0], b[0])+1.27)//10.16)+1):
            for y in range(int((min(a[1], b[1])-1.27)//10.16), int((max(a[1], b[1])+1.27)//10.16)+1):
                pairs.update((other, index) for other in buckets[x,y])
                buckets[x,y].append(index)
    return frozenset(tuple(sorted((segments[i], segments[j]))) for i,j in pairs
                     if segments[i][0] != segments[j][0]
                     and wire_visual_conflict(*segments[i][1:], *segments[j][1:]))


def orientation_conflict_identities(placed, views, pin_nets, route):
    """Additional monotonic safety guards for quarter turns and final rerouting."""
    return dict(escape=_escape_conflict_identities(placed, views, pin_nets),
                visual_clearance=_visual_clearance_conflict_identities(route, pin_nets))


def optimize_passive_orientations(source_placed, views, pin_nets, router, *, locked=(),
                                  baseline=None, region_bounds=None, source_annotations=None):
    """One complete stable sweep, at most three routed trials per passive.

    All three alternatives for a component start from the same incumbent. Only
    the best valid angle commits, and ties preserve the incumbent. The caller
    binds ``router`` to the incumbent's selected routing strategy and performs
    final route-order and serialized-scene validation after this local search.

    ``source_annotations`` distinguishes authored coordinates from frozen
    automatic fields in a prepared baseline; it must contain None for automatic
    fields. Omitting the map preserves annotations supplied by direct callers.
    """
    from copy import copy

    current = []
    for component, x, y, angle in source_placed:
        source = copy(component)
        if source_annotations is not None and component.path in source_annotations:
            source.annotation = source_annotations[component.path]
        current.append((source, x, y, angle))
    placed = freeze_annotations(current, views)
    route = baseline if baseline is not None else router(placed, views, pin_nets)
    before = metric = orientation_metrics(placed, views, pin_nets, route)
    geometry = _geometry(placed, views, pin_nets)
    conflicts = orientation_conflict_identities(placed, views, pin_nets, route)
    locked = set(locked)
    eligibility = []
    eligible = set()
    for component, _, _, _ in sorted(current, key=lambda entry: entry[0].path):
        allowed, reason = _passive_quarter_turn_eligibility(component, views[component.path], locked)
        eligibility.append(dict(path=component.path, eligible=allowed, reason=reason,
                                allowed_rotations=[0, 90, 180, 270] if allowed else []))
        if allowed:
            eligible.add(component.path)
    trials, route_calls, changed = [], 0, False
    for index in sorted(range(len(current)), key=lambda i: current[i][0].path):
        component, x, y, angle = current[index]
        if component.path not in eligible:
            continue
        best = None
        visit_failures = set(route[2])
        for alternative in (0, 90, 180, 270):
            if alternative == angle:
                continue
            candidate = list(current)
            candidate[index] = component, x, y, alternative
            trial_placed = freeze_annotations(candidate, views)
            trial_geometry = _geometry(trial_placed, views, pin_nets)
            reason = next((key for key in ('escape_conflicts', 'collisions')
                           if trial_geometry[key] > geometry[key]), None)
            if not set(trial_geometry.get('collision_pairs', ())) <= set(geometry.get('collision_pairs', ())):
                reason = 'new symbol, field or pin text collision'
            trial_escape_conflicts = _escape_conflict_identities(trial_placed, views, pin_nets)
            if not trial_escape_conflicts <= conflicts['escape']:
                reason = 'new physical escape conflict'
            if trial_geometry['clipped']:
                reason = 'page overflow'
            trial = dict(path=component.path, from_rotation=angle, to_rotation=alternative,
                         selected=False, acceptable=False, geometry=trial_geometry)
            if reason is None:
                trial_route = router(trial_placed, views, pin_nets)
                route_calls += 1
                trial_metric = orientation_metrics(trial_placed, views, pin_nets, trial_route)
                trial['metrics'] = trial_metric
                if region_bounds is not None:
                    a, b, c, d = region_bounds(trial_placed, trial_route)
                    width, height = c-a, d-b
                    trial_geometry['clipped'] = width>375 or height>225 or (width>210 and height>205)
                if trial_geometry['clipped']:
                    reason = 'routed region page overflow'
                elif not set(trial_route[2]) <= visit_failures:
                    reason = 'new failed endpoints'
                elif not _visual_clearance_conflict_identities(trial_route, pin_nets) <= conflicts['visual_clearance']:
                    reason = 'new visual wire clearance conflict'
                elif trial_metric['visual_conflicts'] > metric['visual_conflicts']:
                    reason = 'inadequate visual wire clearance'
                elif passive_orientation_rank(trial_metric) >= passive_orientation_rank(metric):
                    reason = 'incumbent scores better or ties'
                else:
                    trial['acceptable'] = True
                    reason = 'another angle for this component scores better'
                    if best is None or passive_orientation_rank(trial_metric) < passive_orientation_rank(best[3]):
                        best = candidate, trial_placed, trial_route, trial_metric, trial_geometry, len(trials)
            trial['reason'] = reason
            trials.append(trial)
        if best is not None:
            current, placed, route, metric, geometry, chosen = best
            trials[chosen]['selected'] = True
            trials[chosen]['reason'] = 'improved balanced routed score'
            conflicts = orientation_conflict_identities(placed, views, pin_nets, route)
            changed = True
    return placed, route, dict(mode='passive_quarter_turn', eligibility=eligibility,
        trials=trials, sweeps=1 if eligible else 0, route_trials=route_calls,
        eligible_passives=len(eligible), route_trial_limit=3*len(eligible), changed=changed,
        before=before, after=metric,
        final_rotations={component.path: angle for component, _, _, angle in placed},
        metric_scope='Union of local routed wires and fixed pin stubs; weighted cost is length_mm + 2.54*bends. Final serialized label, field and GND findings are checked by the caller.')
