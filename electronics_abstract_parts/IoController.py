from typing import List, Dict

from electronics_model import *
from .PinMappable import AllocatedResource


@abstract_block
class IoController(Block):
  """An abstract IO controller block, that takes power input and provides a grab-bag of common IOs.
  A base interface for microcontrollers and microcontroller-like devices (eg, FPGAs).
  Pin assignments are handled via refinements and can be assigned to pins' allocated names."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.gpio = self.Port(Vector(DigitalBidir.empty()), optional=True)
    self.adc = self.Port(Vector(AnalogSink.empty()), optional=True)
    self.dac = self.Port(Vector(AnalogSource.empty()), optional=True)

    self.spi = self.Port(Vector(SpiMaster.empty()), optional=True)
    self.i2c = self.Port(Vector(I2cMaster.empty()), optional=True)
    self.uart = self.Port(Vector(UartPort.empty()), optional=True)
    self.usb = self.Port(Vector(UsbDevicePort.empty()), optional=True)
    self.can = self.Port(Vector(CanControllerPort.empty()), optional=True)

  def _instantiate_from(self, ios: List[Vector], allocations: List[AllocatedResource]) -> \
      Dict[str, CircuitPort]:
    """Given a mapping of port types to IO vectors and allocated resources from PinMapUtil,
    instantiate vector elements for the allocated resources using their data model and return the pin mapping."""
    ios_by_type = {io.elt_type(): io for io in ios}
    pinmap: Dict[str, CircuitPort] = {}

    for io in ios:
      io.defined()  # mark all vectors as defined - even if they will be empty

    for allocation in allocations:
      io = ios_by_type[type(allocation.port_model)]
      io_port = io.append_elt(allocation.port_model, allocation.name)
      if isinstance(allocation.pin, str):
        assert isinstance(io_port, CircuitPort)
        pinmap[allocation.pin] = io_port
      elif isinstance(allocation.pin, dict):
        assert isinstance(io_port, Bundle)
        for (subport_name, pin_name) in allocation.pin.items():
          subport = getattr(io_port, subport_name)
          assert isinstance(subport, CircuitPort), f"bad sub-port {pin_name} {subport}"
          pinmap[pin_name] = subport
      else:
        raise NotImplementedError(f"unknown allocation pin type {allocation.pin}")
    return pinmap
