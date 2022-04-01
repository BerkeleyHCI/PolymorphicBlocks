from electronics_model import *
from .Categories import *


@abstract_block
class Led(DiscreteSemiconductor):
  def __init__(self):
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.k = self.Port(Passive.empty())


@abstract_block
class RgbLedCommonAnode(DiscreteSemiconductor):
  def __init__(self):
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.k_red = self.Port(Passive.empty())
    self.k_green = self.Port(Passive.empty())
    self.k_blue = self.Port(Passive.empty())
