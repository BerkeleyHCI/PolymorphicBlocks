from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts import JlcCapacitor
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsMlcc(TableDeratingCapacitor, CeramicCapacitor, SmdStandardPackageSelector, JlcPartsBase):
    _JLC_PARTS_FILE_NAMES = ["CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT"]

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            footprint = JlcCapacitor.PACKAGE_FOOTPRINT_MAP[package]
            row_dict[cls.KICAD_FOOTPRINT] = footprint

            nominal_capacitance = attributes.get("Capacitance", float, sub='capacitance')
            # note, tolerance not specified for many devices
            row_dict[cls.CAPACITANCE] = PartParserUtil.parse_abs_tolerance(
                attributes.get("Tolerance", str), nominal_capacitance, '')
            row_dict[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
            row_dict[cls.VOLTAGE_RATING] = Range.zero_to_upper(
                attributes.get("Allowable voltage", float, 0, sub='voltage'))
            row_dict[cls.VOLTCO] = JlcCapacitor.DERATE_VOLTCO_MAP[footprint]

            # arbitrary filter - TODO parameterization
            tempco = attributes.get("Temperature coefficient", str)
            if len(tempco) < 3 or tempco[0] not in ('X', 'C') or tempco[2] not in ('R', 'S', 'G'):
                return None

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None
