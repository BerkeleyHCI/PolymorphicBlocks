"""Fairness, immutable identities, source-owned locks and cached routing."""
import copy
import unittest
from unittest.mock import patch

from .KiCadSchematicExporter import PhysicalComponent, SymbolView, node, SchematicPlacement, SchematicExportOptions
from .KiCadSchematicOrientation import optimize_orientations
from .KiCadSchematicLayout import route_local


class OrientationTest(unittest.TestCase):
    def fixture(self, count=1):
        entries, views, nets = [], {}, {}
        for i in range(count):
            c = PhysicalComponent(f'part{i:03}',f'D{i}','Fixture:Pad','polar',{'1':'anode','2':'cathode'},None,'g')
            entries.append((c,50.+i*10,70.,0))
            views[c.path] = SymbolView(node('symbol'), [('1',-1.,0.,0),('2',1.,0.,180)],'Fixture:Polar')
            nets[c.path,'1'] = 'positive'
            nets[c.path,'2'] = 'negative'
        return entries,views,nets

    def metric(self, placed, *args):
        # Rotating the final device is beneficial even after >32 early paths.
        return dict(primary_fallbacks=0,crossings=0,unrelated_intrusions=0,bends=0,
                    detour_mm=0,length_mm=100-sum(a==180 for _,_,_,a in placed),visual_conflicts=0)

    def geometry(self, *args):
        return dict(escape_conflicts=0,collisions=0,clipped=False)

    def test_every_path_gets_trial_without_starvation_and_two_sweep_limit(self):
        entries,views,nets = self.fixture(40)
        original = copy.deepcopy((entries,views,nets))
        calls=[]
        baseline=([],{},[])
        def router(*args):
            calls.append(args)
            return baseline
        with patch('edg.electronics_model.KiCadSchematicOrientation._geometry',self.geometry), patch(
                'edg.electronics_model.KiCadSchematicOrientation.orientation_metrics',self.metric):
            placed,route,evidence = optimize_orientations(entries,views,nets,router,baseline=baseline)
        self.assertEqual(len(calls),80)
        self.assertEqual([trial['path'] for trial in evidence['trials'][:40]],sorted(c.path for c,_,_,_ in entries))
        self.assertTrue(all(a==180 for _,_,_,a in placed))
        self.assertEqual((entries,views,nets), original)
        self.assertEqual([(x,y) for _,x,y,_ in placed],[(x,y) for _,x,y,_ in entries])
        self.assertEqual(route,baseline)

    def test_lock_and_explicit_annotation_and_ties_preserve_incumbent(self):
        entries,views,nets = self.fixture(2)
        entries[1][0].annotation=(66.,88.)
        with patch('edg.electronics_model.KiCadSchematicOrientation._geometry',self.geometry), patch(
                'edg.electronics_model.KiCadSchematicOrientation.orientation_metrics',self.metric):
            placed,_,evidence=optimize_orientations(entries,views,nets,lambda *args:([],{},[]),locked={'part000'})
        self.assertEqual([a for _,_,_,a in placed],[0,180])
        self.assertEqual(placed[1][0].annotation,(66.,88.))
        self.assertFalse(evidence['eligibility'][0]['eligible'])
        self.assertEqual(len(evidence['trials']),2)
        self.assertFalse(evidence['trials'][-1]['selected'])

    def test_new_failed_endpoint_and_geometry_overflow_rejected(self):
        entries,views,nets=self.fixture()
        baseline=([],{},[])
        with patch('edg.electronics_model.KiCadSchematicOrientation._geometry',self.geometry), patch(
                'edg.electronics_model.KiCadSchematicOrientation.orientation_metrics',self.metric):
            placed,_,evidence=optimize_orientations(entries,views,nets,
                lambda *args:([],{},[(('part000','1'),'positive')]),baseline=baseline)
        self.assertEqual(placed[0][3],0)
        self.assertEqual(evidence['trials'][0]['reason'],'new failed endpoints')
        with patch('edg.electronics_model.KiCadSchematicOrientation._geometry',self.geometry), patch(
                'edg.electronics_model.KiCadSchematicOrientation.orientation_metrics',self.metric):
            _,_,evidence=optimize_orientations(entries,views,nets,lambda *args:baseline,baseline=baseline,
                region_bounds=lambda *args:(0,0,400,240))
        self.assertEqual(evidence['trials'][0]['reason'],'routed region page overflow')

    def test_real_router_shortens_polar_parts_without_swapping_pins(self):
        entries,views,nets = self.fixture(2)
        entries=[(entries[0][0],50.,70.,0),(entries[1][0],90.,70.,0)]
        # Parallel physical pads remain distinct identities on the same net.
        entries[1][0].pins['3']='anode_parallel'
        views['part001'].pins.append(('3',-1.,2.54,0))
        nets['part001','3']='positive'
        original=copy.deepcopy((entries,views,nets))
        actual,route,report=optimize_orientations(entries,views,nets,route_local)
        self.assertEqual((entries,views,nets),original)
        self.assertLess(report['after']['length_mm'],report['before']['length_mm'])
        self.assertEqual(route[2],[])
        self.assertEqual(set(route[1]),set(nets))
        self.assertEqual([(x,y) for _,x,y,_ in actual],[(x,y) for _,x,y,_ in entries])
        repeated=optimize_orientations(entries,views,nets,route_local)
        self.assertEqual(repeated,(actual,route,report))

    def test_converter_primary_fallbacks_use_verified_core_endpoints(self):
        from types import SimpleNamespace
        from .test_schematic_bridge_variants import bridge
        from .test_schematic_functional_placement import part, passive_view
        from .KiCadSchematicOrientation import orientation_metrics
        from .KiCadSchematicPower import topology_primary_endpoints
        _,by_path,views,nets=bridge()
        bank=part('bank',{'1':'supply','2':'return'},'Device:C')
        by_path['bank']=bank
        views['bank']=passive_view('Device:C')
        nets['bank','1']='rail1'
        nets['bank','2']='gnd'
        endpoints=topology_primary_endpoints(list(by_path.values()),nets,views)
        self.assertNotIn(('bank','1'),endpoints['rail1'])
        self.assertIn(('coil','1'),endpoints['sw1'])
        self.assertIn(('hi1','1'),endpoints['hidrv1'])
        placed=[(c,50+i*40,70,0) for i,c in enumerate(by_path.values())]
        for c in by_path.values():
            c.functional_circuit=SimpleNamespace(id='fixture',primary_nets=('rail1','authored_signal'),stages=())
        for failures,expected,noncore in (
                ([(('bank','1'),'rail1')],0,1),
                ([(('coil','1'),'sw1')],1,0),
                ([(('hi1','1'),'hidrv1')],1,0),
                ([(('bank','1'),'authored_signal')],1,0)):
            metric=orientation_metrics(placed,views,nets,([],{},failures))
            self.assertEqual(metric['primary_fallbacks'],expected)
            self.assertEqual(metric['noncore_converter_fallbacks'],noncore)
        # Removing the actual gate connectivity makes topology classification
        # ambiguous/invalid; authored primary nets keep their original meaning.
        nets['hi1','1']='broken_gate'
        metric=orientation_metrics(placed,views,nets,([],{},[(('bank','1'),'rail1')]))
        self.assertEqual(metric['primary_fallbacks'],1)

    def test_public_boolean_validation_and_placement_compatibility(self):
        self.assertTrue(SchematicPlacement('g',1,2).lock_rotation)
        self.assertFalse(SchematicPlacement('g',1,2,180,False,None,False).lock_rotation)
        self.assertTrue(SchematicExportOptions('design').optimize_orientations)
        with self.assertRaises(ValueError):
            SchematicPlacement('g',1,2,lock_rotation=1)
        with self.assertRaises(ValueError):
            SchematicExportOptions('design',optimize_orientations='yes')


if __name__=='__main__':
    unittest.main()


class OrientationPipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from ..core import ScalaCompiler
        from ..electronics_interfaces.test_netlist import TestBasicCircuit
        from .RefdesRefinementPass import RefdesRefinementPass
        cls.compiled=ScalaCompiler.compile(TestBasicCircuit)
        cls.compiled.append_values(RefdesRefinementPass().run(cls.compiled))

    def test_orientation_then_bridge_then_one_route_order_pass(self):
        from .KiCadSchematicExporter import KiCadSchematicExporter
        from .KiCadSchematicLayout import freeze_annotations
        from .KiCadSchematicRouting import route_metrics
        calls=[]
        cached={}
        def orientations(items,views,nets,router,**kwargs):
            calls.append('orientations')
            route=kwargs['baseline']
            cached['oriented']=route
            return freeze_annotations(items,views),route,{'selected':'fixture'}
        def bridges(items,views,nets,baseline,router,**kwargs):
            calls.append('bridge')
            self.assertIs(baseline,cached['oriented'])
            self.assertEqual(set(kwargs['source_annotations']),{c.path for c,_,_,_ in items})
            # A distinct cached result proves that downstream does not reroute
            # the baseline or discard the selected variant's route object.
            route=(list(baseline[0]),dict(baseline[1]),list(baseline[2]))
            cached['bridge']=route
            return items,route,{'selected':'fixture'}
        def route_order(items,views,nets,baseline,router):
            calls.append('route_order')
            self.assertIs(baseline,cached['bridge'])
            metrics=route_metrics(baseline[0],baseline[2])
            return baseline,dict(before=metrics,after=metrics,selected='fixture',candidates=1)
        with patch('edg.electronics_model.KiCadSchematicOrientation.optimize_orientations',orientations), patch(
                'edg.electronics_model.KiCadSchematicPower.compare_bridge_variants',bridges,create=True), patch(
                'edg.electronics_model.KiCadSchematicRouting.optimize_fixed_routes',route_order):
            result=KiCadSchematicExporter().export(self.compiled,SchematicExportOptions('Pipeline'))
        self.assertEqual(calls,['orientations','bridge','route_order']*(len(calls)//3))
        self.assertGreater(len(calls),0)
        self.assertIn('bridge_comparison',result.files['routing.json'])
        with patch('edg.electronics_model.KiCadSchematicOrientation.optimize_orientations',side_effect=AssertionError('off')), patch(
                'edg.electronics_model.KiCadSchematicPower.compare_bridge_variants',side_effect=AssertionError('off'),create=True):
            disabled=KiCadSchematicExporter().export(self.compiled,SchematicExportOptions('Pipeline',optimize_orientations=False))
        self.assertNotIn('bridge_comparison',disabled.files['routing.json'])
        self.assertNotIn('"orientation"',disabled.files['routing.json'])
