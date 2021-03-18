from electronics_model import *
from .Categories import *
from .AbstractPassives import PullupResistor


class I2cPullup(DiscreteApplication):
  def __init__(self) -> None:
    super().__init__()

    # TODO restrictions on I2C voltage, current draw modeling
    self.pwr = self.Port(ElectricalSink(current_draw=Default(RangeExpr.ZERO),
                                        voltage_limits=RangeExpr.ALL),
                         [Power])
    self.i2c = self.Port(I2cPullupPort(), [InOut])


  def contents(self) -> None:
    super().contents()

    res_model = PullupResistor(4.7 * kOhm(tol=0.05))
    self.scl_res = self.Block(res_model)
    self.sda_res = self.Block(res_model)

    self.connect(self.scl_res.pwr, self.sda_res.pwr, self.pwr)
    self.connect(self.scl_res.io, self.i2c.scl)
    self.connect(self.sda_res.io, self.i2c.sda)
