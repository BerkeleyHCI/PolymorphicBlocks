from electronics_model import *
from .Categories import *


LedColor = str  # type alias
LedColorLike = StringLike  # type alias


@abstract_block
class Led(DiscreteSemiconductor):
  # Common color definitions
  Red: LedColor = "red"
  Green: LedColor = "green"
  Blue: LedColor = "blue"
  Yellow: LedColor = "yellow"
  White: LedColor = "white"

  @init_in_parent
  def __init__(self, color: LedColorLike = ""):
    super().__init__()

    self.color = self.ArgParameter(color)

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
