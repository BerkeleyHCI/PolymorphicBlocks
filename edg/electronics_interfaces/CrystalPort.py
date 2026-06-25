from deprecated import deprecated
from typing_extensions import override

from ..electronics_model import *
from ..util import deprecated_param_remap


class CrystalLink(Link):
    def __init__(self) -> None:
        super().__init__()
        self.driver = self.Port(CrystalDriver())
        self.crystal = self.Port(CrystalPort())

        self.drive_voltage = self.Parameter(RangeExpr(self.driver.voltage))
        self.frequency = self.Parameter(RangeExpr(self.crystal.frequency))

    @override
    def contents(self) -> None:
        super().contents()
        self.require(self.driver.frequency_limits.contains(self.frequency))

        self.xi = self.connect(self.driver.xtal_in, self.crystal.xtal_in)
        self.xo = self.connect(self.driver.xtal_out, self.crystal.xtal_out)


class CrystalPort(Port[CrystalLink]):
    link_type = CrystalLink

    def __init__(self, frequency: RangeLike = RangeExpr.ZERO) -> None:
        super().__init__()
        self.xtal_in = self.Port(Passive())
        self.xtal_out = self.Port(Passive())

        self.frequency = self.Parameter(RangeExpr(frequency))


class CrystalDriver(Port[CrystalLink]):
    link_type = CrystalLink

    @deprecated_param_remap(("voltage_out", "voltage"))
    def __init__(self, frequency_limits: RangeLike = RangeExpr.ALL, voltage: RangeLike = RangeExpr.ZERO) -> None:
        super().__init__()
        self.voltage = self.Parameter(RangeExpr(voltage))
        self.xtal_in = self.Port(Passive())
        self.xtal_out = self.Port(Passive())

        self.frequency_limits = self.Parameter(RangeExpr(frequency_limits))

    @property
    @deprecated("use voltage")
    def voltage_out(self) -> RangeExpr:
        return self.voltage
