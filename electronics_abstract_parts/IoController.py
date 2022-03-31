from typing import List, Tuple, Optional

from electronics_model import *

from .PinMappable import AllocatedResource


@abstract_block
class IoController(Block):
  """An abstract IO controller block, that takes power input and provides a grab-bag of common IOs.
  A base interface for microcontrollers and microcontroller-like devices (eg, FPGAs).
  Pin assignments are handled via refinements and can be assigned to pins' allocated names."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.gpio = self.Port(Vector(DigitalBidir.empty()))
    self.adc = self.Port(Vector(AnalogSink.empty()))
    self.dac = self.Port(Vector(AnalogSource.empty()))

    self.spi = self.Port(Vector(SpiMaster(DigitalBidir.empty())))
    self.i2c = self.Port(Vector(I2cMaster(DigitalBidir.empty())))
    self.uart = self.Port(Vector(UartPort(DigitalBidir.empty())))
    self.usb = self.Port(Vector(UsbDevicePort()))
    self.can = self.Port(Vector(CanControllerPort(DigitalBidir.empty())))

  def _instantiate_from(self, ios: List[Vector], assigned: List[AllocatedResource]):
    """Given the list of IO vectors and assigned resources from PinMapUtil, instantiate vector elements for the
    assigned resources using their data model and top-level (user-defined) names."""

