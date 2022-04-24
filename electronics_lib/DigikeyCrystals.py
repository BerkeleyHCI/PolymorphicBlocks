from typing import Optional, Any, Dict
from electronics_abstract_parts import *
from .DigikeyPart import DigikeyTablePart


class DigikeyCrystal(TableCrystal, DigikeyTablePart, FootprintBlock):
  SIZE_PACKAGE_FOOTPRINT_MAP = {
    ('0.126" L x 0.098" W (3.20mm x 2.50mm)', '4-SMD, No Lead'):
      'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm',
  }

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        new_cols[cls.KICAD_FOOTPRINT] = cls.SIZE_PACKAGE_FOOTPRINT_MAP[
          (row['Size / Dimension'], row[cls._PACKAGE_HEADER])
        ]

        if row['Operating Mode'] != 'Fundamental':
          return None

        new_cols[cls.FREQUENCY] = Range.from_tolerance(
          PartsTableUtil.parse_value(row['Frequency'], 'Hz'),
          PartsTableUtil.parse_tolerance(row['Frequency Tolerance'])
        )
        new_cols[cls.CAPACITANCE] = PartsTableUtil.parse_value(row['Load Capacitance'], 'F')

        new_cols.update(cls._parse_digikey_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_Crystals_3.2x2.5_1.csv',
      'Digikey_Crystals_3.2x2.5_2.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: row[cls.COST]
    )

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'X', part[self.KICAD_FOOTPRINT],
      {
        '1': self.crystal.a,
        '2': self.gnd,
        '3': self.crystal.b,
        '4': self.gnd,
      },
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=f"{part['Frequency']}, {part['Load Capacitance']}",
      datasheet=part[self.DATASHEET_COL]
    )
