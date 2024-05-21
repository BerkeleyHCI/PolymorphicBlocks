from ..electronics_abstract_parts import *


class Pesd1can(CanEsdDiode, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.gnd.init_from(Ground())
    self.can.init_from(CanDiffPort())

  def contents(self):
    super().contents()

    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.can.canl,  # TODO technically 1, 2 can be swapped
        '2': self.can.canh,
        '3': self.gnd,
      },
      part='PESD1CAN,215')
