from typing import List, Dict, Set, Type

from electronics_model import *
from .PinMappable import AllocatedResource


@abstract_block
class BaseIoController(Block):
  """An abstract IO controller block, that takes power input and provides a grab-bag of common IOs.
  A base interface for microcontrollers and microcontroller-like devices (eg, FPGAs).
  Pin assignments are handled via refinements and can be assigned to pins' allocated names."""
  def __init__(self) -> None:
    super().__init__()

    self.gpio = self.Port(Vector(DigitalBidir.empty()), optional=True)
    self.adc = self.Port(Vector(AnalogSink.empty()), optional=True)
    self.dac = self.Port(Vector(AnalogSource.empty()), optional=True)

    self.spi = self.Port(Vector(SpiMaster.empty()), optional=True)
    self.i2c = self.Port(Vector(I2cMaster.empty()), optional=True)
    self.uart = self.Port(Vector(UartPort.empty()), optional=True)
    self.usb = self.Port(Vector(UsbDevicePort.empty()), optional=True)
    self.can = self.Port(Vector(CanControllerPort.empty()), optional=True)

    self._io_ports: List[BasePort] = [
      self.gpio, self.adc, self.dac, self.spi, self.i2c, self.uart, self.usb, self.can]

  def _get_io_ports(self) -> List[BasePort]:
    """Returns all the IO ports of this BaseIoController as a list"""
    return self._io_ports

  def _export_ios_from(self, inner: 'BaseIoController', excludes: List[BasePort] = []) -> None:
    """Exports all the IO ports from an inner BaseIoController to this block's IO ports.
    Optional exclude list, for example if a more complex connection is needed."""
    assert isinstance(inner, BaseIoController), "can only export from inner block of type BaseIoController"
    assert len(self._io_ports) == len(inner._io_ports), "self and inner must have same IO ports"
    exclude_set = IdentitySet(*excludes)
    for (self_io, inner_io) in zip(self._io_ports, inner._io_ports):
      assert self_io._type_of() == inner_io._type_of(), "IO ports must be of same type"
      if self_io not in exclude_set:
        if isinstance(inner_io, Vector):  # for array ports connect a slice to allow other connections
          self.connect(self_io, inner_io.request_vector())
        else:
          self.connect(self_io, inner_io)

  @staticmethod
  def _instantiate_from(ios: List[BasePort], allocations: List[AllocatedResource]) -> \
      Dict[str, CircuitPort]:
    """Given a mapping of port types to IO ports and allocated resources from PinMapUtil,
    instantiate vector elements (if a vector) or init the port model (if a port)
    for the allocated resources using their data model and return the pin mapping."""
    ios_by_type = {io.elt_type() if isinstance(io, Vector) else type(io): io for io in ios}
    pinmap: Dict[str, CircuitPort] = {}

    ports_assigned = IdentitySet[Port]()

    for io in ios:
      if isinstance(io, Vector):
        io.defined()  # mark all vectors as defined - even if they will be empty

    for allocation in allocations:
      io = ios_by_type[type(allocation.port_model)]

      if isinstance(io, Vector):
        io_port = io.append_elt(allocation.port_model, allocation.name)
      elif isinstance(io, Port):
        io_port = io
        assert io not in ports_assigned, f"double assignment to {io}"
        ports_assigned.add(io)
        io.init_from(allocation.port_model)
      else:
        raise NotImplementedError(f"unknown port type {io}")

      if isinstance(allocation.pin, str):
        assert isinstance(io_port, CircuitPort)
        pinmap[allocation.pin] = io_port
      elif allocation.pin is None:
        assert isinstance(io_port, CircuitPort)  # otherwise discarded
      elif isinstance(allocation.pin, dict):
        assert isinstance(io_port, Bundle)
        for (subport_name, (pin_name, pin_resource)) in allocation.pin.items():
          subport = getattr(io_port, subport_name)
          assert isinstance(subport, CircuitPort), f"bad sub-port {pin_name} {subport}"
          pinmap[pin_name] = subport
      else:
        raise NotImplementedError(f"unknown allocation pin type {allocation.pin}")
    return pinmap


@abstract_block
class IoController(BaseIoController):
  """An IO controller that takes input power."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
