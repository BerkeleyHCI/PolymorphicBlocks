from edg import *


class BlinkyExample(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.buck.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)

    with self.implicit_connect(
            ImplicitConnect(self.buck.pwr_out, [Power]),
            ImplicitConnect(self.buck.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led0=26',
          'led1=27',
          'led2=28',
          'led3=29',
        ])
      ])