from typing import Optional, Dict, Any
import re

from electronics_abstract_parts import *


@abstract_block
class JlcFootprint(Block):
  @init_in_parent
  def __init__(self, require_basic_part: BoolLike = False):
    super().__init__()
    self.lcsc_part = self.Parameter(StringExpr())
    self.actual_basic_part = self.Parameter(BoolExpr())
    self.require_basic_part = self.ArgParameter(require_basic_part)

    # TODO not enforced while migrating
    # self.require(self.require_basic_part.implies(self.actual_basic_part), "required basic part")


@abstract_block
class JlcTableFootprint(JlcFootprint, PartsTableFootprint):
  MANUFACTURER_HEADER = 'Manufacturer'
  DATASHEET_HEADER = 'Datasheet'
  DESCRIPTION_HEADER = 'Description'
  LCSC_PART_HEADER = 'LCSC Part'
  BASIC_PART_HEADER = 'Library Type'
  BASIC_PART_VALUE = 'Basic'

  _PART_NUMBER_HEADER = 'MFR.Part'  # used only for translation to the PartsTableFootprint col

  COST = PartsTableColumn(float)

  _JLC_TABLE: Optional[PartsTable] = None

  @classmethod
  def _jlc_table(cls) -> PartsTable:
    if JlcTableFootprint._JLC_TABLE is None:  # specifically this class, so results are visible to subclasses
      JlcTableFootprint._JLC_TABLE = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
        'JLCPCB_SMT_Parts_Library.csv'
      ], 'resources'), encoding='gb2312')
    return JlcTableFootprint._JLC_TABLE

  @classmethod
  def _parse_jlcpcb_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""

    #extracts out all the available prices for a given part by order quantity
    price_list = re.findall(":(\d+\.\d*),", row['Price'])
    float_array = [float(x) for x in price_list]

    return {
      #chooses the highest price, which is for the lowest quantity
      cls.COST: float(max(float_array)),
      cls.PART_NUMBER: row[cls._PART_NUMBER_HEADER],
    }
