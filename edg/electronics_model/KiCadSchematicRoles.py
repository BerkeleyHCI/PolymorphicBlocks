"""Verified display pin presentation, transcribed from PB model connection maps.

Only annotates modeled pads. Does not add pins, NCs or electrical connections.
Integration: copy to electronics_model/KiCadSchematicRoles.py after source thaw.
Call infer_pin_names(component, [p.target.name for p in block.path_classes]).
Merge returned names BELOW explicit compiled/board presentation pin names.
"""

from __future__ import annotations
from typing import Any, Mapping, Sequence, TYPE_CHECKING, Optional, cast

if TYPE_CHECKING:
    from .KiCadSchematicExporter import PhysicalComponent

RoleEntry = tuple[set[str], dict[str, str], str]

# Each table follows device.__init__'s .connected(...) maps in these modules.
# Exact direct-child connector classes ensure no intervening pin-flip adapter.
FPC050 = {"edg.parts.connector.Fpc.Afc01", "edg.parts.connector.Fpc.HiroseFh12sh"}
FPC030 = {"edg.parts.connector.Fpc.HiroseFh35cshw"}
OLED = "edg.parts.display.oled."
MAPS: dict[str, RoleEntry] = {
    OLED
    + "Er_Oled_096_1_1.Er_Oled_096_1_1_Device": (
        FPC050,
        {
            "1": "VSS",
            "2": "C2P",
            "3": "C2N",
            "4": "C1P",
            "5": "C1N",
            "6": "VBAT",
            "8": "VSS",
            "9": "VDD",
            "10": "BS0",
            "11": "BS1",
            "12": "BS2 (GND)",
            "13": "CS",
            "14": "RES",
            "15": "DC",
            "16": "PARALLEL (GND)",
            "17": "PARALLEL (GND)",
            "18": "D0/CLK",
            "19": "D1/DATA",
            "20": "D2",
            "21": "D3 (GND)",
            "22": "D4 (GND)",
            "23": "D5 (GND)",
            "24": "D6 (GND)",
            "25": "D7 (GND)",
            "26": "IREF",
            "27": "VCOMH",
            "28": "VCC",
            "29": "NC/GND",
            "30": "VSS",
        },
        "ER-OLED-0.96-1.1 display interface: logic supply, charge pump, IREF and serial control",
    ),
    OLED
    + "Er_Oled_022.Er_Oled022_1_Device": (
        FPC050,
        {
            "1": "VSS",
            "2": "NC/GND",
            "3": "VSS",
            "5": "VDD",
            "6": "BS1",
            "7": "BS2",
            "8": "CS",
            "9": "RES",
            "10": "DC",
            "11": "PARALLEL (GND)",
            "12": "PARALLEL (GND)",
            "13": "D0/CLK",
            "14": "D1/DATA",
            "15": "D2",
            "16": "D3 (GND)",
            "17": "D4 (GND)",
            "18": "D5 (GND)",
            "19": "D6 (GND)",
            "20": "D7 (GND)",
            "21": "IREF",
            "22": "VCOMH",
            "23": "VCC",
            "24": "VSS",
        },
        "ER-OLED022-1 display interface: logic VDD, external VCC, IREF and serial control",
    ),
    OLED
    + "Er_Oled_096_1c.Er_Oled_096_1c_Device": (
        FPC030,
        {
            "1": "VSS",
            "2": "VSL",
            "3": "VCOMH",
            "4": "VP",
            "5": "VCC",
            "6": "IREF",
            "7": "VSS",
            "8": "VDD",
            "9": "RES",
            "10": "DC",
            "11": "CS",
            "12": "BS2 (GND)",
            "13": "BS1",
            "14": "BS0",
            "15": "PARALLEL (GND)",
            "16": "PARALLEL (GND)",
            "17": "VDD",
            "18": "D0/CLK",
            "19": "D1/DATA",
            "20": "D2",
            "21": "D3 (GND)",
            "22": "D4 (GND)",
            "23": "D5 (GND)",
            "24": "D6 (GND)",
            "25": "D7 (GND)",
            "26": "VLSS",
            "27": "VCC",
            "28": "VP",
            "29": "VCOMH",
            "30": "VSL",
            "31": "VSS",
        },
        "ER-OLED0.96-1C RGB display interface: logic VDD, external VCC, VSL/VP bias and serial control",
    ),
    "edg.parts.display.Waveshare_Epd.Waveshare_Epd_Device": (
        FPC050,
        {
            "2": "GDR",
            "3": "RESE",
            "4": "VGL",
            "5": "VGH",
            "8": "BS",
            "9": "BUSY",
            "10": "RST",
            "11": "DC",
            "12": "CS",
            "13": "SCLK",
            "14": "SDIN",
            "15": "VDDIO",
            "16": "VDD",
            "17": "VSS",
            "18": "VDD1V8",
            "20": "VSH",
            "21": "PREVGH",
            "22": "VSL",
            "23": "PREVGL",
            "24": "VCOM",
        },
        "Waveshare-compatible EPD interface: SPI control, boost gate/current sense and display bias rails",
    ),
    "edg.parts.display.EInk_Er_Epd027_2.Er_Epd027_2_Device": (
        FPC050,
        {
            "2": "GDR",
            "3": "RESE",
            "5": "VSHR",
            "8": "BS",
            "9": "BUSY",
            "10": "RST",
            "11": "DC",
            "12": "CS",
            "13": "SCLK",
            "14": "SDIN",
            "15": "VDDIO",
            "16": "VDD",
            "17": "VSS",
            "18": "VDD1V8",
            "20": "VSH",
            "21": "VGH",
            "22": "VSL",
            "23": "VGL",
            "24": "VCOM",
        },
        "ER-EPD027-2 EPD interface: SPI control, boost gate/current sense and display bias rails",
    ),
}


def _entry(
    component: PhysicalComponent, class_names: Sequence[str], connector_length: object = None
) -> Optional[RoleEntry]:
    classes = [c.removeprefix("PolymorphicBlocks.") for c in class_names]
    if len(classes) < 2:
        return None
    entry = MAPS.get(classes[-2])
    if entry is None or classes[-1] not in entry[0]:
        # Fpc050BottomFlip.generate explicitly exports logical n as physical
        # length + 1 - n. Require that exact adapter, leaf model and compiled
        # length; neither footprint text nor omitted-pad count establishes it.
        if (
            len(classes) < 3
            or classes[-2] != "edg.parts.connector.Fpc.Fpc050BottomFlip"
            or classes[-1] != "edg.parts.connector.Fpc.Afc07Top"
        ):
            return None
        entry = MAPS.get(classes[-3])
        if entry is None or connector_length != max(map(int, entry[1])):
            return None
        length = connector_length
        entry = (
            entry[0],
            {str(length + 1 - int(pin)): name for pin, name in entry[1].items()},
            entry[2] + "; pin numbers are physical connector pads",
        )
    # Physical connector mapping is identity pins.N, checked before assigning
    # semantic names. A refined connector with any renumbering stays unknown.
    if any(role.removesuffix(".net") != "pins." + number for number, role in component.pins.items()):
        return None
    if not set(component.pins).issubset(entry[1]):
        return None
    return entry


def infer_pin_names(
    component: PhysicalComponent, class_names: Sequence[str], connector_length: object = None
) -> Mapping[str, str]:
    entry = _entry(component, class_names, connector_length)
    return {number: entry[1][number] for number in component.pins} if entry else {}


def infer_description(component: PhysicalComponent, class_names: Sequence[str], connector_length: object = None) -> str:
    entry = _entry(component, class_names, connector_length)
    if entry:
        return entry[2]
    classes = [c.removeprefix("PolymorphicBlocks.") for c in class_names]
    if not component.pins and classes and classes[-1].endswith("_Outline"):
        verified = {
            OLED
            + "Er_Oled_096_1_1.Er_Oled_096_1_1_Outline": "ER-OLED-0.96-1.1 mechanical panel outline; electrical interface is the FPC connector",
            OLED
            + "Er_Oled_022.Er_Oled022_1_Outline": "ER-OLED022-1 mechanical panel outline; electrical interface is the FPC connector",
            OLED
            + "Er_Oled_096_1c.Er_Oled_096_1c_Outline": "ER-OLED0.96-1C mechanical panel outline; electrical interface is the FPC connector",
        }
        return verified.get(classes[-1], "")
    return ""
