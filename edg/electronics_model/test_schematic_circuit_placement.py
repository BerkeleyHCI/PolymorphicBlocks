"""Circuit-level placement honors authored intent without losing net truth."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from .test_schematic_functional_placement import part, passive_view
from .KiCadSchematicExporter import generic
from .KiCadSchematicPatterns import SchematicPattern
from .KiCadSchematicPlacement import (
    functional_atoms, _whole_candidates, _choose_routes, _staged_template, _candidate_valid,
)


class CircuitPlacementTest(unittest.TestCase):
    def parts(self):
        parts = [part(p, {'1': 'input', '2': 'output', '3': 'gnd'}) for p in ('a', 'b', 'c')]
        views = {c.path: generic(c) for c in parts}
        nets = {(c.path, n): c.path+n for c in parts for n in c.pins}
        nets['a','2'] = nets['b','1'] = 'ab'
        nets['b','2'] = nets['c','1'] = 'bc'
        return parts,views,nets

    def circuit(self, components, stages=(), boundaries=()):
        return SimpleNamespace(id='test', provenance='explicit', template='auto', components=tuple(components),
                               stages=tuple(stages), boundaries=tuple(boundaries), primary_nets=('ab','bc'))

    def test_shared_model_preserves_authored_boundary_against_automatic_union(self):
        parts,views,nets = self.parts()
        first = self.circuit(('a','b'))
        model = SimpleNamespace(circuits=(first,), patterns=(
            SchematicPattern('power_subcircuit',('a','b','c'),('ab','bc')),))
        for c in parts:
            c.circuit_model = model
            c.functional_circuit = first if c.path in first.components else None
        with patch('edg.electronics_model.KiCadSchematicPlacement.discover_patterns',
                   side_effect=AssertionError('shared model must be reused')):
            atoms,_ = functional_atoms(parts,nets,views)
        self.assertEqual(atoms,(('a','b'),('c',)))

    def test_explicit_stages_place_input_to_output_and_rotate_boundary(self):
        from .KiCadSchematicLayout import pins
        parts,views,nets = self.parts()
        boundary = SimpleNamespace(component='a',pin='1',role='input')
        stages = [SimpleNamespace(components=(p,)) for p in ('a','b','c')]
        circuit = self.circuit(('a','b','c'),stages,[boundary])
        for c in parts:
            c.functional_circuit = circuit
        placed = _staged_template(circuit.components,{c.path:c for c in parts},views,nets)
        self.assertIsNotNone(placed)
        self.assertTrue(_candidate_valid(placed,views,nets))
        self.assertEqual([c.path for c,_,_,_ in placed],['a','b','c'])
        self.assertLess(placed[0][1],placed[1][1])
        self.assertLess(placed[1][1],placed[2][1])
        c,x,y,angle = placed[0]
        terminal = next(p for p in pins(views[c.path],x,y,angle) if p[0]=='1')
        self.assertLess(terminal[1],x)

    def test_measured_overflow_splits_authored_stages_without_rejoining(self):
        from .KiCadSchematicExporter import SymbolView, node
        parts,_,nets = self.parts()
        views = {c.path:SymbolView(node('symbol','Large',node('symbol','Large_0_1',
                    node('rectangle',node('start',-65,-35),node('end',65,35)))),
                    [('1',-70,0,0),('2',70,0,180),('3',0,40,90)],'Fixture:Large') for c in parts}
        stages = [SimpleNamespace(components=(p,)) for p in ('a','b','c')]
        circuit = self.circuit(('a','b','c'),stages)
        model = SimpleNamespace(circuits=(circuit,),patterns=(
            SchematicPattern('power_subcircuit',('a','b','c'),('ab','bc')),))
        for c in parts:
            c.functional_circuit=circuit;c.circuit_model=model
        atoms,_ = functional_atoms(parts,nets,views)
        self.assertEqual(atoms,(('a',),('b',),('c',)))
        self.assertTrue(all(c.functional_continuation for c in parts))

    def test_unrelated_stage_space_is_protected_from_through_routes(self):
        from .KiCadSchematicPlacement import _stage_intrusions
        parts,views,nets = self.parts()
        circuit = self.circuit(('a','b','c'),[SimpleNamespace(components=('a','b'))])
        for c in parts:
            c.functional_circuit = circuit
        placed = [(parts[0],40,80,0),(parts[1],100,80,0),(parts[2],150,80,0)]
        unrelated = [('external',(70,60),(70,100))]
        self.assertEqual(_stage_intrusions(placed,unrelated,views,nets),1)
        self.assertEqual(_stage_intrusions(placed,[('ab',(70,60),(70,100))],views,nets),0)

    def test_route_selection_prefers_visible_primary_path_to_shorter_wire(self):
        parts,views,nets = self.parts()
        circuit = self.circuit(('a','b','c'))
        for c in parts:
            c.functional_circuit = circuit
        baseline = [(c,i*45.72,0,0) for i,c in enumerate(parts)]
        candidate = [(c,x+5.08,y,a) for c,x,y,a in baseline]
        original = ([('ab',(40,80),(50,80))],{},[(('a','2'),'ab')])
        clearer = ([('ab',(40,80),(100,80))],{},[])
        with patch('edg.electronics_model.KiCadSchematicLayout.route_local',side_effect=[original,clearer]):
            selected,evidence = _choose_routes(baseline,[('template',baseline),('clear',candidate)],views,nets)
        self.assertEqual(selected,candidate)
        self.assertEqual(evidence['after']['primary_fallbacks'],0)
        self.assertGreater(evidence['after']['length_mm'],evidence['before']['length_mm'])


    def test_explicit_generic_does_not_invoke_power_template(self):
        from .KiCadSchematicPlacement import _circuit_template
        parts,views,nets = self.parts()
        circuit = self.circuit(('a','b','c'))
        circuit.template = 'generic'
        for c in parts:
            c.functional_circuit = circuit
        with patch('edg.electronics_model.KiCadSchematicPower.power_template',
                   side_effect=AssertionError('generic must not select a power layout')):
            entries = _circuit_template(circuit.components,{c.path:c for c in parts},views,nets)
        self.assertEqual({c.path for c,_,_,_ in entries},{'a','b','c'})

    def test_explicit_power_template_dispatch_and_authored_stage_precedence(self):
        from .KiCadSchematicPlacement import _circuit_template
        parts,views,nets = self.parts()
        circuit = self.circuit(('a','b','c'))
        circuit.template = 'buck'
        for c in parts:
            c.functional_circuit = circuit
        marker = [(c,40*i,0,0) for i,c in enumerate(parts)]
        with patch('edg.electronics_model.KiCadSchematicPower.power_template',return_value=marker) as power:
            self.assertEqual(_circuit_template(circuit.components,{c.path:c for c in parts},views,nets),marker)
            power.assert_called_once()
        circuit.stages = tuple(SimpleNamespace(components=(c.path,)) for c in parts)
        with patch('edg.electronics_model.KiCadSchematicPower.power_template',
                   side_effect=AssertionError('authored stages take precedence')):
            entries = _circuit_template(circuit.components,{c.path:c for c in parts},views,nets)
        self.assertEqual([c.path for c,_,_,_ in entries],['a','b','c'])

    def test_authored_serial_chain_uses_functional_stage_placement(self):
        from .KiCadSchematicLayout import place_group
        parts,views,nets = self.parts()
        circuit = self.circuit(('a','b','c'),[SimpleNamespace(components=(c.path,)) for c in parts])
        circuit.template = 'repeated_channel'
        model = SimpleNamespace(circuits=(circuit,), patterns=(
            SchematicPattern('serial_data_chain',('a','b','c'),('ab','bc')),))
        for c in parts:
            c.functional_circuit=circuit;c.circuit_model=model
        with patch('edg.electronics_model.KiCadSchematicLayout._place_group_legacy',
                   side_effect=AssertionError('authored stages must not use legacy bypass')):
            pages = place_group(parts,views,nets)
        self.assertTrue(pages)
        self.assertTrue(all(hasattr(c,'placement_evidence') for page in pages for c,_,_,_ in page))


    def test_authored_repeated_chain_without_stages_retains_inline_template(self):
        from .KiCadSchematicLayout import place_group
        parts,views,nets = self.parts()
        circuit = self.circuit(('a','b','c'))
        circuit.template = 'repeated_channel'
        model = SimpleNamespace(circuits=(circuit,), patterns=(
            SchematicPattern('serial_data_chain',('a','b','c'),('ab','bc')),))
        for c in parts:
            c.functional_circuit=circuit;c.circuit_model=model
        marker = [[(c,40*i,80,0) for i,c in enumerate(parts)]]
        with patch('edg.electronics_model.KiCadSchematicLayout._place_group_legacy',return_value=marker) as inline:
            with patch('edg.electronics_model.KiCadSchematicPlacement.place_functional',
                       side_effect=AssertionError('unstaged repeated chain must retain inline template')):
                self.assertEqual(place_group(parts,views,nets),marker)
        inline.assert_called_once()
        # The template name alone cannot establish a serial relationship.
        model.patterns = ()
        with patch('edg.electronics_model.KiCadSchematicLayout._place_group_legacy',
                   side_effect=AssertionError('serial topology must be verified')):
            with patch('edg.electronics_model.KiCadSchematicPlacement.place_functional',return_value=marker):
                self.assertEqual(place_group(parts,views,nets),marker)


    def test_whole_candidate_budget_deduplication_and_locked_owner(self):
        parts,views,nets = self.parts()
        baseline = [(c,i*45.72,0,0) for i,c in enumerate(parts)]
        candidates = _whole_candidates(baseline,[baseline]*10,views,nets,{'a'})
        self.assertLessEqual(len(candidates),8)
        self.assertEqual(candidates[0],('template',baseline))
        for _,candidate in candidates:
            self.assertEqual(candidate[0],baseline[0])
        keys = [tuple((c.path,x,y,a) for c,x,y,a in entries) for _,entries in candidates]
        self.assertEqual(len(keys),len(set(keys)))

    def test_route_shortlist_is_bounded_and_new_failed_endpoint_rejected(self):
        parts,views,nets = self.parts()
        baseline = [(c,i*45.72,0,0) for i,c in enumerate(parts)]
        candidates = [('template',baseline)] + [(str(i),[(c,x,y+i*2.54,a) for c,x,y,a in baseline])
                                              for i in range(1,8)]
        original = ([],{},[((('a','1')),'a1')])
        invalid = ([],{},[((('b','1')),'ab')])
        with patch('edg.electronics_model.KiCadSchematicLayout.route_local',
                   side_effect=[original,invalid,invalid,invalid]) as router:
            selected,evidence = _choose_routes(baseline,candidates,views,nets)
        self.assertEqual(router.call_count,4)
        self.assertEqual(selected,baseline)
        self.assertEqual(evidence['route_trials'],4)
        self.assertFalse(any(t['acceptable'] for t in evidence['trials']))

    def test_safe_baseline_retained_when_candidate_routes_outside_page(self):
        parts,views,nets = self.parts()
        baseline = [(c,i*45.72,0,0) for i,c in enumerate(parts)]
        candidate = [(c,x+5.08,y,a) for c,x,y,a in baseline]
        original=([('ab',(40,80),(80,80))],{},[])
        outside=([('ab',(5,80),(20,80))],{},[])
        with patch('edg.electronics_model.KiCadSchematicLayout.route_local',side_effect=[original,outside]):
            selected,evidence = _choose_routes(baseline,[('template',baseline),('bad',candidate)],views,nets)
        self.assertEqual(selected,baseline)
        self.assertFalse(evidence['trials'][0]['acceptable'])


if __name__ == '__main__':
    unittest.main()
