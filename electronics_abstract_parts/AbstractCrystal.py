from electronics_model import *
from . import PartsTableFootprintSelector, PartsTableColumn, Capacitor, PartsTableRow
from .Categories import *
from .StandardFootprint import StandardFootprint


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

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>frequency:</b> ", DescriptionString.FormatUnits(self.actual_frequency, "Hz"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.frequency, "Hz"), "\n",
      "<b>capacitance:</b> ", DescriptionString.FormatUnits(self.actual_capacitance, "F")
    )


@non_library
class CrystalStandardFootprint(Crystal, StandardFootprint[Crystal]):
  REFDES_PREFIX = 'X'

  FOOTPRINT_PINNING_MAP = {
    'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm': lambda block: {
      '1': block.crystal.xtal_in,
      '2': block.gnd,
      '3': block.crystal.xtal_out,
      '4': block.gnd,
    },
    'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm': lambda block: {
      '1': block.crystal.xtal_in,
      '2': block.gnd,
      '3': block.crystal.xtal_out,
      '4': block.gnd,
    },
  }


@non_library
class TableCrystal(CrystalStandardFootprint, PartsTableFootprintSelector):
  FREQUENCY = PartsTableColumn(Range)
  CAPACITANCE = PartsTableColumn(float)

  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    """Discrete crystal component."""
    super().__init__(*args, **kwargs)
    self.generator_param(self.frequency)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      (row[self.FREQUENCY] in self.get(self.frequency))

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_frequency, row[self.FREQUENCY])
    self.assign(self.actual_capacitance, row[self.CAPACITANCE])


@abstract_block_default(lambda: OscillatorCrystal)
class OscillatorReference(DiscreteApplication):
  @init_in_parent
  def __init__(self, frequency: RangeLike) -> None:
    """Crystal and supporting circuitry to connect it to an oscillator driver.
    Should include load capacitors."""
    super().__init__()

    self.crystal = self.Port(CrystalPort.empty(), [InOut])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.frequency = self.ArgParameter(frequency)


class OscillatorCrystal(OscillatorReference):  # TODO rename to disambiguate from part?
  """Crystal and supporting circuitry to connect it to an oscillator driver.
  Should include load capacitors."""
  PARASITIC_CAPACITANCE = 5e-12

  # Tolerance selected using table 32 in https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf, which gives suggested
  # load cap values 18pF, 39pF, 57pF. Assume any capacitance in the center could round either way - 22pF goes to 18pF
  # or 39pF, which gives a 28% tolerance.
  # Calculation: for tolerance y and series multiplicative factor a, we need (1+y) = a(1-y)
  # which solves to y=(a-1)/(a+1)
  # Then stack an additive 10% tolerance for the capacitor tolerance, for a total 0.38 tolerance.
  # TODO this should be formalized better.
  CAPACITOR_TOLERANCE = 0.38

  def contents(self) -> None:
    super().contents()

    self.package = self.Block(Crystal(self.frequency))

    cap_model = Capacitor(
      capacitance=(
        (self.package.actual_capacitance - self.PARASITIC_CAPACITANCE) * 2 * (1 - self.CAPACITOR_TOLERANCE),
        (self.package.actual_capacitance - self.PARASITIC_CAPACITANCE) * 2 * (1 + self.CAPACITOR_TOLERANCE)),
      voltage=self.crystal.link().drive_voltage
    )
    self.cap_a = self.Block(cap_model)
    self.cap_b = self.Block(cap_model)
    self.connect(self.crystal, self.package.crystal)
    self.connect(self.crystal.xtal_in, self.cap_a.pos)
    self.connect(self.crystal.xtal_out, self.cap_b.pos)
    self.connect(self.gnd, self.cap_a.neg.adapt_to(Ground()), self.cap_b.neg.adapt_to(Ground()), self.package.gnd)


class CeramicResonator(OscillatorReference):
  """Category for ceramic resonators"""
