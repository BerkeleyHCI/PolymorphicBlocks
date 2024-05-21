import re
from typing import Optional, Dict, Any, List
from ..electronics_abstract_parts import *
from .JlcPart import JlcPart, JlcTableBase, DescriptionParser


class JlcOscillator_Device(InternalSubcircuit, Block):
  """Base oscillator device definition, that takes in the part data from the containing part table.
  Defines a standard interface, and specifies the footprint here."""
  FOOTPRINT: str

  @init_in_parent
  def __init__(self, in_kicad_part: StringLike, in_kicad_value: StringLike, in_kicad_datasheet: StringLike,
               in_lcsc_part: StringLike, in_actual_basic_part: BoolLike):
    super().__init__()
    self.gnd = self.Port(Ground.empty())
    self.vcc = self.Port(VoltageSink.empty())
    self.out = self.Port(DigitalSource.empty())

    self.in_kicad_part = self.ArgParameter(in_kicad_part)
    self.in_kicad_value = self.ArgParameter(in_kicad_value)
    self.in_kicad_datasheet = self.ArgParameter(in_kicad_datasheet)

    self.in_lcsc_part = self.ArgParameter(in_lcsc_part)
    self.in_actual_basic_part = self.ArgParameter(in_actual_basic_part)


class Sg8101cg_Device(JlcOscillator_Device, JlcPart, FootprintBlock):
  FOOTPRINT = 'Crystal:Crystal_SMD_2520-4Pin_2.5x2.0mm'  # doesn't perfectly match datasheet recommended geometry
  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.gnd.init_from(Ground())
    self.vcc.init_from(VoltageSink(voltage_limits=(1.62, 3.62)*Volt,
                                   current_draw=(0.0003, 3.5)*mAmp))  # 1.8 stdby typ to 3.3 max
    self.out.init_from(DigitalSource.from_supply(self.gnd, self.vcc,
                                                 0*mAmp(tol=0)))

    self.footprint(
      'X', self.FOOTPRINT,
      {
        '1': self.vcc,  # ST/OE pin
        '2': self.gnd,
        '3': self.out,
        '4': self.vcc,
      },
      part=self.in_kicad_part, value=self.in_kicad_value, datasheet=self.in_kicad_datasheet)

    self.assign(self.lcsc_part, self.in_lcsc_part)
    self.assign(self.actual_basic_part, self.in_actual_basic_part)


class JlcOscillator(TableOscillator, JlcTableBase, Block):
  SERIES_DEVICE_MAP = {
    'SG-8101CG': Sg8101cg_Device,
  }
  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(±\S+ppm) .* (\S+MHz) .* Pre-programmed Oscillators .*"),
     lambda match: {
       TableOscillator.FREQUENCY: PartParserUtil.parse_abs_tolerance(
         match.group(1), PartParserUtil.parse_value(match.group(2), 'Hz'), 'Hz'),
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] not in ('Pre-programmed Oscillators', 'Oscillators'):
        return None

      footprint = None
      for series, device_cls in cls.SERIES_DEVICE_MAP.items():
        if row[cls.PART_NUMBER_COL].startswith(series):
          assert footprint is None, f"multiple footprint rules match {row[cls.PART_NUMBER_COL]}"
          footprint = device_cls.FOOTPRINT
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

  def _row_generate(self, row: PartsTableRow) -> None:
    for series, device_cls in self.SERIES_DEVICE_MAP.items():
      if row[self.PART_NUMBER_COL].startswith(series):
        self.device = self.Block(device_cls(
          row[self.PART_NUMBER_COL], row[self.DESCRIPTION_COL], row[self.DATASHEET_COL],
          row[self.LCSC_PART_HEADER], row[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE
        ))
        self.connect(self.pwr, self.device.vcc)
        self.connect(self.gnd, self.device.gnd)
        self.connect(self.out, self.device.out)
        self.cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
