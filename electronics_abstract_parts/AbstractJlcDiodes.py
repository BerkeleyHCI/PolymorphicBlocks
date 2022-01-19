from electronics_model import *
from . import Diode
from .Categories import *


@abstract_block
class JlcSwtichingDiode(Diode):

  @init_in_parent
  def __init__(self, reverse_voltage: RangeLike = RangeExpr(), reverse_current: RangeLike = RangeExpr(),
               forward_voltage: RangeLike = RangeExpr(), forward_current: RangeLike = RangeExpr(),
               junction_temperature: RangeLike = RangeExpr(), reverse_recovery: RangeLike = RangeExpr()) -> None:
    super().__init__(reverse_voltage, reverse_current, forward_voltage, forward_current)

    self.anode = self.Port(Passive())
    self.cathode = self.Port(Passive())

    self.junction_temperature = self.Parameter(RangeExpr(junction_temperature))
    self.reverse_recovery = self.Parameter(RangeExpr(reverse_recovery))


@abstract_block
class ZenerDiode(DiscreteSemiconductor):
  """Base class for untyped zeners

  TODO power? capacitance? leakage current?
  """

  @init_in_parent
  def __init__(self, zener_voltage: RangeLike = RangeExpr(),
               forward_voltage_drop: RangeLike = Default(RangeExpr.ALL)) -> None:
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

    self.pwr = self.Port(VoltageSink(), [Power, Input])
    self.gnd = self.Port(Ground(), [Common])

  def contents(self):
    super().contents()
    self.diode = self.Block(ZenerDiode(zener_voltage=self.voltage))
    self.connect(self.diode.cathode.as_voltage_sink(
      voltage_limits=(0, self.voltage.lower()),
      current_draw=(0, 0)*Amp  # TODO should be leakage current
    ), self.pwr)
    self.connect(self.diode.anode.as_voltage_sink(), self.gnd)