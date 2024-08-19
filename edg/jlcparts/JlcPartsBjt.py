from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts.JlcBjt import JlcBjt
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsBjt(TableBjt, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = ["TransistorsBipolar_Transistors___BJT"]
    _CHANNEL_MAP = {
        'NPN': 'NPN',
        'PNP': 'PNP',
    }

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcBjt.PACKAGE_FOOTPRINT_MAP[package]

            row_dict[cls.CHANNEL] = cls._CHANNEL_MAP[attributes.get("Transistor type", str)]
            row_dict[cls.VCE_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Collector-emitter breakdown voltage (vceo)", str), 'V'))
            row_dict[cls.ICE_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Collector current (ic)", str), 'A'))
            row_dict[cls.GAIN] = Range.exact(PartParserUtil.parse_value(
                attributes.get("Dc current gain (hfe@ic,vce)", str).split('@')[0], ''))
            row_dict[cls.POWER_RATING] = Range.zero_to_upper(
                attributes.get("Power dissipation (pd)", float, sub='power'))

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None
