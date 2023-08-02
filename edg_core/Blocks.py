from __future__ import annotations

import inspect
import itertools
from abc import abstractmethod
from enum import Enum
from typing import *

import edgir
from .Array import BaseVector, Vector
from .Binding import AssignBinding, NameBinding
from .ConstraintExpr import ConstraintExpr, BoolExpr, ParamBinding, AssignExpr, StringExpr, BoolLike
from .Core import Refable, HasMetadata, builder, SubElementDict, non_library, EltPropertiesBase
from .HdlUserExceptions import *
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet
from .Ports import BasePort, Port

if TYPE_CHECKING:
  from .Link import Link


class Connection():
  """An incremental connection builder, that validates additional ports as they are added so
  the stack trace can provide the problematic statement."""

  @staticmethod
  def _baseport_leaf_type(port: BasePort) -> Port:
    if isinstance(port, Port):
      return port
    elif isinstance(port, BaseVector):
      return Connection._baseport_leaf_type(port._get_elt_sample())
    else:
      raise ValueError(f"Unknown BasePort subtype {port}")

  class ConnectedLink(NamedTuple):  # link-mediated connection (including bridged ports and inner links)
    link_type: Type[Link]
    is_link_array: bool
    bridged_connects: List[Tuple[BasePort, edgir.LocalPath]]  # external / boundary port <> link port, invalid in links
    link_connects: List[Tuple[BasePort, edgir.LocalPath]]  # internal block port <> link port

  class Export(NamedTuple):  # direct export (1:1, single or vector)
    is_array: bool
    external_port: BasePort
    internal_port: BasePort

  def __init__(self, parent: BaseBlock, flatten: bool) -> None:
    self.parent = parent
    self.flatten = flatten  # vectors are treated as connected to the same link (instead of a link array)

    self.ports: List[BasePort] = []  # all connected ports

    # mutable state for links, initialized when a link is first inferred
    self.link_instance: Optional[Link] = None  # link instance, if connects have built up to be a link
    self.is_link_array = False
    self.link_connected_ports: IdentityDict[BasePort, List[BasePort]] = IdentityDict()  # link port -> [connected ports]
    self.bridged_ports: IdentityDict[BasePort, BasePort] = IdentityDict()  # external port -> internal port on bridge
    self.available_link_ports_by_type: Dict[Type[Port], List[BasePort]] = {}  # sorted by port order

  def _is_export(self) -> Optional[Tuple[BasePort, BasePort]]:  # returns (external, internal) ports if export
    if len(self.ports) != 2:  # two ports, check if it's an export
      return None
    port0 = self.ports[0]
    port1 = self.ports[1]
    if port0._type_of() != port1._type_of():
      return None
    if port0._block_parent() is self.parent and not port1._block_parent() is self.parent:
      return (port0, port1)
    elif port1._block_parent() is self.parent and not port0._block_parent() is self.parent:
      return (port1, port0)
    else:
      return None

  def add_ports(self, ports: Iterable[BasePort]):
    from .HierarchyBlock import Block
    from .Link import Link

    self.ports.extend(ports)
    if len(self.ports) < 1:
      return  # empty connection, doesn't exist

    port0 = self.ports[0]  # first port is special, eg to determine link type
    if len(self.ports) == 1:
      if not (self.flatten and isinstance(port0, BaseVector)):  # flatten can result in multiple connections
        return  # single element connection, can be a naming operation
    elif len(self.ports) == 2:
      is_export = self._is_export()
      if is_export:
        (ext_port, int_port) = is_export
        if ext_port._get_initializers([]):
          raise UnconnectableError(f"Connected boundary port {ext_port._name_from(self.parent)} may not have initializers")
        return  # is an export, not a connection

    # otherwise, is a link-mediated connection
    if self.link_instance is None:  # if link not yet defined, create using the first port as authoritative
      ports_to_connect: Iterable[BasePort] = self.ports  # new link, need to allocate all ports
      # initialize mutable state
      link_type = self._baseport_leaf_type(port0).link_type
      link = self.link_instance = link_type()
      self.is_link_array = isinstance(port0, BaseVector) and not self.flatten
      assert not self.link_connected_ports
      assert not self.bridged_ports
      assert not self.available_link_ports_by_type
      for name, port in link._ports.items():
        self.available_link_ports_by_type.setdefault(type(self._baseport_leaf_type(port)), []).append(port)
    else:
      link = self.link_instance
      ports_to_connect = ports  # other ports previously allocated, only allocate new port

    for port in ports_to_connect:
      if isinstance(self.parent, Block):  # check if bridge is needed
        if port._block_parent() is self.parent:
          if port._get_initializers([]):
            raise UnconnectableError(f"Connected boundary port {port._name_from(self.parent)} may not have initializers")
          if not isinstance(port, Port):
            raise UnconnectableError(f"Can't generate bridge for non-Port {port._name_from(self.parent)}")

          bridge = port._bridge()
          if bridge is None:
            raise UnconnectableError(f"No bridge for {port._name_from(self.parent)}")
          link_facing_port = self.bridged_ports[port] = bridge.inner_link
        else:
          link_facing_port = port
      elif isinstance(self.parent, Link):  # links don't bridge, all ports are treated as internal
        if port._block_parent() is not self.parent:
          raise UnconnectableError(f"Port {port._name_from(self.parent)} not in containing link")
        link_facing_port = port
      else:
        raise ValueError(f"unknown parent {self.parent}")

      if isinstance(link_facing_port, BaseVector):
        if not self.is_link_array and not self.flatten:
          raise UnconnectableError(f"Can't connect array and non-array ports without flattening")

      # allocate the connection
      if self._baseport_leaf_type(link_facing_port).link_type is not type(link):
        raise UnconnectableError(f"Can't connect {port._name_from(self.parent)} to link of type {type(link)}")
      port_type = type(self._baseport_leaf_type(link_facing_port))
      allocatable_link_ports = self.available_link_ports_by_type.get(port_type, None)
      if allocatable_link_ports is None:
        raise UnconnectableError(f"No link port for {port._name_from(self.parent)} of type {port_type}")
      if not allocatable_link_ports:
        raise UnconnectableError(f"No remaining link ports to {port._name_from(self.parent)}")

      allocated_link_port = allocatable_link_ports[0]
      if isinstance(allocated_link_port, BaseVector):  # array on link side, can connected multiple ports
        pass
      else:  # single port on link side, consumed
        assert allocated_link_port not in self.link_connected_ports
        allocatable_link_ports.pop(0)

      self.link_connected_ports.setdefault(allocated_link_port, []).append(port)

  def make_connection(self) -> Optional[Union[ConnectedLink, Export]]:
    if len(self.ports) < 1:
      return None  # empty connection, doesn't exist

    port0 = self.ports[0]
    if len(self.ports) == 1:
      if not (self.flatten and isinstance(port0, BaseVector)):
        return None

    is_export = self._is_export()
    if is_export:
      (ext_port, int_port) = is_export
      return Connection.Export(isinstance(ext_port, BaseVector), ext_port, int_port)

    bridged_connects: List[Tuple[BasePort, edgir.LocalPath]] = []
    link_connects: List[Tuple[BasePort, edgir.LocalPath]] = []
    assert self.link_instance is not None
    link_ref_map = self.link_instance._get_ref_map_allocate(edgir.LocalPath())
    for link_port, connected_ports in self.link_connected_ports.items():
      link_ref = link_ref_map[link_port]
      for connected_port in connected_ports:
        bridged_port = self.bridged_ports.get(connected_port, None)
        if bridged_port is None:  # direct connection, no bridge
          link_connects.append((connected_port, link_ref))
        else:  # bridge
          bridged_connects.append((connected_port, link_ref))

    return Connection.ConnectedLink(type(self.link_instance), self.is_link_array, bridged_connects, link_connects)


class BlockElaborationState(Enum):
  pre_init = 1  # not sure if this is needed, doesn't actually get used
  init = 2
  post_init = 3
  contents = 4
  post_contents = 5
  generate = 6
  post_generate = 7


BaseBlockEdgirType = TypeVar('BaseBlockEdgirType', bound=edgir.BlockLikeTypes)

class DescriptionStringElts():
  @abstractmethod
  def set_elt_proto(self, pb, ref_map=None):
    raise NotImplementedError


class DescriptionString():
  def __init__(self, *elts: Union[str, DescriptionStringElts]):
    self.elts = elts

  def add_to_proto(self, pb, ref_map):
    for elt in self.elts:
      if isinstance(elt, DescriptionStringElts):
        elt.set_elt_proto(pb, ref_map)
      elif isinstance(elt, str):
        new_phrase = pb.description.add()
        new_phrase.text = elt
    return pb

  class FormatUnits(DescriptionStringElts):
    ref: ConstraintExpr
    units: str
    def __init__(self, ref: ConstraintExpr, units: str):
      self.ref = ref
      self.units = units

    def set_elt_proto(self, pb, ref_map):
      new_phrase = pb.description.add()
      new_phrase.param.path.CopyFrom(ref_map[self.ref])
      new_phrase.param.unit = self.units


AbstractBlockProperty = EltPropertiesBase()

@non_library
class BaseBlock(HasMetadata, Generic[BaseBlockEdgirType]):
  """Base block that has ports (IOs), parameters, and constraints between them.
  """
  # __init__ should initialize the object with structural information (parameters, fields)
  # as well as optionally initialization (parameter defaults)
  def __init__(self) -> None:
    self._parent: Optional[Union[BaseBlock, Port]]  # refined from Optional[Refable] in base LibraryElement

    super().__init__()

    self._elaboration_state = BlockElaborationState.init

    self.description: Optional[DescriptionString] = None   # additional string field to be displayed as part of the tooltip for blocks

    # TODO delete type ignore after https://github.com/python/mypy/issues/5374
    self._parameters: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr)  # type: ignore
    self._ports: SubElementDict[BasePort] = self.manager.new_dict(BasePort)  # type: ignore
    self._required_ports = IdentitySet[BasePort]()
    self._connects = self.manager.new_dict(Connection, anon_prefix='anon_link')
    self._connects_by_port = IdentityDict[BasePort, Connection]()  # port -> connection
    self._connect_delegateds = IdentityDict[Connection, List[Connection]]()  # for net joins, joined connect -> prior connects
    self._constraints: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr, anon_prefix='anon_constr')  # type: ignore

    self._name = StringExpr()._bind(NameBinding(self))

  def _all_delegated_connects(self) -> IdentitySet[Connection]:
    """Returns all the prior connects that have been superseded by a joined connect"""
    return IdentitySet(*itertools.chain(*self._connect_delegateds.values()))

  def _all_connects_of(self, base: Connection) -> IdentitySet[Connection]:
    """Returns all connects (including prior / superseded connects) for a joined connect"""
    frontier = [base]
    delegated_connects = IdentitySet[Connection]()
    while frontier:
      cur = frontier.pop()
      if cur in delegated_connects:
        continue
      delegated_connects.add(cur)
      frontier.extend(self._connect_delegateds.get(cur, []))

    return delegated_connects

  def _post_init(self):
    assert self._elaboration_state == BlockElaborationState.init
    self._elaboration_state = BlockElaborationState.post_init

  def name(self) -> StringExpr:
    return self._name

  """Overload this method to define the contents of this block"""
  def contents(self):
    pass

  @abstractmethod
  def _def_to_proto(self) -> BaseBlockEdgirType:
    raise NotImplementedError

  def _elaborated_def_to_proto(self) -> BaseBlockEdgirType:
    assert self._elaboration_state == BlockElaborationState.post_init
    self._elaboration_state = BlockElaborationState.contents
    self.contents()
    self._elaboration_state = BlockElaborationState.post_contents
    return self._def_to_proto()

  def _populate_def_proto_block_base(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    """Populates the structural parts of a block proto: parameters, ports, superclasses"""
    assert self._elaboration_state == BlockElaborationState.post_contents or \
           self._elaboration_state == BlockElaborationState.post_generate

    self._parameters.finalize()
    self._ports.finalize()

    if (self.__class__, AbstractBlockProperty) in self._elt_properties:
      assert isinstance(pb, edgir.HierarchyBlock)
      pb.is_abstract = True
      default_refinement_fn = self._elt_properties[(self.__class__, AbstractBlockProperty)]
      if default_refinement_fn is not None:
        default_refinement = default_refinement_fn()
        assert inspect.isclass(default_refinement), "default refinement must be a type"
        assert issubclass(default_refinement, self.__class__), "default refinement must be a subclass"
        pb.default_refinement.target.name = default_refinement._static_def_name()

    pb.self_class.target.name = self._get_def_name()

    direct_bases, indirect_bases = self._get_bases_of(BaseBlock)  # type: ignore
    for cls in direct_bases:
      pb.superclasses.add().target.name = cls._static_def_name()
    for cls in indirect_bases:
      pb.super_superclasses.add().target.name = cls._static_def_name()

    for (name, param) in self._parameters.items():
      assert isinstance(param.binding, ParamBinding)
      edgir.add_pair(pb.params, name).CopyFrom(param._decl_to_proto())

    for (name, port) in self._ports.items():
      edgir.add_pair(pb.ports, name).CopyFrom(port._instance_to_proto())

    ref_map = self._get_ref_map(edgir.LocalPath())  # TODO dedup ref_map
    for (name, port) in self._ports.items():
      if port in self._required_ports:
        if isinstance(port, Port):
          edgir.add_pair(pb.constraints, f'(reqd){name}').CopyFrom(
            port.is_connected()._expr_to_proto(ref_map)
          )
        elif isinstance(port, Vector):
          edgir.add_pair(pb.constraints, f'(reqd){name}').CopyFrom(
            (port.length() > 0)._expr_to_proto(ref_map)
          )
        else:
          raise ValueError(f"unknown non-optional port type {port}")

    self._constraints.finalize()  # needed for source locator generation

    ref_map = self._get_ref_map(edgir.LocalPath())
    self._populate_metadata(pb.meta, self._metadata, ref_map)

    return pb

  def _populate_def_proto_port_init(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    ref_map = self._get_ref_map(edgir.LocalPath())  # TODO dedup ref_map

    for (name, port) in self._ports.items():
      for (param, path, initializer) in port._get_initializers([name]):
        edgir.add_pair(pb.constraints, f"(init){'.'.join(path)}").CopyFrom(
          AssignBinding.make_assign(param, param._to_expr_type(initializer), ref_map)
        )
    return pb

  def _populate_def_proto_param_init(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    ref_map = self._get_ref_map(edgir.LocalPath())  # TODO dedup ref_map
    for (name, param) in self._parameters.items():
      if param.initializer is not None:
        edgir.add_pair(pb.constraints, f'(init){name}').CopyFrom(
          AssignBinding.make_assign(param, param.initializer, ref_map)
        )
    return pb

  def _populate_def_proto_block_contents(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    """Populates the contents of a block proto: constraints"""
    assert self._elaboration_state == BlockElaborationState.post_contents or \
           self._elaboration_state == BlockElaborationState.post_generate

    self._constraints.finalize()

    ref_map = self._get_ref_map(edgir.LocalPath())

    for (name, constraint) in self._constraints.items():
      edgir.add_pair(pb.constraints, name).CopyFrom(constraint._expr_to_proto(ref_map))

    return pb

  def _populate_def_proto_description(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    description = self.description
    assert(description is None or isinstance(description, DescriptionString))
    if isinstance(description, DescriptionString):
      pb = description.add_to_proto(pb, self._get_ref_map(edgir.LocalPath()))

    return pb

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    return super()._get_ref_map(prefix) + IdentityDict(
      [(self.name(), edgir.localpath_concat(prefix, edgir.NAME))],
      *[param._get_ref_map(edgir.localpath_concat(prefix, name)) for (name, param) in self._parameters.items()],
      *[port._get_ref_map(edgir.localpath_concat(prefix, name)) for (name, port) in self._ports.items()]
    )

  def _bind_in_place(self, parent: Union[BaseBlock, Port]):
    self._parent = parent

  SelfType = TypeVar('SelfType', bound='BaseBlock')
  def _bind(self: SelfType, parent: Union[BaseBlock, Port]) -> SelfType:
    """Returns a clone of this object with the specified binding. This object must be unbound."""
    assert self._parent is None, "can't clone bound block"
    assert builder.get_curr_context() is self._lexical_parent, "can't clone to different context"
    clone = type(self)(*self._initializer_args[0], **self._initializer_args[1])  # type: ignore
    clone._bind_in_place(parent)
    return clone

  def _check_constraint(self, constraint: ConstraintExpr) -> None:
    def check_subexpr(expr: Union[ConstraintExpr, BasePort]) -> None:  # TODO rewrite this whole method
      if isinstance(expr, ConstraintExpr) and isinstance(expr.binding, ParamBinding):
        if isinstance(expr.parent, BaseBlock):
          block_parent = expr.parent
        elif isinstance(expr.parent, BasePort):
          block_parent = cast(BaseBlock, expr.parent._block_parent())  # TODO make less ugly
          assert block_parent is not None
        else:
          raise ValueError(f"unknown parent {expr.parent} of {expr}")

        if isinstance(block_parent._parent, BasePort):
          block_parent_parent: Any = block_parent._parent._block_parent()
        else:
          block_parent_parent = block_parent._parent

        if not (block_parent is self or block_parent_parent is self):
          raise UnreachableParameterError(f"In {type(self)}, constraint references unreachable parameter {expr}. "
                                          "Only own parameters, or immediate contained blocks' parameters can be accessed. "
                                          "To pass in parameters from constructors, don't forget @init_in_parent")
      elif isinstance(expr, BasePort):
        block_parent = cast(BaseBlock, expr._block_parent())
        assert block_parent is not None
        if not block_parent is self or block_parent._parent is self:
          raise UnreachableParameterError(f"In {type(self)}, constraint references unreachable port {expr}. "
                                          "Only own ports, or immediate contained blocks' ports can be accessed. "
                                          "To pass in parameters from constructors, don't forget @init_in_parent")

    for subexpr in constraint._get_exprs():
      check_subexpr(subexpr)

  def require(self, constraint: BoolLike, name: Optional[str] = None, *, unchecked: bool=False) -> BoolExpr:
    constraint_typed = BoolExpr._to_expr_type(constraint)
    if not isinstance(name, (str, type(None))):
      raise TypeError(f"name to constrain(...) must be str or None, got {name} of type {type(name)}")

    if not unchecked:  # before we have const prop need to manually set nested params
      self._check_constraint(constraint_typed)

    self._constraints.register(constraint_typed)

    if name:  # TODO unify naming API with everything else?
      self.manager.add_element(name, constraint_typed)

    return constraint_typed

  ConstrType = TypeVar('ConstrType')
  def assign(self, target: ConstraintExpr[ConstrType, Any],
             value: Union[ConstraintExpr[ConstrType, Any], ConstrType],
             name: Optional[str] = None) -> AssignExpr:
    if not isinstance(target, ConstraintExpr):
      raise TypeError(f"target to assign(...) must be ConstraintExpr, got {target} of type {type(target)}")
    if not isinstance(name, (str, type(None))):
      raise TypeError(f"name to constrain(...) must be str or None, got {name} of type {type(name)}")

    self._check_constraint(target)
    expr_value = target._to_expr_type(value)
    self._check_constraint(expr_value)

    constraint = AssignExpr()._bind(AssignBinding(target, expr_value))
    self._constraints.register(constraint)

    if name:  # TODO unify naming API with everything else?
      self.manager.add_element(name, constraint)

    return constraint

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, *, optional: bool = False) -> T:
    """Registers a port for this Block"""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can't call Port(...) outside __init__",
                                 "call Port(...) inside __init__ only, and remember to call super().__init__()")
    if not isinstance(tpe, BasePort):
      raise TypeError(f"param to Port(...) must be Port, got {tpe} of type {type(tpe)}")

    elt = tpe._bind(self)
    self._ports.register(elt)

    if not optional:
      self._required_ports.add(elt)

    return elt

  ConstraintType = TypeVar('ConstraintType', bound=ConstraintExpr)
  def Parameter(self, tpe: ConstraintType) -> ConstraintType:
    """Registers a parameter for this Block"""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can't call Parameter(...) outside __init__",
                                 "call Parameter(...) inside __init__ only, and remember to call super().__init__()")
    if not isinstance(tpe, ConstraintExpr):
      raise TypeError(f"param to Parameter(...) must be ConstraintExpr, got {tpe} of type {type(tpe)}")

    elt = tpe._bind(ParamBinding(self))
    self._parameters.register(elt)
    if elt.initializer is not None:
      self._check_constraint(elt.initializer)

    return elt

  def connect(self, *connects: Union[BasePort, Connection], flatten=False) -> Connection:
    for connect in connects:
      if not isinstance(connect, (BasePort, Connection)):
        raise TypeError(f"param to connect(...) must be BasePort or Connection, got {connect}")

    connects_ports = [connect for connect in connects if isinstance(connect, BasePort)]
    connects_connects = [connect for connect in connects if isinstance(connect, Connection)]

    connects_ports_new = []
    connects_ports_connects = []
    for port in connects_ports:
      port_connect = self._connects_by_port.get(port, None)
      if port_connect is None:
        connects_ports_new.append(port)
      else:
        connects_ports_connects.append(port_connect)

    existing_connects = connects_connects + connects_ports_connects
    if not existing_connects:
      connect = Connection(self, flatten)
      self._connects.register(connect)
    else:  # append to (potentially multiple) existing connect
      connect = existing_connects[0]  # first one is authoritative
      connect_flattens = set([connect.flatten for connect in existing_connects])
      assert len(connect_flattens) == 1, "all existing connects must have same flatten"
      assert connect_flattens.pop() == flatten, "flatten must be equivalent to existing connect"

      for merge_connect in reversed(existing_connects[1:]):  # preserve order
        connect.add_ports(merge_connect.ports)
        for port in merge_connect.ports:
          self._connects_by_port.update(port, connect)
        self._connect_delegateds.setdefault(connect, []).append(merge_connect)

    for port in connects_ports_new:
      if port._block_parent() is not self:
        enclosing_block = port._block_parent()
        assert enclosing_block is not None
        if enclosing_block._parent is not self:
          raise UnconnectableError("Inaccessible port for connection")
      self._connects_by_port[port] = connect
    connect.add_ports(connects_ports_new)

    return connect

  def ref_to_proto(self) -> str:
    return self.__class__.__module__ + "." + self.__class__.__name__
