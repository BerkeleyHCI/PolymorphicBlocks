from typing import Optional, List, Tuple, Dict

from pydantic import RootModel, BaseModel
import os


class FootprintData(BaseModel):
    area: float
    bbox: Tuple[float, float, float, float]  # [x_min, y_min, x_max, y_max]


class FootprintJson(RootModel[Dict[str, FootprintData]]):  # script relpath imports are weird so this is duplicated here
    root: dict[str, FootprintData]  # footprint name -> data


class FootprintDataTable:
    _table: Optional[FootprintJson] = None

    @classmethod
    def _get_table(cls) -> FootprintJson:
        if cls._table is None:
            with open(os.path.join(os.path.dirname(__file__), "resources", "kicad_footprints.json"), "r") as f:
                cls._table = FootprintJson.model_validate_json(f.read())
        return cls._table

    @classmethod
    def area_of(cls, footprint: str) -> float:
        """Returns the area of a footprint, returning infinity if unavailable"""
        elt = cls._get_table().root.get(footprint)
        if elt is None:
            return float("inf")
        else:
            return elt.area

    @classmethod
    def bbox_of(cls, footprint: str) -> Optional[Tuple[float, float, float, float]]:
        """Returns the bounding box of a footprint, returning None if unavailable"""
        elt = cls._get_table().root.get(footprint)
        if elt is None:
            return None
        else:
            return elt.bbox
