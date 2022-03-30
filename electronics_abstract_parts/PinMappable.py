from abc import ABCMeta, abstractmethod
from typing import List, Type, Tuple, Optional, Union, Any, NamedTuple, Callable

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

  def __eq__(self, other):
    # TODO avoid using is if we can compare port model equality
    return isinstance(other, PinResource) and self.pin == other.pin and self.name_models is other.name_models

  def get_name_model_for_type(self, tpe: Type[Port]) -> Tuple[str, Port]:
    for (name, model) in self.name_models.items():
      if isinstance(model, tpe):
        return (name, model)
    raise ValueError(f"no name/models of type {tpe} in PinResource with {self.name_models}")


class PeripheralFixedPin(BaseLeafPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports can be mapped to pins based on a fixed
  list of options (sort of a very limited switch matrix).
  The internal port model must be fully defined here."""
  def __init__(self, name: str, port_model: Bundle, inner_allowed_pins: dict[str, List[str]]):
    self.name = name
    self.port_model = port_model
    self.inner_allowed_pins = inner_allowed_pins

  def __eq__(self, other):
    # TODO avoid using is if we can compare port model equality
    return isinstance(other, PeripheralFixedPin) and self.name == other.name and \
           self.port_model is other.port_model and self.inner_allowed_pins == other.inner_allowed_pins


class PeripheralAnyPinResource(BaseDelegatingPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports must be delegated to another resource,
  any resource of matching type. Used for chips with a full switch matrix.
  The port model here should have empty models for the internal ports, so the models can be assigned from the inner
  resource. This allows things like digital IOs in a peripheral to inherit from the pin-level definition."""
  def __init__(self, name: str, port_model: Bundle):
    self.name = name
    self.port_model = port_model

  def __eq__(self, other):
    # TODO avoid using is if we can compare port model equality
    return isinstance(other, PeripheralAnyPinResource) and self.name == other.name and \
           self.port_model is other.port_model


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

  def __eq__(self, other):
    # TODO avoid using is if we can compare port model equality
    return isinstance(other, PeripheralFixedResource) and self.name == other.name and \
           self.port_model is other.port_model and self.inner_allowed_names == other.inner_allowed_names


class AssignedResource(NamedTuple):
  port_model: Port  # port model (including defined elements, for bundles)
  name: str  # name given by the user, bundles will have automatic postfixes
  resource: str  # name of the resource assigned, non-delegated bundle elements can have automatic prefixes
  pin: Union[str, dict[str, Any]]  # pin number if port is leaf, or recursive definition for bundles
                                   # Any is used instead of AssignedResource to avoid a cyclic definition

  def __eq__(self, other):
    # TODO better port model check, perhaps by initializer
    return self.port_model is other.port_model and self.name == other.name and self.resource is other.resource and \
           self.pin == other.pin


# Defines a way to convert port models into related types for use in bundles, for example from the
# DigitalBidir in pin definitions to the DigitalSource/Sink used by the Uart bundle.
# Specified as entries of target port type: (source port type, conversion function)
PortTransformsType = dict[Type, Tuple[Type, Callable]]
DefaultPortTransforms: PortTransformsType = {
  DigitalSource: (DigitalBidir, DigitalSource.from_bidir),
  DigitalSink: (DigitalBidir, DigitalSink.from_bidir),
}


class BadUserAssignError(RuntimeError):
  """Indicates an error with an user-specified assignment."""
  pass


class AutomaticAssignError(RuntimeError):
  """If automatic assignment was unable to complete, for example if there were more assigns than resources.
  Not a fundamental error, could simply be because the simplistic assignment algorithm wasn't able to complete."""
  pass


class PinMapUtil:
  """
  Pin mapping utility, that takes in a definition of resources (pins and peripherals on a chip) and assigns them
  automatically, optionally with user-defined explicit assignments.
  """
  def __init__(self, resources: List[BasePinMapResource], transforms: Optional[PortTransformsType] = None):
    self.resources = resources
    self.transforms = DefaultPortTransforms if transforms is None else transforms

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
    return PinMapUtil(remapped_resources, self.transforms)

  @staticmethod
  def _resource_port_types(resource: BasePinMapResource) -> List[Type[Port]]:
    if isinstance(resource, PinResource):
      return [type(model) for resource_name, model in resource.name_models.items()]
    elif isinstance(resource, (PeripheralFixedPin, PeripheralAnyPinResource, PeripheralFixedResource)):
      return [type(resource.port_model)]
    else:
      raise NotImplementedError(f"unsupported resource type {resource}")

  @staticmethod
  def _resource_names(resource: BasePinMapResource) -> List[str]:
    if isinstance(resource, PinResource):
      return [resource.pin] + [resource_name for resource_name, model in resource.name_models.items()]
    elif isinstance(resource, (PeripheralFixedPin, PeripheralAnyPinResource, PeripheralFixedResource)):
      return [resource.name]
    else:
      raise NotImplementedError(f"unsupported resource type {resource}")

  @staticmethod
  def _parse_assignment_spec(assignments_spec: str) -> List[Tuple[List[str], str]]:
    """Parses a user-specified assignment string into structured data as a list of ([named path], resource/pin)."""
    def parse_elt(assignment_spec: str) -> Tuple[List[str], str]:
      assignment_split = assignment_spec.split('=')
      assert len(assignment_split) == 2, f"bad assignment spec {assignments_spec}"
      return (assignment_split[0].split('.'), assignment_split[1])
    return [parse_elt(assignment) for assignment in assignments_spec.split(';') if assignment]

  @staticmethod
  def _group_assignment_spec(assignments_spec_parsed: List[Tuple[List[str], str]]) -> \
      dict[str, List[Tuple[List[str], str]]]:
    """Given a list of parsed assignment specs [([named path], resource/pin)], extracts the first component of the
    path as the dict key, and remaps each entry to only contain the path postfix.
    If the path is empty, it gets mapped to the empty-string key, preserving the empty path."""
    dict_out: dict[str, List[Tuple[List[str], str]]] = {}
    for (named_path, pin) in assignments_spec_parsed:
      if not named_path:
        dict_out.setdefault('', []).append(([], pin))
      else:
        dict_out.setdefault(named_path[0], []).append((named_path[1:], pin))
    return dict_out

  def assign(self, port_types_names: List[Tuple[Type[Port], List[str]]], assignments_spec: str = "") -> \
      List[AssignedResource]:
    """Performs port assignment given a list of port types and their names, and optional user-defined pin assignments
    (which may be empty). Names may be duplicated (either within a port type, or across port types), and multiple
    records will show up accordingly in the output data structure.
    Returns a list of assigned ports, structured as a port model (set recursively for bundle ports), the input name,
    and pin assignment as a pin string for leaf ports, or a dict (possibly recursive) for bundles."""
    # mutable data structure, assignments removed as they are processed
    user_assignments = self._group_assignment_spec(self._parse_assignment_spec(assignments_spec))

    # mutable data structure, resources will be removed as they are assigned
    assignable_resources_by_type: dict[Type[Port], List[BasePinMapResource]] = {}
    for resource in self.resources:
      for supported_type in self._resource_port_types(resource):
        assignable_resources_by_type.setdefault(supported_type, []).append(resource)

    def mark_resource_used(resource: BasePinMapResource):
      for supported_type in self._resource_port_types(resource):
        assignable_resources_by_type[supported_type].remove(resource)

    # unlike the above, resources are not deleted from this
    assignable_resources_by_name: dict[str, List[BasePinMapResource]] = {}
    for resource in self.resources:
      for resource_name in self._resource_names(resource):
        assignable_resources_by_name.setdefault(resource_name, []).append(resource)

    assigned_resources: List[AssignedResource] = []

    # def recursive_assign_port(...) -> None:
    #   ...

    # mutates the above structures
    def assign_port_type(port_type: Type[Port], port_name: str, assignment_spec: List[Tuple[List[str], str]]) -> \
        AssignedResource:
      grouped_assignment_spec = self._group_assignment_spec(assignment_spec)  # mutable, deleted as allocated
      available_resources = assignable_resources_by_type[port_type]

      if '' in grouped_assignment_spec:  # filter the available resources to the assigned ones
        assert len(grouped_assignment_spec['']) == 1, f"multiple assignments to {port_type} {port_name}: {grouped_assignment_spec['']}"
        assigned_resources = assignable_resources_by_name.get(grouped_assignment_spec[''][0][1], [])
        available_resources = [resource for resource in available_resources if resource in assigned_resources]
        del grouped_assignment_spec['']

        if not available_resources:
          raise BadUserAssignError(f"no available assign to {port_name}: {user_assignments}")

      assigned_resource: Optional[AssignedResource] = None
      for resource in available_resources:  # given the available resources, assign the first one possible
        if isinstance(resource, PinResource):
          resource_name, resource_model = resource.get_name_model_for_type(port_type)
          assigned_resource = AssignedResource(resource_model, port_name, resource_name, resource.pin)
          mark_resource_used(resource)
          break
        else:
          raise NotImplementedError(f"unsupported resource type {resource}")

      if len(grouped_assignment_spec) > 0:
        raise BadUserAssignError(f"unprocessed assignments in {port_name}: {user_assignments}")
      if assigned_resource is None:
        raise AutomaticAssignError(f"no available assign to {port_name}: {user_assignments}")

      return assigned_resource

    # process the ports with user-specified assignments first, to avoid potentially conflicting assigns
    unassigned_port_types_names: List[Tuple[Type[Port], str]] = []  # unpacked version of port_type_names
    for (port_type, port_names) in port_types_names:
      for port_name in port_names:
        if port_name in user_assignments:
          assigned_resources.append(assign_port_type(port_type, port_name, user_assignments[port_name]))
          del user_assignments[port_name]
        else:
          unassigned_port_types_names.append((port_type, port_name))

    if len(user_assignments) > 0:
      raise BadUserAssignError(f"unprocessed assignments: {user_assignments}")

    # then automatically assign anything that wasn't user-specified
    for (port_type, port_name) in unassigned_port_types_names:
      assigned_resources.append(assign_port_type(port_type, port_name, []))

    return assigned_resources
