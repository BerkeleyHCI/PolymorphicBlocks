"""Pin escapes remain visible and cache optimization preserves route decisions."""
import os
import random
import unittest
from collections import defaultdict
from unittest.mock import patch
import xml.etree.ElementTree as ET

from .KiCadSchematicExporter import PhysicalComponent, SymbolView, generic, node, uid, effects, S, KiCadSchematicExporter
from .KiCadSchematicLayout import route_local, _NearForeignCache


def legacy_blocked(cache, point, axis, net):
    for nx in (point[0]-1,point[0],point[0]+1):
        for ny in (point[1]-1,point[1],point[1]+1):
            if (nx,ny) == point:
                continue
            foreign = [axes for owner,axes in cache.tracks.get((nx,ny),{}).items() if owner!=net]
            if foreign and ((nx,ny) in cache.protected or any(axis in axes for axes in foreign)):
                return True
    return False


def neck_fixture():
    # Exact U12 left border53.48 and pin5/6 tips50.94,y117.12/120.93.
    ic = PhysicalComponent('bms.ic','U12','Test:IC','BMS',{'5':'scl','6':'sda'},None,'control')
    definition = node('symbol','Fixture:U12',node('symbol','U12_0_1',
        node('rectangle',node('start',-16.52,10.16),node('end',16.52,-10.16))))
    body = definition[2]
    pin_list = []
    for number,dy in (('5',-1.905),('6',1.905)):
        body.append(node('pin',S('passive'),S('line'),node('at',-19.06,-dy,0),node('length',2.54),
                         node('name',ic.pins[number],effects()),node('number',number,effects())))
        pin_list.append((number,-19.06,dy,0))
    views = {ic.path:SymbolView(definition,pin_list,'Fixture:U12')}
    placed=[(ic,70,119.025,0)]
    nets={('bms.ic','5'):'scl',('bms.ic','6'):'sda'}
    # Targets to the right encourage the old illegal shortcut through a pin
    # neck toward the body instead of a visible outside route.
    for index,(net,y) in enumerate((('scl',100),('sda',145)),1):
        target = PhysicalComponent('target'+str(index),'TP'+str(index),'Test:One','Target',{'1':'io'},None,'control')
        views[target.path]=generic(target)
        placed.append((target,125,y,0));nets[target.path,'1']=net
    return placed,views,nets


class PinNeckTest(unittest.TestCase):
    def test_cache_matches_old_rule_across_incremental_tracks_and_protection(self):
        rng=random.Random(137)
        tracks=defaultdict(dict)
        protected=set()
        for _ in range(25):
            p=(rng.randrange(-3,4),rng.randrange(-3,4));net=rng.choice(('a','b','c'))
            tracks[p].setdefault(net,set()).add(rng.randrange(2))
            if rng.randrange(4)==0:protected.add(p)
        cache=_NearForeignCache(tracks,protected)
        def verify():
            for x in range(-4,5):
                for y in range(-4,5):
                    for axis in (0,1):
                        for net in ('a','b','c','absent'):
                            self.assertEqual(cache.blocked((x,y),axis,net),legacy_blocked(cache,(x,y),axis,net),
                                             ((x,y),axis,net))
        verify()
        for iteration in range(100):
            p=(rng.randrange(-3,4),rng.randrange(-3,4));net=rng.choice(('a','b','c'))
            if rng.randrange(3)==0:cache.protect((p,))
            cache.add_track(p,net,{rng.randrange(2)})
            if iteration%10==0:verify()
        verify()

    def test_cache_keeps_legible_exact_perpendicular_interior_crossing(self):
        tracks=defaultdict(dict,{(x,0):{'a':{0}} for x in range(-4,5)})
        cache=_NearForeignCache(tracks,{(-4,0),(4,0)})
        self.assertFalse(cache.blocked((0,0),1,'b'))
        self.assertTrue(cache.blocked((0,1),0,'b'))
        self.assertTrue(cache.blocked((-4,1),1,'b'))

    def test_cache_and_reference_produce_identical_q4_routes(self):
        from .test_schematic_visual_clearance import fixture
        placed,views,nets=fixture()
        cached=route_local(placed,views,nets)
        with patch.object(_NearForeignCache,'blocked',legacy_blocked):
            reference=route_local(placed,views,nets)
        self.assertEqual(cached,reference)

    def test_u12_routes_never_backtrack_inside_pin_stub_or_library_leg(self):
        placed,views,nets=neck_fixture()
        wires,escapes,failures=route_local(placed,views,nets)
        self.assertEqual(failures,[])
        for number in ('5','6'):
            px,py,ex,ey,_=escapes['bms.ic',number]
            self.assertAlmostEqual(px,50.94)
            self.assertAlmostEqual(py,117.12 if number=='5' else 120.93)
            # Fixed stub remains outward. Every generated route segment stays
            # outside the open escape-to-body corridor regardless of net.
            for net,a,b in wires:
                lo_x,hi_x=sorted((a[0],b[0]));lo_y,hi_y=sorted((a[1],b[1]))
                crosses_neck = (max(lo_x,ex+0.4)<min(hi_x,53.48) and lo_y<=py<=hi_y)
                inside_neck_vertical = (ex+0.4<a[0]<53.48 and a[0]==b[0] and lo_y<=py<=hi_y)
                self.assertFalse(crosses_neck or inside_neck_vertical,(number,net,a,b))

    def test_u12_native_nets_preserve_both_bare_pin_identities(self):
        from .test_schematic_scene_native import NativeSceneTest
        clis=tuple(filter(None,os.environ.get('PB_SCHEMATIC_TEST_KICAD_CLIS','').split(os.pathsep)))
        if not clis:self.skipTest('Set PB_SCHEMATIC_TEST_KICAD_CLIS for native acceptance')
        placed,views,nets=neck_fixture()
        wires,escapes,failures=route_local(placed,views,nets)
        self.assertEqual(failures,[])
        wires += [(nets[key],(px,py),(ex,ey)) for key,(px,py,ex,ey,_) in escapes.items()]
        root_id=uid('pin-neck-native','root')
        doc=node('kicad_sch',node('version',20250114),node('generator',S('eeschema')),
                 node('uuid',root_id),node('paper','A3'),node('lib_symbols',*[v.definition for v in views.values()]))
        for c,x,y,angle in placed:
            sid=uid(root_id,c.path)
            symbol=node('symbol',node('lib_id',views[c.path].lib_id),node('at',x,y,angle),node('unit',1),
                        node('in_bom',S('yes')),node('on_board',S('yes')),node('dnp',S('no')),node('uuid',sid))
            for name,value in (('Reference',c.refdes),('Value',c.value),('Footprint',c.footprint)):
                symbol.append(node('property',name,value,node('at',x,y,0),effects(hide=True)))
            symbol.extend(node('pin',n,node('uuid',uid(sid,n))) for n in c.pins)
            symbol.append(node('instances',node('project','Fixture',node('path','/'+root_id,
                          node('reference',c.refdes),node('unit',1)))))
            doc.append(symbol)
        KiCadSchematicExporter._wires(doc,wires,'fixture','pin-neck')
        for cli in clis:
            with self.subTest(cli=cli):
                xml=ET.parse(NativeSceneTest.native(self,cli,doc,'netlist')).getroot()
                native=[{(n.attrib['ref'],n.attrib['pin']) for n in net.findall('node')} for net in xml.findall('./nets/net')]
                self.assertIn({('U12','5'),('TP1','1')},native)
                self.assertIn({('U12','6'),('TP2','1')},native)
