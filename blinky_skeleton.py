from edg import *


class BlinkyExample(BoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.usb.pwr, self.mcu.pwr)
    self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
    self.connect(self.mcu.gpio.request('led'), self.led.signal)
    # your implementation here


if __name__ == "__main__":
  compile_board_inplace(BlinkyExample)
