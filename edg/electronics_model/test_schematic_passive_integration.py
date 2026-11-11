"""Prepared baseline reuse, final geometry plans and serialized rollback."""
import copy
import json
import os
import subprocess
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch

import sexpdata

from ..core import Block, GeneratorBlock, ScalaCompiler
from .CircuitBlock import FootprintBlock
from .PassivePort import Passive
from .KiCadSchematicExporter import KiCadSchematicExporter, SchematicExportOptions, SchematicPlacement, SchematicExport, children
from .KiCadSchematicLayout import freeze_annotations
from .KiCadSchematicPlanner import SchematicSheetPlan
from .RefdesRefinementPass import RefdesRefinementPass


class QuarterPassive(GeneratorBlock, FootprintBlock):
    def __init__(self):
        super().__init__()
        self.a = self.Port(Passive(), optional=True)
        self.gnd = self.Port(Passive(), optional=True)

    def generate(self):
        super().generate()
        self.footprint('C', 'Test:Cap', {'1': self.a, '2': self.gnd}, value='4.7uF')
        self.schematic_symbol('Device:C_Polarized', {'1': '1', '2': '2'})


class QuarterAnchor(GeneratorBlock, FootprintBlock):
    def __init__(self):
        super().__init__()
        self.a = self.Port(Passive(), optional=True)

    def generate(self):
        super().generate()
        self.footprint('J', 'Test:Pad', {'1': self.a}, value='PAD')


class QuarterSpare(GeneratorBlock, FootprintBlock):
    def __init__(self):
        super().__init__()
        self.a = self.Port(Passive(), optional=True)
        self.b = self.Port(Passive(), optional=True)

    def generate(self):
        super().generate()
        self.footprint('U', 'Test:Unmapped', {'1': self.a, '2': self.b}, value='unmapped')


class QuarterCircuit(Block):
    def contents(self):
        super().contents()
        self.passive = self.Block(QuarterPassive())
        self.anchor = self.Block(QuarterAnchor())
        self.spare = self.Block(QuarterSpare())
        self.connect(self.passive.a, self.anchor.a)


LIBRARY = '''(kicad_symbol_lib (version 20211014) (generator test)
 (symbol "C_Polarized" (pin_names (offset 0))
  (property "Reference" "C" (at 2 1 0) (effects (font (size 1.27 1.27))))
  (property "Value" "C_Polarized" (at 2 -1 0) (effects (font (size 1.27 1.27))))
  (symbol "C_Polarized_0_1"
   (rectangle (start -1 3) (end 1 -3) (stroke (width 0) (type default)) (fill (type none))))
  (symbol "C_Polarized_1_1"
   (pin passive line (at 0 5.08 270) (length 2.08) (name "positive") (number "1"))
   (pin passive line (at 0 -5.08 90) (length 2.08) (name "negative") (number "2")))))'''


class PassiveIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        Path(cls.temp.name, 'Device.kicad_sym').write_text(LIBRARY)
        cls.compiled = ScalaCompiler.compile(QuarterCircuit)
        cls.compiled.append_values(RefdesRefinementPass().run(cls.compiled))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def options(self, **kwargs):
        return SchematicExportOptions('QuarterCircuit', symbol_library_dirs=(self.temp.name,),
            placements={'passive':SchematicPlacement('Demo',50,70,lock_rotation=False),
                        'anchor':SchematicPlacement('Demo',110,70)}, **kwargs)

    def evidence(self, bundle):
        return {r['region']:r for r in json.loads(bundle.files['routing.json'])['regions']}

    def poses(self, bundle):
        result = {}
        for name, text in bundle.files.items():
            if not name.endswith('.kicad_sch'):
                continue
            for symbol in children(sexpdata.loads(text),'symbol'):
                props={p[1]:p[2] for p in children(symbol,'property')}
                if 'PBPath' in props:
                    result[props['PBPath']]=children(symbol,'at')[0][1:]
        return result

    def test_default_and_disabled_modes_preserve_legacy_files(self):
        exporter=KiCadSchematicExporter()
        default=exporter.export(self.compiled,self.options())
        explicit=exporter.export(self.compiled,self.options(orientation_mode='half_turn'))
        self.assertEqual(default.files,explicit.files)
        old_off=exporter.export(self.compiled,self.options(optimize_orientations=False))
        quarter_off=exporter.export(self.compiled,self.options(
            optimize_orientations=False,orientation_mode='passive_quarter_turn'))
        self.assertEqual(old_off.files,quarter_off.files)
        self.assertNotIn('passive_orientation',quarter_off.files['routing.json'])
        for value in ('unknown',None,False):
            with self.assertRaises(ValueError):
                self.options(orientation_mode=value)

    def test_real_quarter_turn_after_legacy_routing_is_deterministic_and_immutable(self):
        exporter=KiCadSchematicExporter()
        original=self.compiled.design.SerializeToString(),copy.deepcopy(self.compiled._values)
        options=self.options(orientation_mode='passive_quarter_turn')
        first=exporter.export(self.compiled,options)
        evidence=self.evidence(first)['Demo']['passive_orientation']
        self.assertTrue(evidence['accepted'],evidence)
        self.assertEqual(evidence['final_rotations']['passive'],270)
        self.assertEqual(evidence['route_trials'],3)
        self.assertLess(evidence['after']['length_mm'],evidence['before']['length_mm'])
        self.assertEqual(first.files,exporter.export(self.compiled,options).files)
        self.assertEqual((self.compiled.design.SerializeToString(),self.compiled._values),original)
        base=self.poses(exporter.export(self.compiled,self.options()))
        actual=self.poses(first)
        for axis in (0,1):
            self.assertEqual(round(base['passive'][axis]-base['anchor'][axis],4),
                             round(actual['passive'][axis]-actual['anchor'][axis],4))
        self.assertEqual(base['anchor'][2],actual['anchor'][2])

    def test_adopted_plan_validates_final_quarter_turn_geometry(self):
        exporter=KiCadSchematicExporter()
        options=self.options(orientation_mode='passive_quarter_turn')
        first=exporter.export(self.compiled,options)
        plan=SchematicSheetPlan.from_dict(json.loads(first.files['sheet-plan.json']))
        adopted=exporter.export(self.compiled,replace(options,sheet_plan=plan))
        self.assertEqual(first.files,adopted.files)
        stale=replace(plan,fingerprint='stale')
        with self.assertRaisesRegex(ValueError,'stale'):
            exporter.export(self.compiled,replace(options,sheet_plan=stale))

    def test_serialized_scene_rollback_uses_cached_baseline_without_repreparing(self):
        exporter=KiCadSchematicExporter()
        options=self.options(orientation_mode='passive_quarter_turn')
        baseline=exporter.export(self.compiled,self.options())
        prepare=exporter._prepare_legacy_boards
        with patch.object(exporter,'_prepare_legacy_boards',wraps=prepare) as preparations, patch.object(
                exporter,'_passive_scene_issues',side_effect=[{}, {'(root)':{('label_collision','new'):1.0}}]):
            result=exporter.export(self.compiled,options)
        self.assertEqual(preparations.call_count,1)
        evidence=self.evidence(result)['Demo']['passive_orientation']
        self.assertFalse(evidence['accepted'])
        self.assertEqual(evidence['rollback_reason'],'new blocking serialized scene finding')
        self.assertEqual(self.poses(result),self.poses(baseline))
        self.assertEqual(json.loads(result.files['sheet-plan.json'])['fingerprint'],
                         json.loads(baseline.files['sheet-plan.json'])['fingerprint'])

    def _serialized_label_contacts(self, existing_x, other_x, wires=()):
        # A deliberately preexisting bad label keeps the same UUID and fallback
        # flag. Only its actual serialized obstacle contacts change.
        document = f'''(kicad_sch (uuid "sheet")
          (lib_symbols (symbol "Test:Box"
            (symbol "Box_0_1" (rectangle (start -1 -1) (end 1 1)))))
          (symbol (lib_id "Test:Box") (at {existing_x} 50 0) (uuid "old")
            (property "PBPath" "existing-body" (at 0 0 0)
              (effects (font (size 1.27 1.27)) hide)))
          (symbol (lib_id "Test:Box") (at {other_x} 50 0) (uuid "other")
            (property "PBPath" "other-body" (at 0 0 0)
              (effects (font (size 1.27 1.27)) hide)))
          (label "BUS" (at 50 50 0) (uuid "same-label")
            (effects (font (size 1.27 1.27)))))'''
        wire_nodes = ''.join(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})))' for a,b in wires)
        document = document[:-1] + wire_nodes + ')'
        bundle = SchematicExport({
            'Board.kicad_sch': document,
            'manifest.json': json.dumps({'boards': [{'root': 'Board.kicad_sch', 'scope': '(root)'}]}),
            'layout.json': json.dumps({'label_placement': [{'sheet': 'sheet',
                'conflicts': [{'identity': 'same-label'}], 'unresolved_anchors': []}]}),
            'readability.json': json.dumps({'findings': []}),
        }, [])
        return KiCadSchematicExporter._passive_scene_issues(bundle)['(root)']

    def test_existing_bad_label_new_obstacle_rolls_back(self):
        old = self._serialized_label_contacts(50, 100)
        new = self._serialized_label_contacts(50, 50)
        self.assertEqual(old[('label_collision', 'same-label')],
                         new[('label_collision', 'same-label')])
        key = ('text_body_contact', 'same-label', 'other-body')
        self.assertNotIn(key, old)
        self.assertGreater(new[key], 0)
        self._assert_serialized_contact_rollback(old, new)

    def test_existing_contact_worsened_overlap_rolls_back(self):
        old = self._serialized_label_contacts(53, 100)
        new = self._serialized_label_contacts(52, 100)
        self.assertEqual(set(old), set(new))
        key = ('text_body_contact', 'same-label', 'existing-body')
        self.assertGreater(new[key], old[key])
        self._assert_serialized_contact_rollback(old, new)

    def test_existing_text_wire_contact_worsened_length_rolls_back(self):
        old = self._serialized_label_contacts(100, 120, [((49, 50), (50, 50))])
        split = self._serialized_label_contacts(100, 120,
            [((49, 50), (49.5, 50)), ((49.5, 50), (50, 50))])
        new = self._serialized_label_contacts(100, 120, [((49, 50), (51, 50))])
        key = ('text_wire_contact', 'same-label')
        self.assertEqual(old, split, 'Wire segmentation is not a scene identity')
        self.assertEqual(set(old), set(new))
        self.assertGreater(new[key], old[key])
        self._assert_serialized_contact_rollback(old, new)

    def _assert_serialized_contact_rollback(self, old, new):
        exporter = KiCadSchematicExporter()
        baseline = exporter.export(self.compiled, self.options())
        with patch.object(exporter, '_passive_scene_issues',
                          side_effect=[{'(root)': old}, {'(root)': new}]):
            result = exporter.export(self.compiled, self.options(orientation_mode='passive_quarter_turn'))
        evidence = self.evidence(result)['Demo']['passive_orientation']
        self.assertFalse(evidence['accepted'])
        self.assertEqual(evidence['rollback_reason'], 'new blocking serialized scene finding')
        self.assertEqual(self.poses(result), self.poses(baseline))

    def test_final_route_order_cannot_replace_existing_clearance_pair(self):
        from .KiCadSchematicOrientation import orientation_metrics, passive_orientation_rank
        exporter = KiCadSchematicExporter()
        options = self.options(orientation_mode='passive_quarter_turn')
        prepared = exporter._prepare_legacy_boards(self.compiled, options)
        board = prepared[0][0]
        drawing = next(region for region in board.regions.values() if region.spec.title == 'Demo')
        old_pair = [('old-a', (20, 20), (30, 20)), ('old-b', (20, 20.635), (30, 20.635))]
        old_route = drawing.route_snapshot
        drawing.route_snapshot = (old_route[0] + old_pair, old_route[1], old_route[2])
        drawing.wires = drawing.route_snapshot[0]
        before = orientation_metrics(drawing.placed, board.views, board.pin_nets, drawing.route_snapshot)
        observed = []
        def replace_pair(placed, views, nets, route, router):
            new_pair = [('new-a', (20, 20), (30, 20)), ('new-b', (20, 20.635), (30, 20.635))]
            final = (route[0] + new_pair, route[1], route[2])
            after = orientation_metrics(placed, views, nets, final)
            observed.append(after)
            return final, {'selected': 'baseline'}
        with patch.object(exporter, '_prepare_legacy_boards', return_value=prepared), patch(
                'edg.electronics_model.KiCadSchematicRouting.optimize_fixed_routes', replace_pair):
            result = exporter.export(self.compiled, options)
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]['visual_conflicts'], before['visual_conflicts'])
        self.assertLess(passive_orientation_rank(observed[0]), passive_orientation_rank(before))
        evidence = self.evidence(result)['Demo']['passive_orientation']
        self.assertFalse(evidence['accepted'])
        self.assertEqual(evidence['rollback_reason'], 'final routing or page-fit guard')
        self.assertEqual(evidence['final_rotations'], {c.path: angle for c, _, _, angle in drawing.placed})

    def test_only_changed_regions_receive_additional_route_order_search(self):
        from .KiCadSchematicRouting import optimize_fixed_routes
        calls=[]
        def record(placed,*args,**kwargs):
            calls.append(tuple(sorted(c.path for c,_,_,_ in placed)))
            return optimize_fixed_routes(placed,*args,**kwargs)
        with patch('edg.electronics_model.KiCadSchematicRouting.optimize_fixed_routes',record):
            result=KiCadSchematicExporter().export(self.compiled,self.options(orientation_mode='passive_quarter_turn'))
        self.assertTrue(self.evidence(result)['Demo']['passive_orientation']['accepted'])
        self.assertEqual(calls.count(('anchor','passive')),2)
        self.assertEqual(calls.count(('spare',)),1)

    def test_passive_phase_follows_bridge_and_restores_source_annotation_policy(self):
        from .KiCadSchematicOrientation import optimize_passive_orientations
        from .KiCadSchematicPower import compare_bridge_variants
        calls=[]
        def bridge(*args,**kwargs):
            calls.append('bridge')
            return compare_bridge_variants(*args,**kwargs)
        def passive(items,*args,**kwargs):
            calls.append('passive')
            self.assertEqual(set(kwargs['source_annotations']),{c.path for c,_,_,_ in items})
            self.assertTrue(all(value is None for value in kwargs['source_annotations'].values()))
            self.assertTrue(all(c.annotation is not None for c,_,_,_ in items))
            return optimize_passive_orientations(items,*args,**kwargs)
        with patch('edg.electronics_model.KiCadSchematicPower.compare_bridge_variants',bridge), patch(
                'edg.electronics_model.KiCadSchematicOrientation.optimize_passive_orientations',passive):
            KiCadSchematicExporter().export(self.compiled,self.options(orientation_mode='passive_quarter_turn'))
        # The automatic spare invokes the bridge phase, while the hinted
        # circuit keeps its centers. All template decisions precede this pass.
        self.assertGreater(calls.count('passive'),0)
        self.assertGreater(calls.count('bridge'),0)
        self.assertLess(max(i for i,v in enumerate(calls) if v=='bridge'),
                        min(i for i,v in enumerate(calls) if v=='passive'))


    def test_native_quarter_turn_preserves_physical_inventory_and_connected_pin_sets(self):
        from .NetlistGenerator import NetlistTransform
        from .SchematicVerification import verify_schematic_netlist
        clis=tuple(filter(None,os.environ.get('PB_SCHEMATIC_TEST_KICAD_CLIS','').split(os.pathsep)))
        if not clis:
            clis=tuple(filter(None,(os.environ.get('KICAD_CLI9'),os.environ.get('KICAD_CLI10'))))
        if not clis:
            self.skipTest('Set PB_SCHEMATIC_TEST_KICAD_CLIS or KICAD_CLI9/10 for native acceptance')
        scopes={str(scope):netlist for scope,netlist in NetlistTransform(self.compiled).run().items()}
        for mode in ('half_turn','passive_quarter_turn'):
            bundle=KiCadSchematicExporter().export(self.compiled,self.options(orientation_mode=mode))
            with tempfile.TemporaryDirectory() as directory:
                destination=Path(directory)
                bundle.write(destination)
                for board in json.loads(bundle.files['manifest.json'])['boards']:
                    for index,cli in enumerate(clis):
                        with self.subTest(mode=mode,scope=board['scope'],cli=cli):
                            output=destination/f'native-{index}.xml'
                            result=subprocess.run([cli,'sch','export','netlist','--format','kicadxml',
                                '-o',str(output),str(destination/board['root'])],
                                capture_output=True,text=True,timeout=60)
                            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                            verify_schematic_netlist(scopes[board['scope']],output)


if __name__=='__main__':
    unittest.main()
