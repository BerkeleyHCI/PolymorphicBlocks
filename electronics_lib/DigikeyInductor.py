from typing import Dict, Any, Optional
from electronics_abstract_parts import *
from .DigikeyTable import DigikeyTablePart


class DigikeyInductor(TableInductor, DigikeyTablePart, FootprintBlock):
  PACKAGE_FOOTPRINT_MAP = {  # from Digikey Package / Case to KiCad footprint
    '0603 (1608 Metric)': 'Inductor_SMD:L_0603_1608Metric',
    '0805 (2012 Metric)': 'Inductor_SMD:L_0805_2012Metric',
  }
  SERIES_FOOTPRINT_MAP = {  # from part series to KiCad footprint
    'SRR1015': 'Inductor_SMD:L_Bourns-SRR1005',
    'SRR1210': 'Inductor_SMD:L_Bourns_SRR1210A',
    'SRR1210A': 'Inductor_SMD:L_Bourns_SRR1210A',
    'SRR1260': 'Inductor_SMD:L_Bourns_SRR1260',
    'SRR1260A': 'Inductor_SMD:L_Bourns_SRR1260',
    # Kicad does not have stock 1008 footprint
  }
  # from manufacturer part number to KiCad footprint w/ substitution
  MPN_NR_FOOTPRINT_REGEX = PartsTableUtil.RegexRemapper(
    r'^NR(\d\d).*$', 'Inductor_SMD:L_Taiyo-Yuden_NR-{0}xx')

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        footprint = (cls.PACKAGE_FOOTPRINT_MAP.get(row['Package / Case'], None) or
                     cls.SERIES_FOOTPRINT_MAP.get(row['Series'], None) or
                     cls.MPN_NR_FOOTPRINT_REGEX.apply(row['Manufacturer Part Number']))
        if footprint is None:
          raise KeyError
        new_cols[cls.KICAD_FOOTPRINT] = footprint

        new_cols[cls.INDUCTANCE] = Range.from_tolerance(
          PartsTableUtil.parse_value(row['Inductance'], 'H'),
          PartsTableUtil.parse_tolerance(row['Tolerance'])
        )
        current = PartsTableUtil.parse_value(row['Current Rating (Amps)'], 'A')
        new_cols[cls.CURRENT_RATING] = Range(-current, current)
        new_cols[cls.FREQUENCY_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Frequency - Self Resonant'], 'Hz')
        )
        new_cols[cls.DC_RESISTANCE] = Range.exact(  # TODO debug type below - it doesn't like the default type
          PartsTableUtil.parse_value(row['DC Resistance (DCR)'], 'Ohm', None) or  #type:ignore
          PartsTableUtil.parse_value(row['DC Resistance (DCR)'], 'Ohm Max')
        )

        new_cols.update(cls._parse_digikey_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_Inductors_TdkMlz.csv',
      'Digikey_Inductors_MurataDfe.csv',
      'Digikey_Inductors_TaiyoYudenNr.csv',
      'Digikey_Inductors_Shielded_BournsSRR_1005_1210_1260.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.COST], row[cls.KICAD_FOOTPRINT]]
    )

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'L', part[self.KICAD_FOOTPRINT],
      {
        '1': self.a,
        '2': self.b,
      },
      mfr=part[self.MANUFACTURER_HEADER], part=part[self.PART_NUMBER],
      value=f"{part['Inductance']}, {part['Current Rating (Amps)']}",
      datasheet=part[self.DATASHEET_HEADER]
    )
