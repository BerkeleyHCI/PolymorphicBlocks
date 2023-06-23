from typing import Optional, cast

from electronics_model import *
from .Categories import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprint, PartsTableFootprintSelector
from .StandardFootprint import StandardFootprint


@abstract_block
class Fuse(InternalSubcircuit, Block):
  @init_in_parent
  def __init__(self, trip_current: RangeLike, *, hold_current: RangeLike = RangeExpr.ALL,
               voltage: RangeLike = RangeExpr.ZERO) -> None:
    """Model-wise, equivalent to a VoltageSource|Sink passthrough, with a trip rating."""
    super().__init__()

    self.a = self.Port(Passive())
    self.b = self.Port(Passive())

    self.trip_current = self.ArgParameter(trip_current)  # current at which this will trip
    self.actual_trip_current = self.Parameter(RangeExpr())
    self.hold_current = self.ArgParameter(hold_current)  # current within at which this will NOT trip
    self.actual_hold_current = self.Parameter(RangeExpr())
    self.voltage = self.ArgParameter(voltage)  # operating voltage
    self.actual_voltage_rating = self.Parameter(RangeExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>trip current:</b> ", DescriptionString.FormatUnits(self.actual_trip_current, "A"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.trip_current, "A"), "\n",
      "<b>hold current:</b> ", DescriptionString.FormatUnits(self.actual_hold_current, "A"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.hold_current, "A"), "\n",
      "<b>voltage rating:</b> ", DescriptionString.FormatUnits(self.actual_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.voltage, "V")
    )

    self.require(self.actual_trip_current.within(self.trip_current),
                 "trip current not within specified rating")
    self.require(self.actual_hold_current.within(self.hold_current),
                 "hold current not within specified rating")
    self.require(self.voltage.within(self.actual_voltage_rating),
                 "operating voltage not within rating")


@abstract_block
class PptcFuse(Fuse):
  """PPTC self-resetting fuse"""


@non_library
class FuseStandardFootprint(Fuse, StandardFootprint[Fuse]):
  REFDES_PREFIX = 'F'

  FOOTPRINT_PINNING_MAP = {
    (
      'Resistor_SMD:R_0201_0603Metric',
      'Resistor_SMD:R_0402_1005Metric',
      'Resistor_SMD:R_0603_1608Metric',
      'Resistor_SMD:R_0805_2012Metric',
      'Resistor_SMD:R_1206_3216Metric',
      'Resistor_SMD:R_1210_3225Metric',
      'Resistor_SMD:R_1812_4532Metric',
      'Resistor_SMD:R_2010_5025Metric',
      'Resistor_SMD:R_2512_6332Metric',
    ): lambda block: {
      '1': block.a,
      '2': block.b,
    },
  }

  SMD_FOOTPRINT_MAP = {
    '01005': None,
    '0201': 'Resistor_SMD:R_0201_0603Metric',
    '0402': 'Resistor_SMD:R_0402_1005Metric',
    '0603': 'Resistor_SMD:R_0603_1608Metric',
    '0805': 'Resistor_SMD:R_0805_2012Metric',
    '1206': 'Resistor_SMD:R_1206_3216Metric',
    '1210': 'Resistor_SMD:R_1210_3225Metric',
    '1806': None,
    '1812': 'Resistor_SMD:R_1812_4532Metric',
    '2010': 'Resistor_SMD:R_2010_5025Metric',
    '2512': 'Resistor_SMD:R_2512_6332Metric',
  }


@non_library
class TableFuse(FuseStandardFootprint, PartsTableFootprintSelector):
  TRIP_CURRENT = PartsTableColumn(Range)
  HOLD_CURRENT = PartsTableColumn(Range)
  VOLTAGE_RATING = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.trip_current, self.hold_current, self.voltage)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      row[self.TRIP_CURRENT].fuzzy_in(self.get(self.trip_current)) and \
      row[self.HOLD_CURRENT].fuzzy_in(self.get(self.hold_current)) and \
      self.get(self.voltage).fuzzy_in(row[self.VOLTAGE_RATING])

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_trip_current, row[self.TRIP_CURRENT])
    self.assign(self.actual_hold_current, row[self.HOLD_CURRENT])
    self.assign(self.actual_voltage_rating, row[self.VOLTAGE_RATING])


class SeriesPowerPptcFuse(Protection):
  """Series fuse for power applications"""
  @init_in_parent
  def __init__(self, trip_current: RangeLike) -> None:
    super().__init__()

    self.pwr_out = self.Port(VoltageSource.empty(), [Output])  # forward declaration
    self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])  # forward declaration

    self.fuse = self.Block(PptcFuse(
      trip_current=trip_current,
      hold_current=(self.pwr_out.link().current_drawn.upper(), float('inf')),
      voltage=self.pwr_in.link().voltage
    ))
    self.connect(self.pwr_in, self.fuse.a.adapt_to(VoltageSink(
      voltage_limits=self.fuse.actual_voltage_rating,  # TODO: eventually needs a ground ref
      current_draw=self.pwr_out.link().current_drawn
    )))
    self.connect(self.pwr_out, self.fuse.b.adapt_to(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,  # ignore voltage drop
      current_limits=(0, self.fuse.actual_hold_current.lower())
    )))

  def connected(self, pwr_in: Optional[Port[VoltageLink]] = None, pwr_out: Optional[Port[VoltageLink]] = None) -> \
      'SeriesPowerPptcFuse':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if pwr_in is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_in, self.pwr_in)
    if pwr_out is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_out, self.pwr_out)
    return self
