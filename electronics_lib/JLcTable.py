import re
from .PartsTable import *
import numpy as np

class JLcTable(LazyTable):
  """Shared base class for JLCPCB product tables that contains common row definitions."""

  MANUFACTURER = 'Manufacturer'
  PART_NUMBER = 'MFR.Part'
  DATASHEETS = 'Datasheet'

  COST = PartsTableColumn(float)

  @classmethod
  def _parse_jlcpcb_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""

    price_list = re.findall(":(\d+\.\d*),", row['Price'])
    float_array = [float(x) for x in price_list]

    return {
      cls.COST: float(max(float_array))
    }