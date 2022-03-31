import itertools
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


class UserAssignmentDict:
  """A recursive dict mapping for user assignment strings, structured as a dict keyed by the top-level prefix of the
  assignment name. Contains a root (that is string-valued) and recursive-valued elements."""
  @staticmethod
  def from_string(assignments_spec: str) -> 'UserAssignmentDict':
    def parse_elt(assignment_spec: str) -> Tuple[List[str], str]:
      assignment_split = assignment_spec.split('=')
      assert len(assignment_split) == 2, f"bad assignment spec {assignments_spec}"
      return (assignment_split[0].split('.'), assignment_split[1])
    assignment_spec_list = [parse_elt(assignment) for assignment in assignments_spec.split(';') if assignment]
    root, user_assignments = UserAssignmentDict._from_list(assignment_spec_list, [])
    if root is not None:
      raise BadUserAssignError(f"unexpected root assignment to {root}")
    return user_assignments

  @staticmethod
  def _from_list(assignment_spec_list: List[Tuple[List[str], str]], name: List[str]) -> \
      Tuple[Optional[str], 'UserAssignmentDict']:
    """Given a list of parsed assignment specs [([named path], resource/pin)], extracts the first component of the
    path as the dict key, and remaps each entry to only contain the path postfix.
    If the path is empty, it gets mapped to the empty-string key, preserving the empty path."""
    root_assigns = set[str]()
    dict_out: dict[str, List[Tuple[List[str], str]]] = {}
    for (named_path, pin) in assignment_spec_list:
      if not named_path:
        root_assigns.add(pin)
      else:
        dict_out.setdefault(named_path[0], []).append((named_path[1:], pin))
    if len(root_assigns) >= 1:
      if len(root_assigns) > 1:
        raise BadUserAssignError(f"multiple assigns to {'.'.join(name)}: {','.join(root_assigns)}")
      root_assign: Optional[str] = root_assigns.pop()
    else:
      root_assign = None
    return (root_assign, UserAssignmentDict(dict_out, name))

  def __init__(self, elts: dict[str, List[Tuple[List[str], str]]], name: List[str]):
    self.elts = elts
    self.name = name
    self.marked = set[str]()

  def contains_elt(self, elt: str) -> bool:
    """Returns whether an element is still in the dict, without marking the element as read."""
    return elt in self.elts

  def get_elt(self, elt: str) -> Tuple[Optional[str], 'UserAssignmentDict']:
    """Returns the top-level assignment for an element (or None, if no entry), plus the recursive UserAssignDict.
    Marks the element as read."""
    """Returns a sub-dict assignment, or an empty UserAssignmentDict if no entry present. Marks the element as read."""
    if elt in self.elts:
      self.marked.add(elt)
      return self._from_list(self.elts[elt], self.name + [elt])
    else:
      return (None, UserAssignmentDict({}, self.name + [elt]))

  def check_empty(self) -> None:
    """Checks that all assignments have been processed, otherwise raises a BadUserAssignError."""
    unprocessed = set(self.elts.keys()).difference(self.marked)
    if unprocessed:
      raise BadUserAssignError(f"unprocessed assignments in {'.'.join(self.name)}: {unprocessed}")


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

  def assign(self, port_types_names: List[Tuple[Type[Port], List[str]]], assignments_spec: str = "") -> \
      List[AssignedResource]:
    """Performs port assignment given a list of port types and their names, and optional user-defined pin assignments
    (which may be empty). Names may be duplicated (either within a port type, or across port types), and multiple
    records will show up accordingly in the output data structure.
    Returns a list of assigned ports, structured as a port model (set recursively for bundle ports), the input name,
    and pin assignment as a pin string for leaf ports, or a dict (possibly recursive) for bundles."""
    # mutable data structure, assignments removed as they are processed
    user_assignments = UserAssignmentDict.from_string(assignments_spec)

    # mutable data structure, resources will be removed as they are assigned
    assignable_resources_by_type: dict[Type[Port], List[BasePinMapResource]] = {}
    for resource in self.resources:
      for supported_type in self._resource_port_types(resource):
        assignable_resources_by_type.setdefault(supported_type, []).append(resource)

    def mark_resources_used(resources: List[BasePinMapResource]):
      for resource in resources:
        for supported_type in self._resource_port_types(resource):
          assignable_resources_by_type[supported_type].remove(resource)

    # unlike the above, resources are not deleted from this
    assignable_resources_by_name: dict[str, List[BasePinMapResource]] = {}
    for resource in self.resources:
      for resource_name in self._resource_names(resource):
        assignable_resources_by_name.setdefault(resource_name, []).append(resource)

    assigned_resources: List[AssignedResource] = []

    def try_assign_resource(port_type: Type[Port], port_name: str, resource: BasePinMapResource,
                            user_assignments: UserAssignmentDict) -> \
        Optional[Tuple[AssignedResource, List[BasePinMapResource]]]:
      """Try to assign a port to the specified resource, returning any resources used by this mapping and the
      pin mapping, or None if there are no satisfying mappings starting with this resource."""
      if isinstance(resource, PinResource):  # single pin: just assign it
        user_assignments.check_empty()
        resource_name, resource_model = resource.get_name_model_for_type(port_type)
        assigned_resource = AssignedResource(resource_model, port_name, resource_name, resource.pin)
        return (assigned_resource, [resource])
      elif isinstance(resource, PeripheralFixedPin):  # fixed pin: check user-assignment, or assign first
        inner_map = {}
        for (inner_name, inner_pins) in resource.inner_allowed_pins.items():  # TODO should this be recursive?
          inner_assignment, inner_assignments = user_assignments.get_elt(inner_name)

          if inner_assignment is not None:
            if inner_assignment not in inner_pins:
              raise BadUserAssignError(f"invalid assignment to {port_name}.{inner_name}: {inner_assignment}")
            inner_map[inner_name] = inner_assignment
          else:
            inner_map[inner_name] = inner_pins[0]
          inner_assignments.check_empty()

        user_assignments.check_empty()
        assigned_resource = AssignedResource(resource.port_model, port_name, resource.name, inner_map)
        return (assigned_resource, [resource])
      elif isinstance(resource, (PeripheralAnyPinResource, PeripheralFixedResource)):  # any-pin: delegate allocation
        inner_map = {}
        full_model = resource.port_model
        pin_resources: List[BasePinMapResource] = [resource]
        for (inner_name, inner_model) in resource.port_model._ports.items():
          if type(inner_model) in self.transforms:  # apply transform to search for the resource type, if needed
            inner_type = self.transforms[type(inner_model)][0]
          else:
            inner_type = type(inner_model)
          inner_user_assignment, inner_user_assignments = user_assignments.get_elt(inner_name)

          resource_pool = assignable_resources_by_type[inner_type]
          resource_pool = [resource for resource in resource_pool if resource not in pin_resources]
          if isinstance(resource, PeripheralFixedResource):  # filter further by allowed pins for this peripheral
            peripheral_allowed_names = resource.inner_allowed_names.get(inner_name, [])
            peripheral_allowed = list(itertools.chain(*[assignable_resources_by_name.get(name, [])
                                                        for name in peripheral_allowed_names]))
            resource_pool = [resource for resource in resource_pool if resource in peripheral_allowed]

          recursive_assignment = assign_port_type(resource_pool, inner_type, f'{port_name}.{inner_name}',
                                                  inner_user_assignment, inner_user_assignments)
          if recursive_assignment is None:
            return None
          inner_resource, inner_pin_resources = recursive_assignment
          pin_resources.extend(inner_pin_resources)
          assert isinstance(inner_resource.pin, str)
          inner_map[inner_name] = inner_resource.pin
          if type(inner_model) in self.transforms:  # apply transform to search for the resource type, if needed
            recursive_inner_model = self.transforms[type(inner_model)][1](inner_resource.port_model)
          else:
            recursive_inner_model = inner_resource.port_model
          # TODO assign to outer model

        user_assignments.check_empty()
        assigned_resource = AssignedResource(full_model, port_name, resource.name, inner_map)
        return (assigned_resource, pin_resources)
      else:
        raise NotImplementedError(f"unsupported resource type {resource}")

    def assign_port_type(resource_pool: List[BasePinMapResource],
                         port_type: Type[Port], port_name: str, user_assignment: Optional[str],
                         inner_assignments: UserAssignmentDict) -> \
                        Optional[Tuple[AssignedResource, List[BasePinMapResource]]]:
      if user_assignment is not None:  # filter the available resources to the assigned ones
        assigned_resources = assignable_resources_by_name.get(user_assignment, [])
        resource_pool = [resource for resource in resource_pool if resource in assigned_resources]
        if not resource_pool:
          raise BadUserAssignError(f"no available assign to {port_name}: {user_assignment}")

      for resource in resource_pool:  # given the available resources, assign the first one possible
        assignment = try_assign_resource(port_type, port_name, resource, inner_assignments)
        if assignment is not None:
          return assignment

      return None

    # process the ports with user-specified assignments first, to avoid potentially conflicting assigns
    unassigned_port_types_names: List[Tuple[Type[Port], str]] = []  # unpacked version of port_type_names
    for (port_type, port_names) in port_types_names:
      for port_name in port_names:
        if user_assignments.contains_elt(port_name):
          user_assignment, inner_assignments = user_assignments.get_elt(port_name)
          resource_pool = assignable_resources_by_type[port_type]
          assignment = assign_port_type(resource_pool, port_type, port_name, user_assignment, inner_assignments)
          if assignment is None:
            raise AutomaticAssignError(f"no assigns to {port_name}")

          assigned_resource, pin_resources = assignment
          mark_resources_used(pin_resources)
          assigned_resources.append(assigned_resource)
        else:
          unassigned_port_types_names.append((port_type, port_name))

    user_assignments.check_empty()

    # then automatically assign anything that wasn't user-specified
    for (port_type, port_name) in unassigned_port_types_names:
      resource_pool = assignable_resources_by_type[port_type]
      assignment = assign_port_type(resource_pool, port_type, port_name, None, user_assignments.get_elt(port_name)[1])
      if assignment is None:
        raise AutomaticAssignError(f"no assigns to {port_name}")

      assigned_resource, pin_resources = assignment
      mark_resources_used(pin_resources)
      assigned_resources.append(assigned_resource)

    return assigned_resources
