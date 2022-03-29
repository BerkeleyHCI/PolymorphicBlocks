from abc import ABCMeta, abstractmethod
from typing import List, Type, Tuple, Optional, Union, Any, NamedTuple

from electronics_model import *


@abstract_block
class PinMappable(Block):
  """Abstract base class for pin-mappable devices. Provides a named initializer argument for user-defined explicit
  pin mapping refinements. Actual pin mapping functionality must be implemented by the subclass.
  This may simply delegate the pin mapping to an inner block, for example for a microcontroller application circuit
  to delegate the pin mapping to the microcontroller chip block.
  """
  @init_in_parent
  def __init__(self, pin_mapping: StringLike = "") -> None:
    super().__init__()
    self.pin_mapping = pin_mapping


class BasePinMapResource(metaclass=ABCMeta):
  """Abstract base class for a resource definition for the pin mapping utility. Because these are so intertwined with
  the actual pin mapper, these are just named data structures - the logic for handling these is in the pin mapper."""


class BaseLeafPinMapResource(BasePinMapResource):
  """Abstract base class for a resource that does not delegate any further (leaf-level) - such as a pin."""


class BaseDelegatingPinMapResource(BasePinMapResource):
  """Abstract base class for a resource that delegates inner resources."""


class PinResource(BaseLeafPinMapResource):
  """A resource for a single chip pin, which can be one of several port types (eg, an ADC and DIO sharing a pin)."""
  def __init__(self, pin: str, name_models: dict[str, CircuitPort]):
    self.pin = pin
    self.name_models = name_models


class PeripheralFixedPin(BaseLeafPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports can be mapped to pins based on a fixed
  list of options (sort of a very limited switch matrix).
  The internal port model must be fully defined here."""
  def __init__(self, name: str, port_model: Bundle, inner_allowed_pins: dict[str, List[str]]):
    self.name = name
    self.port_model = port_model
    self.inner_allowed_pins = inner_allowed_pins


class PeripheralAnyPinResource(BaseDelegatingPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports must be delegated to another resource,
  any resource of matching type. Used for chips with a full switch matrix.
  The port model here should have empty models for the internal ports, so the models can be assigned from the inner
  resource. This allows things like digital IOs in a peripheral to inherit from the pin-level definition."""
  def __init__(self, name: str, port_model: Bundle):
    self.name = name
    self.port_model = port_model


class PeripheralFixedResource(BaseDelegatingPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports must be delegated to another resource,
  of a fixed list per pin by resource name. Used for chips which have alternate pin functionality
  (sort of a very limited switch matrix).
  The port model here should have empty models for the internal ports, so the models can be assigned from the inner
  resource. This allows things like digital IOs in a peripheral to inherit from the pin-level definition."""
  def __init__(self, name: str, port_model: Bundle, inner_allowed_names: dict[str, List[str]]):
    self.name = name
    self.port_model = port_model
    self.inner_allowed_names = inner_allowed_names


class AssignedResource(NamedTuple):
  port_model: Port  # port model (including defined elements, for bundles)
  name: str  # name given by the user, bundles will have automatic postfixes
  resource: str  # name of the resource assigned, non-delegated bundle elements can have automatic prefixes
  pin: Union[str, dict[str, 'AssignedResource']]  # pin number if port is leaf, or recursive definition for bundles


class PinMapUtil:
  """
  Goal: given a pin map description for a chip, map the leaf CircuitPorts to pin numbers which can be used in the
  footprint() block.

  TODO: how to support mutex concerns (ADC / DigitalPorts)? how to support different ports of the same type (eg, 5v tolerant)

  Idea of layers?
  Description layer
  - Pin layer (leaf level - ADC capable, DAC capable, digital IO - incl different voltages)
    - "these pins have these IO models"
  - Peripheral layer (which bundles can map where - leaves must be connectable)
    - Problem: no support for heterogeneous models in peripherals
    - use init_from support? esp in bundle elts?

  Concept of hierarchical assignable resources?
  Each incoming port can be assigned to a resource. Resources are hierarchical / recursive.
  Each resource can only be claimed by one port (used once).
  TODO: is it ever needed to uspport some kind of mutual exclusion between several resources?
  Resources are first-order matched based on types.
  Each resource, given a resource manager reference, can assess whether it can be assigned.
  Bundle elements can be recursively delegated.
  eg, LPC1549
  [
    # Pin "resource"
    Pin_OneOf('1', 'PIO0_0', [analog_model, digital5v_model])  # ADC capable
    Pin_OneOf('2', 'PIO0_1', [digital5v_model])  # not ADC capable
    ...
    # Peripheral "resource" - name only - switch matrix, IOs delegated
    # Hierarchical? Automatically assign to compatible leaf type, optionally with assigned pins
    Peripheral_SWM('SPI0', spimaster_model)
    # Peripheral "resource" - fixed pins
    Peripheral_Fixed('I2C0', {'sda': '44', 'scl': '45'}, i2c_model)
    # TBD: how to handle
  ]

  Mapping layer
  - Take in ports with suggested-names, returns two mappings:
    - a mapping of pin number to leaf ports - can be directly passed into footprint
    - a mapping of ports to port model - used as initializers
      - this includes both leaves and bundles, so either the leaves will be empty,
        or the bundles will have its member ports be empty so they can be initialized
        from leaves (allowing differentiated IOs)
  """
  def __init__(self, resources: List[BasePinMapResource]):
    self.resources = resources

  def remap_pins(self, pinmap: dict[str, str]) -> 'PinMapUtil':
    """Returns a new PinMapUtil with pin names remapped according to the argument dict. Useful for a chip series
    to define a generic pin mapping using pin names, and then remap those to pin numbers for specific packages.
    Pins that are not in the pinmap are discarded."""
    def remap_resource(resource: BasePinMapResource) -> Optional[BasePinMapResource]:
      if isinstance(resource, PinResource):
        if resource.pin in pinmap:
          return PinResource(pinmap[resource.pin], resource.name_models)
        else:
          return None
      elif isinstance(resource, PeripheralFixedPin):
        remapped_pins = {elt_name: [pinmap[elt_pin] for elt_pin in elt_pins if elt_pin in pinmap]
                         for elt_name, elt_pins in resource.inner_allowed_pins.items()}
        return PeripheralFixedPin(resource.name, resource.port_model, remapped_pins)
      elif isinstance(resource, BaseDelegatingPinMapResource):
        return resource
      else:
        raise NotImplementedError(f"unknown resource {resource}")

    remapped_resources_raw = [remap_resource(resource) for resource in self.resources]
    remapped_resources = [resource for resource in remapped_resources_raw if resource is not None]
    return PinMapUtil(remapped_resources)

  def assign(self, ports_names: List[Tuple[Port, Optional[str]]], assignments: str) -> \
      Tuple[dict[str, CircuitPort], List[Tuple[Port, Port]]]:
    """Performs port assignment given a list of ports and their (optional) user-defined names, and optional
    user-defined explicit assignments. Names (except where part of preassigns) may be duplicated.
    Returns a list of pin mappings to leaf-level ports (CircuitPort) and a mapping of ports to models.
    For the ports-to-model references, it is guaranteed that a container port and model will appear earlier than
    a contained port, allowing recursive initialization in the order returned.

    TBD: assign by type only?
    can asisgn be called several times?

    """
    pass

  def assign_types(self, port_types_names: List[Tuple[Type[Port], List[str]]], assignments: str = "") -> \
      List[AssignedResource]:
    """Performs port assignment given a list of port types and their names, and optional user-defined pin assignments
    (which may be empty). Names may be duplicated (either within a port type, or across port types), and multiple
    records will show up accordingly in the output data structure.
    Returns a list of assigned ports, structured as a port model (set recursively for bundle ports), the input name,
    and pin assignment as a pin string for leaf ports, or a dict (possibly recursive) for bundles."""
    pass
