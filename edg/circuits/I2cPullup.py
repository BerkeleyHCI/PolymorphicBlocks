from typing_extensions import override

from ..abstract_parts import *


class I2cPullup(Interface, Block):
    def __init__(self, resistance: RangeLike = 4.7 * kOhm(tol=0.05)) -> None:
        super().__init__()
        self.resistance = self.ArgParameter(resistance)
        # TODO restrictions on I2C voltage, current draw modeling
        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.i2c = self.Port(I2cPullupPort.empty(), [InOut])

    @override
    def contents(self) -> None:
        super().contents()

        res_model = PullupResistor(self.resistance)
        self.scl_res = self.Block(res_model).connected(self.pwr, self.i2c.scl)
        self.sda_res = self.Block(res_model).connected(self.pwr, self.i2c.sda)
