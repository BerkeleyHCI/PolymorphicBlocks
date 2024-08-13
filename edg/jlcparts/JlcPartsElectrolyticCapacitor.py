from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts import JlcResistor
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsElectrolyticCapacitor(TableResistor, SmdStandardPackageSelector, JlcPartsBase):
    # _JLC_PARTS_FILE_NAME = "ResistorsChip_Resistor___Surface_Mount"

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            # row_dict[cls.KICAD_FOOTPRINT] = JlcResistor.PACKAGE_FOOTPRINT_MAP[package]

            return row_dict
        except (KeyError, TypeError, PartParserUtil.ParseError):
            return None
