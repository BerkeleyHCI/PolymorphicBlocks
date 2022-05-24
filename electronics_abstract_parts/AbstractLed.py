from electronics_model import *
from .Categories import *


@abstract_block
class Led(DiscreteSemiconductor):
  Color = str  # type alias
  ColorLike = StringLike  # type alias

  # Common color definitions
  Red: Color = "red"
  Green: Color = "green"
  Blue: Color = "blue"
  Yellow: Color = "yellow"
  White: Color = "white"
  Any: Color = ""

  @init_in_parent
  def __init__(self, color: ColorLike = Any):
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
