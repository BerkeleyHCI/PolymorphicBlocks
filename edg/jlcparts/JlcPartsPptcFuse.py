from typing import Any, Optional, Dict

from typing_extensions import override

from ..abstract_parts import *
from ..parts.JlcPptcFuse import JlcPptcFuse
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsPptcFuse(PartsTableSelectorFootprint, JlcPartsBase, TableFuse, PptcFuse):
    _JLC_PARTS_FILE_NAMES = ["Circuit_ProtectionResettable_Fuses"]

    @classmethod
    @override
    def _entry_to_table_row(
        cls, row_dict: Dict[PartsTableColumn, Any], filename: str, package: str, attributes: JlcPartsAttributes
    ) -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcPptcFuse.PACKAGE_FOOTPRINT_MAP[package]

            row_dict[cls.VOLTAGE_RATING] = Range.zero_to_upper(
                PartParserUtil.parse_value(attributes.get("Operating voltage (max)", str), "V")
            )
            row_dict[cls.TRIP_CURRENT] = Range.exact(
                PartParserUtil.parse_value(attributes.get("Trip current", str), "A")
            )
            row_dict[cls.HOLD_CURRENT] = Range.exact(
                PartParserUtil.parse_value(attributes.get("Hold current", str), "A")
            )

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None


lambda: JlcPartsPptcFuse()  # ensure class is instantiable (non-abstract)
