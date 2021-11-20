from edg import *


class NewExample(SimpleBoardTop):
	def contents(self) -> None:
		super().contents()




if __name__ == "__main__":
	compile_board_inplace(NewExample)
