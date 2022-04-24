from typing import Dict, Any
from electronics_abstract_parts import *


class DigikeyTablePart(PartsTableFootprint):
  """Shared base class for Digikey product tables that contains common row definitions.
  Can be overridden by subclasses as needed.
  """
  PART_NUMBER_COL = 'Manufacturer Part Number'
  MANUFACTURER_COL = 'Manufacturer'
  DESCRIPTION_COL = 'Description'
  DATASHEET_COL = 'Datasheets'

  _PACKAGE_HEADER = 'Package / Case'

  _COST_HEADER = 'Unit Price (USD)'
  COST = PartsTableColumn(float)

  @classmethod
  def _parse_digikey_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""
    return {
      cls.COST: float(row[cls._COST_HEADER])
    }
