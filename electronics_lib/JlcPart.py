from typing import Optional, Dict, Any, Tuple, Callable, List
import re

from electronics_abstract_parts import *


@non_library
class JlcPart(Block):
  """Provides additional data fields for JLCPCB parts for their SMT service.
  By default, this does not check for basic parts, but that can be changed in refinements.
  """
  @init_in_parent
  def __init__(self, require_basic_part: BoolLike = False):
    super().__init__()
    self.lcsc_part = self.Parameter(StringExpr())
    self.actual_basic_part = self.Parameter(BoolExpr())
    self.require_basic_part = self.ArgParameter(require_basic_part)

    self.require(self.require_basic_part.implies(self.actual_basic_part), "required basic part")


DescriptionParser = Tuple[re.Pattern,
                          Callable[[re.Match], Dict[PartsTableColumn, Any]]]
class JlcTableBase(PartsTableBase):
  """Defines common table headers, columns, and functionality for parsing JLCPCB parts tables."""
  PART_NUMBER_COL = 'MFR.Part'  # used only for translation to the PartsTableFootprint col
  MANUFACTURER_COL = 'Manufacturer'
  DESCRIPTION_COL = 'Description'
  DATASHEET_COL = 'Datasheet'

  _PACKAGE_HEADER = 'Package'

  LCSC_PART_HEADER = 'LCSC Part'
  BASIC_PART_HEADER = 'Library Type'
  BASIC_PART_VALUE = 'Basic'

  COST_HEADER = 'Price'
  COST = PartsTableColumn(float)

  __JLC_TABLE: Optional[PartsTable] = None

  @classmethod
  def _jlc_table(cls) -> PartsTable:
    """Returns the full JLC parts table, saving the result for future use."""
    if JlcTableBase.__JLC_TABLE is None:  # specifically this class, so results are visible to subclasses
      JlcTableBase.__JLC_TABLE = PartsTable.from_csv_files(PartsTable.with_source_dir([
        'Pruned_JLCPCB SMT Parts Library(20220419).csv'
      ], 'resources'), encoding='gb2312')
    return JlcTableBase.__JLC_TABLE

  @classmethod
  def _parse_jlcpcb_common(cls, row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
    """Returns a dict with the cost row, or errors out with KeyError."""
    # extracts out all the available prices for a given part by order quantity
    price_list = re.findall(":(\d+\.\d*),", row[cls.COST_HEADER])
    float_array = [float(x) for x in price_list]
    if not float_array:
      cost = float('inf')  # disprefer heavily if no price listed
    else:
      cost = max(float_array)  # choose the highest price, which is for the lowest quantity

    return {
      cls.COST: cost,
    }

  @staticmethod
  def parse(description: str, regex_dictionary: Dict[str, re.Pattern]):
    extraction_table = {}

    for key, pattern in regex_dictionary.items():
      matches = pattern.findall(description)
      if matches:  # discard if not matched
        assert len(matches) == 1  # excess matches fail noisily
        assert key not in extraction_table  # duplicate matches fail noisily
        extraction_table[key] = matches[0]

    return extraction_table

  @staticmethod
  def parse_full_description(description: str, parser_options: List[DescriptionParser]) -> \
      Optional[Dict[PartsTableColumn, Any]]:
    for parser, match_fn in parser_options:
      parsed_values = parser.match(description)
      if parsed_values:
        return match_fn(parsed_values)

    return None  # exhausted all options


@non_library
class JlcTableSelector(PartsTableSelector, JlcPart, JlcTableBase, PartsTableFootprint):
  @classmethod
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    return [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.lcsc_part, row[self.LCSC_PART_HEADER])
    self.assign(self.actual_basic_part, row[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE)
