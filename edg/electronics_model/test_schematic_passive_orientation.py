"""Quarter turns preserve electrical identities while improving real wire paths."""
import copy
import unittest
from unittest.mock import patch

from .KiCadSchematicExporter import PhysicalComponent, SymbolView, node
from .KiCadSchematicLayout import route_local
from .KiCadSchematicOrientation import optimize_passive_orientations, passive_orientation_rank, orientation_conflict_identities, _visual_clearance_conflict_identities, _visual_conflicts
from .test_schematic_functional_placement import passive_view


MODULE = 'edg.electronics_model.KiCadSchematicOrientation.'


class PassiveOrientationTest(unittest.TestCase):
    def fixture(self, count=1):
        entries, views, nets = [], {}, {}
        for index in range(count):
            component = PhysicalComponent(f'part{index:03}', f'R{index}', 'Fixture:Pad', 'part',
                                          {'1': 'a', '2': 'b'}, None, 'circuit')
            entries.append((component, 50.+index*20, 70., 0))
            views[component.path] = passive_view('Device:R')
            nets[component.path, '1'] = 'positive'
            nets[component.path, '2'] = 'negative'
        return entries, views, nets

    def geometry(self, *args):
        return dict(escape_conflicts=0, collisions=0, collision_pairs=[], clipped=False)

    def metric(self, placed, *args):
        return dict(primary_fallbacks=0, crossings=0, unrelated_intrusions=0,
                    length_mm=1000-sum(angle==(90 if int(c.path[-3:])%2==0 else 270)
                                      for c, _, _, angle in placed),
                    bends=0, detour_mm=0, visual_conflicts=0)

    def test_all_three_angles_share_incumbent_and_every_path_gets_one_visit(self):
        entries, views, nets = self.fixture(40)
        original = copy.deepcopy((entries, views, nets))
        calls = []
        baseline = ([], {}, [])
        def router(*args):
            calls.append(args)
            return baseline
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', self.metric), patch(MODULE+'_escape_conflict_identities', return_value=frozenset()):
            placed, _, evidence = optimize_passive_orientations(entries, views, nets, router, baseline=baseline)
        self.assertEqual(len(calls), 120)
        self.assertEqual(evidence['route_trial_limit'], 120)
        self.assertEqual(evidence['sweeps'], 1)
        self.assertEqual([trial['path'] for trial in evidence['trials']],
                         [c.path for c, _, _, _ in entries for _ in range(3)])
        for offset in range(0, 120, 3):
            trials = evidence['trials'][offset:offset+3]
            self.assertEqual([trial['to_rotation'] for trial in trials], [90, 180, 270])
            self.assertEqual([trial['from_rotation'] for trial in trials], [0, 0, 0])
            self.assertEqual(sum(trial['selected'] for trial in trials), 1)
        self.assertEqual([angle for _, _, _, angle in placed], [90, 270]*20)
        self.assertEqual((entries, views, nets), original)
        self.assertEqual([(x, y) for _, x, y, _ in entries], [(x, y) for _, x, y, _ in placed])

    def test_replacement_escape_conflict_same_count_is_rejected(self):
        entries, views, nets = self.fixture()
        old = [('a', (0, 0), (10, 0), 'moving', '1'),
               ('b', (0, 0), (0, 10), 'old-neighbor', '1'),
               ('c', (20, 0), (20, 10), 'new-neighbor', '1')]
        new = [('a', (10, 0), (20, 0), 'moving', '1'), *old[1:]]
        def escapes(placed, *args):
            return old if placed[0][3] == 0 else new
        baseline = ([], {}, [])
        with patch('edg.electronics_model.KiCadSchematicPlacement.pin_escapes', escapes), patch(
                MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', self.metric):
            initial = orientation_conflict_identities(entries, views, nets, baseline)['escape']
            changed = orientation_conflict_identities([(entries[0][0], 50, 70, 90)], views, nets, baseline)['escape']
            self.assertEqual(len(initial), len(changed))
            self.assertNotEqual(initial, changed)
            calls = []
            _, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: calls.append(args) or baseline, baseline=baseline)
        self.assertFalse(evidence['changed'])
        self.assertEqual(calls, [])
        self.assertTrue(all(t['reason'] == 'new physical escape conflict' for t in evidence['trials']))

    def test_replacement_wire_clearance_same_count_is_rejected(self):
        entries, views, nets = self.fixture()
        old_wires = [('a', (0, 0), (10, 0)), ('b', (0, .635), (10, .635))]
        new_wires = [('a', (0, 0), (10, 0)), ('c', (0, .635), (10, .635))]
        self.assertEqual(_visual_conflicts(old_wires), _visual_conflicts(new_wires))
        self.assertNotEqual(_visual_clearance_conflict_identities((old_wires, {}, []), nets),
                            _visual_clearance_conflict_identities((new_wires, {}, []), nets))
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', self.metric), patch(
                MODULE+'_escape_conflict_identities', return_value=frozenset()):
            _, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: (new_wires, {}, []), baseline=(old_wires, {}, []))
        self.assertFalse(evidence['changed'])
        self.assertEqual(evidence['route_trials'], 3)
        self.assertTrue(all(t['reason'] == 'new visual wire clearance conflict' for t in evidence['trials']))

    def test_visual_clearance_identities_ignore_straight_wire_segmentation(self):
        whole = [('a', (0, 0), (10, 0)), ('b', (0, .635), (10, .635))]
        split = [('a', (0, 0), (5, 0)), ('a', (5, 0), (10, 0)),
                 ('b', (10, .635), (3, .635)), ('b', (3, .635), (0, .635))]
        self.assertEqual(_visual_clearance_conflict_identities((whole, {}, []), {}),
                         _visual_clearance_conflict_identities((split, {}, []), {}))

    def test_verified_symbol_policy_ignores_reference_and_footprint_guesses(self):
        entries, views, nets = self.fixture(8)
        ids = ['Device:R', 'Device:R_US_PB_mapping', 'Device:C', 'Device:C_Polarized',
               'Device:L', 'Fixture:Capacitor', 'PB:generic', 'Device:R']
        for (component, _, _, _), lib in zip(entries, ids):
            views[component.path].lib_id = lib
        views['part007'].pins.append(('3', 5.08, 0., 180))
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', self.metric), patch(MODULE+'_escape_conflict_identities', return_value=frozenset()):
            _, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, []), baseline=([], {}, []), locked={'part004'})
        self.assertEqual([item['eligible'] for item in evidence['eligibility']],
                         [True, True, True, True, False, False, False, False])
        self.assertEqual(evidence['route_trials'], 12)
        self.assertEqual(evidence['eligibility'][4]['reason'], 'explicit rotation lock')
        self.assertIn('two distinct', evidence['eligibility'][7]['reason'])

    def test_custom_symbol_name_cannot_masquerade_as_verified_id(self):
        from .KiCadSchematicOrientation import _passive_quarter_turn_eligibility
        entries, views, _ = self.fixture()
        component = entries[0][0]
        view = views[component.path]
        view.lib_id = 'Device:R_PB_custom_PB_resolvermap'
        self.assertFalse(_passive_quarter_turn_eligibility(component, view, set())[0])
        view.lib_id = 'Device:R_PB_resolvermap'
        self.assertTrue(_passive_quarter_turn_eligibility(component, view, set())[0])

    def test_auto_fields_recomputed_authored_annotations_preserved_and_inputs_unchanged(self):
        entries, views, nets = self.fixture(2)
        entries[0][0].annotation = (900., 900.)  # a frozen automatic baseline
        entries[1][0].annotation = (100., 120.)  # authored; partial map preserves it
        original = copy.deepcopy((entries, views, nets))
        observations = []
        def router(placed, *args):
            observations.append({c.path: c.annotation for c, _, _, _ in placed})
            return [], {}, []
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', self.metric):
            placed, _, evidence = optimize_passive_orientations(entries, views, nets, router,
                baseline=([], {}, []), locked={'part001'}, source_annotations={'part000': None})
        self.assertTrue(all(item['part000'] != (900., 900.) for item in observations))
        self.assertTrue(all(item['part001'] == (100., 120.) for item in observations))
        self.assertEqual(placed[1][0].annotation, (100., 120.))
        self.assertEqual((entries, views, nets), original)
        self.assertEqual(evidence['final_rotations'], {'part000': 90, 'part001': 0})

    def test_ties_preserve_angle_and_locked_components_consume_no_trials(self):
        entries, views, nets = self.fixture(2)
        entries[0] = (*entries[0][:3], 90)
        metric = dict(primary_fallbacks=0, crossings=0, unrelated_intrusions=0,
                      length_mm=20, bends=0, detour_mm=0, visual_conflicts=0)
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', return_value=metric):
            placed, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, []), baseline=([], {}, []), locked={'part001'})
        self.assertEqual([angle for _, _, _, angle in placed], [90, 0])
        self.assertEqual([trial['to_rotation'] for trial in evidence['trials']], [0, 180, 270])
        self.assertFalse(evidence['changed'])
        self.assertEqual(evidence['route_trials'], 3)

    def test_weighted_cost_tie_keeps_incumbent_despite_fewer_bends(self):
        entries, views, nets = self.fixture()
        def metric(items, *args):
            result = self.metric(items, *args)
            angle = items[0][3]
            result.update(length_mm=100.0 if angle == 0 else 102.54,
                          bends=1 if angle == 0 else 0, detour_mm=0)
            return result
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', metric):
            placed, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, []), baseline=([], {}, []))
        self.assertEqual(placed[0][3], 0)
        self.assertFalse(evidence['changed'])
        self.assertEqual(evidence['route_trials'], 3)
        self.assertTrue(all(t['reason'] == 'incumbent scores better or ties' for t in evidence['trials']))

    def test_equal_cost_improving_alternatives_keep_first_stable_angle(self):
        entries, views, nets = self.fixture()
        def metric(items, *args):
            result = self.metric(items, *args)
            angle = items[0][3]
            length, bends = {0: (200., 0), 90: (100., 1),
                             180: (102.54, 0), 270: (110., 0)}[angle]
            result.update(length_mm=length, bends=bends, detour_mm=length)
            return result
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', metric):
            placed, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, []), baseline=([], {}, []))
        self.assertEqual(placed[0][3], 90)
        self.assertTrue(evidence['changed'])
        self.assertEqual(evidence['route_trials'], 3)
        self.assertEqual([t['to_rotation'] for t in evidence['trials'] if t['selected']], [90])

    def test_new_failed_endpoint_rejected(self):
        entries, views, nets = self.fixture()
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', self.metric):
            placed, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, [(('part000', '1'), 'positive')]), baseline=([], {}, []))
        self.assertEqual(placed[0][3], 0)
        self.assertTrue(all(trial['reason']=='new failed endpoints' for trial in evidence['trials']))

    def test_collisions_and_overflow_are_recorded_without_routing_invalid_angles(self):
        entries, views, nets = self.fixture()
        def geometry(placed, *args):
            angle = placed[0][3]
            return dict(escape_conflicts=0, collisions=0,
                collision_pairs=[('part000', 0, 'foreign', 0)] if angle==90 else [], clipped=angle==270)
        with patch(MODULE+'_geometry', geometry), patch(MODULE+'orientation_metrics', self.metric):
            _, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, []), baseline=([], {}, []))
        self.assertEqual(evidence['route_trials'], 1)
        self.assertEqual(evidence['trials'][0]['reason'], 'new symbol, field or pin text collision')
        self.assertEqual(evidence['trials'][2]['reason'], 'page overflow')
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', self.metric):
            _, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, []), baseline=([], {}, []), region_bounds=lambda *args: (0, 0, 500, 500))
        self.assertTrue(all(t['reason']=='routed region page overflow' for t in evidence['trials']))

    def test_balanced_wire_cost_allows_a_shorter_path_with_an_extra_bend(self):
        entries, views, nets = self.fixture()
        def metric(placed, *args):
            angle = placed[0][3]
            length, bends = {0:(100., 0),90:(90., 1),180:(99., 0),270:(89., 5)}[angle]
            return dict(primary_fallbacks=0, crossings=0, unrelated_intrusions=0,
                        length_mm=length, bends=bends, detour_mm=0, visual_conflicts=0)
        with patch(MODULE+'_geometry', self.geometry), patch(MODULE+'orientation_metrics', metric):
            placed, _, evidence = optimize_passive_orientations(entries, views, nets,
                lambda *args: ([], {}, []), baseline=([], {}, []))
        self.assertEqual(placed[0][3], 90)
        self.assertLess(passive_orientation_rank(evidence['after']), passive_orientation_rank(evidence['before']))

    def real_fixture(self, lib_id, target_angle, parallel=False):
        component = PhysicalComponent('passive', 'C1', 'Fixture:Passive', '4.7uF',
                                      {'1':'pos', '2':'neg'}, None, 'circuit')
        anchor = PhysicalComponent('anchor', 'J1', 'Fixture:Pad', 'PAD', {'1':'power'}, None, 'circuit')
        view = passive_view(lib_id)
        nets = {('passive','1'):'power', ('passive','2'):'gnd', ('anchor','1'):'power'}
        if parallel:
            component.pins['3'] = 'pos'
            view.pins.append(('3', *view.pins[0][1:]))
            nets['passive','3']='power'
        views={'passive':view,'anchor':SymbolView(node('symbol',node('symbol','anchor_0_1',
            node('rectangle',node('start',-1,-1),node('end',1,1)))),
            [('1',0.,0.,0 if target_angle==270 else 180)],'Fixture:Anchor')}
        px, ax = (50.,90.) if target_angle==270 else (90.,50.)
        return [(component,px,70.,0),(anchor,ax,70.,0)],views,nets

    def test_real_router_quarter_turns_shorten_rcl_preserving_parallel_pads_and_polarity(self):
        for lib_id in ('Device:R','Device:R_US','Device:C','Device:C_Polarized','Device:L'):
            for angle in (90,270):
                with self.subTest(lib_id=lib_id,angle=angle):
                    entries, views, nets = self.real_fixture(lib_id, angle, parallel=True)
                    original = copy.deepcopy((entries,views,nets))
                    placed, route, evidence = optimize_passive_orientations(entries,views,nets,route_local)
                    self.assertEqual(placed[0][3],angle)
                    self.assertLess(evidence['after']['length_mm'],evidence['before']['length_mm'])
                    self.assertLess(passive_orientation_rank(evidence['after']),passive_orientation_rank(evidence['before']))
                    self.assertEqual(route[2],[])
                    self.assertEqual(set(route[1]),set(nets))
                    self.assertEqual((entries,views,nets),original)
                    self.assertEqual([(x,y) for _,x,y,_ in entries],[(x,y) for _,x,y,_ in placed])
                    self.assertEqual(optimize_passive_orientations(entries,views,nets,route_local),
                                     (placed,route,evidence))


if __name__ == '__main__':
    unittest.main()
