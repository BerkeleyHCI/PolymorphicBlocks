from typing import *

from edg_core import *
from .PassivePort import Passive
from .ElectricalPorts import ElectricalSink, ElectricalSource


class CrystalLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.driver = self.Port(CrystalDriver())
    self.crystal = self.Port(CrystalPort())

    self.drive_voltage = self.Parameter(RangeExpr(self.driver.voltage_out))
    self.frequency = self.Parameter(RangeExpr(self.crystal.frequency))

  def contents(self) -> None:
    super().contents()
    self.require(self.driver.frequency_limits.contains(self.frequency))

    self.xi = self.connect(self.driver.xtal_in, self.crystal.a)
    self.xo = self.connect(self.driver.xtal_out, self.crystal.b)


class CrystalPort(Bundle[CrystalLink]):
  def __init__(self, frequency: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    super().__init__()
    self.link_type = CrystalLink

    self.a = self.Port(Passive())  # TODO replace w/ ElectricalPassive
    self.b = self.Port(Passive())

    self.frequency = self.Parameter(RangeExpr(frequency))


class CrystalDriver(Bundle[CrystalLink]):
  def __init__(self, frequency_limits: RangeLike = Default(RangeExpr.ALL),
               voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    super().__init__()
    self.link_type = CrystalLink

    self.voltage_out = self.Parameter(RangeExpr(voltage_out))
    self.xtal_in = self.Port(Passive())
    self.xtal_out = self.Port(Passive())

    self.frequency_limits = self.Parameter(RangeExpr(frequency_limits))
