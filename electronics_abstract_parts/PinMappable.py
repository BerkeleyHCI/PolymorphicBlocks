from abc import ABCMeta, abstractmethod
from typing import List, Type

from electronics_model import *


@abstract_block
class PinMappable(Block):
  """Abstract base class for pin-mappable devices. Provides a named initializer argument for user-defined explicit
  pin mapping refinements. Actual pin mapping functionality must be implemented by the subclass.
  This may simply delegate the pin mapping to an inner block, for example for a microcontroller application circuit
  to delegate the pin mapping to the microcontroller chip block.
  """
  @init_in_parent
  def __init__(self, pin_mapping: StringLike) -> None:
    super().__init__()
    self.pin_mapping = pin_mapping


class BasePinMapResource(metaclass=ABCMeta):
  """Abstract base class for a resource definition for the pin mapping utility."""
  @abstractmethod
  def mappable_port_types(self) -> List[Type[Port]]:
    """Returns all the port types that can map to this resource."""
    ...


class BaseLeafPinMapResource(BasePinMapResource):
  """Abstract base class for a resource that does not delegate any further (leaf-level) - such as a pin."""


class BaseDelegatingPinMapResource(BasePinMapResource):
  """Abstract base class for a resource that delegates inner resources."""


class PinResource(BaseLeafPinMapResource):
  """A resource for a single chip pin, which can be one of several port types (eg, an ADC and DIO sharing a pin)."""
  def __init__(self, pin: str, name_models: dict[str, CircuitPort]):
    self.pin = pin
    self.name_models = name_models

  def mappable_port_types(self) -> List[Type[Port]]:
    return [type(port_model) for name, port_model in self.name_models]


class PeripheralAnyPinResource(BaseDelegatingPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports must be delegated to another resource,
  any resource of matching type. Used for chips with a full switch matrix.
  The port model here should have empty models for the internal ports, so the models can be assigned from the inner
  resource. This allows things like digital IOs in a peripheral to inherit from the pin-level definition."""
  def __init__(self, name: str, port_model: Bundle):
    self.name = name
    self.port_model = port_model

  def mappable_port_types(self) -> List[Type[Port]]:
    return type(self.port_model)


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

  def mappable_port_types(self) -> List[Type[Port]]:
    return type(self.port_model)


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
