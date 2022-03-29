from typing import List, Tuple

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

    self.gpio = self.Port(Vector(DigitalBidir.empty()))
    self.adc = self.Port(Vector(AnalogSink.empty()))
    self.dac = self.Port(Vector(AnalogSource.empty()))

    self.spi = self.Port(Vector(SpiMaster(DigitalBidir.empty())))
    self.i2c = self.Port(Vector(I2cMaster(DigitalBidir.empty())))
    self.uart = self.Port(Vector(UartPort(DigitalBidir.empty())))
    self.usb = self.Port(Vector(UsbDevicePort()))
    self.can = self.Port(Vector(CanControllerPort(DigitalBidir.empty())))

  def _instantiate_ios(self, ios: List[Tuple[Vector, List[str]]]) -> List[Tuple[Port, str]]:
    """Given a list of allocated IOs (as a list of the port vector and list of allocates), return all the
    allocated ports and their allocated names. Allocated names may overlap, in particular where it might
    have been auto-generated.
    Vector elements are initialized with their sample element."""
    ports_list = []
    for (io_vector, io_allocates) in ios:
      for io_allocate in io_allocates:
        ports_list.append(io_vector.append_elt(io_vector._elt, io_allocate))
    return ports_list
