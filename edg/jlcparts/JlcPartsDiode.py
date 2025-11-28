from typing import Any, Optional, Dict

from typing_extensions import override

from ..abstract_parts import *
from ..parts.JlcDiode import JlcDiode
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsDiode(PartsTableSelectorFootprint, JlcPartsBase, TableDiode):
    _JLC_PARTS_FILE_NAMES = [
        "DiodesSchottky_Barrier_Diodes__SBD_",
        "DiodesDiodes___Fast_Recovery_Rectifiers",
        "DiodesDiodes___General_Purpose",
        "DiodesSwitching_Diode",
    ]

    @classmethod
    @override
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcDiode.PACKAGE_FOOTPRINT_MAP[package]

            row_dict[cls.VOLTAGE_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Reverse voltage (vr)", str), 'V'))
            row_dict[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Forward voltage (vf@if)", str).split('@')[0], 'V'))
            if "Average rectified current (io)" in attributes:
                row_dict[cls.CURRENT_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                    attributes.get("Average rectified current (io)", str), 'A'))
            elif "Rectified current" in attributes:  # different key for some files
                row_dict[cls.CURRENT_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                    attributes.get("Rectified current", str), 'A'))
            else:
                raise KeyError("no current rating")

            try:  # sometimes '-'
                reverse_recovery = Range.exact(PartParserUtil.parse_value(
                    attributes.get("Reverse recovery time (trr)", str), 's'))
            except (KeyError, PartParserUtil.ParseError):
                if filename == "DiodesDiodes___Fast_Recovery_Rectifiers":
                    reverse_recovery = Range(0, 500e-9)  # arbitrary <500ns
                else:
                    reverse_recovery = Range.all()
            row_dict[cls.REVERSE_RECOVERY] = reverse_recovery

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None


class JlcPartsZenerDiode(TableZenerDiode, PartsTableSelectorFootprint, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = ["DiodesZener_Diodes"]

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcDiode.PACKAGE_FOOTPRINT_MAP[package]

            if "Zener voltage (range)" in attributes:  # note, some devices have range='-'
                zener_voltage_split = attributes.get("Zener voltage (range)", str).split('~')
                zener_voltage = Range(
                    PartParserUtil.parse_value(zener_voltage_split[0], 'V'),
                    PartParserUtil.parse_value(zener_voltage_split[1], 'V')
                )
            else:  # explicit tolerance
                zener_voltage = PartParserUtil.parse_abs_tolerance(
                    attributes.get("Tolerance", str),
                    PartParserUtil.parse_value(attributes.get("Zener voltage (nom)", str), 'V'),
                    '')
            row_dict[cls.ZENER_VOLTAGE] = zener_voltage

            row_dict[cls.POWER_RATING] = Range.zero_to_upper(PartParserUtil.parse_value(
                attributes.get("Power dissipation", str), 'W'))

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None


lambda: (JlcPartsDiode(), JlcPartsZenerDiode())  # ensure class is instantiable (non-abstract)
