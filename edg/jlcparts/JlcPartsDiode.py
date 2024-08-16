from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts import JlcDiode
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsDiode(TableDiode, SmdStandardPackageSelector, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = [
        "DiodesDiodes___Fast_Recovery_Rectifiers",
        "DiodesDiodes___General_Purpose",
        "DiodesSchottky_Barrier_Diodes__SBD_",
        "DiodesSwitching_Diode",
    ]

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcDiode.PACKAGE_FOOTPRINT_MAP[package]

            row_dict[cls.VOLTAGE_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Reverse voltage (vr)", str), 'V'))
            row_dict[cls.CURRENT_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Average rectified current (io)", str), 'A'))
            row_dict[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Forward voltage (vf@if)", str).split('@')[0], 'V'))

            try:  # sometimes '-'
                reverse_recovery = Range.exact(PartParserUtil.parse_value(
                    attributes.get("Reverse recovery time (trr)", str), 's'))
            except (KeyError, PartParserUtil.ParseError):
                reverse_recovery = Range.all()
            row_dict[cls.REVERSE_RECOVERY] = reverse_recovery

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None
