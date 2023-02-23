from electronics_model import *
from .Categories import *
from .AbstractResistor import PullupResistor


class I2cPullup(Interface, Block):
  def __init__(self) -> None:
    super().__init__()

    # TODO restrictions on I2C voltage, current draw modeling
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.i2c = self.Port(I2cPullupPort.empty(), [InOut])


  def contents(self) -> None:
    super().contents()

    res_model = PullupResistor(4.7 * kOhm(tol=0.05))
    self.scl_res = self.Block(res_model).connected(self.pwr, self.i2c.scl)
    self.sda_res = self.Block(res_model).connected(self.pwr, self.i2c.sda)
