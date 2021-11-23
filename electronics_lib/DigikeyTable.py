from .TableDeratingCapacitor import *

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
