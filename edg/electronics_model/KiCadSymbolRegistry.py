"""Conservative library-symbol defaults for compiled physical component models.

This registry never selects symbols by reference designator. Each entry identifies
an exact leaf PB model and, where a model selects several parts, an actual part
or verified terminal roles. Missing libraries and unknown variants return None.
The exporter must retain the actual component Value and Footprint properties.

ESP32-C6-WROOM-1 is provided by Espressif's official KiCad library:
https://github.com/espressif/kicad-libraries/blob/main/symbols/Espressif.kicad_sym
Other symbols below are from the official KiCad libraries. No library files are
bundled here. Unmodeled pins are omitted deliberately; never emit invented NCs.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence, Protocol, TYPE_CHECKING
from .KiCadSchematicTypes import SExpr

if TYPE_CHECKING:
    from .KiCadSchematicExporter import PhysicalComponent


class LibraryResolver(Protocol):
    def load(self, lib_id: str) -> SExpr: ...


def _leaf_class(class_names: Sequence[str]) -> str:
    if not class_names:
        return ""
    # A path's last entry describes the physical block, not a functional ancestor.
    return class_names[-1].removeprefix("PolymorphicBlocks.")


def _children(tree: SExpr, name: str) -> list[SExpr]:
    return [item for item in tree if isinstance(item, list) and item and str(item[0]) == name]


def _checked_mapping(
    component: PhysicalComponent, resolver: LibraryResolver, lib_id: str, pinning: Optional[Mapping[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """Require an installed definition and a complete one-to-one physical pin map."""
    try:
        definition = resolver.load(lib_id)
    except (LookupError, FileNotFoundError):
        return None
    available = {
        str(_children(pin, "number")[0][1])
        for body in _children(definition, "symbol")
        for pin in _children(body, "pin")
    }
    if pinning is None:
        pinning = {number: number for number in component.pins}
    mapping = dict(pinning)
    if (
        not set(mapping).issubset(available)
        or set(mapping.values()) != set(component.pins)
        or len(mapping.values()) != len(set(mapping.values()))
    ):
        return None
    return {"lib_id": lib_id, "pinning": mapping, "_omit_unmodeled": True}


def _role_pins(component: PhysicalComponent) -> Dict[str, str]:
    """Use declared PB terminal semantics, never a guess from copper or pad order."""
    aliases = {"a": "anode", "k": "cathode"}
    roles: Dict[str, str] = {}
    for number, path in component.pins.items():
        terms = path.split(".")
        role = terms[-2] if terms[-1] == "net" and len(terms) > 1 else terms[-1]
        role = aliases.get(role, role)
        if role in roles:
            return {}  # ambiguous parallel pads require a part-specific entry
        roles[role] = number
    return roles


def infer_symbol(
    component: PhysicalComponent,
    class_names: Sequence[str],
    part: str,
    resolver: LibraryResolver,
    evidence: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Resolve verified defaults, optionally retaining failed library lookup evidence."""
    attempts = []

    class RecordingResolver:
        def load(self, lib_id: str) -> SExpr:
            attempt = {"lib_id": lib_id}
            attempts.append(attempt)
            try:
                result = resolver.load(lib_id)
            except (LookupError, FileNotFoundError) as error:
                attempt.update(
                    reason=str(error),
                    category=("missing_library" if isinstance(error, FileNotFoundError) else "missing_symbol"),
                )
                raise
            attempt["category"] = "loaded"
            return result

    result = _infer_symbol(component, class_names, part, RecordingResolver())
    if evidence is not None:
        evidence.update(attempts=attempts)
        if result is None:
            failure = next((a for a in reversed(attempts) if a["category"] != "loaded"), None)
            evidence.update(
                category=(
                    failure["category"] if failure else ("invalid_registry_mapping" if attempts else "missing_mapping")
                ),
                reason=(
                    failure["reason"]
                    if failure
                    else (
                        "verified symbol does not match modeled pin inventory"
                        if attempts
                        else "no schematic symbol mapping"
                    )
                ),
            )
    return result


def _infer_symbol(
    component: PhysicalComponent, class_names: Sequence[str], part: str, resolver: LibraryResolver
) -> Optional[Dict[str, Any]]:
    """Return explicit library-pin -> physical-pad mapping, or None if unverified.

    ``class_names`` is the compiled hierarchy's library class names in path order,
    with the physical block's class last. Both ``edg`` import namespaces work.
    ``part`` is NetBlock.part (part identifier followed by optional manufacturer).
    ``component`` supplies physical ``pins`` and ``footprint``; resolver.load()
    returns a fully resolved KiCad symbol definition.
    """
    cls = _leaf_class(class_names)
    identifier = part.split(" (", 1)[0].strip()
    pins = set(component.pins)

    if (
        cls == "edg.parts.analog.Comparator_Lmv331.Lmv331_Device"
        and identifier == "LMV331IDCKR"
        and component.footprint == "Package_TO_SOT_SMD:SOT-353_SC-70-5"
        and _role_pins(component) == {"inp": "1", "gnd": "2", "inn": "3", "out": "4", "vcc": "5"}
    ):
        # TI LMV331 datasheet, Pin Configuration and Functions (DBV/DCK):
        # https://www.ti.com/lit/ds/symlink/lmv331.pdf
        # 1=IN+, 2=GND, 3=IN-, 4=OUT, 5=VCC. The official single-unit
        # Comparator:LMV331 symbol uses these same numbers in KiCad 9 and 10.
        return _checked_mapping(component, resolver, "Comparator:LMV331")

    if (
        cls == "edg.vendor_parts.generic.CustomFet.CustomFet"
        and identifier == "IRF540N"
        and component.footprint
        in {
            "Package_TO_SOT_THT:TO-220-3_Horizontal_TabUp",
            "Package_TO_SOT_THT:TO-220-3_Horizontal_TabDown",
            "Package_TO_SOT_THT:TO-220-3_Vertical",
        }
        and _role_pins(component) == {"gate": "1", "drain": "2", "source": "3"}
    ):
        # Infineon IRF540N datasheet TO-220 front view: 1=G, 2=D, 3=S.
        # https://www.infineon.com/assets/row/public/documents/24/49/
        # infineon-irf540n-datasheet-en.pdf
        # Official KiCad single-unit IRF540N has the same physical inventory.
        return _checked_mapping(component, resolver, "Transistor_FET:IRF540N")

    if (
        cls == "edg.vendor_parts.generic.GenericCapacitor.GenericMlcc"
        and component.footprint
        in {
            "Capacitor_SMD:C_0402_1005Metric",
            "Capacitor_SMD:C_0603_1608Metric",
            "Capacitor_SMD:C_0805_2012Metric",
            "Capacitor_SMD:C_1206_3216Metric",
            "Capacitor_SMD:C_1210_3225Metric",
            "Capacitor_SMD:C_1812_4532Metric",
        }
        and pins == {"1", "2"}
        and _role_pins(component) == {"pos": "1", "neg": "2"}
    ):
        # GenericMlcc.PACKAGE_SPECS enumerates these nonpolar ceramic packages;
        # generate() explicitly declares physical 1=pos,2=neg. This also covers
        # Datalogger's direct generic capacitors, not only parallel dummy leaves.
        return _checked_mapping(component, resolver, "Device:C")

    if (
        cls
        in {
            "edg.vendor_parts.jlc.JlcCapacitor.JlcDummyCapacitor",
            "edg.abstract_parts.Capacitor.DummyCapacitorFootprint",
        }
        and component.footprint.startswith("Capacitor_SMD:C_")
        and pins == {"1", "2"}
        and _role_pins(component) == {"pos": "1", "neg": "2"}
    ):
        # DummyCapacitorFootprint.__init__ explicitly declares 1=pos, 2=neg.
        # C_ packages are the verified nonpolar standard SMD family; CP_ is not.
        return _checked_mapping(component, resolver, "Device:C")

    if (
        cls == "lib.power.converter.Tps631000.Tps631000_Inductor"
        and identifier == "DFE252012F-1R0M=P2"
        and component.footprint == "fp:DFE252012P-1R0M=P2"
        and dict(component.pins) == {"1": "a", "2": "b"}
    ):
        # The local model declares the two nonpolar coil terminals as 1=a,2=b.
        return _checked_mapping(component, resolver, "Device:L")

    if (
        cls == "lib.esp32.Esp32c6.Esp32c6_Wroom_1_Device"
        and identifier == "ESP32-C6-WROOM-1-N4"
        and component.footprint == "Espressif:ESP32-C6-WROOM-1"
    ):
        # Vendor symbol and PB model use the module's exact physical pad numbers.
        return _checked_mapping(component, resolver, "Espressif:ESP32-C6-WROOM-1")

    if cls == "edg.parts.connector.UsbPorts.UsbCReceptacle_Device":
        if component.footprint == "Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11":
            # KiCad names the physical shield SH; this footprint/model calls it S1.
            # KiCad 9 calls the shield S1; KiCad 10 calls it SH.
            identity = _checked_mapping(component, resolver, "Connector:USB_C_Receptacle_USB2.0_16P")
            if identity is not None:
                return identity
            mapping = {("SH" if number == "S1" else number): number for number in pins}
            return _checked_mapping(component, resolver, "Connector:USB_C_Receptacle_USB2.0_16P", mapping)

    if cls in {
        "edg.vendor_parts.jlc.JlcFet.JlcFet",
        "edg.vendor_parts.jlc.JlcFet.JlcSwitchFet",
        "lib.power.Ao3400a.Ao3400a",
    }:
        roles = _role_pins(component)
        if set(roles) == {"gate", "source", "drain"}:
            mapping = {"1": roles["gate"], "2": roles["source"], "3": roles["drain"]}
            exact = {"AO3400A": "AO3400A", "AO3401A": "AO3401A", "2N7002": "2N7002"}
            if identifier in exact:
                return _checked_mapping(component, resolver, "Transistor_FET:" + exact[identifier], mapping)
            if identifier == "SI2301CDS-T1-GE3":
                # Verified PB model records gate/source/drain; this PMOS pin order
                # is explicitly 1=G, 2=S, 3=D in the generic standard symbol.
                return _checked_mapping(component, resolver, "Transistor_FET:Q_PMOS_GSD", mapping)

    if cls == "edg.vendor_parts.jlc.JlcBjt.JlcBjt" and identifier in {
        "MMBT3904",
        "MMBT3906",
    }:
        # Exact KiCad definitions use 1=B, 2=E, 3=C. PB physical pad roles,
        # rather than SOT-23 ordering, determine the remapping.
        roles = _role_pins(component)
        if set(roles) == {"base", "emitter", "collector"}:
            return _checked_mapping(
                component,
                resolver,
                "Transistor_BJT:" + identifier,
                {"1": roles["base"], "2": roles["emitter"], "3": roles["collector"]},
            )

    diode_classes = {
        "edg.vendor_parts.jlc.JlcDiode.JlcDiode": "Device:D",
        "edg.vendor_parts.jlc.JlcDiode.JlcZenerDiode": "Device:D_Zener",
    }
    led_classes = {
        "edg.vendor_parts.jlc.JlcLed.JlcLed",
        "lib.human_interface.Kt0603y.Kt0603y",
        "lib.power.converter.XinglightXl4008uwc.XinglightXl4008uwc",
    }
    if cls in diode_classes or cls in led_classes:
        roles = _role_pins(component)
        if set(roles) == {"anode", "cathode"}:
            lib_id = "Device:LED" if cls in led_classes else diode_classes[cls]
            if cls in diode_classes and identifier in ("1N5819WS", "BAT60B"):
                lib_id = "Device:D_Schottky"
            return _checked_mapping(component, resolver, lib_id, {"1": roles["cathode"], "2": roles["anode"]})

    connector_classes = {
        "lib.connector.Jst.JlcJstPhKVerticalTwoPin": ("Connector_Generic:Conn_01x02", {"1", "2"}),
        "lib.components_lib.JlcPwmPinHeader254Vertical": ("Connector_Generic:Conn_01x03", {"1", "2", "3"}),
        "edg.parts.connector.TagConnect.TagConnectNonLegged": (
            "Connector_Generic:Conn_02x03_Odd_Even",
            {str(i) for i in range(1, 7)},
        ),
        "edg.parts.connector.Fpc.Afc01": ("Connector_Generic:Conn_01x30", {str(i) for i in range(1, 31)}),
    }
    if cls in connector_classes:
        lib_id, expected = connector_classes[cls]
        if pins == expected:
            return _checked_mapping(component, resolver, lib_id)
        if (
            cls == "edg.parts.connector.Fpc.Afc01"
            and identifier == "AFC01-S30FC*-00"
            and pins
            and pins.issubset(expected)
        ):
            # The OLED connector intentionally does not model unused pad 7.
            return _checked_mapping(component, resolver, lib_id)

    if (
        cls == "edg.vendor_parts.jlc.JlcSwitches.JlcSwitch"
        and identifier == "5.1mm switch"
        and component.footprint == "Button_Switch_SMD:SW_SPST_SKQG_WithoutStem"
        and pins == {"1", "2"}
    ):
        return _checked_mapping(component, resolver, "Switch:SW_Push")

    if (
        cls == "lib.human_interface.Sk6812sideas.Sk6812SideAS_Device"
        and identifier == "SK6812SIDE-A-S"
        and component.footprint == "fp:LED_SK6812SIDE_A_S"
    ):
        roles = _role_pins(component)
        if set(roles) == {"din", "vdd", "dout", "gnd"}:
            # Explicit family-graphic alias, NOT an identical physical package.
            # Both are single-wire addressable RGB LEDs (PB Neopixel model).
            # KiCad LED:SK6812 has 1=VSS, 2=DIN, 3=VDD, 4=DOUT.
            # SIDE-A-S datasheet/model instead has 1=DIN, 2=VDD, 3=DOUT, 4=GND:
            # https://atta.szlcsc.com/upload/public/pdf/source/20230330/
            # F1A167741926C16B6569128F16D7FD80.pdf
            # The exporter retains the SIDE-A-S Value and custom Footprint.
            return _checked_mapping(
                component,
                resolver,
                "LED:SK6812",
                {"1": roles["gnd"], "2": roles["din"], "3": roles["vdd"], "4": roles["dout"]},
            )

    if cls == "edg.parts.debug.TestPoint_Keystone.CompactKeystone5015" and pins == {"1"}:
        return _checked_mapping(component, resolver, "Connector:TestPoint")

    if cls in {"edg.BoardTop.JlcToolingHole", "edg.parts.Mechanicals.MountingHole_NoPad_M2_5"} and not pins:
        return _checked_mapping(component, resolver, "Mechanical:MountingHole")

    return None
