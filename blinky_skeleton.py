from edg import *
from electronics_model.KiCadSchematicBlock import KiCadSchematicBlock


class KiCadBlock(KiCadSchematicBlock):
  def __init__(self) -> None:
    super().__init__()

    self.PORT_A = self.Port(Passive())

  def contents(self) -> None:
    super().contents()

    self.import_kicad('C:\\Users\\Nathan Nguyendinh\\Documents\\PCB Files\\EDG-IDE Simple Circuit\\EDG-IDE Simple Circuit.net')

class BlinkyExample(BoardTop):
  def contents(self) -> None:
    super().contents()
    self.test = self.Block(KiCadBlock())


if __name__ == "__main__":
  compile_board_inplace(BlinkyExample)
