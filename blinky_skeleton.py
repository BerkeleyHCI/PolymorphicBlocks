from typing_extensions import override

from edg import *


class BlinkyExample(SimpleBoardTop):
    @override
    def contents(self) -> None:
        super().contents()
        # your implementation here


if __name__ == "__main__":
    compile_board_inplace(BlinkyExample)
