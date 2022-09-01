from electronics_model import *
from . import PartsTableFootprint, PartsTableColumn, Capacitor, PartsTableRow
from .Categories import *
from .StandardPinningFootprint import StandardPinningFootprint


@abstract_block
class Crystal(DiscreteComponent):
  @init_in_parent
  def __init__(self, frequency: RangeLike) -> None:
    """Discrete crystal component."""
    super().__init__()

    self.frequency = self.ArgParameter(frequency)
    self.actual_frequency = self.Parameter(RangeExpr())
    self.actual_capacitance = self.Parameter(FloatExpr())

    self.crystal = self.Port(CrystalPort(self.actual_frequency), [InOut])  # set by subclass
    self.gnd = self.Port(Ground(), [Common])

    self.description = DescriptionString(
      "<b>frequency:</b> ", DescriptionString.FormatUnits(self.actual_frequency, "Hz"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.frequency, "Hz"), "\n",
      "<b>capacitance:</b> ", DescriptionString.FormatUnits(self.actual_capacitance, "F")
    )

@abstract_block
class CrystalStandardPinning(Crystal, StandardPinningFootprint[Crystal]):
  FOOTPRINT_PINNING_MAP = {
    'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm': lambda block: {
      '1': block.crystal.a,
      '2': block.gnd,
      '3': block.crystal.b,
      '4': block.gnd,
    },
    'Crystal_SMD_3225-4Pin_3.2x2.5mm': lambda block: {
      '1': block.crystal.a,
      '2': block.gnd,
      '3': block.crystal.b,
      '4': block.gnd,
    },
  }


@abstract_block
class TableCrystal(CrystalStandardPinning, PartsTableFootprint, GeneratorBlock):
  FREQUENCY = PartsTableColumn(Range)
  CAPACITANCE = PartsTableColumn(float)

  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    """Discrete crystal component."""
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.frequency, self.part, self.footprint_spec)

  def select_part(self, frequency: Range, part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.FREQUENCY] in frequency
    ))
    part = parts.first(f"no crystal matching f={frequency} Hz")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, len(parts))
    self.assign(self.actual_frequency, part[self.FREQUENCY])
    self.assign(self.actual_capacitance, part[self.CAPACITANCE])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'X', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )


class OscillatorCrystal(DiscreteApplication):  # TODO rename to disambiguate from part?
  PARASITIC_CAPACITANCE = 5e-12

  # Tolerance selected using table 32 in https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf, which gives suggested
  # load cap values 18pF, 39pF, 57pF. Assume any capacitance in the center could round either way - 22pF goes to 18pF
  # or 39pF, which gives a 28% tolerance.
  # Calculation: for tolerance y and series multiplicative factor a, we need (1+y) = a(1-y)
  # which solves to y=(a-1)/(a+1)
  # Then stack an additive 10% tolerance for the capacitor tolerance, for a total 0.38 tolerance.
  # TODO this should be formalized better.
  CAPACITOR_TOLERANCE = 0.38

  @init_in_parent
  def __init__(self, frequency: RangeLike) -> None:
    """Crystal and supporting circuitry to connect it to an oscillator driver.
    Should include load capacitors."""
    super().__init__()

    self.package = self.Block(Crystal(frequency=frequency))
    self.crystal = self.Export(self.package.crystal, [InOut])
    self.gnd = self.Export(self.package.gnd, [Common])

    cap_model = Capacitor(
      capacitance=(
        (self.package.actual_capacitance - self.PARASITIC_CAPACITANCE) * 2 * (1 - self.CAPACITOR_TOLERANCE),
        (self.package.actual_capacitance - self.PARASITIC_CAPACITANCE) * 2 * (1 + self.CAPACITOR_TOLERANCE)),
      voltage=self.crystal.link().drive_voltage
    )
    self.cap_a = self.Block(cap_model)
    self.cap_b = self.Block(cap_model)
    self.connect(self.cap_a.pos, self.crystal.a)
    self.connect(self.cap_b.pos, self.crystal.b)
    self.connect(self.gnd, self.cap_a.neg.adapt_to(Ground()),
                 self.cap_b.neg.adapt_to(Ground()))
