from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts import JlcLed
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsLed(TableLed, SmdStandardPackageSelector, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = [
        "OptoelectronicsLED_Indication___Discrete",
        "Photoelectric_DevicesLight_Emitting_Diodes__LED_",
        "OptocouplerakaLEDakaDigital_TubeakaPhotoelectric_DeviceLight_Emitting_Diodes__LED_",
        ]
    _COLOR_MAP = {
        'red': Led.Red,
        'orange': Led.Orange,
        'amber': Led.Yellow,
        'yellow': Led.Yellow,
        'green/yellow-green': Led.GreenYellow,
        'yellow-green': Led.GreenYellow,
        'green-yellow': Led.GreenYellow,
        'emerald': Led.Green,
        'blue': Led.Blue,
        'ice blue': Led.Blue,
        'white': Led.White,
        'white light': Led.White,
    }

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcLed.PACKAGE_FOOTPRINT_MAP[package]

            table_color = attributes.get('Emitted color', str).lower()
            row_dict[cls.COLOR] = cls._COLOR_MAP[table_color]

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None
