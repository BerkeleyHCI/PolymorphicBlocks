from electronics_abstract_parts import *


class PassiveDummy(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(Passive(), [InOut])
