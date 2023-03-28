from typing import Optional, cast, Dict

from electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprint
from .Categories import *
from .StandardPinningFootprint import StandardPinningFootprint


@abstract_block
class FerriteBead(PassiveComponent, KiCadImportableBlock):
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name in ('Device:L_Ferrite', 'Device:L_Ferrite_Small')
    return {'1': self.a, '2': self.b}

  @init_in_parent
  def __init__(self, *, current: RangeLike = Default(RangeExpr.ZERO),
               hf_impedance: RangeLike = Default(RangeExpr.ALL),
               dc_resistance: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())

    self.current = self.ArgParameter(current)  # operating current range
    self.hf_impedance = self.ArgParameter(hf_impedance)
    self.dc_resistance = self.ArgParameter(dc_resistance)
    self.actual_current_rating = self.Parameter(RangeExpr())
    self.actual_hf_impedance = self.Parameter(RangeExpr())
    self.actual_dc_resistance = self.Parameter(RangeExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>current rating:</b> ", DescriptionString.FormatUnits(self.actual_current_rating, "A"),
      " <b>of operating</b> ", DescriptionString.FormatUnits(self.current, "A"), "\n",
      "<b>HF impedance:</b> ", DescriptionString.FormatUnits(self.actual_hf_impedance, "Ω"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.hf_impedance, "Ω"), "\n",
      "<b>DC resistance:</b> ", DescriptionString.FormatUnits(self.actual_dc_resistance, "Ω"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.dc_resistance, "Ω")
    )


@non_library
class FerriteBeadStandardPinning(FerriteBead, StandardPinningFootprint[FerriteBead]):
  FOOTPRINT_PINNING_MAP = {
    (
      'Inductor_SMD:L_0201_0603Metric',
      'Inductor_SMD:L_0402_1005Metric',
      'Inductor_SMD:L_0603_1608Metric',
      'Inductor_SMD:L_0805_2012Metric',
      'Inductor_SMD:L_1206_3216Metric',
      'Inductor_SMD:L_1210_3225Metric',
      'Inductor_SMD:L_1812_4532Metric',
      'Inductor_SMD:L_2010_5025Metric',
      'Inductor_SMD:L_2512_6332Metric',
    ): lambda block: {
      '1': block.a,
      '2': block.b,
    },
  }


from .SmdStandardPackage import SmdStandardPackage  # TODO should be a separate leaf-class mixin
@non_library
class TableFerriteBead(SmdStandardPackage, FerriteBeadStandardPinning, PartsTableFootprint, GeneratorBlock):
  CURRENT_RATING = PartsTableColumn(Range)
  HF_IMPEDANCE = PartsTableColumn(Range)
  DC_RESISTANCE = PartsTableColumn(Range)

  SMD_FOOTPRINT_MAP = {
    '01005': None,
    '0201': 'Inductor_SMD:L_0201_0603Metric',
    '0402': 'Inductor_SMD:L_0402_1005Metric',
    '0603': 'Inductor_SMD:L_0603_1608Metric',
    '0805': 'Inductor_SMD:L_0805_2012Metric',
    '1206': 'Inductor_SMD:L_1206_3216Metric',
    '1210': 'Inductor_SMD:L_1210_3225Metric',
    '1806': None,
    '1812': 'Inductor_SMD:L_1812_4532Metric',
    '2010': 'Inductor_SMD:L_2010_5025Metric',
    '2512': 'Inductor_SMD:L_2512_6332Metric',
  }

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.current, self.hf_impedance, self.dc_resistance,
                   self.part, self.footprint_spec, self.smd_min_package)

  def select_part(self, current: Range, hf_impedance: Range, dc_resistance: Range,
                  part_spec: str, footprint_spec: str, smd_min_package: str) -> None:
    minimum_invalid_footprints = SmdStandardPackage.get_smd_packages_below(smd_min_package, self.SMD_FOOTPRINT_MAP)
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        (row[self.KICAD_FOOTPRINT] not in minimum_invalid_footprints) and
        current.fuzzy_in(row[self.CURRENT_RATING]) and
        row[self.HF_IMPEDANCE].fuzzy_in(hf_impedance) and
        row[self.DC_RESISTANCE].fuzzy_in(dc_resistance)
    )).sort_by(self._row_sort_by)
    part = parts.first(f"no matching ferrite bead")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))
    self.assign(self.actual_current_rating, part[self.CURRENT_RATING])
    self.assign(self.actual_hf_impedance, part[self.HF_IMPEDANCE])
    self.assign(self.actual_dc_resistance, part[self.DC_RESISTANCE])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'FB', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )


class SeriesPowerFerriteBead(DiscreteApplication, KiCadImportableBlock):
  """Series ferrite bead for power applications"""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name in ('Device:L_Ferrite', 'Device:L_Ferrite_Small')
    return {'1': self.pwr_in, '2': self.pwr_out}

  @init_in_parent
  def __init__(self, hf_impedance: RangeLike = Default(RangeExpr.ALL),
               dc_resistance: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()

    self.pwr_out = self.Port(VoltageSource.empty(), [Output])  # forward declaration
    self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])  # forward declaration

    self.fb = self.Block(FerriteBead(
      current=self.pwr_out.link().current_drawn,
      hf_impedance=hf_impedance,
      dc_resistance=dc_resistance
    ))
    self.connect(self.pwr_in, self.fb.a.adapt_to(VoltageSink(
      voltage_limits=Range.all(),  # ideal
      current_draw=self.pwr_out.link().current_drawn
    )))
    self.connect(self.pwr_out, self.fb.b.adapt_to(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,  # ignore voltage drop
      current_limits=self.fb.actual_current_rating
    )))

  def connected(self, pwr_in: Optional[Port[VoltageLink]] = None, pwr_out: Optional[Port[VoltageLink]] = None) -> \
      'SeriesPowerFerriteBead':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if pwr_in is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_in, self.pwr_in)
    if pwr_out is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_out, self.pwr_out)
    return self
