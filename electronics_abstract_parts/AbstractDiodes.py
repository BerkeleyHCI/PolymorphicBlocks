from typing import cast
from electronics_model import *
from .Categories import *


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

    self.anode = self.Port(Passive())
    self.cathode = self.Port(Passive())

    self.reverse_voltage = cast(RangeExpr, reverse_voltage)
    self.current = cast(RangeExpr, current)
    self.voltage_drop = cast(RangeExpr, voltage_drop)
    self.reverse_recovery_time = cast(RangeExpr, reverse_recovery_time)


@abstract_block
class ZenerDiode(DiscreteSemiconductor):
  """Base class for untyped zeners

  TODO power? capacitance? leakage current?
  """

  @init_in_parent
  def __init__(self, zener_voltage: RangeLike, *,
               forward_voltage_drop: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()

    self.anode = self.Port(Passive())
    self.cathode = self.Port(Passive())

    self.zener_voltage = cast(RangeExpr, zener_voltage)
    self.forward_voltage_drop = cast(RangeExpr, forward_voltage_drop)


class ProtectionZenerDiode(DiscreteApplication):
  """Zener diode reversed across a power rail to provide transient overvoltage protection (and become an incandescent
  indicator on a reverse voltage)"""
  @init_in_parent
  def __init__(self, voltage: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power, Input])
    self.gnd = self.Port(Ground(), [Common])

    self.voltage = cast(RangeExpr, voltage)

  def contents(self):
    super().contents()
    self.diode = self.Block(ZenerDiode(zener_voltage=self.voltage))
    self.connect(self.diode.cathode.as_voltage_sink(
      voltage_limits=(0, self.voltage.lower()),
      current_draw=(0, 0)*Amp  # TODO should be leakage current
    ), self.pwr)
    self.connect(self.diode.anode.as_voltage_sink(), self.gnd)
