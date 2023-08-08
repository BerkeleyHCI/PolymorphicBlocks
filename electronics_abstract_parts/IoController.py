from itertools import chain
from typing import List, Dict, Tuple, Type

from deprecated import deprecated

from electronics_model import *
from .PinMappable import AllocatedResource, PinMappable, PinMapUtil
from .Categories import ProgrammableController


@abstract_block
class BaseIoController(PinMappable, Block):
  """An abstract IO controller block, that takes power input and provides a grab-bag of common IOs.
  A base interface for microcontrollers and microcontroller-like devices (eg, FPGAs).
  Pin assignments are handled via refinements and can be assigned to pins' allocated names.

  This should not be instantiated as a generic block."""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.gpio = self.Port(Vector(DigitalBidir.empty()), optional=True)
    self.adc = self.Port(Vector(AnalogSink.empty()), optional=True)

    self.spi = self.Port(Vector(SpiController.empty()), optional=True)
    self.i2c = self.Port(Vector(I2cController.empty()), optional=True)
    self.uart = self.Port(Vector(UartPort.empty()), optional=True)

    self.spi_peripheral = self.Port(Vector(SpiPeripheral.empty()), optional=True)
    self.i2c_target = self.Port(Vector(I2cTarget.empty()), optional=True)

    self.io_current_draw = self.Parameter(RangeExpr())  # total current draw for all leaf-level IO sinks

    self._io_ports: List[BasePort] = [  # ordered by assignment order, most restrictive should be first
      self.adc, self.spi, self.i2c, self.uart, self.spi_peripheral, self.i2c_target, self.gpio]

  def _type_of_io(self, io_port: BasePort) -> Type[Port]:
    if isinstance(io_port, Vector):
      return io_port.elt_type()
    elif isinstance(io_port, Port):
      return type(io_port)
    else:
      raise NotImplementedError(f"unknown port type {io_port}")

  @deprecated("use BaseIoControllerExportable")
  def _export_ios_from(self, inner: 'BaseIoController', excludes: List[BasePort] = []) -> None:
    """Exports all the IO ports from an inner BaseIoController to this block's IO ports.
    Optional exclude list, for example if a more complex connection is needed."""
    assert isinstance(inner, BaseIoController), "can only export from inner block of type BaseIoController"
    self_ios_by_type = {self._type_of_io(io_port): io_port for io_port in self._io_ports}
    exclude_set = IdentitySet(*excludes)
    for inner_io in inner._io_ports:
      if inner_io in exclude_set:
        continue
      inner_io_type = self._type_of_io(inner_io)
      assert inner_io_type in self_ios_by_type, f"outer missing IO of type {inner_io_type}"
      self.connect(self_ios_by_type[inner_io_type], inner_io)
    self.assign(self.io_current_draw, inner.io_current_draw)

  @staticmethod
  def _instantiate_from(ios: List[BasePort], allocations: List[AllocatedResource]) -> \
      Tuple[Dict[str, CircuitPort], RangeExpr]:
    """Given a mapping of port types to IO ports and allocated resources from PinMapUtil,
    instantiate vector elements (if a vector) or init the port model (if a port)
    for the allocated resources using their data model and return the pin mapping."""
    ios_by_type = {io.elt_type() if isinstance(io, Vector) else type(io): io for io in ios}
    pinmap: Dict[str, CircuitPort] = {}

    ports_assigned = IdentitySet[Port]()
    io_current_draw_builder = RangeExpr._to_expr_type(RangeExpr.ZERO)

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

      if isinstance(io_port, DigitalBidir):
        io_current_draw_builder = io_current_draw_builder + (
          io_port.link().current_drawn.lower().min(0), io_port.link().current_drawn.upper().max(0)
        )
      elif isinstance(io_port, AnalogSink):
        pass  # assumed no current draw into a sink
      elif isinstance(io_port, AnalogSource):
        io_current_draw_builder = io_current_draw_builder + (
          io_port.link().current_drawn.lower().min(0), io_port.link().current_drawn.upper().max(0)
        )
      elif isinstance(io_port, Bundle):
        pass  # TODO: don't assume signal bundles have zero current draw
      else:
        raise NotImplementedError(f"unknown port type {io_port}")

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

    return (pinmap, io_current_draw_builder)


@non_library
class BaseIoControllerPinmapGenerator(BaseIoController, GeneratorBlock):
  """BaseIoController with generator code to set pin mappings"""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.generator_param(self.pin_assigns)

  def contents(self):
    super().contents()
    for io_port in self._io_ports:  # defined in contents() so subclass __init__ can define additional _io_ports
      if isinstance(io_port, Vector):
        self.generator_param(io_port.requested())
      elif isinstance(io_port, Port):
        self.generator_param(io_port.is_connected())
      else:
        raise NotImplementedError(f"unknown port type {io_port}")

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    """Implement me. Defines the fixed pin mappings from pin number to port."""
    raise NotImplementedError

  def _io_pinmap(self) -> PinMapUtil:
    """Implement me. Defines the assignable IO pinmaps."""
    raise NotImplementedError

  def _make_pinning(self) -> Dict[str, CircuitPort]:
    allocation_list = []
    for io_port in self._io_ports:
      if isinstance(io_port, Vector):  # derive Vector connections from requested
        allocation_list.append((io_port.elt_type(), self.get(io_port.requested())))
      elif isinstance(io_port, Port):  # derive Port connections from is_connected
        if self.get(io_port.is_connected()):
          requested = [self._name_of_child(io_port)]  # generate requested name from port name if connected
        else:
          requested = []
        allocation_list.append((type(io_port), requested))
      else:
        raise NotImplementedError(f"unknown port type {io_port}")

    allocated = self._io_pinmap().allocate(allocation_list, self.get(self.pin_assigns))
    self.generator_set_allocation(allocated)
    io_pins, current_draw = self._instantiate_from(self._io_ports, allocated)
    self.assign(self.io_current_draw, current_draw)

    return dict(chain(self._system_pinmap().items(), io_pins.items()))


@non_library
class BaseIoControllerExportable(BaseIoController, GeneratorBlock):
  """BaseIoController wrapper (this is a BaseIoController, which wraps another BaseIoController)
  which automatically exports my IOs from the internal IOs in an extensible way (additional connects
  to internal IOs are allowed).
  The export is also customizable, e.g. if additional subcircuits are needed for some connection.
  Also defines a function for adding additional internal pin assignments.
  The internal device (self.ic) must have been created (e.g., in contents()) before this generate() is called."""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.ic: BaseIoController
    self.generator_param(self.pin_assigns)

  def contents(self):  # TODO can this be deduplicated w/ BaseIoControllerPinmapGenerator?
    super().contents()
    for io_port in self._io_ports:  # defined in contents() so subclass __init__ can define additional _io_ports
      if isinstance(io_port, Vector):
        self.generator_param(io_port.requested())
      elif isinstance(io_port, Port):
        self.generator_param(io_port.is_connected())
      else:
        raise NotImplementedError(f"unknown port type {io_port}")

  def _make_export_io(self, self_io: Port, inner_io: Port):
    """Connects my external IO to some inner IO, with IOs being either top-level ports or array elements.
    This function can be overloaded to handle special cases, e.g. if additional circuitry is required.
    Called within generate, has access to generator params."""
    self.connect(self_io, inner_io)

  def _inner_pin_assigns(self) -> List[str]:
    """Integration point to define pin assigns to pass to the inner device.
    Called within generate, has access to generator params."""
    return self.get(self.pin_assigns).copy()

  def generate(self):
    super().generate()
    inner_ios_by_type = {self._type_of_io(io_port): io_port for io_port in self.ic._io_ports}
    for self_io in self._io_ports:
      self_io_type = self._type_of_io(self_io)
      assert self_io_type in inner_ios_by_type, f"inner missing IO of type {self_io_type}"
      inner_io = inner_ios_by_type[self_io_type]

      if isinstance(self_io, Vector):
        self_io.defined()
        assert isinstance(inner_io, Vector)
        for io_requested in self.get(self_io.requested()):
          self_io_elt = self_io.append_elt(self_io.elt_type().empty(), io_requested)
          self._make_export_io(self_io_elt, inner_io.request(io_requested))
      else:
        assert isinstance(self_io, Port) and isinstance(inner_io, Port)
        if self.get(self_io.is_connected()):
          self._make_export_io(self_io, inner_io)

    self.assign(self.io_current_draw, self.ic.io_current_draw)

    self.assign(self.ic.pin_assigns, self._inner_pin_assigns())
    self.assign(self.actual_pin_assigns, self.ic.actual_pin_assigns)


def makeIdealIoController():  # needed to avoid circular import
  from .IdealIoController import IdealIoController
  return IdealIoController


@abstract_block_default(makeIdealIoController)
class IoController(ProgrammableController, BaseIoController):
  """An abstract, generic IO controller with optional common IOs and power ports."""
  def __init__(self, *awgs, **kwargs) -> None:
    super().__init__(*awgs, **kwargs)

    self.pwr = self.Port(VoltageSink.empty(), [Power], optional=True)
    self.gnd = self.Port(Ground.empty(), [Common], optional=True)


@non_library
class IoControllerPowerRequired(IoController):
  """IO controller with required power pins."""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.require(self.pwr.is_connected())
    self.require(self.gnd.is_connected())
