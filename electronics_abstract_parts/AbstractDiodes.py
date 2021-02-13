from electronics_model import *
from .Categories import *


@abstract_block
class Diode(DiscreteSemiconductor):
  """Base class for untyped (ElectricalBase ports) diodes

  TODO power? capacitance? leakage current?
  """

  @init_in_parent
  def __init__(self, reverse_voltage: RangeLike = RangeExpr(), current: RangeLike = RangeExpr(),
               voltage_drop: RangeLike = RangeExpr(), reverse_recovery_time: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.anode = self.Port(Passive())
    self.cathode = self.Port(Passive())

    self.reverse_voltage = self.Parameter(RangeExpr(reverse_voltage))
    self.current = self.Parameter(RangeExpr(current))
    self.reverse_recovery_time = self.Parameter(RangeExpr(reverse_recovery_time))
    self.voltage_drop = self.Parameter(RangeExpr(voltage_drop))


@abstract_block
class ZenerDiode(DiscreteSemiconductor):
  """Base class for untyped (ElectricalBase ports) zener

  TODO power? capacitance? leakage current?
  """

  @init_in_parent
  def __init__(self, zener_voltage: RangeLike = RangeExpr(), forward_voltage_drop: RangeLike = RangeExpr()
               ) -> None:
    super().__init__()

    self.anode = self.Port(Passive())
    self.cathode = self.Port(Passive())

    self.zener_voltage = self.Parameter(RangeExpr(zener_voltage))
    self.forward_voltage_drop = self.Parameter(RangeExpr(forward_voltage_drop))


class ProtectionZenerDiode(DiscreteApplication):
  """Zener diode reversed across a power rail to provide transient overvoltage protection (and become an incandescent
  indicator on a reverse voltage)"""
  @init_in_parent
  def __init__(self, voltage: RangeLike = RangeExpr()):
    super().__init__()
    self.voltage = self.Parameter(RangeExpr(voltage))

    self.pwr = self.Port(ElectricalSink(
      voltage_limits=(0, self.voltage.lower()),
      current_draw=(0, 0)*Amp  # TODO should be leakage current
    ), [Power, Input])
    self.gnd = self.Port(Ground(), [Common])

  def contents(self):
    super().contents()
    self.diode = self.Block(ZenerDiode(zener_voltage=self.voltage))
    self.connect(self.diode.cathode.as_electrical_sink(), self.pwr)
    self.connect(self.diode.anode.as_electrical_sink(), self.gnd)
