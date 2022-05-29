from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from itertools import chain
from typing import *

import edgir
from .Array import BaseVector, Vector
from .Binding import AssignBinding, NameBinding
from .ConstraintExpr import ConstraintExpr, BoolExpr, ParamBinding, AssignExpr, StringExpr
from .Core import Refable, HasMetadata, builder, SubElementDict, non_library
from .Exceptions import *
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet
from .Ports import BasePort, Port
from .StructuredMetadata import MetaNamespaceOrder

if TYPE_CHECKING:
  from .Link import Link


class Connection():
  class PortRecord(NamedTuple):  # internal structure for each connected port - TBD add debugging data
    port: BasePort

  class ConnectedLink(NamedTuple):  # link-mediated connection (including bridged ports and inner links)
    link_type: Type[Link]
    is_link_array: bool
    bridged_connects: List[Tuple[BasePort, edgir.LocalPath]]  # external / boundary port <> link port, invalid in links
    link_connects: List[Tuple[BasePort, edgir.LocalPath]]  # internal block port <> link port

  class Export(NamedTuple):  # direct export (1:1, single or vector)
    is_array: bool
    external_port: BasePort
    internal_port: BasePort

  """A data structure that tracks connected ports."""
  def __init__(self, flatten: bool) -> None:
    self.connected: List[Connection.PortRecord] = []
    self.flatten = flatten  # vectors are treated as connected to a link

  def add_ports(self, ports: Iterable[BasePort]):
    for port in ports:
      self.connected.append(Connection.PortRecord(port))

  @staticmethod
  def _baseport_leaf_type(port: BasePort) -> Port:
    if isinstance(port, Port):
      return port
    elif isinstance(port, BaseVector):
      return Connection._baseport_leaf_type(port._get_elt_sample())
    else:
      raise ValueError(f"Unknown BasePort subtype {port}")

  def ports(self) -> Iterable[BasePort]:
    return [port_record.port for port_record in self.connected]

  def contains(self, port: BasePort) -> bool:
    # TODO maybe we can maintain a parallel Set data structure to make this faster
    return True in [port is port_record.port for port_record in self.connected]

  def make_connection(self, parent: BaseBlock) -> Optional[Union[ConnectedLink, Export]]:
    from .HierarchyBlock import Block
    from .Link import Link
    ports = [port_record.port for port_record in self.connected]

    if len(ports) == 1 and not (self.flatten and isinstance(ports[0], BaseVector)):
      return None  # not a real connection, eg could be a name assignment

    elif len(ports) == 2 and ports[0]._type_of() == ports[1]._type_of() and (
          (ports[0]._block_parent() is parent and not ports[1]._block_parent() is parent) or
          (ports[1]._block_parent() is parent and not ports[0]._block_parent() is parent)):
      is_vector = isinstance(ports[0], BaseVector)
      if ports[0]._block_parent() is parent:
        return Connection.Export(is_vector, ports[0], ports[1])
      else:
        return Connection.Export(is_vector, ports[1], ports[0])

    else:  # link-mediated case
      bridged_ports_tuples: List[Tuple[BasePort, BasePort]] = []  # from link-facing-port to boundary-port
      if isinstance(parent, Link):  # links don't bridge, all ports are treated as internal
        for port in ports:
          assert port._block_parent() is parent
        link_facing_ports = ports
      elif isinstance(parent, Block):  # blocks need to create bridges
        link_facing_ports = []
        for port in ports:
          if port._block_parent() is parent:  # is boundary port that needs bridge
            assert isinstance(port, Port), "can only bridge Ports (bridged arrays not supported)"
            bridge = port._bridge()
            if bridge is None:
              raise UnconnectableError(f"no bridge for {port}")
            link_facing_ports.append(bridge.inner_link)
            bridged_ports_tuples.append((bridge.inner_link, port))
          else:  # no bridge needed
            link_facing_ports.append(port)
      else:
        raise ValueError(f"unknown parent {parent}")
      bridged_ports = IdentityDict(bridged_ports_tuples)

      is_vectors = set([isinstance(port, BaseVector) for port in link_facing_ports])
      link_types = set([self._baseport_leaf_type(port).link_type for port in link_facing_ports])

      if len(link_types) == 1:
        link_type = link_types.pop()
        link = link_type()
      else:
        raise UnconnectableError(f"Ambiguous link {link_types} for connection between {ports}")
      link_ports_by_type: Dict[Type[Port], List[BasePort]] = {}  # sorted by port order; mutable and consumed as allocated
      for name, port in link._ports.items():
        link_ports_by_type.setdefault(type(self._baseport_leaf_type(port)), []).append(port)
      link_ref_map = link._get_ref_map_allocate(edgir.LocalPath())

      if self.flatten or is_vectors == {False}:  # element connect case
        is_link_array = False
      elif is_vectors == {True}:  # vector connect case
        is_link_array = True
      else:
        raise UnconnectableError(f"Can't connect array and non-array types without flattening")

      # assign connections to link-facing ports, consuming link ports as needed
      bridged_connects: List[Tuple[BasePort, edgir.LocalPath]] = []
      link_connects: List[Tuple[BasePort, edgir.LocalPath]] = []
      for link_facing_port in link_facing_ports:
        allocatable_link_ports = link_ports_by_type[type(self._baseport_leaf_type(link_facing_port))]
        if not allocatable_link_ports:
          raise UnconnectableError(f"No remaining link ports to {link_facing_port}")
        allocated_link_port = allocatable_link_ports[0]

        if isinstance(allocated_link_port, BaseVector):  # array on link side, can connect as many as needed
          link_ref = link_ref_map[allocated_link_port]
        else:  # single port, can only connect one thing
          if not is_link_array and isinstance(link_facing_port, BaseVector):
            raise UnconnectableError("Can't connect array to link-side non-array port")
          link_ref = link_ref_map[allocated_link_port]
          allocatable_link_ports.pop(0)

        if link_facing_port in bridged_ports:
          bridged_connects.append((bridged_ports[link_facing_port], link_ref))
        else:
          link_connects.append((link_facing_port, link_ref))

      return Connection.ConnectedLink(link_type, is_link_array, bridged_connects, link_connects)


class BlockElaborationState(Enum):
  pre_init = 1  # not sure if this is needed, doesn't actually get used
  init = 2
  post_init = 3
  contents = 4
  post_contents = 5
  generate = 6
  post_generate = 7

  def __lt__(self, other):  # allow comparisons, since these states are ordered
    if self.__class__ is other.__class__:
      return self.value < other.value
    return NotImplemented


BaseBlockEdgirType = TypeVar('BaseBlockEdgirType', bound=edgir.BlockLikeTypes)
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

    # TODO delete type ignore after https://github.com/python/mypy/issues/5374
    self._parameters: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr)  # type: ignore
    self._ports: SubElementDict[BasePort] = self.manager.new_dict(BasePort)  # type: ignore
    self._required_ports = IdentitySet[BasePort]()
    self._connects = self.manager.new_dict(Connection, anon_prefix='anon_link')
    self._constraints: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr, anon_prefix='anon_constr')  # type: ignore

    self._name = StringExpr()._bind(NameBinding(self))

    self._namespace_order = self.Metadata(MetaNamespaceOrder())

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

    if (self.__class__, 'abstract') in self._elt_properties:
      assert isinstance(pb, edgir.HierarchyBlock)
      pb.is_abstract = True

    pb.self_class.target.name = self._get_def_name()

    for cls in self._get_bases_of(BaseBlock):  # type: ignore  # TODO avoid 'only concrete class' error
      super_pb = pb.superclasses.add()
      super_pb.target.name = cls._static_def_name()

    for (name, param) in self._parameters.items():
      assert isinstance(param.binding, ParamBinding)
      pb.params[name].CopyFrom(param._decl_to_proto())

    for (name, port) in self._ports.items():
      pb.ports[name].CopyFrom(port._instance_to_proto())

    self._constraints.finalize()  # needed for source locator generation

    # generate base-block order
    # TODO unified namespace order
    # TODO this also appends to end, which may not be desirable
    for name in chain(self._parameters.keys_ordered(), self._ports.keys_ordered(),
                      self._constraints.keys_ordered()):
      self._namespace_order.append(name)

    ref_map = self._get_ref_map(edgir.LocalPath())
    pb.meta.CopyFrom(self._metadata_to_proto(self._metadata, [], ref_map))

    return pb

  def _populate_def_proto_port_init(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    ref_map = self._get_ref_map(edgir.LocalPath())  # TODO dedup ref_map

    for (name, port) in self._ports.items():
      for (param, path, initializer) in port._get_initializers([name]):
        pb.constraints[f"(init){'.'.join(path)}"].CopyFrom(
          AssignBinding.make_assign(param, param._to_expr_type(initializer), ref_map)
        )
        self._namespace_order.append(f"(init){'.'.join(path)}")

    return pb

  def _populate_def_proto_param_init(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    ref_map = self._get_ref_map(edgir.LocalPath())  # TODO dedup ref_map
    for (name, param) in self._parameters.items():
      if param.initializer is not None:
        pb.constraints[f'(init){name}'].CopyFrom(
          AssignBinding.make_assign(param, param.initializer, ref_map)
        )
        self._namespace_order.append(f'(init){name}')
    return pb

  def _populate_def_proto_block_contents(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    """Populates the contents of a block proto: constraints"""
    assert self._elaboration_state == BlockElaborationState.post_contents or \
           self._elaboration_state == BlockElaborationState.post_generate

    self._constraints.finalize()

    ref_map = self._get_ref_map(edgir.LocalPath())

    for (name, constraint) in self._constraints.items():
      pb.constraints[name].CopyFrom(constraint._expr_to_proto(ref_map))

    for (name, port) in self._ports.items():
      if port in self._required_ports:
        if isinstance(port, Port):
          pb.constraints[f'(reqd){name}'].CopyFrom(
            port.is_connected()._expr_to_proto(ref_map)
          )
        elif isinstance(port, Vector):
          pb.constraints[f'(reqd){name}'].CopyFrom(
            (port.length() > 0)._expr_to_proto(ref_map)
          )
        else:
          raise ValueError(f"unknown non-optional port type {port}")
        self._namespace_order.append(f'(reqd){name}')

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

  def require(self, constraint: BoolExpr, name: Optional[str] = None, *, unchecked: bool=False) -> BoolExpr:
    if not isinstance(constraint, BoolExpr):
      raise TypeError(f"constraint to constrain(...) must be BoolExpr, got {constraint} of type {type(constraint)}")
    if not isinstance(name, (str, type(None))):
      raise TypeError(f"name to constrain(...) must be str or None, got {name} of type {type(name)}")

    if not unchecked:  # before we have const prop need to manually set nested params
      self._check_constraint(constraint)

    self._constraints.register(constraint)

    if name:  # TODO unify naming API with everything else?
      self.manager.add_element(name, constraint)

    return constraint

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
      port_connects = [connect for connect in self._connects.all_values_temp() if connect.contains(port)]
      if not port_connects:
        connects_ports_new.append(port)
      else:
        connects_ports_connects.extend(port_connects)

    existing_connects = connects_connects + connects_ports_connects
    if len(existing_connects) == 1:
      connect = existing_connects[0]
      assert connect.flatten == flatten, "flatten must be equivalent to existing connect"
    elif not existing_connects:
      connect = Connection(flatten)
      self._connects.register(connect)
    else:  # more than 1 existing connect
      raise ValueError("TODO implement net join")

    for port in connects_ports_new:
      if port._block_parent() is not self:
        enclosing_block = port._block_parent()
        assert enclosing_block is not None
        if enclosing_block._parent is not self:
          raise UnconnectableError("Inaccessible port for connection")
    connect.add_ports(connects_ports_new)

    return connect

  def ref_to_proto(self) -> str:
    return self.__class__.__module__ + "." + self.__class__.__name__
