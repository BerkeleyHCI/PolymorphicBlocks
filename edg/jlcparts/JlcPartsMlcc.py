from typing import Any, Optional, Dict
from ..abstract_parts import *
from ..parts import JlcCapacitor
from .JlcPartsBase import JlcPartsBase, JlcPartsAttributes


class JlcPartsMlcc(JlcPartsBase):
    _kFileName = "CapacitorsMultilayer_Ceramic_Capacitors_MLCC___SMDakaSMT.json.gz"

    @classmethod
    def _entry_to_table_row(cls, row_dict: Dict[PartsTableColumn, Any], package: str, attributes: JlcPartsAttributes) \
            -> Optional[Dict[PartsTableColumn, Any]]:
        try:
            row_dict[cls.KICAD_FOOTPRINT] = JlcCapacitor.PACKAGE_FOOTPRINT_MAP[package]
            return row_dict
        except KeyError:
            return None
