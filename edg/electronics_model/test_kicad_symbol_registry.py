"""Default symbol selection must preserve physical identity and terminal roles."""

import unittest
from types import SimpleNamespace

import sexpdata

from .KiCadSymbolRegistry import infer_symbol


class FixtureResolver:
    """Pin inventories transcribed from official KiCad/Espressif library symbols."""

    def __init__(self, inventories):
        self.inventories = inventories

    def load(self, lib_id):
        pins = self.inventories[lib_id]
        sym = sexpdata.Symbol
        return [
            sym("symbol"),
            lib_id,
            [
                sym("symbol"),
                "Body_1_1",
                *[[sym("pin"), sym("passive"), sym("line"), [sym("number"), number]] for number in pins],
            ],
        ]


class KiCadSymbolRegistryTest(unittest.TestCase):
    def test_datalogger_generic_mlcc_requires_exact_model_package_and_roles(self):
        classes = ["edg.vendor_parts.generic.GenericCapacitor.GenericMlcc"]
        component = SimpleNamespace(footprint="Capacitor_SMD:C_0603_1608Metric", pins={"1": "pos", "2": "neg"})
        resolver = FixtureResolver({"Device:C": ["1", "2"]})
        result = infer_symbol(component, classes, "", resolver)
        self.assertEqual(result["lib_id"], "Device:C")
        self.assertEqual(result["pinning"], {"1": "1", "2": "2"})
        self.assertIsNone(infer_symbol(component, ["custom.Capacitor"], "", resolver))
        component.pins = {"1": "neg", "2": "pos"}
        self.assertIsNone(infer_symbol(component, classes, "", resolver))
        component.pins = {"1": "pos", "2": "neg", "3": "shield"}
        self.assertIsNone(infer_symbol(component, classes, "", resolver))
        component.pins = {"1": "pos", "2": "neg"}
        for footprint in ("Capacitor_SMD:CP_Elec_5x5.8", "Capacitor_SMD:C_Custom"):
            component.footprint = footprint
            self.assertIsNone(infer_symbol(component, classes, "", resolver))

    def test_symbol_lookup_evidence_distinguishes_mapping_symbol_and_library(self):
        classes = ["edg.vendor_parts.generic.GenericCapacitor.GenericMlcc"]
        component = SimpleNamespace(footprint="Capacitor_SMD:C_0603_1608Metric", pins={"1": "pos", "2": "neg"})
        evidence = {}
        self.assertIsNone(infer_symbol(component, ["custom.Capacitor"], "", FixtureResolver({}), evidence))
        self.assertEqual(evidence["category"], "missing_mapping")
        evidence = {}
        self.assertIsNone(infer_symbol(component, classes, "", FixtureResolver({}), evidence))
        self.assertEqual(evidence["category"], "missing_symbol")
        self.assertEqual(evidence["attempts"][0]["lib_id"], "Device:C")
        class MissingLibrary:
            def load(self, lib_id):
                raise FileNotFoundError(lib_id)
        evidence = {}
        self.assertIsNone(infer_symbol(component, classes, "", MissingLibrary(), evidence))
        self.assertEqual(evidence["category"], "missing_library")
        evidence = {}
        self.assertIsNone(infer_symbol(component, classes, "", FixtureResolver({"Device:C": ["1"]}), evidence))
        self.assertEqual(evidence["category"], "invalid_registry_mapping")

    def test_custom_irf540n_requires_exact_part_package_and_terminal_order(self):
        component = SimpleNamespace(
            footprint="Package_TO_SOT_THT:TO-220-3_Horizontal_TabUp",
            pins={"1": "gate", "2": "drain", "3": "source"},
        )
        classes = ["edg.vendor_parts.generic.CustomFet.CustomFet"]
        resolver = FixtureResolver({"Transistor_FET:IRF540N": ["1", "2", "3"]})
        result = infer_symbol(component, classes, "IRF540N", resolver)
        self.assertEqual(result["lib_id"], "Transistor_FET:IRF540N")
        self.assertEqual(result["pinning"], {"1": "1", "2": "2", "3": "3"})
        self.assertIsNone(infer_symbol(component, classes, "IRF9540", resolver))
        component.pins["2"], component.pins["3"] = component.pins["3"], component.pins["2"]
        self.assertIsNone(infer_symbol(component, classes, "IRF540N", resolver))

    def test_lmv331_exact_package_and_declared_polarity(self):
        component = SimpleNamespace(
            footprint="Package_TO_SOT_SMD:SOT-353_SC-70-5",
            pins={"1": "inp", "2": "gnd", "3": "inn", "4": "out", "5": "vcc"},
        )
        classes = ["edg.parts.analog.Comparator_Lmv331.Lmv331_Device"]
        resolver = FixtureResolver({"Comparator:LMV331": ["1", "2", "3", "4", "5"]})
        result = infer_symbol(component, classes, "LMV331IDCKR (Texas Instruments)", resolver)
        self.assertEqual(result["lib_id"], "Comparator:LMV331")
        self.assertEqual(result["pinning"], {str(n): str(n) for n in range(1, 6)})
        component.pins["1"], component.pins["3"] = component.pins["3"], component.pins["1"]
        self.assertIsNone(infer_symbol(component, classes, "LMV331IDCKR", resolver))

    def test_parallel_dummy_capacitor_uses_nonpolar_symbol_only(self):
        component = SimpleNamespace(footprint="Capacitor_SMD:C_1206_3216Metric", pins={"1": "pos", "2": "neg"})
        cls = ["PolymorphicBlocks.edg.vendor_parts.jlc.JlcCapacitor.JlcDummyCapacitor"]
        resolver = FixtureResolver({"Device:C": ["1", "2"]})
        result = infer_symbol(component, cls, "CL31A226KPHNNNE", resolver)
        self.assertEqual(result["pinning"], {"1": "1", "2": "2"})
        component.footprint = "Capacitor_SMD:CP_Elec_5x5.8"
        self.assertIsNone(infer_symbol(component, cls, "CL31A226KPHNNNE", resolver))

    def test_local_buck_boost_inductor_requires_verified_model_and_terminals(self):
        component = SimpleNamespace(footprint="fp:DFE252012P-1R0M=P2", pins={"1": "a", "2": "b"})
        cls = ["lib.power.converter.Tps631000.Tps631000_Inductor"]
        resolver = FixtureResolver({"Device:L": ["1", "2"]})
        result = infer_symbol(component, cls, "DFE252012F-1R0M=P2 (Murata)", resolver)
        self.assertEqual(result["pinning"], {"1": "1", "2": "2"})
        component.pins["3"] = "tap"
        self.assertIsNone(infer_symbol(component, cls, "DFE252012F-1R0M=P2 (Murata)", resolver))

    def test_exact_module_identity_and_omitted_unmodeled_pins(self):
        component = SimpleNamespace(
            footprint="Espressif:ESP32-C6-WROOM-1",
            pins={"1": "gnd.net", "2": "pwr.net", "29": "gnd.net"},
        )
        classes = ["lib.esp32.Esp32c6.Esp32c6_Wroom_1_Device"]
        resolver = FixtureResolver({"Espressif:ESP32-C6-WROOM-1": [str(i) for i in range(1, 30)]})
        result = infer_symbol(component, classes, "ESP32-C6-WROOM-1-N4 (Espressif Systems)", resolver)
        self.assertEqual(result["pinning"], {"1": "1", "2": "2", "29": "29"})
        self.assertTrue(result["_omit_unmodeled"])
        self.assertIsNone(infer_symbol(component, classes, "ESP32-C6-MINI-1", resolver))
        component.pins["99"] = "unknown"
        self.assertIsNone(infer_symbol(component, classes, "ESP32-C6-WROOM-1-N4", resolver))

    def test_functional_ancestor_cannot_select_child_symbol(self):
        component = SimpleNamespace(footprint="Espressif:ESP32-C6-WROOM-1", pins={"1": "a", "2": "b"})
        classes = [
            "lib.esp32.Esp32c6.Esp32c6_Wroom_1_Device",
            "PolymorphicBlocks.edg.vendor_parts.jlc.JlcCapacitor.JlcCapacitor",
        ]
        self.assertIsNone(infer_symbol(component, classes, "ESP32-C6-WROOM-1-N4", FixtureResolver({})))

    def test_diode_mapping_uses_terminal_roles(self):
        component = SimpleNamespace(footprint="Test:Diode", pins={"4": "anode", "7": "cathode"})
        result = infer_symbol(
            component,
            ["edg.vendor_parts.jlc.JlcDiode.JlcDiode"],
            "1N5819WS",
            FixtureResolver({"Device:D_Schottky": ["1", "2"]}),
        )
        self.assertEqual(result["pinning"], {"1": "7", "2": "4"})

    def test_exact_bjt_uses_verified_role_mapping(self):
        component = SimpleNamespace(
            footprint="Test:Package",
            pins={"7": "base", "8": "collector", "9": "emitter"},
        )
        classes = ["edg.vendor_parts.jlc.JlcBjt.JlcBjt"]
        result = infer_symbol(
            component,
            classes,
            "MMBT3904",
            FixtureResolver({"Transistor_BJT:MMBT3904": ["1", "2", "3"]}),
        )
        self.assertEqual(result["pinning"], {"1": "7", "2": "9", "3": "8"})
        self.assertIsNone(infer_symbol(component, classes, "UNKNOWN", FixtureResolver({})))

    def test_fet_unknown_part_cannot_guess_polarity(self):
        component = SimpleNamespace(
            footprint="Package_TO_SOT_SMD:SOT-23",
            pins={"1": "gate", "2": "source", "3": "drain"},
        )
        self.assertIsNone(
            infer_symbol(
                component,
                ["edg.vendor_parts.jlc.JlcFet.JlcFet"],
                "UNKNOWN_FET",
                FixtureResolver({}),
            )
        )

    def test_usb_shield_pin_rename_between_kicad_versions(self):
        component = SimpleNamespace(
            footprint="Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11",
            pins={"A1": "gnd.net", "A6": "usb.dp", "S1": "shield.net"},
        )
        cls = ["edg.parts.connector.UsbPorts.UsbCReceptacle_Device"]
        lib_id = "Connector:USB_C_Receptacle_USB2.0_16P"
        old = infer_symbol(
            component,
            cls,
            "USB-C Receptacle",
            FixtureResolver({lib_id: ["A1", "A6", "S1"]}),
        )
        new = infer_symbol(
            component,
            cls,
            "USB-C Receptacle",
            FixtureResolver({lib_id: ["A1", "A6", "SH"]}),
        )
        self.assertEqual(old["pinning"]["S1"], "S1")
        self.assertEqual(new["pinning"]["SH"], "S1")

    def test_rgb_family_graphic_alias_explicitly_remaps_pads(self):
        component = SimpleNamespace(
            footprint="fp:LED_SK6812SIDE_A_S",
            pins={"1": "din.net", "2": "vdd.net", "3": "dout.net", "4": "gnd.net"},
        )
        result = infer_symbol(
            component,
            ["lib.human_interface.Sk6812sideas.Sk6812SideAS_Device"],
            "SK6812SIDE-A-S (OPSCO Optoelectronics)",
            FixtureResolver({"LED:SK6812": ["1", "2", "3", "4"]}),
        )
        self.assertEqual(result["pinning"], {"1": "4", "2": "1", "3": "2", "4": "3"})

    def test_missing_library_is_not_an_unsafe_substitution(self):
        component = SimpleNamespace(footprint="Test:LED", pins={"1": "k", "2": "a"})
        self.assertIsNone(
            infer_symbol(
                component,
                ["edg.vendor_parts.jlc.JlcLed.JlcLed"],
                "LED",
                FixtureResolver({}),
            )
        )


if __name__ == "__main__":
    unittest.main()
