from __future__ import annotations

from enum import Enum
from typing import *
from abc import abstractmethod
from itertools import chain

import edgir
from .Exceptions import *
from .Array import BaseVector, DerivedVector, Vector
from .Core import Refable, HasMetadata, builder, SubElementDict, non_library
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet
from .Binding import AssignBinding, NameBinding
from .ConstraintExpr import ConstraintExpr, BoolExpr, ParamBinding, ParamVariableBinding, AssignExpr, StringExpr
from .Ports import BasePort, Port, Bundle
from .StructuredMetadata import MetaNamespaceOrder


class ConnectedPorts():
  """Internal data structure to track ports which are connected, infer a link, and incrementally assign connected ports
  to link ports"""
  class Connections(NamedTuple):
    """Output data structure for the upper level to generate connect statements"""
    link_type: Optional[Type[Link]]  # if None: means a direct export should be inferred
    bridged_connects: List[Tuple[BasePort, edgir.LocalPath]]  # bridged/exported port <> path from link
    direct_connects: List[Tuple[BasePort, edgir.LocalPath]]  # internal block ports <> path from link

  class ConnectState(NamedTuple):
    """Tracks connections once a link is deemed necessary"""
    link: Link  # Persistent link reference so port references are stable
    bridged_connects: List[Tuple[BasePort, BasePort]]  # bridged/exported port <> link port
    direct_connects: List[Tuple[BasePort, BasePort]]  # internal block ports <> link port

    def generate_connections(self) -> ConnectedPorts.Connections:
      link_ref_map = self.link._get_ref_map_allocate(edgir.LocalPath())
      bridged_connects = [(port, link_ref_map[tar]) for port, tar in self.bridged_connects]
      direct_connects = [(port, link_ref_map[tar]) for port, tar in self.direct_connects]
      return ConnectedPorts.Connections(type(self.link), bridged_connects, direct_connects)

  def __init__(self, parent: BaseBlock) -> None:
    self.parent = parent  # TODO a bit ugly, but we need the parent to create a block for bridge inference

    self.ports = IdentitySet[BasePort]()  # set of all ports as passed in
    self.connect: Optional[ConnectedPorts.ConnectState] = None

  def add_ports(self, ports: Iterable[BasePort]) -> None:
    self._add_ports(ports)

  def join(self, other: ConnectedPorts) -> None:
    raise NotImplementedError("net joining not implemented, connect statements should be additive")

  def _validate_connect(self, port: BasePort) -> None:
    block_parent = port._block_parent()
    if block_parent is None:
      raise UnconnectableError(f"In {self.parent}, can't connect port model {port}, "
                               "need to assign it to a block using self.Port(...)")
    elif block_parent is not self.parent:
      if block_parent.parent is None:
        raise UnconnectableError(f"In {self.parent}, can't connect port {port}, "
                                 "belonging to a block not assigned to parent with self.Block(...)")
      elif block_parent.parent is not self.parent:
        raise UnconnectableError(f"In {self.parent}, can't connect port {port}, "
                                 "belonging to a block at level above or nested more than one level deep")
    if block_parent is not self.parent and not (
        (port.parent is block_parent) or (isinstance(port.parent, Vector) and port.parent.parent is block_parent)):
      # TODO the one-level-deep vector check is a bit of a hack - this should be a bit more principled
      # note: connecting to sub-ports of parent block's exterior ports are allowed,
      # provided there is no overlap of connectionss
      raise UnconnectableError(f"In {self.parent}, can't connect port sub-element {port}, "
                               "can only connect top-level ports of internal blocks")

  def _add_ports(self, ports: Iterable[BasePort]) -> None:
    from .HierarchyBlock import Block

    for port in ports:
      self._validate_connect(port)

    self.ports.update(ports)
    ports_tuple = tuple(self.ports)

    # for some special cases, don't need to infer a link
    if len(self.ports) == 1 and not isinstance(ports_tuple[0], BaseVector):
      return  # not a real connection yet
    elif len(self.ports) == 2:  # TODO maybe need to support exported arrays on Blocks in future
      if ports_tuple[0]._type_of() == ports_tuple[1]._type_of() and (
          (ports_tuple[0]._block_parent() is self.parent and not ports_tuple[1]._block_parent() is self.parent) or
          (ports_tuple[1]._block_parent() is self.parent and not ports_tuple[0]._block_parent() is self.parent)):
        return  # exported constraint

    # ok, we need to infer a link now
    def resolve_link_type(port: BasePort) -> Type[Link]:
      if isinstance(port, Port):
        return port.link_type
      elif isinstance(port, BaseVector):
        return resolve_link_type(port._get_elt_sample())
      else:
        raise ValueError(f"Unknown BasePort subtype {port}")

    def can_connect_to(block_port: BasePort, link_port: BasePort) -> bool:
      if isinstance(block_port, BaseVector) and isinstance(link_port, BaseVector):
        return can_connect_to(block_port._get_elt_sample(), link_port._get_elt_sample())
      elif isinstance(block_port, Port) and isinstance(link_port, BaseVector):
        return can_connect_to(block_port, link_port._get_elt_sample())
      elif isinstance(block_port, BaseVector) and isinstance(link_port, Port):
        return False
      elif isinstance(block_port, Port) and isinstance(link_port, Port):
        return type(block_port) == type(link_port)
      else:
        raise ValueError(f"Can't handle connect between {type(block_port)} and {type(link_port)}")

    if self.connect is None:
      # TODO this assumes that bridging does not change a port's link type
      link_candidates = set([resolve_link_type(port) for port in ports_tuple])
      if len(link_candidates) != 1:
        raise UnconnectableError(f"Can't connect ports {ports_tuple} with ambiguous links {link_candidates}")
      self.connect = self.ConnectState((link_candidates.pop())(), [], [])

    if self.connect is not None:
      connected_ports = IdentitySet(*(
          [port for port, tar in self.connect.bridged_connects] +
          [port for port, tar in self.connect.direct_connects]))
      link_connected_ports = IdentitySet(*(
          [tar for port, tar in self.connect.bridged_connects] +
          [tar for port, tar in self.connect.direct_connects]))

      unconnected_ports = [port for port in self.ports if port not in connected_ports]
      # Free ports list is specifically ordered, for first-connect semantics
      link_free_ports = [port for name, port in self.connect.link._ports.items()
                         if port not in link_connected_ports or isinstance(port, BaseVector)]

      for port in unconnected_ports:
        if resolve_link_type(port) != type(self.connect.link):
          raise UnconnectableError(f"In {self.parent}, can't connect {port} with link type {resolve_link_type(port)} to {type(self.connect.link)}")

        if port._block_parent() is self.parent and isinstance(self.parent, Block):
          # bridge inference required, allocate the right kind of port on the link
          assert isinstance(port, Port)  # TODO this needs to be fixed for Vectors on Blocks, probably adding resolve_port_bridge_type
          bridge = port._bridge()
          if bridge is None:
            raise UnconnectableError(f"In {self.parent}, can't connect {port} because {type(port)} does not define a bridge")
          reqd_port = bridge.inner_link
        else:
          reqd_port = port

        link_connectable_ports = [link_port for link_port in link_free_ports
                                  if can_connect_to(reqd_port, link_port)]
        if not link_connectable_ports:
          raise UnconnectableError(f"In {self.parent}, can't find connection for {port} to {type(self.connect.link)}")

        link_connect_port = link_connectable_ports[0]
        if not isinstance(link_connect_port, BaseVector):
          # deallocate the port to prevent double connection
          # note, we can't use .remove since it uses __eq__ for comparison
          link_free_ports = [port for port in link_free_ports if port is not link_connect_port]

        if port._block_parent() is self.parent:
          self.connect.bridged_connects.append((port, link_connect_port))
        else:
          self.connect.direct_connects.append((port, link_connect_port))

  def generate_connections(self) -> Optional[ConnectedPorts.Connections]:
    if self.connect is not None:
      return self.connect.generate_connections()
    elif len(self.ports) == 2:  # for direct exports
      exterior_port = [port for port in self.ports if port._block_parent() is self.parent]
      internal_port = [port for port in self.ports if port._block_parent() is not self.parent]
      assert len(exterior_port) == 1 and len(internal_port) == 1
      return self.Connections(
        None,
        [(exterior_port[0], edgir.LocalPath())],  # TODO maybe have a separate type for bridged connections?
        [(internal_port[0], edgir.LocalPath())]
      )
    elif len(self.ports) == 1:
      return None
    else:
      raise ValueError("internal error: bad connection state")


class BlockElaborationState(Enum):
  pre_init = 1  # not sure if this is needed, doesn't actually get used
  init = 2
  post_init = 3
  contents = 4
  post_contents = 5
  generate = 6
  post_generate = 7


BaseBlockEdgirType = TypeVar('BaseBlockEdgirType', bound=edgir.BlockLikeTypes)
@non_library
class BaseBlock(HasMetadata, Generic[BaseBlockEdgirType]):
  """Base block that has ports (IOs), parameters, and constraints between them.
  """
  # __init__ should initialize the object with structural information (parameters, fields)
  # as well as optionally initialization (parameter defaults)
  def __init__(self) -> None:
    super().__init__()

    self.parent: Optional[Union[BaseBlock, Port]]  # actual field definition left to subclass
    self.manager_ignored.add('parent')

    self._elaboration_state = BlockElaborationState.init

    # TODO delete type ignore after https://github.com/python/mypy/issues/5374
    self._parameters: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr)  # type: ignore
    self._ports: SubElementDict[BasePort] = self.manager.new_dict(BasePort)  # type: ignore
    self._required_ports = IdentitySet[BasePort]()
    self._connects = self.manager.new_dict(ConnectedPorts, anon_prefix='anon_link')
    self._constraints: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr, anon_prefix='anon_constr')  # type: ignore

    self._name = StringExpr()._bind(ParamVariableBinding(NameBinding(self)))

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

  def _populate_def_proto_port_init(self, pb: BaseBlockEdgirType,
                                    ignore_ports: IdentitySet[BasePort] = IdentitySet()) -> BaseBlockEdgirType:
    # TODO this is structurally ugly!
    # TODO TODO: for non-generated exported initializers, check and assert default-ness
    ref_map = self._get_ref_map(edgir.LocalPath())  # TODO dedup ref_map

    def check_recursive_no_initializer(port: BasePort, path: List[str]) -> None:
      if isinstance(port, (Port, Bundle)):
        for (name, subparam) in port._parameters.items():
          assert subparam.initializer is None, f"unexpected initializer in {port} at {path}"

      if isinstance(port, Bundle):
        for (name, subport) in port._ports.items():
          check_recursive_no_initializer(subport, path + [name])
      elif isinstance(port, Vector):
        check_recursive_no_initializer(port._get_elt_sample(), path)
      # TODO needs to be something like sealed types for match comprehensiveness

    def process_port_inits(port: BasePort, path: List[str]) -> None:
      if port in ignore_ports:
        return

      if isinstance(port, (Port, Bundle)):
        for (name, subparam) in port._parameters.items():
          if subparam.initializer is not None:
            pb.constraints[f"(init){'.'.join(path + [name])}"].CopyFrom(
              AssignBinding.make_assign(subparam,
                                        subparam._to_expr_type(subparam.initializer), ref_map)
            )
            self._namespace_order.append(f"(init){'.'.join(path + [name])}")

      if isinstance(port, Bundle):
        for (name, subport) in port._ports.items():
          process_port_inits(subport, path + [name])
      elif isinstance(port, Vector):
        check_recursive_no_initializer(port._get_elt_sample(), path)
      # TODO needs to be something like sealed types for match comprehensiveness

    for (name, port) in self._ports.items():
      process_port_inits(port, [name])

    return pb

  def _populate_def_proto_param_init(self, pb: BaseBlockEdgirType,
                                    ignore_params: IdentitySet[ConstraintExpr] = IdentitySet()) -> BaseBlockEdgirType:
    ref_map = self._get_ref_map(edgir.LocalPath())  # TODO dedup ref_map
    for (name, param) in self._parameters.items():
      if param.initializer is not None and param not in ignore_params:
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
    self.parent = parent

  SelfType = TypeVar('SelfType', bound='BaseBlock')
  def _bind(self: SelfType, parent: Union[BaseBlock, Port], ignore_context: bool = False) -> SelfType:
    """Returns a clone of this object with the specified binding. This object must be unbound."""
    assert self.parent is None, "can't clone bound block"
    if not ignore_context:
      # TODO get rid of this hack, needed in Driver
      assert builder.get_curr_context() is self._parent, "can't clone to different context"
    clone = type(self)(*self._initializer_args[0], **self._initializer_args[1])  # type: ignore
    clone._bind_in_place(parent)
    return clone

  def _check_constraint(self, constraint: ConstraintExpr) -> None:
    def check_subexpr(expr: Union[ConstraintExpr, BasePort]) -> None:  # TODO rewrite this whole method
      if isinstance(expr, ConstraintExpr) and isinstance(expr.binding, (ParamVariableBinding, ParamBinding)):
        if isinstance(expr.parent, BaseBlock):
          block_parent = expr.parent
        elif isinstance(expr.parent, BasePort):
          block_parent = cast(BaseBlock, expr.parent._block_parent())  # TODO make less ugly
          assert block_parent is not None
        else:
          raise ValueError(f"unknown parent {expr.parent} of {expr}")

        if isinstance(block_parent.parent, BasePort):
          block_parent_parent: Any = block_parent.parent._block_parent()
        else:
          block_parent_parent = block_parent.parent

        if not (block_parent is self or block_parent_parent is self):
          raise UnreachableParameterError(f"In {type(self)}, constraint references unreachable parameter {expr}. "
                                          "Only own parameters, or immediate contained blocks' parameters can be accessed. "
                                          "To pass in parameters from constructors, don't forget @init_in_parent")
      elif isinstance(expr, BasePort):
        block_parent = cast(BaseBlock, expr._block_parent())
        assert block_parent is not None
        if not block_parent is self or block_parent.parent is self:
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

  def connect(self, *ports: BasePort) -> ConnectedPorts:
    for port in ports:
      if not isinstance(port, BasePort):
        raise TypeError(f"param to connect(...) must be BasePort, got {port} of type {type(port)}")

    existing_connect: Optional[ConnectedPorts] = None
    for connect in self._connects.all_values_temp():
      for port in ports:
        if port in connect.ports:
          assert existing_connect is None, "TODO implement net join"
          existing_connect = connect

    if existing_connect is None:
      existing_connect = ConnectedPorts(self)
      self._connects.register(existing_connect)

    existing_connect.add_ports(ports)

    return existing_connect

  def ref_to_proto(self) -> str:
    return self.__class__.__module__ + "." + self.__class__.__name__


@non_library
class Link(BaseBlock[edgir.Link]):
  def __init__(self) -> None:
    super().__init__()
    self.parent: Optional[Port] = None

  # Returns the ref_map, but with a trailing ALLOCATE for BaseVector ports
  def _get_ref_map_allocate(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    def map_port_allocate(ref: Refable, path: edgir.LocalPath) -> edgir.LocalPath:
      if isinstance(ref, BaseVector):
        new_path = edgir.LocalPath()
        new_path.CopyFrom(path)
        new_path.steps.append(edgir.LocalStep(allocate=''))
        return new_path
      else:
        return path

    return IdentityDict([(port, map_port_allocate(port, path))
                         for port, path in self._get_ref_map(prefix).items()])

  def _def_to_proto(self) -> edgir.Link:
    for cls in self._get_bases_of(BaseBlock):  # type: ignore  # TODO avoid 'only concrete class' error
      assert issubclass(cls, Link)

    pb = self._populate_def_proto_block_base(edgir.Link())
    pb = self._populate_def_proto_block_contents(pb)
    pb = self._populate_def_proto_param_init(pb)
    # specifically ignore the port initializers

    # actually generate the links and connects
    ref_map = self._get_ref_map(edgir.LocalPath())
    self._connects.finalize()
    self._links_order: Dict[str, str] = self.Metadata({})
    for name, connect in self._connects.items_ordered():
      self._links_order[str(len(self._links_order))] = f"{name}"

      connect_elts = connect.generate_connections()
      assert connect_elts is not None and connect_elts.link_type is not None, "bad connect definition in link"

      link_path = edgir.localpath_concat(edgir.LocalPath(), name)
      pb.links[name].lib_elem.target.name = connect_elts.link_type._static_def_name()

      for idx, (self_port, link_port_path) in enumerate(connect_elts.bridged_connects):
        # TODO handle Vector types
        if isinstance(self_port, DerivedVector):  # TODO unify once we get rid of ref_map, especially to be more robust
          pb.constraints[f"(export){name}_{idx}"].exported.exterior_port.map_extract.container.ref.CopyFrom(ref_map[self_port.base])
          pb.constraints[f"(export){name}_{idx}"].exported.exterior_port.map_extract.path.steps.add().name = self_port.base._get_elt_sample()._name_of(self_port.target)
        else:
          pb.constraints[f"(export){name}_{idx}"].exported.exterior_port.ref.CopyFrom(ref_map[self_port])
        pb.constraints[f"(export){name}_{idx}"].exported.internal_block_port.ref.CopyFrom(
          edgir.localpath_concat(link_path, link_port_path)
        )
        self._namespace_order.append(f"(export){name}_{idx}")

    return pb

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, **kwargs) -> T:  # for links only, ports can be the less restrictive BasePort type
    # TODO better fix to get rid of type ignore
    # TODO assert can't mix vector and non-vector types of port
    return super().Port(tpe, **kwargs)  # type: ignore
