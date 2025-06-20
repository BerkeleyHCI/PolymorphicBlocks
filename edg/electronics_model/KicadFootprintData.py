from typing import Optional, List

from pydantic import RootModel, BaseModel
import os


class FootprintData(BaseModel):
  area: float
  bbox: List[float]  # [x_min, y_min, x_max, y_max]


class FootprintJson(RootModel):  # script relpath imports are weird so this is duplicated here
  root: dict[str, FootprintData]  # footprint name -> data


class FootprintDataTable:
  _table: Optional[FootprintJson] = None

  @classmethod
  def area_of(cls, footprint: str) -> float:
    """Returns the area of a footprint, returning infinity if unavailable"""
    if cls._table is None:
      with open(os.path.join(os.path.dirname(__file__), "resources", "kicad_footprints.json"), 'r') as f:
        cls._table = FootprintJson.model_validate_json(f.read())
    elt = cls._table.root.get(footprint)
    if elt is None:
      return float('inf')
    else:
      return elt.area
