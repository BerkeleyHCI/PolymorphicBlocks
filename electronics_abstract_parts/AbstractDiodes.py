from electronics_model import *
from .Categories import *
from .PartsTable import PartsTableColumn
from .PartsTablePart import PartsTablePart, PartsTableFootprint


@abstract_block
class Diode(DiscreteSemiconductor):
  """Base class for untyped diodes

  TODO power? capacitance? leakage current?
  """

  @init_in_parent
  def __init__(self, reverse_voltage: RangeLike, current: RangeLike, *,
               voltage_drop: RangeLike = Default(Range.all()),
               reverse_recovery_time: RangeLike = Default(Range.all())) -> None:
    super().__init__()

    self.anode = self.Port(Passive.empty())
    self.cathode = self.Port(Passive.empty())

    self.reverse_voltage = self.ArgParameter(reverse_voltage)
    self.current = self.ArgParameter(current)
    self.voltage_drop = self.ArgParameter(voltage_drop)
    self.reverse_recovery_time = self.ArgParameter(reverse_recovery_time)


@abstract_block
class ZenerDiode(DiscreteSemiconductor):
  """Base class for untyped zeners

  TODO power? capacitance? leakage current?
  """

  @init_in_parent
  def __init__(self, zener_voltage: RangeLike) -> None:
    super().__init__()

    self.anode = self.Port(Passive.empty())
    self.cathode = self.Port(Passive.empty())

    self.zener_voltage = self.ArgParameter(zener_voltage)


@abstract_block
class TableZenerDiode(ZenerDiode, PartsTableFootprint, GeneratorBlock):
  ZENER_VOLTAGE = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.actual_zener_voltage = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.zener_voltage, self.part, self.footprint_spec)

  def select_part(self, zener_voltage: Range, part_spec: str, footprint_spec: str) -> None:
    part = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.ZENER_VOLTAGE].fuzzy_in(zener_voltage)
    )).first(f"no zener diodes in Vz={zener_voltage} V")

    self.assign(self.actual_zener_voltage, part[self.ZENER_VOLTAGE])
    self.assign(self.actual_part, part[self.PART_NUMBER])

    self._make_footprint(part)


class ProtectionZenerDiode(DiscreteApplication):
  """Zener diode reversed across a power rail to provide transient overvoltage protection (and become an incandescent
  indicator on a reverse voltage)"""
  @init_in_parent
  def __init__(self, voltage: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power, InOut])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.voltage = self.ArgParameter(voltage)

  def contents(self):
    super().contents()
    self.diode = self.Block(ZenerDiode(zener_voltage=self.voltage))
    self.connect(self.diode.cathode.as_voltage_sink(
      voltage_limits=(0, self.voltage.lower()),
      current_draw=(0, 0)*Amp  # TODO should be leakage current
    ), self.pwr)
    self.connect(self.diode.anode.as_voltage_sink(), self.gnd)
