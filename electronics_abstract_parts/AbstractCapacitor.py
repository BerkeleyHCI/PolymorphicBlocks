from abc import abstractmethod
from typing import Optional, cast, Dict, Any, List
import math

from electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow, PartsTable
from .PartsTablePart import PartsTableFootprint
from .Categories import *
from .StandardPinningFootprint import StandardPinningFootprint


@abstract_block
class UnpolarizedCapacitor(PassiveComponent):
  """Base type for a capacitor, that defines its parameters and without ports (since capacitors can be polarized)"""
  @init_in_parent
  def __init__(self, capacitance: RangeLike, voltage: RangeLike) -> None:
    super().__init__()

    self.capacitance = self.ArgParameter(capacitance)
    self.voltage = self.ArgParameter(voltage)  # defined as operating voltage range

    self.actual_capacitance = self.Parameter(RangeExpr())
    self.actual_voltage_rating = self.Parameter(RangeExpr())

    self.description = DescriptionString(
      "<b>capacitance:</b> ", DescriptionString.FormatUnits(self.actual_capacitance, "F"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.capacitance, "F"), "\n",
      "<b>voltage rating:</b> ", DescriptionString.FormatUnits(self.actual_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.voltage, "V")
    )

@abstract_block
class Capacitor(UnpolarizedCapacitor):
  """Polarized capacitor, which we assume will be the default"""
  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.pos = self.Port(Passive.empty())
    self.neg = self.Port(Passive.empty())


@abstract_block
class CapacitorStandardPinning(Capacitor, StandardPinningFootprint[Capacitor]):
  # IMPORTANT! DummyFootprint doesn't use this, it will break on anything that isn't this pinning
  FOOTPRINT_PINNING_MAP = {
    (
      'Capacitor_SMD:C_0201_0603Metric',
      'Capacitor_SMD:C_0402_1005Metric',
      'Capacitor_SMD:C_0603_1608Metric',
      'Capacitor_SMD:C_0805_2012Metric',
      'Capacitor_SMD:C_1206_3216Metric',
      'Capacitor_SMD:C_1210_3225Metric',
      'Capacitor_SMD:C_1812_4532Metric',
      'Capacitor_SMD:C_2512_6332Metric',
    ): lambda block: {
      '1': block.pos,
      '2': block.neg,
    },
  }


@abstract_block
class TableCapacitor(Capacitor):
  """Abstract table-based capacitor, providing some interface column definitions.
  DO NOT USE DIRECTLY - this provides no selection logic implementation."""
  CAPACITANCE = PartsTableColumn(Range)
  NOMINAL_CAPACITANCE = PartsTableColumn(float)  # nominal capacitance, even with asymmetrical tolerances
  VOLTAGE_RATING = PartsTableColumn(Range)


@abstract_block
class TableDeratingCapacitor(CapacitorStandardPinning, TableCapacitor, PartsTableFootprint, GeneratorBlock):
  """Abstract table-based capacitor with derating based on a part-part voltage coefficient."""
  VOLTCO = PartsTableColumn(float)
  DERATED_CAPACITANCE = PartsTableColumn(Range)

  PARALLEL_COUNT = PartsTableColumn(int)
  PARALLEL_CAPACITANCE = PartsTableColumn(Range)
  PARALLEL_DERATED_CAPACITANCE = PartsTableColumn(Range)

  # default derating parameters
  DERATE_MIN_VOLTAGE = 3.6  # voltage at which derating is zero
  DERATE_MIN_CAPACITANCE = 1.0e-6
  DERATE_LOWEST = 0.2  # floor for maximum derating factor
  # LOOSELY approximated from https://www.maximintegrated.com/en/design/technical-documents/tutorials/5/5527.html

  @init_in_parent
  def __init__(self, *args, single_nominal_capacitance: RangeLike = Default((0, 22)*uFarad), **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.capacitance, self.voltage, single_nominal_capacitance,
                   self.part, self.footprint_spec)

    self.actual_derated_capacitance = self.Parameter(RangeExpr())

    # TODO there should be a way to add the part number here without duplicating
    # the description string in the main superclass

  def select_part(self, capacitance: Range, voltage: Range, single_nominal_capacitance: Range,
                  part_spec: str, footprint_spec: str) -> None:
    # Pre-filter out by the static parameters
    # Note that we can't filter out capacitance before derating
    prefiltererd_parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        voltage.fuzzy_in(row[self.VOLTAGE_RATING]) and
        Range.exact(row[self.NOMINAL_CAPACITANCE]).fuzzy_in(single_nominal_capacitance)
    ))

    def add_derated_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if voltage.upper < self.DERATE_MIN_VOLTAGE:  # zero derating at low voltages
        derated = row[self.CAPACITANCE]
      elif row[self.NOMINAL_CAPACITANCE] <= self.DERATE_MIN_CAPACITANCE:  # don't derate below 1uF
        derated = row[self.CAPACITANCE]
      else:  # actually derate
        factor = 1 - row[self.VOLTCO] * (voltage.upper - 3.6)
        if factor < self.DERATE_LOWEST:
          factor = self.DERATE_LOWEST
        derated = row[self.CAPACITANCE] * Range(factor, 1)

      return {self.DERATED_CAPACITANCE: derated}

    derated_parts = prefiltererd_parts.map_new_columns(add_derated_row)

    # If the min required capacitance is above the highest post-derating minimum capacitance, use the parts table.
    # An empty parts table handles the case where it's below the minimum or does not match within a series.
    derated_max_min_capacitance = max(derated_parts.map(lambda row: row[self.DERATED_CAPACITANCE].lower))

    if capacitance.lower <= derated_max_min_capacitance:
      self._make_single_capacitor(derated_parts, capacitance, voltage)
    else:  # Otherwise, generate multiple capacitors
      self._make_parallel_capacitors(derated_parts, capacitance, voltage)

  def _make_single_capacitor(self, derated_parts: PartsTable, capacitance: Range, voltage: Range):
    parts = derated_parts.filter(lambda row: (
        row[self.DERATED_CAPACITANCE] in capacitance
    ))
    part = parts.first(f"no single capacitor in {capacitance} F, {voltage} V")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))
    self.assign(self.actual_voltage_rating, part[self.VOLTAGE_RATING])
    self.assign(self.actual_capacitance, part[self.CAPACITANCE])
    self.assign(self.actual_derated_capacitance, part[self.DERATED_CAPACITANCE])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'C', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )

  def _make_parallel_capacitors(self, derated_parts: PartsTable, capacitance: Range, voltage: Range):
    def add_parallel_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      count = math.ceil(capacitance.lower / row[self.DERATED_CAPACITANCE].lower)
      derated_parallel_capacitance = row[self.DERATED_CAPACITANCE] * count
      if not derated_parallel_capacitance.fuzzy_in(capacitance):  # not satisfying spec - filter here
        return None

      new_cols: Dict[PartsTableColumn, Any] = {}
      new_cols[self.PARALLEL_COUNT] = count
      new_cols[self.PARALLEL_DERATED_CAPACITANCE] = derated_parallel_capacitance
      new_cols[self.PARALLEL_CAPACITANCE] = row[self.CAPACITANCE] * count
      return new_cols

    parts = derated_parts.map_new_columns(
      add_parallel_row
    ).sort_by(self._parallel_sort_criteria)
    part = parts.first(f"no parallel capacitor in {capacitance} F, {voltage} V")

    self.assign(self.actual_part, f"{part[self.PARALLEL_COUNT]}x {part[self.PART_NUMBER_COL]}")
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))
    self.assign(self.actual_voltage_rating, part[self.VOLTAGE_RATING])
    self.assign(self.actual_capacitance, part[self.PARALLEL_CAPACITANCE])
    self.assign(self.actual_derated_capacitance, part[self.PARALLEL_DERATED_CAPACITANCE])

    self._make_parallel_footprints(part)

  def _parallel_sort_criteria(self, row: PartsTableRow) -> List:
    """Provides a hook to allow re-sorting of parallel caps."""
    return [row[self.PARALLEL_COUNT]]

  @abstractmethod
  def _make_parallel_footprints(self, part: PartsTableRow) -> None:
    """Given a selected part (row), creates the parallel internal capacitors. Implement me."""
    ...


class DummyCapacitorFootprint(DummyDevice, Capacitor, FootprintBlock):
  """Dummy capacitor that takes in all its parameters (footprint, value, etc) and does not do any computation.
  Used as the leaf block for generating parallel capacitors.

  TODO: use footprint table?
  """

  @init_in_parent
  def __init__(self, footprint: StringLike = "", manufacturer: StringLike = "", part_number: StringLike = "",
               value: StringLike = "",
               *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.footprint(
      'C', footprint,
      {
        '1': self.pos,
        '2': self.neg,
      },
      mfr=manufacturer, part=part_number,
      value=value
    )


class DecouplingCapacitor(DiscreteApplication):
  """Optionally polarized capacitor used for DC decoupling, with VoltageSink connections with voltage inference.
  Implemented as a shim block."""
  @init_in_parent
  def __init__(self, capacitance: RangeLike) -> None:
    super().__init__()

    self.cap = self.Block(Capacitor(capacitance, voltage=RangeExpr()))
    self.gnd = self.Export(self.cap.neg.adapt_to(Ground()), [Common])
    self.pwr = self.Export(self.cap.pos.adapt_to(VoltageSink(
      voltage_limits=(self.cap.actual_voltage_rating + self.gnd.link().voltage).hull(self.gnd.link().voltage),
      current_draw=0*Amp(tol=0)
    )), [Power])

    self.assign(self.cap.voltage, self.pwr.link().voltage - self.gnd.link().voltage)

    # TODO there should be a way to forward the description string of the inner element

  def connected(self, gnd: Optional[Port[VoltageLink]] = None, pwr: Optional[Port[VoltageLink]] = None) -> \
      'DecouplingCapacitor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if gnd is not None:
      cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
    if pwr is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr, self.pwr)
    return self
