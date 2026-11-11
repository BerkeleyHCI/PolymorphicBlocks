"""Power-circuit presentation from verified symbols and compiled terminal nets."""
from collections import defaultdict


def role_nets(component, pin_nets):
    """Parallel physical pads may share a role only when their nets agree."""
    roles = defaultdict(set)
    for number, port in component.pins.items():
        role = port.removesuffix('.net').split('.')[-1].lower()
        roles[role].add(pin_nets.get((component.path, number)))
    return {role: next(iter(nets)) for role, nets in roles.items()
            if len(nets) == 1 and None not in nets}


def symbol_id(view):
    return view.lib_id.rsplit('_PB_', 1)[0]


def led_buck_topology(members, by_path, views, pin_nets):
    """Verified TPS92200 model plus unique compiled bootstrap/sense witnesses.

    A BOOT-like spelling on another model is not permission to specialize its
    layout. Parallel modeled pads are allowed only when their role nets agree.
    """
    controllers = [p for p in members if getattr(by_path[p], 'hierarchy', ())
                   and by_path[p].hierarchy[-1][1].removeprefix('PolymorphicBlocks.') ==
                   'edg.parts.power.LedDriver_Tps92200.Tps92200_Device']
    if not controllers:
        return None, None
    if len(controllers) != 1:
        return None, 'ambiguous LED buck controllers in region'
    ic = controllers[0]
    roles = role_nets(by_path[ic], pin_nets)
    declared = {n: r.removesuffix('.net') for n, r in by_path[ic].pins.items()}
    required = {'1': 'fb', '2': 'dim', '3': 'gnd', '4': 'vin', '5': 'sw', '6': 'boot'}
    if any(declared.get(n) != role for n, role in required.items()) or not set(required.values()) <= roles.keys():
        return None, 'verified LED buck terminal roles do not match compiled pins'
    if len({roles[r] for r in required.values()}) != 6:
        return None, 'LED buck terminal nets are not distinct'
    circuit = getattr(by_path[ic], 'functional_circuit', None)
    if circuit is not None and (circuit.template not in ('auto', 'buck') or circuit.stages):
        return None, 'authored circuit template or stages take precedence'
    nets = {p: {pin_nets.get((p, n)) for n in by_path[p].pins} for p in members}
    caps = [p for p in members if symbol_id(views[p]) in ('Device:C', 'Device:C_Polarized')]
    boots = [p for p in caps if nets[p] == {roles['boot'], roles['sw']}]
    senses = [p for p in members if symbol_id(views[p]) in ('Device:R', 'Device:R_US')
              and nets[p] == {roles['fb'], roles['gnd']}]
    coils = [p for p in members if symbol_id(views[p]) == 'Device:L'
             and len(nets[p]) == 2 and None not in nets[p] and roles['sw'] in nets[p]
             and not (nets[p] & {roles['vin'], roles['gnd'], roles['boot'], roles['fb']})]
    if len(boots) != 1 or len(senses) != 1 or len(coils) != 1:
        return None, 'bootstrap capacitor, sense resistor or output inductor is missing or ambiguous'
    output = next(iter(nets[coils[0]] - {roles['sw']}))
    # This verified model exports the FB/sense node as LED cathode. Some boards
    # solder the load directly to existing pads and use virtual DummyPassive
    # endpoints, so there need not be another modeled physical pad on this net.
    outside = [(p, n) for (p, n), net in pin_nets.items() if p not in members and net == roles['fb']]
    return dict(kind='led_buck', ic=ic, coil=coils[0], bootstrap=boots[0], sense=senses[0],
                input=roles['vin'], switch=roles['sw'], boot=roles['boot'], feedback=roles['fb'],
                ground=roles['gnd'], output=output, roles=roles,
                input_caps=sorted(p for p in caps if nets[p] == {roles['vin'], roles['gnd']}),
                output_caps=sorted(p for p in caps if nets[p] == {output, roles['gnd']}),
                load_return_witnesses=sorted(outside)), None


def led_buck_candidates(topology, by_path, views, pin_nets):
    """Four finite measured arrangements; no movement of an authored plan."""
    from .KiCadSchematicLayout import pins, snap
    from .KiCadSchematicPlacement import atom_bounds, _rotation_for_pin
    t = topology
    candidates = []
    for gap in (5.08, 10.16):
        for sense_side in ('above', 'below'):
            entries = {}
            def put(path, x, y, angle=0):
                entries[path] = (by_path[path], snap(x), snap(y), angle)
            def local(path, net, angle=0):
                ps = [(x, y) for n, x, y, _ in pins(views[path], 0, 0, angle)
                      if pin_nets.get((path, n)) == net]
                return sum(x for x, y in ps)/len(ps), sum(y for x, y in ps)/len(ps)
            def angle(path, net, direction):
                n = next(n for n in by_path[path].pins if pin_nets.get((path, n)) == net)
                return _rotation_for_pin(views[path], n, direction)
            ic, coil, boot, sense = (t[k] for k in ('ic', 'coil', 'bootstrap', 'sense'))
            put(ic, 0, 0)
            box = atom_bounds([entries[ic]], views)
            sx, sy = local(ic, t['switch'])
            bx, by = local(ic, t['boot'])
            # SW branches at the capacitor's upper terminal; BOOT occupies the
            # lower corridor. Neither wire needs to circle the whole channel.
            ba = angle(boot, t['switch'], (0, -1))
            bpx, bpy = local(boot, t['switch'], ba)
            put(boot, max(box[2], sx, bx)+gap-bpx, sy-bpy, ba)
            boot_box = atom_bounds([entries[boot]], views)
            ca = angle(coil, t['switch'], (-1, 0))
            cx, cy = local(coil, t['switch'], ca)
            put(coil, max(boot_box[2], box[2])+gap-cx, sy-cy, ca)
            coil_box = atom_bounds([entries[coil]], views)
            fx, fy = local(ic, t['feedback'])
            ra = angle(sense, t['ground'], (0, 1))
            rx, ry = local(sense, t['feedback'], ra)
            # FB is on the left. Keep its sense shunt outside VIN/DIM pin
            # escapes, with a short GND glyph instead of a ground return loop.
            sense_y = min(fy, box[1]-gap) if sense_side == 'above' else max(fy, box[3]+gap)
            sense_box = atom_bounds([(by_path[sense], 0, 0, ra)], views)
            put(sense, min(box[0], fx)-gap-sense_box[2], sense_y-ry, ra)
            for key, rail, x0, y0, direction in (
                    ('input_caps', t['input'], box[0]-gap, local(ic, t['input'])[1]+gap, -1),
                    ('output_caps', t['output'], coil_box[2]+gap, sy+gap, 1)):
                x = x0
                for path in t[key]:
                    a = angle(path, rail, (0, -1))
                    px, py = local(path, rail, a)
                    local_box = atom_bounds([(by_path[path], 0, 0, a)], views)
                    # Pack measured field edges, not terminal centers: left-
                    # facing bank growth otherwise puts the next capacitor's
                    # right-hand value text through its neighbour's body.
                    put(path, x-local_box[2 if direction < 0 else 0], y0-py, a)
                    bounds = atom_bounds([entries[path]], views)
                    x = (bounds[2]+gap if direction > 0 else bounds[0]-gap)
            remaining = sorted(set(by_path)-set(entries))
            if remaining:
                bounds = atom_bounds(list(entries.values()), views)
                x, y = bounds[0], bounds[3]+gap
                for path in remaining:
                    bounds = atom_bounds([(by_path[path], 0, 0, 0)], views)
                    put(path, x-bounds[0], y-bounds[1])
                    x += bounds[2]-bounds[0]+gap
            candidates.append((f'led_buck_{gap:g}_{sense_side}', list(entries.values())))
    return candidates


def compare_led_buck_variants(placed, views, pin_nets, baseline, router, *, source_annotations=None,
                              region_bounds=None):
    """Try at most four routes against one cached incumbent, then select once."""
    import copy
    from .KiCadSchematicLayout import freeze_annotations, snap
    from .KiCadSchematicPlacement import packing_bounds
    from .KiCadSchematicOrientation import (orientation_metrics, passive_orientation_rank, _geometry,
                                           _escape_conflict_identities)
    by_path = {c.path: c for c, _, _, _ in placed}
    t, reason = led_buck_topology(tuple(sorted(by_path)), by_path, views, pin_nets)
    if t is None:
        return placed, baseline, (dict(accepted=False, reason=reason, route_trials=0, trials=[]) if reason else None)
    source = {}
    for path, c in by_path.items():
        source[path] = copy.copy(c)
        source[path].annotation = (source_annotations or {}).get(path)
    before = best = orientation_metrics(placed, views, pin_nets, baseline)
    original_geometry = _geometry(placed, views, pin_nets)
    original_escapes = _escape_conflict_identities(placed, views, pin_nets)
    original_failures = set(baseline[2])
    a, b, _, _ = packing_bounds(placed, views, pin_nets)
    selected, selected_route, selected_name = placed, baseline, 'incumbent'
    trials, calls = [], 0
    for name, entries in led_buck_candidates(t, source, views, pin_nets):
        x, y, _, _ = packing_bounds(entries, views, pin_nets)
        candidate = freeze_annotations([(c, snap(px+a-x), snap(py+b-y), r) for c, px, py, r in entries], views)
        geometry = _geometry(candidate, views, pin_nets)
        trial = dict(candidate=name, geometry=geometry, selected=False)
        reason = None
        if geometry['collision_pairs'] or geometry['collisions']:
            reason = 'symbol, field or pin text collision'
        elif (geometry['escape_conflicts'] > original_geometry['escape_conflicts']
              or not _escape_conflict_identities(candidate, views, pin_nets) <= original_escapes):
            reason = 'new pin escape conflict'
        elif geometry['clipped']:
            reason = 'page overflow'
        if reason is None:
            route = router(candidate, views, pin_nets)
            calls += 1
            metric = orientation_metrics(candidate, views, pin_nets, route)
            trial['metrics'] = metric
            bounds = region_bounds(candidate, route) if region_bounds else packing_bounds(candidate, views, pin_nets)
            w, h = bounds[2]-bounds[0], bounds[3]-bounds[1]
            if not set(route[2]) <= original_failures:
                reason = 'new failed endpoints'
            elif w > 375 or h > 225 or (w > 210 and h > 205):
                reason = 'routed region page overflow'
            elif metric['visual_conflicts'] > before['visual_conflicts']:
                reason = 'degraded wire clearance'
            elif passive_orientation_rank(metric) >= passive_orientation_rank(best):
                reason = 'incumbent scores better or ties'
            else:
                selected, selected_route, best, selected_name = candidate, route, metric, name
                reason = 'improved routed score'
                trial['selected'] = True
        trial['reason'] = reason
        trials.append(trial)
    for trial in trials:
        trial['selected'] = trial['candidate'] == selected_name
    return selected, selected_route, dict(accepted=selected_name != 'incumbent', selected=selected_name,
        topology={k: v for k, v in t.items() if k != 'roles'}, route_trials=calls,
        candidate_limit=4, before=before, after=best, trials=trials)


def power_topology(members, by_path, views, pin_nets):
    """Recognize a single buck or four-switch bridge; ambiguous cases decline."""
    roles = {p: role_nets(by_path[p], pin_nets) for p in members}
    coils = [p for p in members if symbol_id(views[p]) == 'Device:L']
    matches = []
    for ic in members:
        r = roles[ic]
        ground = r.get('gnd', r.get('pgnd'))
        if ground is None:
            continue
        for coil in coils:
            nets = {pin_nets.get((coil, n)) for n in by_path[coil].pins}
            if len(nets) != 2 or None in nets:
                continue
            if ('sw' in r and r['sw'] in nets and ('vin' in r or 'pwr_in' in r)
                    and r.get('vin', r.get('pwr_in')) not in nets):
                matches.append(dict(kind='buck', ic=ic, coil=coil, ground=ground,
                                    input=r.get('vin', r.get('pwr_in')), output=next(iter(nets-{r['sw']})),
                                    switch=r['sw'], roles=roles))
            elif {'sw1', 'sw2', 'hidrv1', 'hidrv2', 'lodrv1', 'lodrv2'} <= r.keys() and nets == {r['sw1'], r['sw2']}:
                bridges = []
                for index in (1, 2):
                    sw = r[f'sw{index}']
                    hi = [p for p, fr in roles.items() if fr.get('source') == sw and fr.get('gate') == r[f'hidrv{index}'] and 'drain' in fr]
                    lo = [p for p, fr in roles.items() if fr.get('drain') == sw and fr.get('source') == ground and fr.get('gate') == r[f'lodrv{index}']]
                    if len(hi) != 1 or len(lo) != 1:
                        break
                    bridges.append((hi[0], lo[0], roles[hi[0]]['drain']))
                if len(bridges) == 2:
                    matches.append(dict(kind='bridge', ic=ic, coil=coil, ground=ground,
                                        bridges=bridges, input=bridges[0][2], output=bridges[1][2], roles=roles))
    return matches[0] if len(matches) == 1 else None


def bridge_kernel(topology, members, by_path, views, pin_nets):
    """Controller, bridge, rail banks, shunts and actual bootstrap branches.

    Sense-filter and configuration networks remain separate functional detail.
    The power kernel is bounded independently of their number.
    """
    t = topology
    selected = {t['ic'], t['coil']} | {p for hi, lo, _ in t['bridges'] for p in (hi, lo)}
    r, rails = t['roles'][t['ic']], {t['input'], t['output']}
    caps = {p for p in members if symbol_id(views[p]) in ('Device:C', 'Device:C_Polarized')}
    resistors = {p for p in members if symbol_id(views[p]) in ('Device:R', 'Device:R_US')}
    nets = {p: {pin_nets.get((p, n)) for n in by_path[p].pins} for p in members}
    # Series shunts link a bridge rail to another rail with its own ground bank.
    bank_rails = {next(iter(nets[p]-{t['ground']})) for p in caps
                  if len(nets[p]) == 2 and t['ground'] in nets[p]}
    for p in sorted(resistors):
        if len(nets[p]) == 2 and nets[p] & rails and nets[p] <= bank_rails:
            selected.add(p); rails |= nets[p]
    selected |= {p for p in caps if len(nets[p]) == 2 and t['ground'] in nets[p] and nets[p] & rails}
    boot_pairs = [{r.get(f'btst{i}'), r[f'sw{i}']} for i in (1, 2)]
    selected |= {p for p in caps if nets[p] in boot_pairs}
    return selected


def topology_primary_nets(components, views, pin_nets):
    """Primary paths from a unique verified converter, never net-name guesses.

    Include both rail directions for bidirectional bridges. Gate/bootstrap paths
    are part of recognizing the drawn converter, while a shared return does not
    make every ground connection a primary routed power path.
    """
    by_path = {component.path: component for component in components}
    t = power_topology(tuple(sorted(by_path)), by_path, views, pin_nets)
    if t is None:
        return frozenset()
    primary = {t['input'], t['output']}
    if t['kind'] == 'buck':
        primary.add(t['switch'])
        led, _ = led_buck_topology(tuple(sorted(by_path)), by_path, views, pin_nets)
        if led is not None:
            primary.update((led['boot'], led['feedback']))
    else:
        roles = t['roles'][t['ic']]
        primary.update(roles[role] for role in (
            'sw1', 'sw2', 'hidrv1', 'hidrv2', 'lodrv1', 'lodrv2', 'btst1', 'btst2')
            if role in roles)
        kernel = bridge_kernel(t, tuple(sorted(by_path)), by_path, views, pin_nets)
        for path in kernel:
            if symbol_id(views[path]) in ('Device:R', 'Device:R_US'):
                primary.update(pin_nets[path, number] for number in by_path[path].pins
                               if (path, number) in pin_nets)
    primary.discard(t['ground'])
    return frozenset(primary)


def topology_primary_endpoints(components, pin_nets, views):
    """Core terminals whose missing drawn wire hides converter operation.

    Rail-bank and bypass labels do not interrupt the main controller/bridge/
    inductor path. Classifying the endpoint as well as the net distinguishes
    those presentation fallbacks without changing electrical net identity.
    """
    components = tuple(components)
    by_path = {component.path: component for component in components}
    t = power_topology(tuple(sorted(by_path)), by_path, views, pin_nets)
    if t is None:
        return {}
    nets = topology_primary_nets(components, views, pin_nets)
    core = {t['ic'], t['coil']}
    roles = t['roles'][t['ic']]
    if t['kind'] == 'bridge':
        core.update(path for hi,lo,_ in t['bridges'] for path in (hi,lo))
        kernel = bridge_kernel(t, tuple(sorted(by_path)), by_path, views, pin_nets)
        core.update(path for path in kernel
                    if symbol_id(views[path]) in ('Device:R', 'Device:R_US'))
        bootstrap_pairs = [{roles.get('btst%d'%i),roles.get('sw%d'%i)} for i in (1,2)]
    else:
        bootstrap_pairs = [{roles.get(role),t['switch']} for role in ('btst','bst') if role in roles]
        led, _ = led_buck_topology(tuple(sorted(by_path)), by_path, views, pin_nets)
        if led is not None:
            core.add(led['sense'])
            bootstrap_pairs.append({led['boot'], led['switch']})
    core.update(path for path,component in by_path.items()
                if symbol_id(views[path]) in ('Device:C','Device:C_Polarized')
                and {pin_nets.get((path,n)) for n in component.pins} in bootstrap_pairs)
    return {net: frozenset((path,number) for path in core for number in by_path[path].pins
                          if pin_nets.get((path,number)) == net) for net in nets}


def power_template(members, by_path, views, pin_nets):
    """Place signal-bearing power geometry before measured support packing."""
    from .KiCadSchematicLayout import pins, snap
    from .KiCadSchematicPlacement import (atom_bounds, packing_bounds, _horizontal,
        _rotation_for_pin, _score)
    t = power_topology(members, by_path, views, pin_nets)
    if t is None:
        return None
    entries = {}
    def put(path, x, y, angle=0):
        entries[path] = (by_path[path], snap(x), snap(y), angle)
    def terminal(path, net, angle=0):
        found = [v for v in pins(views[path], 0, 0, angle) if pin_nets.get((path, v[0])) == net]
        return (sum(v[1] for v in found)/len(found), sum(v[2] for v in found)/len(found))
    def orient_net(path, net, desired):
        number = next(n for n in by_path[path].pins if pin_nets.get((path, n)) == net)
        return _rotation_for_pin(views[path], number, desired)
    ic, coil = t['ic'], t['coil']
    put(ic, 0, 0)
    ic_box = atom_bounds([entries[ic]], views)
    if t['kind'] == 'buck':
        sx, sy = terminal(ic, t['switch'])
        angle = orient_net(coil, t['switch'], (-1, 0))
        cx, cy = terminal(coil, t['switch'], angle)
        put(coil, max(ic_box[2], sx)+25.4-cx, sy-cy, angle)
        coil_box = atom_bounds([entries[coil]], views)
        bank_origins = {t['input']: (ic_box[0]-30.48, ic_box[1]+15.24, -1),
                        t['output']: (coil_box[2]+20.32, sy+20.32, 1)}
    else:
        # Two vertical half bridges joined at their switch midpoints. Source/
        # drain orientation comes from physical pins, never guessed pin numbers.
        for x, (hi, lo, rail) in zip((-50.8, 50.8), t['bridges']):
            ah = orient_net(hi, t['roles'][hi]['source'], (0, 1))
            al = orient_net(lo, t['roles'][lo]['drain'], (0, -1))
            put(hi, x, -17.78, ah); put(lo, x, 17.78, al)
        put(coil, 0, 0, _horizontal(views[coil]))
        # Controller sits below both bridges, preserving short local gate paths.
        rotated_box = atom_bounds([(by_path[ic], 0, 0, 90)], views)
        put(ic, 0, 40.64-rotated_box[1], 90)
        bank_origins = {t['input']: (-91.44, -15.24, -1), t['output']: (91.44, -15.24, 1)}
    # Separate input and output banks. Every capacitor keeps its actual rail
    # identity; a shared ground alone cannot choose a bank.
    for rail, (x0, y0, direction) in bank_origins.items():
        bank = sorted(p for p in members if p not in entries
                      and symbol_id(views[p]) in ('Device:C', 'Device:C_Polarized')
                      and {pin_nets.get((p,n)) for n in by_path[p].pins} == {rail, t['ground']})
        columns = 2 if t['kind'] == 'bridge' else 3
        for i, path in enumerate(bank):
            angle = orient_net(path, rail, (0,-1))
            put(path, x0 + direction*(i % columns)*25.4, y0+(i//columns)*30.48, angle)
    # Remaining sense/bootstrap/configuration parts are packed below the
    # principal circuit in real measured cells, outside its power paths.
    occupied = atom_bounds(list(entries.values()), views)
    x0, y0 = occupied[0], occupied[3]+15.24
    x, y, row = x0, y0, 0.0
    supports = sorted(set(members)-set(entries))
    if t['kind'] == 'bridge':
        # Measured horizontal support rows sit below the controller, leaving
        # gate escapes and the bridge switch midpoint clear.
        columns = [(-139.7, 88.9), (-40.64, 88.9), (60.96, 88.9)]
        for index, path in enumerate(supports):
            column = index % 3
            x, y = columns[column]
            angle = _horizontal(views[path])
            box = atom_bounds([(by_path[path], 0, 0, angle)], views)
            put(path, x-box[0], y-box[1], angle)
            columns[column] = (x, y+box[3]-box[1]+10.16)
        supports = []
    for path in supports:
        box = atom_bounds([(by_path[path],0,0,0)], views)
        width, height = box[2]-box[0], box[3]-box[1]
        if x > x0 and x+width > x0+300:
            x,y,row=x0,y+row+12.7,0.0
        put(path,x-box[0],y-box[1]);x+=width+12.7;row=max(row,height)
    result = list(entries.values())
    bounds = packing_bounds(result, views, pin_nets)
    if bounds[2]-bounds[0]+17.78 <=340 and bounds[3]-bounds[1]+17.78<=205 and _score(result,views,pin_nets)[:2] == (0,0):
        return result
    return None


def power_template_candidates(members, by_path, views, pin_nets):
    """Four measured bridge proposals and explicit geometry rejection evidence.

    This is a presentation search over a uniquely verified physical topology.
    Rail names and component reference prefixes never choose a terminal role.
    """
    from .KiCadSchematicLayout import pins, snap
    from .KiCadSchematicPlacement import (atom_bounds, packing_bounds, _horizontal,
                                         _rotation_for_pin, _score)
    topology = power_topology(members, by_path, views, pin_nets)
    if topology is None or topology['kind'] != 'bridge':
        return [], [dict(candidate='four_switch_bridge', acceptable=False,
                         reason='topology ambiguity or no unique four-switch bridge')]
    t = topology
    def orientation(path, net, direction):
        number = next(n for n in by_path[path].pins if pin_nets.get((path, n)) == net)
        return _rotation_for_pin(views[path], number, direction)
    def box(path, angle):
        return atom_bounds([(by_path[path], 0, 0, angle)], views)
    def netset(path):
        return {pin_nets.get((path, n)) for n in by_path[path].pins}
    ic, coil = t['ic'], t['coil']
    # Follow the controller's measured gate-pin order. A bidirectional
    # converter has no implied left-to-right power direction.
    controller_pins = pins(views[ic], 0, 0, 90)
    def gate_position(bridge):
        gate_net = t['roles'][bridge[0]]['gate']
        positions = [x for number, x, _, _ in controller_pins
                     if pin_nets.get((ic, number)) == gate_net]
        return sum(positions)/len(positions)
    bridges = sorted(enumerate(t['bridges'], 1), key=lambda item: gate_position(item[1]))
    candidates, diagnostics = [], []
    for gap in (15.24, 25.4):
        for offset in (0.0, 12.7):
            name = 'bridge_spacing_%g_controller_%g' % (gap, offset)
            entries = {}
            def put(path, x, y, angle=0):
                entries[path] = (by_path[path], snap(x), snap(y), angle)
            coil_angle = _horizontal(views[coil]); cb = box(coil, coil_angle)
            put(coil, 0, 0, coil_angle)
            # Measured occupied rectangles determine separation, including
            # fields and pin text. Switch nodes face the inductor midline.
            bridge_x = []
            for direction, (_, (hi, lo, rail)) in zip((-1, 1), bridges):
                ah = orientation(hi, t['roles'][hi]['source'], (0, 1))
                al = orientation(lo, t['roles'][lo]['drain'], (0, -1))
                hb, lb = box(hi, ah), box(lo, al)
                x = (cb[0] - gap - max(hb[2], lb[2]) if direction < 0
                     else cb[2] + gap - min(hb[0], lb[0]))
                bridge_x.append(x)
                put(hi, x, -gap/2-hb[3], ah)
                put(lo, x, gap/2-lb[1], al)
            # The wide rotated controller lives beneath both bridge legs.
            core = atom_bounds(list(entries.values()), views)
            ib = box(ic, 90)
            put(ic, offset, core[3]+10.16-ib[1], 90)
            controller_bounds = atom_bounds([entries[ic]], views)
            # Each true rail owns its capacitor bank, outward from its leg.
            # Shunts retain the same side as the rail they physically join.
            for index, (_, (hi, lo, rail)) in enumerate(bridges):
                direction = -1 if index == 0 else 1
                leg = atom_bounds([entries[hi], entries[lo]], views)
                bank = sorted(p for p in members if p not in entries
                    and symbol_id(views[p]) in ('Device:C', 'Device:C_Polarized')
                    and netset(p) == {rail, t['ground']})
                y = leg[1]
                for ordinal, path in enumerate(bank):
                    angle = orientation(path, rail, (0, -1)); b = box(path, angle)
                    x = leg[0]-gap-b[2] if direction < 0 else leg[2]+gap-b[0]
                    # Reserve physical pin escapes beyond the visible body.
                    # Start stable path order beside the controller, then grow
                    # toward the far row. This avoids attempting isolated far
                    # branches before the nearer rail tree exists.
                    x += direction * (ordinal % 2) * 30.48
                    put(path, x, y+((len(bank)-1)//2-ordinal//2)*30.48-b[1], angle)
            # A uniquely connected series resistor is a rail shunt, placed
            # above its actual high-side drain, with its outer bank nearby.
            for index, (_, (hi, lo, rail)) in enumerate(bridges):
                shunts = sorted(p for p in members if p not in entries
                    and symbol_id(views[p]) in ('Device:R', 'Device:R_US')
                    and len(netset(p)) == 2 and rail in netset(p))
                if len(shunts) != 1:
                    continue
                path = shunts[0]; angle = orientation(path, rail, (0, 1))
                hb = atom_bounds([entries[hi]], views); b = box(path, angle)
                put(path, bridge_x[index], hb[1]-12.7-b[3], angle)
                outer = next(iter(netset(path)-{rail}))
                raw = sorted(p for p in members if p not in entries
                    and symbol_id(views[p]) in ('Device:C', 'Device:C_Polarized')
                    and netset(p) == {outer, t['ground']})
                direction = -1 if index == 0 else 1
                for ordinal, cap in enumerate(raw):
                    ca = orientation(cap, outer, (0, -1)); bb = box(cap, ca)
                    capx = hb[0]-gap-bb[2] if direction < 0 else hb[2]+gap-bb[0]
                    put(cap, capx+direction*ordinal*30.48, hb[1]-20.32-bb[3], ca)
            # Bootstrap branches beside their actual switch; remaining parts
            # are measured shelves below, retaining exact component identity.
            r = t['roles'][ic]
            for side, (index, (hi, lo, rail)) in enumerate(bridges):
                pair = {r.get('btst%d'%index), r['sw%d'%index]}
                branch = sorted(p for p in members if p not in entries and netset(p) == pair)
                direction = -1 if side == 0 else 1
                leg = atom_bounds([entries[hi]], views)
                for path in branch:
                    angle = _horizontal(views[path]); b = box(path, angle)
                    x = bridge_x[side] - direction * 15.24
                    put(path, x, -0.5*(b[1]+b[3]), angle)
            # A controller driver-supply bypass belongs beside its actual
            # supply pin, rather than extending the unrelated support shelf.
            # Only an exact capacitor between the compiled supply and return
            # qualifies; no component or reference names participate.
            supplies = {r[role] for role in ('regn', 'drv_sup') if role in r}
            for supply in sorted(supplies):
                bypasses = sorted(p for p in members if p not in entries
                    and symbol_id(views[p]) in ('Device:C', 'Device:C_Polarized')
                    and netset(p) == {supply, t['ground']})
                terminals = [(x, y) for number, x, y, _ in pins(views[ic], *entries[ic][1:])
                             if pin_nets.get((ic, number)) == supply]
                if not terminals:
                    continue
                px = sum(x for x,y in terminals)/len(terminals)
                py = max(y for x,y in terminals)
                supply_bounds = packing_bounds([entries[ic]], views, pin_nets)
                for ordinal, path in enumerate(bypasses):
                    angle = orientation(path, supply, (0, -1))
                    b = box(path, angle)
                    # Dense controller pins reserve vertical external-label
                    # corridors below the body. Keep the bypass outside the
                    # entire measured corridor, not merely outside the body.
                    left = supply_bounds[0]-12.7-b[2]
                    right = supply_bounds[2]+12.7-b[0]
                    proposals = [(x, py+ordinal*25.4+dy) for dy in (0,-15.24,15.24)
                                 for x in sorted((left,right),key=lambda x: (abs(x-px),x))]
                    for x,y in proposals:
                        candidate = (by_path[path],snap(x),snap(y),angle)
                        if _score(list(entries.values())+[candidate],views,pin_nets)[:2] == (0,0):
                            entries[path]=candidate
                            break
                    else:
                        # The final measured gate reports a specific failure;
                        # it must never move the part into the label corridor.
                        put(path,left,py+ordinal*25.4,angle)
            remaining = sorted(set(members)-set(entries))
            occupied = atom_bounds(list(entries.values()), views)
            x0, y = occupied[0], occupied[3]+10.16
            x, row = x0, 0.0
            for path in remaining:
                angle = _horizontal(views[path]); b = box(path, angle)
                width,height=b[2]-b[0],b[3]-b[1]
                if x > x0 and x+width > x0+300:
                    x,y,row=x0,y+row+10.16,0.0
                put(path,x-b[0],y-b[1],angle)
                x+=width+10.16;row=max(row,height)
            result=list(entries.values()); bounds=packing_bounds(result,views,pin_nets)
            geometry=_score(result,views,pin_nets)
            reasons=[]
            if geometry[0]:reasons.append('escape conflict')
            if geometry[1]:reasons.append('symbol or field collision')
            width,height=bounds[2]-bounds[0]+17.78,bounds[3]-bounds[1]+17.78
            if width>340 or height>205:reasons.append('overflow')
            diagnostics.append(dict(candidate=name,acceptable=not reasons,
                reason='; '.join(reasons) if reasons else 'valid measured bridge',
                escape_conflicts=geometry[0],collisions=geometry[1],
                width_mm=round(width,4),height_mm=round(height,4)))
            if not reasons:candidates.append((name,result))
    return candidates, diagnostics


def compare_bridge_variants(placed, views, pin_nets, baseline, router, *,
                            region_bounds=None, source_annotations=None):
    """Compare measured bridges against an already oriented, cached incumbent.

    At most four baseline-router calls, with exactly the orientation pass's
    objective. No second orientation sweep or route-order optimizer is hidden
    inside this bounded comparison.
    """
    import copy
    from .KiCadSchematicLayout import freeze_annotations, snap
    from .KiCadSchematicPlacement import packing_bounds
    from .KiCadSchematicOrientation import orientation_metrics, _rank, _geometry
    by_path = {c.path: c for c, _, _, _ in placed}
    circuits = {c.functional_circuit.id: c.functional_circuit for c in by_path.values()
                if getattr(c, 'functional_circuit', None) is not None
                and c.functional_circuit.template == 'four_switch_bridge'}
    if len(circuits) != 1:
        return placed, baseline, None
    circuit = next(iter(circuits.values()))
    if not set(by_path) <= set(circuit.components) or any(
            getattr(getattr(c, 'functional_circuit', None), 'id', None) != circuit.id
            for c in by_path.values()):
        return placed, baseline, dict(selected='orientation_only', route_trials=0,
            reason='region includes components outside the bridge circuit', trials=[])
    source_by_path = {}
    for path, component in by_path.items():
        source = copy.copy(component)
        source.annotation = (source_annotations or {}).get(path)
        source_by_path[path] = source
    candidates, diagnostics = power_template_candidates(tuple(sorted(source_by_path)),source_by_path,views,pin_nets)
    before = best = orientation_metrics(placed,views,pin_nets,baseline)
    original_failures = set(baseline[2])
    selected, selected_route, name = placed, baseline, 'orientation_only'
    old_bounds = packing_bounds(placed,views,pin_nets)
    geometry = _geometry(placed,views,pin_nets)
    trials, calls = [], 0
    for candidate_name, entries in candidates:
        bounds = packing_bounds(entries,views,pin_nets)
        dx,dy = snap(old_bounds[0]-bounds[0]),snap(old_bounds[1]-bounds[1])
        source = []
        for c,x,y,angle in entries:
            component = copy.copy(c)
            annotation = (source_annotations or {}).get(c.path)
            component.annotation = annotation
            source.append((component,snap(x+dx),snap(y+dy),angle))
        candidate = freeze_annotations(source,views)
        trial_geometry = _geometry(candidate,views,pin_nets)
        reason = None
        if trial_geometry['escape_conflicts']>geometry['escape_conflicts']:
            reason = 'escape conflict'
        elif trial_geometry['collisions'] or trial_geometry['collision_pairs']:
            reason = 'symbol, field or pin text collision'
        elif trial_geometry['clipped']:
            reason = 'page overflow'
        trial = dict(candidate=candidate_name,selected=False,geometry=trial_geometry)
        if reason is None:
            route = router(candidate,views,pin_nets);calls += 1
            metric = orientation_metrics(candidate,views,pin_nets,route)
            trial['metrics'] = metric
            clipped = False
            if region_bounds is not None:
                a,b,c,d=region_bounds(candidate,route);w,h=c-a,d-b
                clipped=w>375 or h>225 or (w>210 and h>205)
            if clipped:
                reason='routed region page overflow'
            elif not set(route[2]) <= original_failures:
                reason='new failed endpoints'
            elif metric['visual_conflicts']>best['visual_conflicts']:
                reason='inadequate visual wire clearance'
            elif _rank(metric)>=_rank(best):
                reason='incumbent scores better or ties'
            else:
                selected,selected_route,best,name=candidate,route,metric,candidate_name
                trial['selected']=True;reason='improved routed score'
        trial['reason']=reason;trials.append(trial)
    return selected,selected_route,dict(selected=name,route_trials=calls,before=before,after=best,
        candidates=diagnostics,trials=trials)


def gate_driver_circuits(components, pin_nets, views):
    """Verify a split pull-up/down driver, source return and local bootstrap."""
    if views is None:
        return []
    by_path = {c.path: c for c in components}
    roles = {p: role_nets(c, pin_nets) for p, c in by_path.items()}
    nets = {p: {pin_nets.get((p, n)) for n in c.pins} for p, c in by_path.items()}
    resistors = {p for p in by_path if symbol_id(views[p]) in ('Device:R', 'Device:R_US')}
    capacitors = {p for p in by_path if symbol_id(views[p]) in ('Device:C', 'Device:C_Polarized')}
    diodes = {p for p in by_path if symbol_id(views[p]) in ('Device:D', 'Device:D_Schottky', 'Device:D_Zener')}
    result = []
    for anchor, r in sorted(roles.items()):
        if not {'tgup', 'tgdn', 'ts', 'bst', 'vcc', 'gnd'} <= r.keys():
            continue
        fets = [p for p, terminals in roles.items() if terminals.get('gate') == r['tgdn']
                and terminals.get('source') == r['ts'] and 'drain' in terminals]
        gate_resistors = [p for p in resistors if nets[p] == {r['tgup'], r['tgdn']}]
        bootstrap = [p for p in capacitors if nets[p] == {r['bst'], r['ts']}]
        if len(fets) != 1 or len(gate_resistors) != 1 or len(bootstrap) != 1:
            continue
        members = {anchor, fets[0], gate_resistors[0], bootstrap[0]}
        members |= {p for p in resistors if nets[p] == {r['tgdn'], r['ts']}}
        members |= {p for p in diodes if nets[p] in ({r['vcc'], r['bst']}, {r['gnd'], r['ts']})}
        result.append((anchor, tuple(sorted(members - {anchor})), tuple(sorted({r['tgup'], r['tgdn'], r['ts'], r['bst']}))))
    return result
