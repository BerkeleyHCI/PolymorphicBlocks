from ..core import *
from .PassivePort import Passive


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

    self.xi = self.connect(self.driver.xtal_in, self.crystal.xtal_in)
    self.xo = self.connect(self.driver.xtal_out, self.crystal.xtal_out)


class CrystalPort(Bundle[CrystalLink]):
  link_type = CrystalLink

  def __init__(self, frequency: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()
    self.xtal_in = self.Port(Passive())
    self.xtal_out = self.Port(Passive())

    self.frequency = self.Parameter(RangeExpr(frequency))


class CrystalDriver(Bundle[CrystalLink]):
  link_type = CrystalLink

  def __init__(self, frequency_limits: RangeLike = RangeExpr.ALL,
               voltage_out: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()
    self.voltage_out = self.Parameter(RangeExpr(voltage_out))
    self.xtal_in = self.Port(Passive())
    self.xtal_out = self.Port(Passive())

    self.frequency_limits = self.Parameter(RangeExpr(frequency_limits))
