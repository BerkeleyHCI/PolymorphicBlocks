from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts.JlcResistor import JlcResistor
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsResistorSmd(TableResistor, PartsTableAreaSelector, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = ["ResistorsChip_Resistor___Surface_Mount"]

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcResistor.PACKAGE_FOOTPRINT_MAP[package]

            row_dict[cls.RESISTANCE] = PartParserUtil.parse_abs_tolerance(
                attributes.get("Tolerance", str), attributes.get("Resistance", float, sub='resistance'), '')

            row_dict[cls.POWER_RATING] = Range.zero_to_upper(
                attributes.get("Power", float, 0, sub='power')
            )

            try:  # sometimes '-'
                voltage_rating = PartParserUtil.parse_value(attributes.get("Overload voltage (max)", str), 'V')
            except (KeyError, PartParserUtil.ParseError):
                voltage_rating = 0
            row_dict[cls.VOLTAGE_RATING] = Range.zero_to_upper(voltage_rating)

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None


lambda: JlcPartsResistorSmd()  # ensure class is instantiable (non-abstract)
