from typing import Optional, cast, Dict

from ..electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprintSelector
from .Categories import *
from .StandardFootprint import StandardFootprint


@abstract_block
class FerriteBead(PassiveComponent, KiCadImportableBlock):
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name in ('Device:L_Ferrite', 'Device:L_Ferrite_Small')
    return {'1': self.a, '2': self.b}

  @init_in_parent
  def __init__(self, *, current: RangeLike = RangeExpr.ZERO,
               hf_impedance: RangeLike = RangeExpr.ALL,
               dc_resistance: RangeLike = RangeExpr.ALL) -> None:
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
class FerriteBeadStandardFootprint(FerriteBead, StandardFootprint[FerriteBead]):
  REFDES_PREFIX = 'FB'

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


@non_library
class TableFerriteBead(FerriteBeadStandardFootprint, PartsTableFootprintSelector):
  CURRENT_RATING = PartsTableColumn(Range)
  HF_IMPEDANCE = PartsTableColumn(Range)
  DC_RESISTANCE = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.current, self.hf_impedance, self.dc_resistance)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      self.get(self.current).fuzzy_in(row[self.CURRENT_RATING]) and \
      row[self.HF_IMPEDANCE].fuzzy_in(self.get(self.hf_impedance)) and \
      row[self.DC_RESISTANCE].fuzzy_in(self.get(self.dc_resistance))

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_current_rating, row[self.CURRENT_RATING])
    self.assign(self.actual_hf_impedance, row[self.HF_IMPEDANCE])
    self.assign(self.actual_dc_resistance, row[self.DC_RESISTANCE])


class SeriesPowerFerriteBead(DiscreteApplication, KiCadImportableBlock):
  """Series ferrite bead for power applications"""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name in ('Device:L_Ferrite', 'Device:L_Ferrite_Small')
    return {'1': self.pwr_in, '2': self.pwr_out}

  @init_in_parent
  def __init__(self, hf_impedance: RangeLike = RangeExpr.ALL,
               dc_resistance: RangeLike = RangeExpr.ALL) -> None:
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
