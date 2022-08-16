import itertools
from abc import ABCMeta, abstractmethod
from typing import List, Type, Tuple, Optional, Union, Any, NamedTuple, Callable, Dict, Set

from electronics_model import *


@abstract_block
class PinMappable(Block):
  """Abstract base class for pin-mappable devices. Provides a named initializer argument for user-defined explicit
  pin mapping refinements. Actual pin mapping functionality must be implemented by the subclass.
  This may simply delegate the pin mapping to an inner block, for example for a microcontroller application circuit
  to delegate the pin mapping to the microcontroller chip block.
  """
  @init_in_parent
  def __init__(self, pin_assigns: ArrayStringLike = []) -> None:
    super().__init__()
    self.pin_assigns = self.ArgParameter(pin_assigns)
    self.actual_pin_assigns = self.Parameter(ArrayStringExpr())

  def generator_set_allocation(self, allocations: List['AllocatedResource']):
    allocation_strs = []
    for allocation in allocations:
      if allocation.pin is None:
        allocation_strs.append(f"{allocation.name}={allocation.resource_name}")
      elif isinstance(allocation.pin, str):
        allocation_strs.append(f"{allocation.name}={allocation.resource_name}, {allocation.pin}")
      elif isinstance(allocation.pin, dict):
        allocation_strs.append(f"{allocation.name}={allocation.resource_name}")
        for subport_name, (subport_pin, subport_resource) in allocation.pin.items():
          if subport_resource is not None:
            allocation_strs.append(f"{allocation.name}.{subport_name}={subport_resource}, {subport_pin}")
          else:
            allocation_strs.append(f"{allocation.name}.{subport_name}={subport_pin}")
      else:
        raise ValueError(f"unknown allocation type {allocation}")

    self.assign(self.actual_pin_assigns, allocation_strs)


class BasePinMapResource(metaclass=ABCMeta):
  """Abstract base class for a resource definition for the pin mapping utility. Because these are so intertwined with
  the actual pin mapper, these are just named data structures - the logic for handling these is in the pin mapper."""


class BaseLeafPinMapResource(BasePinMapResource):
  """Abstract base class for a resource that does not delegate any further (leaf-level) - such as a pin."""


class BaseDelegatingPinMapResource(BasePinMapResource):
  """Abstract base class for a resource that delegates inner resources."""


class PinResource(BaseLeafPinMapResource):
  """A resource for a single chip pin, which can be one of several port types (eg, an ADC and DIO sharing a pin)."""
  def __init__(self, pin: str, name_models: Dict[str, CircuitPort]):
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
  """A resource for a peripheral as a Bundle port, where the internal ports are fixed. No allocation happens.
  The internal port model must be fully defined here."""
  def __init__(self, name: str, port_model: Bundle, inner_allowed_pins: Dict[str, str]):
    self.name = name
    self.port_model = port_model
    self.inner_allowed_pins = inner_allowed_pins

  def __eq__(self, other):
    # TODO avoid using is if we can compare port model equality
    return isinstance(other, PeripheralFixedPin) and self.name == other.name and \
           self.port_model is other.port_model and self.inner_allowed_pins == other.inner_allowed_pins


class PeripheralAnyResource(BaseDelegatingPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports must be delegated to another resource,
  any resource of matching type. Used for chips with a full switch matrix.
  The port model here should have empty models for the internal ports, so the models can be assigned from the inner
  resource. This allows things like digital IOs in a peripheral to inherit from the pin-level definition."""
  def __init__(self, name: str, port_model: Bundle):
    self.name = name
    self.port_model = port_model

  def __eq__(self, other):
    # TODO avoid using is if we can compare port model equality
    return isinstance(other, PeripheralAnyResource) and self.name == other.name and \
           self.port_model is other.port_model


class PeripheralFixedResource(BaseDelegatingPinMapResource):
  """A resource for a peripheral as a Bundle port, where the internal ports must be delegated to another resource,
  of a fixed list per pin by resource name. Used for chips which have alternate pin functionality
  (sort of a very limited switch matrix).
  The port model here should have empty models for the internal ports, so the models can be assigned from the inner
  resource. This allows things like digital IOs in a peripheral to inherit from the pin-level definition."""
  def __init__(self, name: str, port_model: Bundle, inner_allowed_names: Dict[str, List[str]]):
    self.name = name
    self.port_model = port_model
    self.inner_allowed_names = inner_allowed_names

  def __eq__(self, other):
    # TODO avoid using is if we can compare port model equality
    return isinstance(other, PeripheralFixedResource) and self.name == other.name and \
           self.port_model is other.port_model and self.inner_allowed_names == other.inner_allowed_names


class AllocatedResource(NamedTuple):
  port_model: Port  # port model (including defined elements, for bundles)
  name: str  # name given by the user, bundles will have automatic postfixes
  resource_name: str  # name of the resource assigned, non-delegated bundle elements can have automatic prefixes
  # TODO recursive definition for bundles with Dict[str, AllocatedResource]? but mypy doesn't like recursive types
  pin: Union[str, None, Dict[str, Tuple[str, Optional[str]]]]  # pin number if port is leaf, or
                                                               # recursive definition for bundles (pin, resource)

  def __eq__(self, other):
    # TODO better port model check, perhaps by initializer
    return self.port_model is other.port_model and self.name == other.name and \
           self.resource_name is other.resource_name and self.pin == other.pin


# Defines a way to convert port models into related types for use in bundles, for example from the
# DigitalBidir in pin definitions to the DigitalSource/Sink used by the Uart bundle.
# Specified as entries of target port type: (source port type, conversion function)
PortTransformsType = Dict[Type, Tuple[Type, Callable]]
DefaultPortTransforms: PortTransformsType = {
  DigitalSource: (DigitalBidir, DigitalSource.from_bidir),
  DigitalSink: (DigitalBidir, DigitalSink.from_bidir),
}


class BadUserAssignError(RuntimeError):
  """Indicates an error with an user-specified assignment."""
  pass


class AutomaticAllocationError(RuntimeError):
  """If automatic assignment was unable to complete, for example if there were more assigns than resources.
  Not a fundamental error, could simply be because the simplistic assignment algorithm wasn't able to complete."""
  pass


class UserAssignmentDict:
  """A recursive dict mapping for user assignment strings, structured as a dict keyed by the top-level prefix of the
  assignment name. Contains a root (that is string-valued) and recursive-valued elements."""
  @staticmethod
  def from_spec(assignments_spec: List[str]) -> 'UserAssignmentDict':
    def parse_elt(assignment_spec: str) -> Tuple[List[str], str]:
      assignment_split = assignment_spec.split('=')
      assert len(assignment_split) == 2, f"bad assignment spec {assignment_spec}"
      return (assignment_split[0].split('.'), assignment_split[1])
    assignment_spec_list = [parse_elt(assignment) for assignment in assignments_spec]
    root, assignments = UserAssignmentDict._from_list(assignment_spec_list, [])
    if root is not None:
      raise BadUserAssignError(f"unexpected root assignment to {root}")
    return assignments

  @staticmethod
  def _from_list(assignment_spec_list: List[Tuple[List[str], str]], name: List[str]) -> \
      Tuple[Optional[str], 'UserAssignmentDict']:
    """Given a list of parsed assignment specs [([named path], resource/pin)], extracts the first component of the
    path as the dict key, and remaps each entry to only contain the path postfix.
    If the path is empty, it gets mapped to the empty-string key, preserving the empty path."""
    root_assigns: Set[str] = set()
    dict_out: Dict[str, List[Tuple[List[str], str]]] = {}
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

  def __init__(self, elts: Dict[str, List[Tuple[List[str], str]]], name: List[str]):
    self.elts = elts
    self.name = name
    self.marked: Set[str] = set()

  def contains_elt(self, elt: str) -> bool:
    """Returns whether an element is still in the dict, without marking the element as read."""
    return elt in self.elts

  def get_elt(self, elt: str) -> Tuple[Optional[str], 'UserAssignmentDict']:
    """Returns the top-level assignment for an element (or None, if no entry), plus the recursive UserAssignDict.
    Marks the element as read."""
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
  """Pin mapping utility, that takes in a definition of resources (pins and peripherals on a chip) and assigns them
  automatically, optionally with user-defined explicit assignments."""
  def __init__(self, resources: List[BasePinMapResource], transforms: Optional[PortTransformsType] = None):
    self.resources = resources
    self.transforms = DefaultPortTransforms if transforms is None else transforms

  def remap_pins(self, pinmap: Dict[str, str]) -> 'PinMapUtil':
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
        remapped_pins = {elt_name: pinmap[elt_pin] for elt_name, elt_pin in resource.inner_allowed_pins.items()
                         if elt_pin in pinmap}
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
    elif isinstance(resource, (PeripheralFixedPin, PeripheralAnyResource, PeripheralFixedResource)):
      return [type(resource.port_model)]
    else:
      raise NotImplementedError(f"unsupported resource type {resource}")

  @staticmethod
  def _resource_names(resource: BasePinMapResource) -> List[str]:
    if isinstance(resource, PinResource):
      return [resource.pin] + [resource_name for resource_name, model in resource.name_models.items()]
    elif isinstance(resource, (PeripheralFixedPin, PeripheralAnyResource, PeripheralFixedResource)):
      return [resource.name]
    else:
      raise NotImplementedError(f"unsupported resource type {resource}")

  def allocate(self, port_types_names: List[Tuple[Type[Port], List[str]]], assignments_spec: List[str] = []) -> \
      List[AllocatedResource]:
    """Performs port assignment given a list of port types and their names, and optional user-defined pin assignments
    (which may be empty). Names may be duplicated (either within a port type, or across port types), and multiple
    records will show up accordingly in the output data structure.
    Returns a list of assigned ports, structured as a port model (set recursively for bundle ports), the input name,
    and pin assignment as a pin string for leaf ports, or a dict (possibly recursive) for bundles."""
    assignments = UserAssignmentDict.from_spec(assignments_spec)

    # mutable data structure, resources will be removed as they are assigned
    free_resources_by_type: Dict[Type[Port], List[BasePinMapResource]] = {}
    for resource in self.resources:
      for supported_type in self._resource_port_types(resource):
        free_resources_by_type.setdefault(supported_type, []).append(resource)

    def mark_resource_used(resource: BasePinMapResource):
      for supported_type in self._resource_port_types(resource):
        free_resources_by_type[supported_type].remove(resource)

    # unlike the above, resources are not deleted from this
    resources_by_name: Dict[str, List[BasePinMapResource]] = {}
    for resource in self.resources:
      for resource_name in self._resource_names(resource):
        resources_by_name.setdefault(resource_name, []).append(resource)

    allocated_resources: List[AllocatedResource] = []

    def try_allocate_resource(port_type: Type[Port], port_name: str, resource: BasePinMapResource,
                              sub_assignments: UserAssignmentDict) -> AllocatedResource:
      """Try to assign a port to the specified resource, returning any resources used by this mapping and
      the pin mapping.
      Backtracking search is not implemented, this cannot fail."""
      if isinstance(resource, PinResource):  # single pin: just assign it
        sub_assignments.check_empty()
        resource_name, resource_model = resource.get_name_model_for_type(port_type)
        allocated_resource = AllocatedResource(resource_model, port_name, resource_name, resource.pin)
        return allocated_resource
      elif isinstance(resource, PeripheralFixedPin):  # fixed pin: check user-assignment, or assign first
        inner_pin_map: Dict[str, Tuple[str, Optional[str]]] = {}
        for (inner_name, inner_pin) in resource.inner_allowed_pins.items():  # TODO should this be recursive?
          inner_assignment, inner_sub_assignments = sub_assignments.get_elt(inner_name)
          if inner_assignment is not None and inner_assignment != inner_pin:
            raise BadUserAssignError(f"invalid assignment to {port_name}.{inner_name}: {inner_assignment}")

          inner_pin_map[inner_name] = (inner_pin, None)
          inner_sub_assignments.check_empty()

        sub_assignments.check_empty()
        allocated_resource = AllocatedResource(resource.port_model, port_name, resource.name, inner_pin_map)
        return allocated_resource
      elif isinstance(resource, (PeripheralAnyResource, PeripheralFixedResource)):  # any-pin: delegate allocation
        inner_pin_map = {}
        resource_model = resource.port_model  # typer gets confused if this is put directly where it is used
        inner_models = {}
        resource_name = resource.name  # typer gets confused if this is put directly where it is used
        for (inner_name, inner_model) in resource.port_model._ports.items():
          inner_type = type(inner_model)
          if inner_type in self.transforms:  # apply transform to search for the resource type, if needed
            inner_type = self.transforms[inner_type][0]

          inner_assignment, inner_sub_assignments = sub_assignments.get_elt(inner_name)

          resource_pool = free_resources_by_type[inner_type]
          if isinstance(resource, PeripheralFixedResource):  # filter further by allowed pins for this peripheral
            allowed_names = resource.inner_allowed_names.get(inner_name, [])
            allowed_resources = list(itertools.chain(*[resources_by_name.get(name, [])
                                                       for name in allowed_names]))
            resource_pool = [resource for resource in resource_pool if resource in allowed_resources]

          inner_allocation = allocate_port_type(resource_pool, inner_type, f'{port_name}.{inner_name}',
                                                inner_assignment, inner_sub_assignments)
          if inner_allocation.pin is not None:
            assert isinstance(inner_allocation.pin, str)
            inner_pin_map[inner_name] = (inner_allocation.pin, inner_allocation.resource_name)

          inner_models[inner_name] = inner_allocation.port_model
          if type(inner_model) in self.transforms:  # apply transform to search for the resource type, if needed
            inner_models[inner_name] = self.transforms[type(inner_model)][1](inner_models[inner_name])
        sub_assignments.check_empty()
        resource_model = resource_model.with_elt_initializers(inner_models)
        allocated_resource = AllocatedResource(resource_model, port_name, resource_name, inner_pin_map)
        return allocated_resource
      else:
        raise NotImplementedError(f"unsupported resource type {resource}")

    # allocates a resource greedily (or errors out), and consumes the relevant resource
    def allocate_port_type(resource_pool: List[BasePinMapResource], port_type: Type[Port], port_name: str,
                           assignment: Optional[str], sub_assignments: UserAssignmentDict) -> AllocatedResource:
      if assignment == 'NC':  # not connected, create ideal port
        return AllocatedResource(port_type(), port_name, 'NC', None)

      if assignment is not None:  # filter the available resources to the assigned ones
        allowed_resources = resources_by_name.get(assignment, [])
        resource_pool = [resource for resource in resource_pool if resource in allowed_resources]
        if not resource_pool:  # specifically is a bad assignment
          raise BadUserAssignError(f"no available allocation for {port_name}: {assignment}")

      for resource in resource_pool:  # given the available resources, assign the first one possible
        allocated = try_allocate_resource(port_type, port_name, resource, sub_assignments)
        mark_resource_used(resource)
        return allocated

      raise AutomaticAllocationError(f"no available allocation for {port_name}: {assignment}")

    # process the ports with user-specified assignments first, to avoid potentially conflicting assigns
    unallocated_port_types_names: List[Tuple[Type[Port], str]] = []  # unpacked version of port_type_names
    for (port_type, port_names) in port_types_names:
      for port_name in port_names:
        if assignments.contains_elt(port_name):
          assignment, sub_assignments = assignments.get_elt(port_name)
          resource_pool = free_resources_by_type[port_type]
          allocated_resources.append(
            allocate_port_type(resource_pool, port_type, port_name, assignment, sub_assignments))
        else:
          unallocated_port_types_names.append((port_type, port_name))

    assignments.check_empty()

    # then automatically assign anything that wasn't user-specified
    for (port_type, port_name) in unallocated_port_types_names:
      resource_pool = free_resources_by_type[port_type]
      allocated_resources.append(
        allocate_port_type(resource_pool, port_type, port_name, None, assignments.get_elt(port_name)[1]))

    return allocated_resources
