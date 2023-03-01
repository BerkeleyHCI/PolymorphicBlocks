from edg_core import *


class IdealModel(Block):
  def contents(self):
    super().contents()
    self.require(False, "ideal model")
