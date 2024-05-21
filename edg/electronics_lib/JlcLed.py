from typing import Optional, Dict, Any

from ..electronics_abstract_parts import *
from .JlcPart import JlcTableSelector


class JlcLed(LedStandardFootprint, JlcTableSelector, SmdStandardPackageSelector, PartsTableFootprintSelector):
  PACKAGE_FOOTPRINT_MAP = {
    # 0201 not in parts table, LED_0201_0603Metric

    '0402': 'LED_SMD:LED_0402_1005Metric',
    '0603': 'LED_SMD:LED_0603_1608Metric',
    '0805': 'LED_SMD:LED_0805_2012Metric',
    '1206': 'LED_SMD:LED_1206_3216Metric',

    'LED_0402': 'LED_SMD:LED_0402_1005Metric',
    'LED_0603': 'LED_SMD:LED_0603_1608Metric',
    'LED_0805': 'LED_SMD:LED_0805_2012Metric',
    'LED_1206': 'LED_SMD:LED_1206_3216Metric',
  }

  # because the description formatting is so inconsistent, the table is just hardcoded here
  # instead of trying to parse the parts table
  PART_COLOR_MAP = {
    'C2286': Led.Red,
    'C2290': Led.White,
    'C2293': Led.Blue,
    'C2296': Led.Yellow,
    'C2297': Led.Green,
    'C34499': Led.White,
    'C72038': Led.Yellow,
    'C72041': Led.Blue,
    'C72043': Led.Green,  # "emerald"
    'C84256': Led.Red,
  }

  # TODO this should probably be refactored into TableLed or something
  COLOR = PartsTableColumn(str)

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Light Emitting Diodes (LED)':
        return None

      footprint = cls.PACKAGE_FOOTPRINT_MAP.get(row[cls._PACKAGE_HEADER])
      if footprint is None:
        return None

      color = cls.PART_COLOR_MAP.get(row[cls.LCSC_PART_HEADER])
      if color is None:
        return None

      new_cols = {}
      new_cols[cls.COLOR] = color
      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.color)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      (not self.get(self.color) or row[self.COLOR] == self.get(self.color))

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_color, row[self.COLOR])
