import sys
from edg import *


class BlinkyExample(Block):
  def contents(self) -> None:
    super().contents()
    # implementation here


if __name__ == '__main__':
  ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
    BlinkyExample(),
    "examples/blinky_example"
  )
