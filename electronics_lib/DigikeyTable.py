from typing import Dict, Any
from electronics_abstract_parts import *
from electronics_abstract_parts.PartsTable import LazyTable


class DigikeyTable(LazyTable):
  """Shared base class for Digikey product tables that contains common row definitions.
  Can be overridden by subclasses as needed.
  """
  MANUFACTURER = 'Manufacturer'
  PART_NUMBER = 'Manufacturer Part Number'
  DATASHEETS = 'Datasheets'
  DESCRIPTION = 'Description'

  _RAW_COST_COLUMN = 'Unit Price (USD)'
  COST = PartsTableColumn(float)

  @classmethod
  def _parse_digikey_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""
    return {
      cls.COST: float(row[cls._RAW_COST_COLUMN])
    }


class DigikeyTablePart(PartsTableFootprint):
  """Shared base class for Digikey product tables that contains common row definitions.
  Can be overridden by subclasses as needed.
  """
  MANUFACTURER_HEADER = 'Manufacturer'
  _PART_NUMBER_HEADER = 'Manufacturer Part Number'
  DESCRIPTION_HEADER = 'Description'
  DATASHEET_HEADER = 'Datasheets'
  _PACKAGE_HEADER = 'Package / Case'

  _COST_HEADER = 'Unit Price (USD)'
  COST = PartsTableColumn(float)

  @classmethod
  def _parse_digikey_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""
    return {
      cls.PART_NUMBER: row[cls._PART_NUMBER_HEADER],
      cls.COST: float(row[cls._COST_HEADER])
    }
