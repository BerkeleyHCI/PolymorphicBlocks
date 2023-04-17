from itertools import chain
from typing import List, Dict, Tuple, Type, Any, Optional

from electronics_model import *
from . import VariantPinRemapper
from .PinMappable import AllocatedResource, PinMappable, PinMapUtil
from .Categories import ProgrammableController, IdealModel


@non_library
class BaseIoController(Block):
  """An abstract IO controller block, that takes power input and provides a grab-bag of common IOs.
  A base interface for microcontrollers and microcontroller-like devices (eg, FPGAs).
  Pin assignments are handled via refinements and can be assigned to pins' allocated names.

  This should not be instantiated as a generic block."""
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

    self.io_current_draw = self.Parameter(RangeExpr())  # total current draw for all leaf-level IO sinks

    # TODO dedup w/ pinmapping IO port w/ port type
    self._io_ports: List[BasePort] = [  # ordered by assignment order, most restrictive should be first
      self.dac, self.adc, self.spi, self.i2c, self.uart, self.usb, self.can, self.gpio]

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
        self.connect(self_io, inner_io)
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


class PinMappableIoController(PinMappable, BaseIoController, GeneratorBlock):
  """BaseIoController with generator code to set pin mappings"""
  def __init__(self) -> None:
    super().__init__()
    from edg_core.Generator import GeneratorParam
    # TODO dedup w/ BaseIoController _io_ports
    self._pinmap_io_ports: List[Tuple[Type[Port], Vector[Any]]] = [  # ordered by assignment order, most restrictive should be first
      (AnalogSource, self.dac), (AnalogSink, self.adc),
      (SpiMaster, self.spi), (I2cMaster, self.i2c), (UartPort, self.uart),
      (UsbDevicePort, self.usb), (CanControllerPort, self.can),
      (DigitalBidir, self.gpio)
    ]

    self.io_requested = ElementDict[GeneratorParam[List[str]]]()
    self.assignments_value = self.GeneratorParam(self.pin_assigns)

  def contents(self) -> None:
    for (port_tpe, io_port) in self._pinmap_io_ports:
      self.io_requested[str(port_tpe)] = self.GeneratorParam(io_port.requested())

  def allocate_pins(self, io_pinmaps: PinMapUtil) -> Dict[str, CircuitPort]:
    allocated = io_pinmaps.allocate(
      [(port_tpe, self.io_requested[str(port_tpe)].get()) for (port_tpe, io_port) in self._pinmap_io_ports],
      self.assignments_value.get())
    self.generator_set_allocation(allocated)
    io_pins, current_draw = self._instantiate_from(self._get_io_ports(), allocated)
    self.assign(self.io_current_draw, current_draw)

    return io_pins

  def generate(self):
    super().generate()

    self.assign(self.has_chip_pu, True)

    self.assign(self.lcsc_part, 'C701342')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'RF_Module:ESP32-WROOM-32',
      dict(chain(self.system_pinmaps.items(), self.allocate_pins(io_pinmaps).items())),
      mfr='Espressif Systems', part='ESP32-WROOM-32',
      datasheet='https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf',
    )


@abstract_block_default(lambda: IdealIoController)
class IoController(ProgrammableController, BaseIoController):
  """An abstract, generic IO controller with common IOs and power ports."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])


class IdealIoController(IoController, IdealModel, GeneratorBlock):
  """An ideal IO controller, with as many IOs as requested.
  Output have voltages at pwr/gnd, all other parameters are ideal."""
  def __init__(self) -> None:
    super().__init__()
    self.generator(self.generate,
                   self.gpio.requested(), self.adc.requested(), self.dac.requested(),
                   self.spi.requested(), self.i2c.requested(), self.uart.requested(),
                   self.usb.requested(), self.can.requested())

  def generate(self,
               gpio_requests: List[str], adc_requests: List[str], dac_requests: List[str],
               spi_requests: List[str], i2c_requests: List[str], uart_requests: List[str],
               usb_requests: List[str], can_requests: List[str]) -> None:
    self.pwr.init_from(VoltageSink())
    self.gnd.init_from(Ground())

    dio_model = DigitalBidir(
      voltage_out=self.gnd.link().voltage.hull(self.pwr.link().voltage),
      pullup_capable=True, pulldown_capable=True
    )

    self.gpio.defined()
    for elt in gpio_requests:
      self.gpio.append_elt(dio_model, elt)
    self.adc.defined()
    for elt in adc_requests:
      self.adc.append_elt(AnalogSink(), elt)
    self.dac.defined()
    for elt in dac_requests:
      self.dac.append_elt(AnalogSource(
        voltage_out=self.gnd.link().voltage.hull(self.pwr.link().voltage)
      ), elt)
    self.spi.defined()
    for elt in spi_requests:
      self.spi.append_elt(SpiMaster(dio_model), elt)
    self.i2c.defined()
    for elt in i2c_requests:
      self.i2c.append_elt(I2cMaster(dio_model), elt)
    self.uart.defined()
    for elt in uart_requests:
      self.uart.append_elt(UartPort(dio_model), elt)
    self.usb.defined()
    for elt in usb_requests:
      self.usb.append_elt(UsbDevicePort(), elt)
    self.can.defined()
    for elt in can_requests:
      self.can.append_elt(CanControllerPort(dio_model), elt)
