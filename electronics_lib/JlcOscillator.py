import re
from typing import Optional, Dict, Any, List
from electronics_abstract_parts import *
from .JlcPart import JlcPart, JlcTablePart, DescriptionParser


class JlcOscillator_Device(JlcPart, FootprintBlock, GeneratorBlock):
  """Parameter-defined device, other than the fixed oscillator refdes prefix.
  TODO: can this be shared infrastructure?"""
  @init_in_parent
  def __init__(self, kicad_pins: ArrayStringLike, kicad_footprint: StringLike,
               kicad_part: StringLike, kicad_value: StringLike, kicad_datasheet: StringLike,
               lcsc_part: StringLike, actual_basic_part: StringLike):
    super().__init__()
    self.ports = self.Port(Vector(Passive()))
    self.kicad_footprint = self.ArgParameter(kicad_footprint)
    self.kicad_part = self.ArgParameter(kicad_part)
    self.kicad_value = self.ArgParameter(kicad_value)
    self.kicad_datasheet = self.ArgParameter(kicad_datasheet)

    self.assign(self.lcsc_part, lcsc_part)
    self.assign(self.actual_basic_part, actual_basic_part)

    self.generator(self.generate, kicad_pins)

  def generate(self, kicad_pins: List[str]):
    mapping = {pin_name: self.ports.append_elt(Passive(), pin_name)
               for pin_name in kicad_pins}
    self.footprint('X', self.kicad_footprint, mapping,
                   part=self.kicad_part, value=self.kicad_value, datasheet=self.kicad_datasheet)


class JlcOscillator(TableOscillator, JlcTablePart, Block):
  """TODO: this technically shouldn't be a JlcPart?"""
  SERIES_PACKAGE_FOOTPRINT_PIN_MAP = {
    ('SG–8101CG', 'SMD2520-4P'): ('Crystal:Crystal_SMD_2520-4Pin_2.5x2.0mm',
                                  lambda block: {
                                    '1': block.pwr, '2': block.gnd, '3': block.out, '4': block.pwr
                                  }),
  }
  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(±\S+ppm) .* (\S+MHz) .*Pre-programmed Oscillators .*"),
     lambda match: {
       TableOscillator.FREQUENCY: Range.from_tolerance(PartParserUtil.parse_value(match.group(2), 'Hz'),
                                                       PartParserUtil.parse_tolerance(match.group(1))),
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Crystals':
        return None

      footprint = None
      for (series, package), (map_footprint, map_pinning) in cls.SERIES_PACKAGE_FOOTPRINT_PIN_MAP.items():
        if row[cls.PART_NUMBER_COL].startswith(series) and row[cls._PACKAGE_HEADER] == package:
          assert footprint is None, f"multiple footprint rules match {row[cls.PART_NUMBER_COL]}"
          footprint = map_footprint
      if footprint is None:
        return None

      new_cols = cls.parse_full_description(row[cls.DESCRIPTION_COL], cls.DESCRIPTION_PARSERS)
      if new_cols is None:
        return None

      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]
    )

  def _implementation(self, row: PartsTableRow) -> None:
    for (series, package), (map_footprint, map_pinning) in self.SERIES_PACKAGE_FOOTPRINT_PIN_MAP.items():
      if row[self.PART_NUMBER_COL].startswith(series) and row[self._PACKAGE_HEADER] == package:
        # TODO implement me
        pinning = map_pinning(self)
        self.device = self.Block(JlcOscillator_Device(
          list(pinning.keys()), row[self.KICAD_FOOTPRINT],
          row[self.PART_NUMBER_COL], row[self.DESCRIPTION_COL], row[self.DATASHEET_COL],
          row[self.LCSC_PART_HEADER], row[self.BASIC_PART_HEADER]
        ))
        self.cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)

