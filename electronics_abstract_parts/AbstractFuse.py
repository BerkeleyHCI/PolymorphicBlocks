from electronics_model import *
from .Categories import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprint
from .StandardPinningFootprint import StandardPinningFootprint


@abstract_block
class Fuse(DiscreteComponent, DiscreteApplication):
  @init_in_parent
  def __init__(self, trip_current: RangeLike, *, hold_current: RangeLike = Default(RangeExpr.ALL),
               voltage: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    """Model-wise, equivalent to a VoltageSource|Sink passthrough, with a trip rating."""
    super().__init__()

    self.trip_current = self.ArgParameter(trip_current)  # current at which this will trip
    self.actual_trip_current = self.Parameter(RangeExpr())

    self.hold_current = self.ArgParameter(hold_current)  # current within at which this will NOT trip
    self.actual_hold_current = self.Parameter(RangeExpr())

    self.voltage = self.ArgParameter(voltage)  # operating voltage
    self.actual_voltage_rating = self.Parameter(RangeExpr())

    self.pwr_in = self.Port(VoltageSink.empty(), [Input])
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=(0, self.actual_trip_current.lower())
    ), [Output])  # TODO: GND port for voltage rating?
    self.pwr_in.init_from(VoltageSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.pwr_out.link().current_drawn
    ))

    self.require(self.actual_trip_current.within(self.trip_current),
                 "fuse rating not within specified rating")

    self.description = DescriptionString(
      "<b>trip current:</b> ", DescriptionString.FormatUnits(self.actual_trip_current, "A"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.trip_current, "A"), "\n",
      "<b>hold current:</b> ", DescriptionString.FormatUnits(self.actual_hold_current, "A"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.hold_current, "A"), "\n",
      "<b>voltage rating:</b> ", DescriptionString.FormatUnits(self.actual_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.voltage, "V")
    )


@abstract_block
class PptcFuse(Fuse):
  """PPTC self-resetting fuse"""


@abstract_block
class FuseStandardPinning(Fuse, StandardPinningFootprint[Fuse]):
  FOOTPRINT_PINNING_MAP = {
    (
      'Resistor_SMD:R_0201_0603Metric',
      'Resistor_SMD:R_0402_1005Metric',
      'Resistor_SMD:R_0603_1608Metric',
      'Resistor_SMD:R_0805_2012Metric',
      'Resistor_SMD:R_1206_3216Metric',
      'Resistor_SMD:R_1210_3225Metric',
      'Resistor_SMD:R_1210_3225Metric',
      'Resistor_SMD:R_1812_4532Metric',
      'Resistor_SMD:R_2010_5025Metric',
      'Resistor_SMD:R_2512_6332Metric',
    ): lambda block: {
      '1': block.a,
      '2': block.b,
    },
  }


@abstract_block
class TableFuse(FuseStandardPinning, PartsTableFootprint, GeneratorBlock):
  TRIP_CURRENT = PartsTableColumn(Range)
  HOLD_CURRENT = PartsTableColumn(Range)
  VOLTAGE_RATING = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.trip_current, self.hold_current, self.voltage, self.part, self.footprint_spec)

  def select_part(self, trip_current: Range, hold_current: Range, voltage: Range,
                  part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.TRIP_CURRENT].fuzzy_in(trip_current) and
        row[self.HOLD_CURRENT].fuzzy_in(hold_current) and
        voltage.fuzzy_in(row[self.VOLTAGE_RATING])
    ))
    part = parts.first(f"no matching part")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))
    self.assign(self.actual_trip_current, part[self.TRIP_CURRENT])
    self.assign(self.actual_hold_current, part[self.HOLD_CURRENT])
    self.assign(self.actual_voltage_rating, part[self.VOLTAGE_RATING])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'F', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )
