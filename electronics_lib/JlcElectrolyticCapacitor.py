from typing import Optional, Any, Dict, List
import re

from electronics_abstract_parts import *
from .JlcPart import DescriptionParser, JlcTableSelector


class JlcElectrolyticCapacitor(TableCapacitor, ElectrolyticCapacitor, SmdStandardPackageSelector, JlcTableSelector):
  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+F) .*(\S+V) .*(±\S+%) .*(?:([\d\.]+x[\d\.]+)mm) .*Aluminum Electrolytic Capacitors .*"),
     lambda match: {  # discard the HF impedance parameter
       TableCapacitor.NOMINAL_CAPACITANCE: PartParserUtil.parse_value(match.group(1), 'V'),
       TableCapacitor.CAPACITANCE: PartParserUtil.parse_abs_tolerance(
         match.group(3), PartParserUtil.parse_value(match.group(1), 'V'), 'V'),
       TableCapacitor.VOLTAGE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'V')),

       SmdStandardPackageSelector.KICAD_FOOTPRINT: f"Capacitor_SMD:CP_Elec_{match.group(4)}",
     }),
  ]

  @init_in_parent
  def __init__(self, *args, capacitance_minimum_size: BoolLike = True, **kwargs):
    super().__init__(*args, **kwargs)
    self.capacitance_minimum_size = self.ArgParameter(capacitance_minimum_size)
    self.generator_param(self.capacitance_minimum_size)

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Aluminum Electrolytic Capacitors - SMD':
        return None

      new_cols = {}

      desc_cols = cls.parse_full_description(row[cls.DESCRIPTION_COL], cls.DESCRIPTION_PARSERS)
      if desc_cols is not None:
        new_cols.update(desc_cols)
      else:
        return None

      if new_cols[cls.KICAD_FOOTPRINT] not in cls._footprint_pinning_map():
        return None

      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row)
