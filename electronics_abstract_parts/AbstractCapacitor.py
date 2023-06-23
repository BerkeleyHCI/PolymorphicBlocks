import re
from abc import abstractmethod
from typing import Optional, cast, Dict, Any, List, Tuple, Mapping
import math

from electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow, PartsTable
from .PartsTablePart import PartsTableFootprintSelector
from .Categories import *
from .StandardFootprint import StandardFootprint


@abstract_block
class UnpolarizedCapacitor(PassiveComponent):
  """Base type for a capacitor, that defines its parameters and without ports (since capacitors can be polarized)"""
  @init_in_parent
  def __init__(self, capacitance: RangeLike, voltage: RangeLike, *,
               voltage_rating_derating: FloatLike = 0.5,
               exact_capacitance: BoolLike = False) -> None:
    super().__init__()

    self.capacitance = self.ArgParameter(capacitance)
    self.voltage = self.ArgParameter(voltage)  # defined as operating voltage range

    # this is the scaling derating factor applied to the rated voltage spec
    # eg, a value of 0.5 would mean the labeled rated voltage must be 2x the actual voltage
    # 0.5 is the general rule of thumb for ceramic capacitors: https://www.sparkfun.com/news/1271
    # this does not apply to capacitance derating, which is handled separately
    self.voltage_rating_derating = self.ArgParameter(voltage_rating_derating)

    # indicates whether the capacitance is exact (True) or nominal (False - typical case)
    # in particular, nominal capacitance does not capacitance derate
    self.exact_capacitance = self.ArgParameter(exact_capacitance)

    self.actual_capacitance = self.Parameter(RangeExpr())
    self.actual_voltage_rating = self.Parameter(RangeExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>capacitance:</b> ", DescriptionString.FormatUnits(self.actual_capacitance, "F"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.capacitance, "F"), "\n",
      "<b>voltage rating:</b> ", DescriptionString.FormatUnits(self.actual_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.voltage, "V")
    )

@abstract_block
class Capacitor(UnpolarizedCapacitor, KiCadInstantiableBlock):
  """Polarized capacitor, which we assume will be the default"""
  CAPACITOR_REGEX = re.compile("^" + f"([\d.{PartParserUtil.SI_PREFIXES}]+(?:\s*[{PartParserUtil.SI_PREFIXES}])?)\s*F?" +
                               "\s*" + "((?:\+-|\+/-|±)?\s*[\d.]+\s*%)?" +
                               "\s*" + f"([\d.{PartParserUtil.SI_PREFIXES}]+(?:\s*[{PartParserUtil.SI_PREFIXES}])?\s*V)" + "$")
  CAPACITOR_DEFAULT_TOL = 0.20  # TODO this should be unified elsewhere

  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name in ('Device:C', 'Device:C_Small', 'Device:C_Polarized', 'Device:C_Polarized_Small')
    return {'1': self.pos, '2': self.neg}

  @classmethod
  def parse_capacitor(cls, value: str) -> Tuple[Range, Range]:
    match = cls.CAPACITOR_REGEX.match(value)
    assert match is not None, f"could not parse capacitor from value '{value}'"
    center = PartParserUtil.parse_value(match.group(1), '')
    voltage = PartParserUtil.parse_value(match.group(3), 'V')
    if match.group(2) is not None:
      tolerance = PartParserUtil.parse_tolerance(match.group(2))
    else:
      tolerance = (-cls.CAPACITOR_DEFAULT_TOL, cls.CAPACITOR_DEFAULT_TOL)
    return (Range.from_tolerance(center, tolerance), Range.zero_to_upper(voltage))

  @classmethod
  def block_from_symbol(cls, symbol_name: str, properties: Mapping[str, str]) -> 'Capacitor':
    return Capacitor(*cls.parse_capacitor(properties['Value']))

  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.pos = self.Port(Passive.empty())
    self.neg = self.Port(Passive.empty())


@non_library
class CapacitorStandardFootprint(Capacitor, StandardFootprint[Capacitor]):
  REFDES_PREFIX = 'C'

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

  SMD_FOOTPRINT_MAP = {
    '01005': None,
    '0201': 'Capacitor_SMD:C_0201_0603Metric',
    '0402': 'Capacitor_SMD:C_0402_1005Metric',
    '0603': 'Capacitor_SMD:C_0603_1608Metric',
    '0805': 'Capacitor_SMD:C_0805_2012Metric',
    '1206': 'Capacitor_SMD:C_1206_3216Metric',
    '1210': 'Capacitor_SMD:C_1210_3225Metric',
    '1806': None,
    '1812': 'Capacitor_SMD:C_1812_4532Metric',
    '2010': None,
    '2512': 'Capacitor_SMD:C_2512_6332Metric',
  }


@non_library
class TableCapacitor(Capacitor):
  """Abstract table-based capacitor, providing some interface column definitions.
  DO NOT USE DIRECTLY - this provides no selection logic implementation."""
  CAPACITANCE = PartsTableColumn(Range)
  NOMINAL_CAPACITANCE = PartsTableColumn(float)  # nominal capacitance, even with asymmetrical tolerances
  VOLTAGE_RATING = PartsTableColumn(Range)


@non_library
class TableDeratingCapacitor(CapacitorStandardFootprint, TableCapacitor, PartsTableFootprintSelector):
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
  def __init__(self, *args, single_nominal_capacitance: RangeLike = (0, 22)*uFarad, **kwargs):
    super().__init__(*args, **kwargs)
    self.single_nominal_capacitance = self.ArgParameter(single_nominal_capacitance)
    self.generator_param(self.capacitance, self.voltage, self.single_nominal_capacitance,
                         self.voltage_rating_derating, self.exact_capacitance)

    self.actual_derated_capacitance = self.Parameter(RangeExpr())

  def _row_filter(self, row: PartsTableRow) -> bool:
    derated_voltage = self.get(self.voltage) / self.get(self.voltage_rating_derating)
    return super()._row_filter(row) and \
      derated_voltage.fuzzy_in(row[self.VOLTAGE_RATING]) and \
      Range.exact(row[self.NOMINAL_CAPACITANCE]).fuzzy_in(self.get(self.single_nominal_capacitance))

  def _table_postprocess(self, table: PartsTable) -> PartsTable:
    def add_derated_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if not self.get(self.exact_capacitance):
        derated = row[self.CAPACITANCE]
      elif self.get(self.voltage).upper < self.DERATE_MIN_VOLTAGE:  # zero derating at low voltages
        derated = row[self.CAPACITANCE]
      elif row[self.NOMINAL_CAPACITANCE] <= self.DERATE_MIN_CAPACITANCE:  # don't derate below 1uF
        derated = row[self.CAPACITANCE]
      else:  # actually derate
        factor = 1 - row[self.VOLTCO] * (self.get(self.voltage).upper - 3.6)
        if factor < self.DERATE_LOWEST:
          factor = self.DERATE_LOWEST
        derated = row[self.CAPACITANCE] * Range(factor, 1)

      count = math.ceil(self.get(self.capacitance).lower / derated.lower)
      derated_parallel_capacitance = derated * count
      if not derated_parallel_capacitance.fuzzy_in(self.get(self.capacitance)):  # not satisfying spec, remove row
        return None

      return {self.DERATED_CAPACITANCE: derated,
              self.PARALLEL_COUNT: count,
              self.PARALLEL_DERATED_CAPACITANCE: derated_parallel_capacitance,
              self.PARALLEL_CAPACITANCE: row[self.CAPACITANCE] * count}

    return table.map_new_columns(add_derated_row).filter(lambda row: (
        row[self.PARALLEL_DERATED_CAPACITANCE] in self.get(self.capacitance)
    ))

  def _row_generate(self, row: PartsTableRow) -> None:
    if row[self.PARALLEL_COUNT] == 1:
      super()._row_generate(row)  # creates the footprint
      self.assign(self.actual_voltage_rating, row[self.VOLTAGE_RATING])
      self.assign(self.actual_capacitance, row[self.CAPACITANCE])
      self.assign(self.actual_derated_capacitance, row[self.DERATED_CAPACITANCE])
    else:
      self.assign(self.actual_part, f"{row[self.PARALLEL_COUNT]}x {row[self.PART_NUMBER_COL]}")
      self.assign(self.actual_voltage_rating, row[self.VOLTAGE_RATING])
      self.assign(self.actual_capacitance, row[self.PARALLEL_CAPACITANCE])
      self.assign(self.actual_derated_capacitance, row[self.PARALLEL_DERATED_CAPACITANCE])
      self._make_parallel_footprints(row)

  @abstractmethod
  def _make_parallel_footprints(self, row: PartsTableRow) -> None:
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


class DecouplingCapacitor(DiscreteApplication, KiCadImportableBlock):
  """Optionally polarized capacitor used for DC decoupling, with VoltageSink connections with voltage inference.
  Implemented as a shim block."""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name in ('Device:C', 'Device:C_Small', 'Device:C_Polarized', 'Device:C_Polarized_Small')
    return {'1': self.pwr, '2': self.gnd}

  @init_in_parent
  def __init__(self, capacitance: RangeLike, *, exact_capacitance: BoolLike = False) -> None:
    super().__init__()

    self.cap = self.Block(Capacitor(capacitance, voltage=RangeExpr(), exact_capacitance=exact_capacitance))
    self.gnd = self.Export(self.cap.neg.adapt_to(VoltageSink()), [Common])
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
