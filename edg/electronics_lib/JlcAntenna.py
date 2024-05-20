from typing import Optional, Dict, Any

from electronics_abstract_parts import *
from .JlcPart import JlcTableSelector


class JlcAntenna(TableAntenna, JlcTableSelector, PartsTableFootprintSelector):
  FOOTPRINT_PIN_MAP = {  # no antenna-specific footprints, re-use the diode footprints which have a polarity indicator
    'Diode_SMD:D_0402_1005Metric': '1',
    'Diode_SMD:D_0603_1608Metric': '1',
    'Diode_SMD:D_0805_2012Metric': '1',
    'Diode_SMD:D_1206_3216Metric': '1',
  }

  # because the description formatting is so inconsistent, the table is just hardcoded here
  # instead of trying to parse the parts table
  PART_FREQUENCY_IMPEDANCE_POWER_FOOTPRINT_MAP = {
    'C293767': (Range(2320e6, 2580e6), Range.exact(50), Range(0, 1), 'Diode_SMD:D_1206_3216Metric'),
    # 'C486319' # requires matching circuit?
    # 'C504002' # requires matching circuit?
    # 'C504001' # requires matching circuit?
    # 'C127629': (Range(2400, 2500)*MHertz, 50*Ohm, None, 'Diode_SMD:D_1206_3216Metric'), # requires matching circuit?
    # 'C96742' # part number says 3R400G, which doesn't exist on the datasheet
    # 'C239243' # GPS antenna 10mmx3mm
  }

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Antennas':
        return None

      entry = cls.PART_FREQUENCY_IMPEDANCE_POWER_FOOTPRINT_MAP.get(row[cls.LCSC_PART_HEADER])
      if entry is None:
        return None

      new_cols: Dict[PartsTableColumn, Any] = {}
      new_cols[cls.FREQUENCY_RATING] = entry[0]
      new_cols[cls.IMPEDANCE] = entry[1]
      new_cols[cls.POWER_RATING] = entry[2]
      new_cols[cls.KICAD_FOOTPRINT] = entry[3]
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row)

  def _make_pinning(self, footprint: str) -> Dict[str, CircuitPort]:
    return {
      self.FOOTPRINT_PIN_MAP[footprint]: self.a,
    }
