from typing import Optional, Dict, Any

from electronics_abstract_parts import *
from electronics_lib.JlcPart import JlcTablePart


class JlcLed(Led, GeneratorBlock, JlcTablePart, SmdStandardPackage, FootprintBlock):
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

  SMD_FOOTPRINT_MAP = {
    '01005': None,
    '0201': None,
    '0402': 'LED_SMD:LED_0402_1005Metric',
    '0603': 'LED_SMD:LED_0603_1608Metric',
    '0805': 'LED_SMD:LED_0805_2012Metric',
    '1206': 'LED_SMD:LED_1206_3216Metric',
    '1210': None,
    '1806': None,
    '1812': None,
    '2010': None,
    '2512': None,
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

  @classmethod
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    return [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.actual_color = self.Parameter(StringExpr())
    self.generator(self.select_part, self.color, self.part, self.footprint_spec, self.minimum_smd_package)

  def select_part(self, color: str, part_spec: str, footprint_spec: str, minimum_smd_package: str) -> None:
    minimum_invalid_footprints = SmdStandardPackage.get_smd_packages_below(minimum_smd_package, self.SMD_FOOTPRINT_MAP)
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        (row[self.KICAD_FOOTPRINT] not in minimum_invalid_footprints) and
        (not color or row[self.COLOR] == color)
    )).sort_by(self._row_sort_by)
    part = parts.first(f"no LEDs in color={color}")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))
    self.assign(self.actual_color, part[self.COLOR])
    self.assign(self.lcsc_part, part[self.LCSC_PART_HEADER])
    self.assign(self.actual_basic_part, part[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE)

    self.footprint(
      'D', part[self.KICAD_FOOTPRINT],
      {
        '2': self.a,
        '1': self.k,
      },
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )
