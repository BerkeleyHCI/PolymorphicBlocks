from edg import *


class BlinkyExample(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.mcu = self.Block(Xiao_Esp32c3())
    self.pololu = self.Block(PololuA4988())
    self.connect(self.pololu.gnd, self.mcu.gnd)
    self.connect(self.pololu.pwr, self.mcu.vusb_out)
    self.connect(self.pololu.pwr_logic, self.mcu.pwr_out)

    # your implementation here



if __name__ == "__main__":
  compile_board_inplace(BlinkyExample)
