"""Source-owned circuit intent is checked against compiled physical witnesses."""
import copy
import unittest

from .KiCadSchematicCircuits import build_circuits
from .KiCadSchematicPresentation import SchematicPresentation
from .KiCadSchematicExporter import PhysicalComponent, generic


def resistor(path):
    return PhysicalComponent(path, "R1", "FP", "1k", {"1": "a", "2": "b"}, {"lib_id": "Device:R"}, "group")


def circuit(*members, **options):
    return dict(id="chain", title="Input protection", summary="Series input path", components=list(members), **options)


class CircuitPresentationTest(unittest.TestCase):
    def fixture(self):
        components = [resistor("first"), resistor("second"), resistor("other")]
        wiring = {("first", "1"): "in", ("first", "2"): "middle", ("second", "1"): "middle",
                  ("second", "2"): "out", ("other", "1"): "unrelated", ("other", "2"): "return"}
        views = {c.path: generic(c) for c in components}
        return components, wiring, views

    def test_schema1_unchanged_schema2_roundtrip_and_input_copy(self):
        self.assertEqual(SchematicPresentation().to_dict(), dict(schema=1, components={}, interfaces=[], groups={}))
        value = dict(schema=2, circuits=[circuit("first", "second")])
        presentation = SchematicPresentation.from_dict(value)
        saved = presentation.to_dict()
        value["circuits"][0]["components"].append("other")
        self.assertEqual(saved, presentation.to_dict())
        self.assertEqual(saved, SchematicPresentation.from_dict(saved).to_dict())
        self.assertEqual(SchematicPresentation.from_dict(dict(schema=2)).to_dict()["schema"], 2)
        with self.assertRaisesRegex(ValueError, "schema 2"):
            SchematicPresentation.from_dict(dict(circuits=[circuit("first")]))

    def test_invalid_structure_and_membership(self):
        invalid = [
            [circuit("first", "first")],
            [circuit("first", template="mystery")],
            [circuit("first", unknown=True)],
            [circuit("first"), dict(circuit("second"), id="chain")],
            [circuit("first"), dict(circuit("first"), id="another")],
            [circuit("first", boundaries=[dict(component="second", pin="1", name="Input", role="input")])],
            [circuit("first", boundaries=[dict(component="first", pin="1", name="Input", role="guess")])],
            [circuit("first", stages=[dict(id="stage", components=["second"])])],
        ]
        for entries in invalid:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                SchematicPresentation.from_dict(dict(schema=2, circuits=entries))

    def test_physical_references_and_boundaries(self):
        for entries in [
            [circuit("missing")],
            [circuit("first", boundaries=[dict(component="first", pin="99", name="Input", role="input")])],
        ]:
            p = SchematicPresentation.from_dict(dict(schema=2, circuits=entries))
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                p.validate({"first": {"1": "a", "2": "b"}})

    def test_compiled_witnesses_and_determinism(self):
        components, wiring, views = self.fixture()
        original = copy.deepcopy(wiring)
        p = SchematicPresentation.from_dict(dict(schema=2, circuits=[circuit("first", "second",
            stages=[dict(id="input", components=["first"]), dict(id="output", components=["second"])],
            boundaries=[dict(component="first", pin="1", name="External input", role="input"),
                        dict(component="second", pin="2", name="Protected output", role="output")])]))
        model = build_circuits(components, wiring, views, p)
        entry = next(c for c in model.circuits if c.provenance == "explicit")
        self.assertEqual(entry.primary_nets, ("in", "out"))
        self.assertEqual(entry.boundaries[0].net, "in")
        self.assertEqual([s.id for s in entry.stages], ["input", "output"])
        self.assertEqual(model.to_dict(), build_circuits(list(reversed(components)), dict(reversed(list(wiring.items()))), views, p).to_dict())
        self.assertEqual(wiring, original)

    def test_board_scope_missing_net_and_duplicate_titles_rejected(self):
        components, wiring, views = self.fixture()
        p = SchematicPresentation(circuits=(circuit("first", "second"),))
        with self.assertRaisesRegex(ValueError, "scope"):
            build_circuits(components, wiring, views, p, scope_by_path={"first": "board1", "second": "board2", "other": "board1"})
        with self.assertRaisesRegex(ValueError, "scope"):
            build_circuits(components[:1], wiring, views, p)
        p = SchematicPresentation(circuits=(circuit("first", boundaries=[dict(component="first", pin="1", name="Input", role="input")]),))
        del wiring["first", "1"]
        with self.assertRaisesRegex(ValueError, "no compiled net"):
            build_circuits(components, wiring, views, p)
        p = SchematicPresentation(circuits=(circuit("first"), dict(circuit("second"), id="different")))
        with self.assertRaisesRegex(ValueError, "duplicate circuit title"):
            build_circuits(components, wiring, views, p)

    def test_ordered_stages_require_real_connection(self):
        components, wiring, views = self.fixture()
        p = SchematicPresentation(circuits=(circuit("first", "other", stages=[dict(id="a", components=["first"]), dict(id="b", components=["other"])]),))
        with self.assertRaisesRegex(ValueError, "lack a non-supply connection"):
            build_circuits(components, wiring, views, p)
        p = SchematicPresentation(circuits=(circuit("first", "second", template="buck"),))
        with self.assertRaisesRegex(ValueError, "lacks required compiled"):
            build_circuits(components, wiring, views, p)

    def test_shared_rails_do_not_create_automatic_circuit(self):
        components, wiring, views = self.fixture()
        for c in components:
            c.pins = {"1": "vdd", "2": "gnd"}
            wiring[c.path, "1"], wiring[c.path, "2"] = "common_supply", "common_return"
        model = build_circuits(components, wiring, views, SchematicPresentation())
        self.assertEqual({c.components for c in model.circuits}, {("first",), ("second",), ("other",)})
        self.assertTrue(all({b.role for b in c.boundaries} == {"supply", "return"} for c in model.circuits))
        self.assertFalse(any(c.primary_nets for c in model.circuits))

    def test_schema2_rail_stage_flow_requires_explicit_flow_witness(self):
        components, wiring, views = self.fixture()
        components[0].pins = {"1": "vin", "2": "vout"}
        components[1].pins = {"1": "vin", "2": "vout"}
        stages = [dict(id="a", components=["first"]), dict(id="b", components=["second"])]
        p = SchematicPresentation(circuits=(circuit("first", "second", stages=stages),))
        with self.assertRaisesRegex(ValueError, "lack a non-supply connection"):
            build_circuits(components, wiring, views, p)
        p = SchematicPresentation(circuits=(circuit("first", "second", stages=stages,
            boundaries=[dict(component="first", pin="2", name="Power output", role="output")]),))
        self.assertTrue(build_circuits(components, wiring, views, p).circuits)

    def test_automatic_boundaries_are_undirected_without_authored_intent(self):
        components, wiring, views = self.fixture()
        model = build_circuits(components, wiring, views, SchematicPresentation())
        first = next(c for c in model.circuits if c.components == ("first",))
        self.assertEqual([(b.pin, b.net, b.role) for b in first.boundaries], [("2", "middle", "bidirectional")])
        self.assertEqual(first.primary_nets, ("middle",))

    def test_ambiguous_bypass_ownership_remains_diagnostic(self):
        components, wiring, views = self.fixture()
        components[0].hierarchy = (("first.wrapper", "edg.abstract_parts.Capacitor.DecouplingCapacitor"),)
        model = build_circuits(components, wiring, views, SchematicPresentation())
        self.assertEqual(len(model.diagnostics), 1)
        self.assertIn("Unassigned bypass ownership: first", model.diagnostics[0])


class ConnectorProtectionEvidenceTest(unittest.TestCase):
    def test_protection_requires_connector_signal_attachment_not_common_rails(self):
        connector = PhysicalComponent('connector','J1','FP','Connector',
                                      {'1':'pins.0','2':'pins.1','3':'pins.2'},None,'group')
        clamp = PhysicalComponent('clamp','D1','FP','TVS',{'1':'a','2':'k'},None,'group')
        device = PhysicalComponent('device','U1','FP','Receiver',
                                   {'1':'input','2':'gnd','3':'vcc'},None,'group')
        components=[connector,clamp,device]
        views={c.path:generic(c) for c in components}
        views['connector'].lib_id='Connector_Generic:Conn_01x03'
        views['clamp'].lib_id='Device:D_TVS'
        nets={('connector','1'):'signal',('connector','2'):'gnd',('connector','3'):'vcc',
              ('device','1'):'signal',('device','2'):'gnd',('device','3'):'vcc',
              ('clamp','1'):'signal',('clamp','2'):'gnd'}
        presentation=SchematicPresentation(circuits=(circuit('connector','clamp','device',
            template='connector_protection',
            stages=[dict(id='entry',components=['connector']),dict(id='protected',components=['clamp','device'])]),))
        self.assertTrue(build_circuits(components,nets,views,presentation).circuits)
        for invalid_net in ('unrelated','vcc'):
            with self.subTest(net=invalid_net):
                nets['clamp','1']=invalid_net
                with self.assertRaisesRegex(ValueError,'lacks required compiled connectivity'):
                    build_circuits(components,nets,views,presentation)
