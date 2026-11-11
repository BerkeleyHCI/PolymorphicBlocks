"""Functional circuits remain complete, compact and deterministic during layout."""
import unittest

from .KiCadSchematicExporter import PhysicalComponent, SymbolView, generic, node
from .KiCadSchematicLayout import place_group, split_group
from .KiCadSchematicPlacement import functional_atoms, component_boxes, _overlap, signal_nets


def part(path, pins, lib_id=None):
    return PhysicalComponent(path, path.rsplit('.', 1)[-1], 'Test:FP', 'part', pins,
                             {'lib_id': lib_id} if lib_id else None, 'circuit')


def passive_view(lib_id):
    return SymbolView(node('symbol', lib_id,
        node('symbol', 'part_0_1', node('rectangle', node('start', -1, 3), node('end', 1, -3)))),
        [('1', 0, -5.08, 270), ('2', 0, 5.08, 90)], lib_id)


class FunctionalPlacementTest(unittest.TestCase):
    def test_power_roles_allow_parallel_pads_only_on_same_net(self):
        from .KiCadSchematicPower import role_nets
        ic = part('ic', {'1': 'sw', '2': 'sw', '3': 'gnd'})
        nets = {('ic', '1'): 'switch', ('ic', '2'): 'switch', ('ic', '3'): 'return'}
        self.assertEqual(role_nets(ic, nets)['sw'], 'switch')
        nets['ic', '2'] = 'different'
        self.assertNotIn('sw', role_nets(ic, nets))

    def test_buck_coil_aligns_with_switch_terminal(self):
        from .KiCadSchematicPower import power_template
        from .KiCadSchematicLayout import pins
        ic = part('ic', {'1': 'vin', '2': 'sw', '3': 'gnd'})
        coil = part('coil', {'1': 'a', '2': 'b'}, 'Device:L')
        views = {'ic': generic(ic), 'coil': passive_view('Device:L')}
        nets = {('ic', '1'): 'in', ('ic', '2'): 'switch', ('ic', '3'): 'gnd',
                ('coil', '1'): 'switch', ('coil', '2'): 'out'}
        entries = power_template(['ic', 'coil'], {'ic': ic, 'coil': coil}, views, nets)
        self.assertIsNotNone(entries)
        terminals = {}
        for component, x, y, angle in entries:
            for number, px, py, _ in pins(views[component.path], x, y, angle):
                if nets[component.path, number] == 'switch':
                    terminals[component.path] = (px, py)
        self.assertEqual(terminals['ic'][1], terminals['coil'][1])
        self.assertGreater(terminals['coil'][0], terminals['ic'][0])

    def test_input_inductor_does_not_claim_buck_topology(self):
        from .KiCadSchematicPower import power_topology
        ic = part('ic', {'1': 'vin', '2': 'sw', '3': 'gnd'})
        coil = part('coil', {'1': 'a', '2': 'b'}, 'Device:L')
        parts = {'ic': ic, 'coil': coil}
        views = {'ic': generic(ic), 'coil': passive_view('Device:L')}
        nets = {('ic', '1'): 'in', ('ic', '2'): 'sw', ('ic', '3'): 'gnd',
                ('coil', '1'): 'in', ('coil', '2'): 'sw'}
        self.assertIsNone(power_topology(parts, parts, views, nets))

    def test_bridge_kernel_excludes_unrelated_control_fet(self):
        from .KiCadSchematicPower import power_topology, bridge_kernel
        ic = part('ic', {str(i): role for i, role in enumerate(
            ['gnd', 'sw1', 'sw2', 'hidrv1', 'hidrv2', 'lodrv1', 'lodrv2'])})
        coil = part('coil', {'1': 'sw1', '2': 'sw2'}, 'Device:L')
        parts = [ic, coil]
        for i in (1, 2):
            parts += [part(f'hi{i}', {'1': 'gate', '2': 'source', '3': 'drain'}),
                      part(f'lo{i}', {'1': 'gate', '2': 'source', '3': 'drain'})]
        parts.append(part('ce', {'1': 'gate', '2': 'source', '3': 'drain'}))
        nets = {(ic.path, n): role for n, role in ic.pins.items()}
        nets.update({('coil', '1'): 'sw1', ('coil', '2'): 'sw2'})
        for i in (1, 2):
            nets.update({(f'hi{i}', '1'): f'hidrv{i}', (f'hi{i}', '2'): f'sw{i}',
                         (f'hi{i}', '3'): f'rail{i}', (f'lo{i}', '1'): f'lodrv{i}',
                         (f'lo{i}', '2'): 'gnd', (f'lo{i}', '3'): f'sw{i}'})
        nets.update({('ce', '1'): 'enable', ('ce', '2'): 'gnd', ('ce', '3'): 'ce'})
        by_path = {c.path: c for c in parts}
        views = {c.path: generic(c) for c in parts}; views['coil'] = passive_view('Device:L')
        topology = power_topology(list(by_path), by_path, views, nets)
        self.assertEqual(topology['kind'], 'bridge')
        kernel = bridge_kernel(topology, by_path, by_path, views, nets)
        self.assertEqual(kernel, set(by_path) - {'ce'})

    def test_gate_driver_cross_sibling_graph_requires_gate_and_return(self):
        from .KiCadSchematicPower import gate_driver_circuits
        roles = ['vcc', 'gnd', 'gnd', 'tgup', 'tgdn', 'ts', 'bst']
        ic = part('driver', {str(i): r for i, r in enumerate(roles)})
        fet = part('switch', {'1': 'gate', '2': 'source', '3': 'drain'})
        res = part('gate_r', {'1': 'a', '2': 'b'}, 'Device:R')
        cap = part('bootstrap', {'1': 'pos', '2': 'neg'}, 'Device:C')
        unrelated = part('unrelated', {'1': 'pos', '2': 'neg'}, 'Device:C')
        parts = [ic, fet, res, cap, unrelated]
        views = {c.path: generic(c) for c in parts}
        for c, lib in [(res, 'Device:R'), (cap, 'Device:C'), (unrelated, 'Device:C')]:
            views[c.path] = passive_view(lib)
        nets = {(ic.path, n): role for n, role in ic.pins.items()}
        nets.update({('switch', '1'): 'tgdn', ('switch', '2'): 'ts', ('switch', '3'): 'power',
                     ('gate_r', '1'): 'tgup', ('gate_r', '2'): 'tgdn',
                     ('bootstrap', '1'): 'bst', ('bootstrap', '2'): 'ts',
                     ('unrelated', '1'): 'vcc', ('unrelated', '2'): 'gnd'})
        circuits = gate_driver_circuits(parts, nets, views)
        self.assertEqual(len(circuits), 1)
        self.assertEqual(set(circuits[0][1]), {'switch', 'gate_r', 'bootstrap'})
        nets['switch', '2'] = 'another_return'
        self.assertFalse(gate_driver_circuits(parts, nets, views))

    def test_differential_sense_filters_form_support_atoms(self):
        from .KiCadSchematicPatterns import discover_patterns
        ic = part('charger.ic', {'1': 'acp', '2': 'acn', '3': 'gnd', '4': 'gnd'})
        rp = part('charger.rp', {'1': 'a', '2': 'b'}, 'Device:R')
        rn = part('charger.rn', {'1': 'a', '2': 'b'}, 'Device:R')
        cap = part('charger.c', {'1': 'pos', '2': 'neg'}, 'Device:C')
        parts = [ic, rp, rn, cap]
        nets = {('charger.ic', '1'): 'p', ('charger.ic', '2'): 'n',
                ('charger.ic', '3'): 'gnd', ('charger.ic', '4'): 'gnd',
                (rp.path, '1'): 'p', (rp.path, '2'): 'input',
                (rn.path, '1'): 'n', (rn.path, '2'): 'output',
                (cap.path, '1'): 'p', (cap.path, '2'): 'n'}
        patterns = discover_patterns(parts, nets)
        sense = next(p for p in patterns if p.kind == 'differential_sense_filter')
        self.assertEqual(set(sense.components), {rp.path, rn.path, cap.path})
        views = {ic.path: generic(ic), rp.path: passive_view('Device:R'),
                 rn.path: passive_view('Device:R'), cap.path: passive_view('Device:C')}
        atoms, _ = functional_atoms(parts, nets, views)
        self.assertIn(tuple(sorted(sense.components)), atoms)

    def test_large_mcu_with_five_bypasses_uses_measured_bank(self):
        from .KiCadSchematicPlacement import _template, packing_bounds, _score
        ic = part('control.mcu.ic', {str(i): f'gpio{i}' for i in range(64)})
        ic.pins.update({'64': 'gnd', '65': 'gnd', '66': 'vdd', '67': 'vdd'})
        caps = [part(f'control.mcu.pwr_cap[{i}].cap', {'1': 'pos', '2': 'neg'}, 'Device:C')
                for i in range(5)]
        for c in caps:
            c.hierarchy = ((c.path.rpartition('.')[0], 'edg.abstract_parts.Capacitor.DecouplingCapacitor'),)
        parts = [ic, *caps]
        views = {ic.path: generic(ic), **{c.path: passive_view('Device:C') for c in caps}}
        nets = {(ic.path, n): role if role in ('gnd', 'vdd') else 'signal'+n for n, role in ic.pins.items()}
        for c in caps:
            nets[c.path, '1'] = 'vdd'; nets[c.path, '2'] = 'gnd'
        atoms, patterns = functional_atoms(parts, nets, views)
        self.assertEqual(len(atoms), 1)
        entries = _template(atoms[0], patterns, {c.path: c for c in parts}, views, nets)
        bounds = packing_bounds(entries, views, nets)
        self.assertLessEqual(bounds[2]-bounds[0]+17.78, 340)
        self.assertLessEqual(bounds[3]-bounds[1]+17.78, 205)
        self.assertEqual(_score(entries, views, nets)[:2], (0, 0))
        self.assertEqual(len(place_group(parts, views, nets)), 1)

    def amplifier(self, prefix='amp'):
        amp = part(prefix + '.ic', {'1': 'out', '2': 'inp', '3': 'inn', '4': 'vcc', '5': 'gnd'})
        fb = part(prefix + '.feedback', {'1': 'a', '2': 'b'}, 'Device:R')
        cap = part(prefix + '.bypass.cap', {'1': 'pos', '2': 'neg'}, 'Device:C')
        cap.hierarchy = ((prefix + '.bypass', 'edg.abstract_parts.Capacitor.DecouplingCapacitor'),)
        parts = [amp, fb, cap]
        views = {amp.path: generic(amp), fb.path: passive_view('Device:R'), cap.path: passive_view('Device:C')}
        wiring = {(amp.path, '1'): prefix + '_output', (amp.path, '2'): prefix + '_input',
                  (amp.path, '3'): prefix + '_negative', (amp.path, '4'): 'common_positive',
                  (amp.path, '5'): 'common_return', (fb.path, '1'): prefix + '_output',
                  (fb.path, '2'): prefix + '_negative', (cap.path, '1'): 'common_positive',
                  (cap.path, '2'): 'common_return'}
        return parts, views, wiring

    def test_same_net_escape_cannot_cross_neighbor_pin_number(self):
        from .KiCadSchematicPlacement import escape_conflicts
        from .KiCadSchematicExporter import S
        a = part("a", {"1": "p"})
        b = part("b", {"1": "p"})
        definition = node("symbol", "Fixture", node("symbol", "Fixture_1_1",
                          node("pin", S("passive"), S("line"), node("at", 0, 0, 0),
                               node("length", 2.54), node("number", "3"))))
        views = {"a": SymbolView(node("symbol"), [("1", 0, 0, 0)], "Fixture:A"),
                 "b": SymbolView(definition, [("1", 0, 0, 0)], "Fixture:B")}
        entries = [(a, 50, 50, 0), (b, 46, 51.397, 0)]
        nets = {("a", "1"): "same", ("b", "1"): "same"}
        self.assertGreater(escape_conflicts(entries, views, nets), 0)
        definition.append(node("pin_numbers", S("hide")))
        self.assertEqual(escape_conflicts(entries, views, nets), 0)

    def test_compiled_repeated_channels_keep_all_support_parts_together(self):
        first, va, wa = self.amplifier('balance[0]')
        second, vb, wb = self.amplifier('balance[1]')
        for group in (first, second):
            for c in group:
                owner = c.path.split('.')[0]
                c.hierarchy = ((owner, 'Test.BalanceChannel'),) + c.hierarchy
        parts, views, wiring = first + second, {**va, **vb}, {**wa, **wb}
        atoms, patterns = functional_atoms(parts, wiring, views)
        self.assertEqual(sum(p.kind == 'repeated_subcircuit' for p in patterns), 2)
        self.assertEqual({frozenset(a) for a in atoms},
                         {frozenset(c.path for c in group) for group in (first, second)})
        for page in place_group(parts, views, wiring):
            members = {entry[0].path for entry in page}
            for atom in atoms:
                self.assertTrue(not set(atom) & members or set(atom) <= members)

    def test_verified_power_subtree_keeps_controller_and_stage_together(self):
        ic = part('supply.ic', {'1': 'sw', '2': 'gnd', '3': 'vin', '4': 'fb', '5': 'en', '6': 'pg'})
        coil = part('supply.coil', {'1': 'a', '2': 'b'}, 'Device:L')
        cap = part('supply.cap', {'1': 'pos', '2': 'neg'}, 'Device:C')
        res = part('supply.res', {'1': 'a', '2': 'b'}, 'Device:R')
        parts = [ic, coil, cap, res]
        for c in parts:
            c.hierarchy = (('supply', 'Test.PowerCircuit'),)
        views = {ic.path: generic(ic), **{c.path: passive_view(c.mapping['lib_id']) for c in parts[1:]}}
        wiring = {(ic.path, '1'): 'switch', (ic.path, '2'): 'return',
                  (coil.path, '1'): 'switch', (coil.path, '2'): 'output',
                  (cap.path, '1'): 'output', (cap.path, '2'): 'return',
                  (res.path, '1'): 'output', (res.path, '2'): 'feedback', (ic.path, '4'): 'feedback'}
        atoms, patterns = functional_atoms(parts, wiring, views)
        self.assertEqual(len(atoms), 1)
        self.assertTrue(any(p.kind == 'power_subcircuit' for p in patterns))
        pages = place_group(parts, views, wiring)
        self.assertEqual(len(pages), 1)
        self.assertIsNone(split_group(pages[0], views, wiring))

    def test_repeated_channel_order_is_numeric(self):
        parts, views, wiring = [], {}, {}
        for index in (10, 2, 0):
            group, gv, gw = self.amplifier(f'channel[{index}]')
            for c in group:
                c.hierarchy = ((f'channel[{index}]', 'Test.Channel'),) + c.hierarchy
            parts += group; views.update(gv); wiring.update(gw)
        pages = place_group(parts, views, wiring)
        self.assertEqual([c.path for page in pages for c, _, _, _ in page if c.path.endswith('.ic')],
                         ['channel[0].ic', 'channel[2].ic', 'channel[10].ic'])

    def test_oversized_repeated_channel_splits_at_compiled_child_boundaries(self):
        parts, views, wiring = [], {}, {}
        for channel in range(2):
            owner = f'channel[{channel}]'
            for child in ('driver', 'isolator', 'regulator'):
                parent = owner + '.' + child
                device = part(parent + '.ic', {'1': 'input', '2': 'output', '3': 'gnd'})
                cap = part(parent + '.cap', {'1': 'pos', '2': 'neg'}, 'Device:C')
                for c in (device, cap):
                    c.hierarchy = ((owner, 'Test.ComplexChannel'), (parent, 'Test.SupportCircuit'))
                parts.extend((device, cap))
                views[device.path] = SymbolView(node('symbol', 'Test:Large', node('symbol', 'part_0_1',
                    node('rectangle', node('start', -60, -50), node('end', 60, 50)))),
                    [('1', -65, 0, 0), ('2', 65, 0, 180), ('3', 0, 55, 90)], 'Test:Large')
                views[cap.path] = passive_view('Device:C')
                wiring.update({(device.path, '2'): parent + '.local', (cap.path, '1'): parent + '.local',
                               (device.path, '3'): 'return', (cap.path, '2'): 'return'})
        atoms, patterns = functional_atoms(parts, wiring, views)
        self.assertEqual(len(atoms), 6)
        self.assertTrue(all(len(atom) == 2 for atom in atoms))
        self.assertTrue(all('measured whole circuit exceeds A3' == c.functional_continuation['reason'] for c in parts))
        self.assertTrue(any(p.kind == 'functional_section' for p in patterns))

    def test_shared_rails_do_not_establish_repeated_channel_ownership(self):
        from .KiCadSchematicPatterns import hierarchy_circuits
        parts = [part(f'array[{channel}].cap{index}', {'1': 'pos', '2': 'neg'}, 'Device:C')
                 for channel in range(2) for index in range(3)]
        for c in parts:
            c.hierarchy = ((c.path.split('.')[0], 'Test.Channel'),)
        views = {c.path: passive_view('Device:C') for c in parts}
        wiring = {(c.path, n): net for c in parts for n, net in [('1', 'supply'), ('2', 'return')]}
        self.assertEqual(hierarchy_circuits(parts, wiring, views), ())

    def test_overlapping_feedback_and_bypass_patterns_form_one_atom(self):
        parts, views, wiring = self.amplifier()
        atoms, patterns = functional_atoms(parts, wiring, views)
        self.assertEqual(atoms, (tuple(sorted(p.path for p in parts)),))
        self.assertEqual({p.kind for p in patterns}, {'amplifier_feedback', 'local_decoupling'})
        pages = place_group(parts, views, wiring)
        self.assertEqual(len(pages), 1)
        positions = {e[0].path: e for e in pages[0]}
        amp, fb, cap = [positions[p.path] for p in parts]
        self.assertLess(fb[2], amp[2])
        self.assertGreater(cap[2], amp[2])
        self.assertEqual(cap[1], amp[1])
        self.assertLess(abs(fb[1] - amp[1]) + abs(fb[2] - amp[2]), 50)
        self.assertIsNone(split_group(pages[0], views, wiring))

    def test_compact_template_has_no_body_or_field_overlap(self):
        parts, views, wiring = self.amplifier()
        page = place_group(parts, views, wiring)[0]
        for i, entry in enumerate(page):
            for other in page[i + 1:]:
                for a in component_boxes(entry, views):
                    for b in component_boxes(other, views):
                        self.assertFalse(_overlap(a, b))

    def test_packed_amplifier_vp_vn_bypass_stays_in_its_owner_atom(self):
        parts, views, wiring = self.amplifier()
        owner, _, cap = parts
        owner.pins['4'], owner.pins['5'] = 'vp', 'vn'
        atoms, patterns = functional_atoms(parts, wiring, views)
        self.assertEqual(atoms, (tuple(sorted(p.path for p in parts)),))
        self.assertIn('local_decoupling', {p.kind for p in patterns})
        wiring[cap.path, '2'] = 'other_return'
        atoms, patterns = functional_atoms(parts, wiring, views)
        self.assertNotIn('local_decoupling', {p.kind for p in patterns})

    def test_repeated_channels_keep_distinct_bypass_ownership(self):
        first, va, wa = self.amplifier('channel[0]')
        second, vb, wb = self.amplifier('channel[1]')
        parts, views, wiring = first + second, {**va, **vb}, {**wa, **wb}
        atoms, _ = functional_atoms(parts, wiring, views)
        self.assertEqual({frozenset(a) for a in atoms},
                         {frozenset(p.path for p in first), frozenset(p.path for p in second)})
        pages = place_group(parts, views, wiring)
        self.assertEqual(pages, place_group(list(reversed(parts)), views, dict(reversed(list(wiring.items())))))
        flattened = [e for page in pages for e in page]
        self.assertEqual(sorted(e[0].path for e in flattened), sorted(p.path for p in parts))
        for p in parts:
            self.assertLessEqual(p.placement_evidence['candidates'], 64)
        for page in pages:
            membership = {e[0].path for e in page}
            for atom in atoms:
                self.assertTrue(not set(atom) & membership or set(atom) <= membership)

    def test_repeated_signature_requires_compiled_classes_and_same_connectivity(self):
        from .KiCadSchematicPlacement import channel_signature
        first, va, wa = self.amplifier('channel[0]')
        second, vb, wb = self.amplifier('channel[1]')
        parts, views, wiring = first + second, {**va, **vb}, {**wa, **wb}
        for group in (first, second):
            for i, c in enumerate(group):
                c.hierarchy = ((c.path.rpartition('.')[0], 'Test.CompiledClass' + str(i)),) + c.hierarchy
        by_path = {c.path: c for c in parts}
        atoms, patterns = functional_atoms(parts, wiring, views)
        self.assertEqual(len(atoms), 2)
        signatures = [channel_signature(atom, by_path, wiring, views, patterns) for atom in atoms]
        self.assertIsNotNone(signatures[0])
        self.assertEqual(signatures[0], signatures[1])
        changed = dict(wiring)
        changed[second[1].path, '1'] = 'distinct_output'
        self.assertNotEqual(signatures[1], channel_signature(atoms[1], by_path, changed, views, patterns))
        second[0].hierarchy = ()
        self.assertIsNone(channel_signature(atoms[1], by_path, wiring, views, patterns))

    def test_declared_supply_roles_exclude_anonymously_named_rails(self):
        parts, views, wiring = self.amplifier()
        signals = signal_nets(parts, wiring)
        self.assertNotIn('common_positive', signals)
        self.assertNotIn('common_return', signals)
        self.assertIn('amp_output', signals)

    def test_split_prefers_fewer_signal_boundaries_over_component_midpoint(self):
        # A-B-C is a complete signal island; D is isolated. Splitting in the
        # middle would cut the actual path even though it balances pin count.
        parts = [part(p, {'1': 'sig', '2': 'other', '3': 'gnd'}) for p in ('a', 'b', 'c', 'd')]
        views = {p.path: generic(p) for p in parts}
        wiring = {('a', '1'): 'ab', ('b', '1'): 'ab', ('b', '2'): 'bc', ('c', '1'): 'bc'}
        for p in parts:
            wiring[p.path, '3'] = 'shared_return'
        placed = [(p, 30 + i * 50, 70, 0) for i, p in enumerate(parts)]
        left, right = split_group(placed, views, wiring)
        self.assertEqual([e[0].path for e in left], ['a', 'b', 'c'])
        self.assertEqual([e[0].path for e in right], ['d'])

    def test_feedback_diodes_cannot_share_cross_net_escape_endpoint(self):
        from .KiCadSchematicPlacement import escape_conflicts, _score
        amp = part('packed.ic', {'1': 'outa', '2': 'inna', '3': 'inpa', '5': 'inpb', '6': 'innb', '7': 'outb'})
        d9 = part('control.err_sink.diode', {'1': 'cathode', '2': 'anode'}, 'Device:D')
        d8 = part('control.err_source.diode', {'1': 'cathode', '2': 'anode'}, 'Device:D')
        # Real D9/D8 geometry from the native SMU failure: a 10.16 mm
        # pin-tip gap lets opposite 5.08 mm escapes touch exactly.
        definition = node('symbol', 'Device:D', node('symbol', 'D_0_1',
                          node('rectangle', node('start', -1, 1), node('end', 1, -1))))
        views = {amp.path: generic(amp),
                 d9.path: SymbolView(definition, [('1', 3.81, 0, 180), ('2', -3.81, 0, 0)], 'Device:D'),
                 d8.path: SymbolView(definition, [('1', -3.81, 0, 0), ('2', 3.81, 0, 180)], 'Device:D')}
        wiring = {(amp.path, '1'): 'out0', (amp.path, '2'): 'negative', (amp.path, '3'): 'signal0',
                  (amp.path, '7'): 'out1', (amp.path, '6'): 'negative', (amp.path, '5'): 'signal1',
                  (d9.path, '1'): 'out0', (d9.path, '2'): 'negative',
                  (d8.path, '1'): 'negative', (d8.path, '2'): 'out1'}
        touching = [(d9, 48.4, 56.16, 0), (d8, 66.18, 56.16, 0)]
        safe = [(d9, 48.4, 56.16, 0), (d8, 66.18, 61.24, 0)]
        self.assertGreater(escape_conflicts(touching, views, wiring), 0)
        self.assertEqual(escape_conflicts(safe, views, wiring), 0)
        self.assertLess(_score(safe, views, wiring), _score(touching, views, wiring))
        pages = place_group([amp, d9, d8], views, wiring)
        for page in pages:
            self.assertEqual(escape_conflicts(page, views, wiring), 0)
        shared = dict(wiring)
        shared[d9.path, '1'] = shared[d8.path, '1']
        self.assertEqual(escape_conflicts(touching, views, shared), 0)

    def test_packing_reserves_mcu_header_external_label_corridors(self):
        from .KiCadSchematicPlacement import packing_bounds
        mcu = part('mcu.ic', {'1': 'uart_tx', '2': 'uart_rx', '3': 'gnd'})
        header = part('header.conn', {'1': 'a', '2': 'b'})
        wiring = {(mcu.path, '1'): 'uart.tx', (header.path, '1'): 'uart.tx',
                  (mcu.path, '2'): 'uart.rx', (header.path, '2'): 'uart.rx',
                  (mcu.path, '3'): 'gnd'}
        mcu.net_labels = {'1': 'serial.interface.transmit', '2': 'serial.interface.receive', '3': 'gnd'}
        header.net_labels = {'1': mcu.net_labels['1'], '2': mcu.net_labels['2']}
        views = {c.path: generic(c) for c in (mcu, header)}
        pages = place_group([mcu, header], views, wiring)
        for page in pages:
            for i, entry in enumerate(page):
                for other in page[i + 1:]:
                    self.assertFalse(_overlap(packing_bounds([entry], views, wiring),
                                              packing_bounds([other], views, wiring)))
        self.assertEqual(pages, place_group([header, mcu], views, wiring))

    def test_packing_does_not_reserve_unrendered_internal_label_wall(self):
        from .KiCadSchematicPlacement import packing_bounds, atom_bounds
        a = part('a', {'1': 'a', '2': 'b'})
        b = part('b', {'1': 'a', '2': 'b'})
        views = {c.path: passive_view('Device:R') for c in (a, b)}
        wiring = {(a.path, '1'): 'inner', (b.path, '1'): 'inner'}
        a.net_labels = b.net_labels = {'1': 'long_internal_connection' * 8}
        entries = [(a, 40, 100, 90), (b, 80, 100, 270)]
        bound = packing_bounds(entries, views, wiring)
        # The internal label would be over 200 mm wide; packing only needs
        # bodies/fields and exact pin escapes because this net is inside atom.
        self.assertLess(bound[2] - bound[0], 100)
        wiring['outside', '1'] = 'inner'
        outside = packing_bounds(entries, views, wiring)
        self.assertGreater(outside[2] - outside[0], bound[2] - bound[0] + 100)

    def test_indicator_pairs_are_inline_atomic_even_when_entire_group_is_two_terminal(self):
        from .KiCadSchematicLayout import pins
        for count in (1, 4):
            parts, views, wiring, pairs = [], {}, {}, []
            for i in range(count):
                led = part(f'branch[{i}].led', {'1': 'a', '2': 'k'}, 'Device:LED')
                resistor = part(f'branch[{i}].resistor', {'1': 'a', '2': 'b'}, 'Device:R')
                parts.extend((led, resistor)); pairs.append((led, resistor))
                views[led.path] = passive_view('Device:LED')
                views[resistor.path] = passive_view('Device:R')
                wiring[led.path, '1'] = wiring[resistor.path, '1'] = f'inner{i}'
                wiring[led.path, '2'] = 'return'
                wiring[resistor.path, '2'] = f'input{i}'
            pages = place_group(parts, views, wiring)
            self.assertEqual(sorted(e[0].path for page in pages for e in page), sorted(p.path for p in parts))
            for led, resistor in pairs:
                owning = [page for page in pages if any(e[0] is led for e in page)]
                self.assertEqual(len(owning), 1)
                entries = {e[0].path: e for e in owning[0]}
                self.assertIn(resistor.path, entries)
                a, b = entries[led.path], entries[resistor.path]
                self.assertEqual(a[2], b[2])
                self.assertLess(a[1], b[1])
                # Both actual shared terminals face each other horizontally.
                p1 = next(pin for pin in pins(views[led.path], *a[1:]) if pin[0] == '1')
                p2 = next(pin for pin in pins(views[resistor.path], *b[1:]) if pin[0] == '1')
                self.assertEqual(p1[3], 180)
                self.assertEqual(p2[3], 0)

    def test_route_guard_rejects_new_fallback_endpoint(self):
        from unittest.mock import patch
        from .KiCadSchematicPlacement import _route_guard
        parts, views, wiring = self.amplifier()
        baseline = [(parts[0], 0, 0, 0), (parts[1], 40, 0, 90)]
        candidate = [(parts[0], 0, 0, 0), (parts[1], 30, 0, 90)]
        # Even an equal failure count is insufficient if a formerly visible
        # endpoint becomes a different label fallback.
        old = ([], {}, [((parts[0].path, '1'), 'amp_output')])
        new = ([], {}, [((parts[1].path, '1'), 'amp_output')])
        with patch('edg.electronics_model.KiCadSchematicLayout.route_local', side_effect=[old, new]):
            selected, evidence = _route_guard(baseline, candidate, views, wiring)
        self.assertEqual(selected, baseline)
        self.assertFalse(evidence['accepted'])
        self.assertEqual(evidence['route_trials'], 2)

    def test_route_guard_translates_both_local_templates_into_router_window(self):
        from unittest.mock import patch
        from .KiCadSchematicPlacement import _route_guard, atom_bounds
        parts, views, wiring = self.amplifier()
        baseline = [(parts[0], 0, 0, 0), (parts[1], 0, -30.48, 90)]
        candidate = [(parts[0], 0, 0, 0), (parts[1], 2.54, -30.48, 90)]
        with patch('edg.electronics_model.KiCadSchematicLayout.route_local', return_value=([], {}, [])) as route:
            _route_guard(baseline, candidate, views, wiring)
        trials = [call.args[0] for call in route.call_args_list]
        self.assertEqual(len(trials), 2)
        shifts = []
        for original, trial in zip((baseline, candidate), trials):
            box = atom_bounds(trial, views)
            self.assertGreater(box[0], 20)
            self.assertGreater(box[1], 55)
            shifts.append((trial[0][1] - original[0][1], trial[0][2] - original[0][2]))
        self.assertEqual(shifts[0], shifts[1])

    def test_divider_uses_vertical_resistor_pair_beside_owner(self):
        owner = part('reg.ic', {'1': 'fb', '2': 'gnd', '3': 'vin'})
        hi = part('reg.top', {'1': 'a', '2': 'b'}, 'Device:R')
        lo = part('reg.bottom', {'1': 'a', '2': 'b'}, 'Device:R')
        parts = [owner, hi, lo]
        views = {owner.path: generic(owner), hi.path: passive_view('Device:R'), lo.path: passive_view('Device:R')}
        wiring = {(owner.path, '1'): 'fb', (owner.path, '2'): 'gnd', (owner.path, '3'): 'input',
                  (hi.path, '1'): 'output', (hi.path, '2'): 'fb', (lo.path, '1'): 'fb', (lo.path, '2'): 'gnd'}
        page = place_group(parts, views, wiring)[0]
        placements = {e[0].path: e for e in page}
        self.assertGreater(placements[hi.path][1], placements[owner.path][1])
        self.assertGreater(placements[lo.path][1], placements[owner.path][1])
        self.assertLess(placements[hi.path][2], placements[lo.path][2])


if __name__ == '__main__':
    unittest.main()
