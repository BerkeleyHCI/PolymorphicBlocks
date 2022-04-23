from .PassiveCapacitor import *
from .JlcFootprint import JlcFootprint


class JlcBaseDiodeTable(JlcTable):
  FOOTPRINT = PartsTableColumn(str)

  PACKAGE_FOOTPRINT_MAP = {
    'LL-34': 'Diode_SMD:D_MiniMELF',
    'SOD-123': 'Diode_SMD:D_SOD-123',
    'SOD-323': 'Diode_SMD:D_SOD-323',
    'SMA,DO-214AC': 'Diode_SMD:D_SMA',
    'SMB,DO-214AA': 'Diode_SMD:D_SMB',
    'SMC,DO-214AB': 'Diode_SMD:D_SMC',
  }


DescriptionParser = Tuple[re.Pattern,
                          Callable[[re.Match],
                                   Dict[PartsTableColumn, Any]]]
class JlcZenerTable(JlcBaseDiodeTable):
  ZENER_VOLTAGE = PartsTableColumn(Range)
  FORWARD_VOLTAGE = PartsTableColumn(Range)

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("±(\d+\.?\d*%) (\d+\.?\d*V) (\d+\.?\d*\w?A) @ (\d+\.?\d*V) (\d+\.?\d*\w?W).*"),
     lambda match: {
       JlcZenerTable.ZENER_VOLTAGE: Range.from_tolerance(PartsTableUtil.parse_value(match.group(2), 'V'),
                                                         PartsTableUtil.parse_tolerance(match.group(1)))
     }),
    (re.compile("(\d+\.?\d*V)(\(Min\))?~(\d+\.?\d*V)(\(Max\))? (\d+\.?\d*\w?A) @ (\d+\.?\d*V) (\d+\.?\d*\w?W).*"),
     lambda match: {
       JlcZenerTable.ZENER_VOLTAGE: Range(PartsTableUtil.parse_value(match.group(1), 'V'),
                                          PartsTableUtil.parse_value(match.group(3), 'V'))
     }),
  ]

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Library Type'] != 'Basic' or row['Second Category'] != 'Zener Diodes':
        return None
      footprint = cls.PACKAGE_FOOTPRINT_MAP.get(row['Package'])
      if footprint is None:
        return None

      new_cols: Optional[Dict[PartsTableColumn, Any]] = None
      for parser, match_fn in cls.DESCRIPTION_PARSERS:
        parsed_values = parser.match(row[JlcTable.DESCRIPTION])
        if parsed_values:
          new_cols = match_fn(parsed_values)
          break

      if new_cols is None:
        return None

      new_cols[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[footprint]
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.FOOTPRINT], row[cls.COST]]
    )


class JlcZenerDiode(ZenerDiode, JlcFootprint, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, *args, part: StringLike = Default(""), footprint: StringLike = Default(""), **kwargs):
    super().__init__(*args, **kwargs)
    self.actual_zener_voltage = self.Parameter(RangeExpr())
    self.actual_forward_voltage_drop = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.zener_voltage, part, footprint)

  def select_part(self, zener_voltage: Range, part_spec: str, footprint_spec: str) -> None:
    part = JlcZenerTable.table().filter(lambda row: (
        (not part_spec or part_spec == row[JlcTable.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[JlcTable.FOOTPRINT]) and
        row[JlcZenerTable.ZENER_VOLTAGE].fuzzy_in(zener_voltage)
    )).first(f"no zener diodes in Vz={zener_voltage} V")

    self.assign(self.actual_zener_voltage, part[JlcZenerTable.ZENER_VOLTAGE])

    self.footprint(
      'D', part[JlcTable.FOOTPRINT],
      {
        '1': self.cathode,
        '2': self.anode,
      },
      mfr=part[JlcTable.MANUFACTURER], part=part[JlcTable.PART_NUMBER],
      value=part[JlcTable.DESCRIPTION],
      datasheet=part[JlcTable.DATASHEETS]
    )
    self.assign(self.lcsc_part, part[JlcTable.JLC_PART_NUMBER])
