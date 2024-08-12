from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts import JlcResistor
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsResistorSmd(TableResistor, SmdStandardPackageSelector, JlcPartsBase):
    _kFileName = "ResistorsChip_Resistor___Surface_Mount"

    _kAttrResistance = "Resistance"
    _kAttrResistanceTol = "Tolerance"
    _kAttrPower = "Power"
    _kAttrVoltageRating = "Overload voltage (max)"

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcResistor.PACKAGE_FOOTPRINT_MAP[package]

            row_dict[cls.RESISTANCE] = PartParserUtil.parse_abs_tolerance(
                list(attributes.root[cls._kAttrResistanceTol].values.values())[0][0],
                list(attributes.root[cls._kAttrResistance].values.values())[0][0],
                ''
            )

            row_dict[cls.POWER_RATING] = Range.zero_to_upper(
                attributes.get(cls._kAttrPower, float, 0)
            )

            try:
                voltage_rating = float(PartParserUtil.parse_value(
                    attributes.get(cls._kAttrVoltageRating, str), 'V'))
            except (KeyError, PartParserUtil.ParseError):  # sometimes '-'
                voltage_rating = 0
            row_dict[cls.VOLTAGE_RATING] = Range.zero_to_upper(voltage_rating)

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None