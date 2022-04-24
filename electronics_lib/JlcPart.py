from typing import Optional, Dict, Any
import re

from electronics_abstract_parts import *


@abstract_block
class JlcPart(Block):
  """Provides additional data fields for JLCPCB parts for their SMT service."""
  @init_in_parent
  def __init__(self, require_basic_part: BoolLike = True):
    super().__init__()
    self.lcsc_part = self.Parameter(StringExpr())
    self.actual_basic_part = self.Parameter(BoolExpr())
    self.require_basic_part = self.ArgParameter(require_basic_part)

    self.require(self.require_basic_part.implies(self.actual_basic_part), "required basic part")


@abstract_block
class JlcTablePart(JlcPart, PartsTableFootprint):
  """Defines common table headers, columns, and functionality for parsing JLCPCB parts tables."""
  MANUFACTURER_HEADER = 'Manufacturer'
  _PART_NUMBER_HEADER = 'MFR.Part'  # used only for translation to the PartsTableFootprint col
  DESCRIPTION_HEADER = 'Description'
  DATASHEET_HEADER = 'Datasheet'
  _PACKAGE_HEADER = 'Package'

  LCSC_PART_HEADER = 'LCSC Part'
  BASIC_PART_HEADER = 'Library Type'
  BASIC_PART_VALUE = 'Basic'

  COST_HEADER = 'Price'
  COST = PartsTableColumn(float)

  _JLC_TABLE: Optional[PartsTable] = None

  @classmethod
  def _jlc_table(cls) -> PartsTable:
    if JlcTablePart._JLC_TABLE is None:  # specifically this class, so results are visible to subclasses
      JlcTablePart._JLC_TABLE = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
        'JLCPCB_SMT_Parts_Library.csv'
      ], 'resources'), encoding='gb2312')
    return JlcTablePart._JLC_TABLE

  @classmethod
  def _parse_jlcpcb_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""

    #extracts out all the available prices for a given part by order quantity
    price_list = re.findall(":(\d+\.\d*),", row[cls.COST_HEADER])
    float_array = [float(x) for x in price_list]
    if not float_array:
      cost = float('inf')  # disprefer heavily if no price listed
    else:
      cost = max(float_array)  # choose the highest price, which is for the lowest quantity

    return {
      cls.COST: cost,
      cls.PART_NUMBER: row[cls._PART_NUMBER_HEADER],
    }

  @staticmethod
  def parse(description, regex_dictionary):
    extraction_table = {}

    for key in regex_dictionary:
      matches = re.findall(regex_dictionary[key], description)
      if matches:  # discard if not matched
        assert len(matches) == 1  # excess matches fail noisily
        assert key not in extraction_table  # duplicate matches fail noisily
        extraction_table[key] = matches[0]

    return extraction_table
