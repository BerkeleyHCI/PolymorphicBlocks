from electronics_model import *

@abstract_block
class IoController(Block):
  """An abstract IO controller block, that takes power input and provides a grab-bag of common IOs.
  A base interface for microcontrollers and microcontroller-like devices (eg, FPGAs).
  Pin assignments are handled via refinements and can be assigned to pins' allocated names."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.gpio = self.Port(Vector(DigitalBidir()))
    self.spi = self.Port(Vector(SpiMaster()))
    self.i2c = self.Port(Vector(I2cMaster()))
    self.uart = self.Port(Vector(UartPort()))
    self.usb = self.Port(Vector(UsbDevicePort()))
    self.can = self.Port(Vector(CanControllerPort()))
    self.adc = self.Port(Vector(AnalogSink()))
    self.dac = self.Port(Vector(AnalogSource()))
