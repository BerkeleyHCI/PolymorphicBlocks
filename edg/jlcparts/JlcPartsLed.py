from typing import Any, Optional, Dict

from typing_extensions import override

from ..abstract_parts import *
from ..parts.JlcLed import JlcLed
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsLed(PartsTableSelectorFootprint, JlcPartsBase, TableLed):
    _JLC_PARTS_FILE_NAMES = [
        "OptoelectronicsLight_Emitting_Diodes__LED_",
        "OptoelectronicsLED_Indication___Discrete",
        "Photoelectric_DevicesLight_Emitting_Diodes__LED_",
        "OptocouplerakaLEDakaDigital_TubeakaPhotoelectric_DeviceLight_Emitting_Diodes__LED_",
        "Optocouplers_and_LEDs_and_InfraredLight_Emitting_Diodes__LED_",
    ]
    _COLOR_MAP = {
        "red": Led.Red,
        "orange": Led.Orange,
        "amber": Led.Yellow,
        "yellow": Led.Yellow,
        "green/yellow-green": Led.GreenYellow,
        "yellow-green": Led.GreenYellow,
        "green-yellow": Led.GreenYellow,
        "emerald": Led.Green,
        "blue": Led.Blue,
        "ice blue": Led.Blue,
        "white": Led.White,
        "white light": Led.White,
    }

    @classmethod
    @override
    def _entry_to_table_row(
        cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes
    ) -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcLed.PACKAGE_FOOTPRINT_MAP[package]

            part_color: Optional[str] = None
            if "Emitted color" in attributes:
                table_color = attributes.get("Emitted color", str).lower()
                part_color = cls._COLOR_MAP[table_color]
            else:  # older basic parts don't have the parametrics
                desc = row_dict[cls.DESCRIPTION_COL].lower()
                for color_str, color in cls._COLOR_MAP.items():
                    if color_str in desc:
                        part_color = color
                        break
            if part_color is None:
                raise KeyError
            row_dict[cls.COLOR] = part_color

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None


lambda: JlcPartsLed()  # ensure class is instantiable (non-abstract)
