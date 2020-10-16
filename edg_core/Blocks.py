from __future__ import annotations

from enum import Enum
from typing import *
from abc import abstractmethod

from . import edgir
from .Exception import *
from .Array import BaseVector, DerivedVector
from .Core import Refable, HasMetadata, builder, SubElementDict, non_library
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet
from .ConstraintExpr import ConstraintExpr, BoolExpr, ParamBinding, ParamVariableBinding
from .Ports import BasePort, Port, Bundle


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
      link_ref_map = self.link._get_ref_map(edgir.LocalPath())
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
    port_parent = port._block_parent()
    if port_parent is None:
      raise UnconnectableError(f"In {self.parent}, can't connect port model {port}, "
                               "need to assign it to a block using self.Port(...)")
    elif port_parent is not self.parent:
      if port_parent.parent is None:
        raise UnconnectableError(f"In {self.parent}, can't connect port {port}, "
                                 "belonging to a block not assigned to parent with self.Block(...)")
      elif port_parent.parent is not self.parent:
        raise UnconnectableError(f"In {self.parent}, can't connect port {port}, "
                                 "belonging to a block at level above or nested more than one level deep")
    if port_parent is not self.parent and port.parent is not port_parent:
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
    elif len(self.ports) == 2:
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
    self._constraints = self.manager.new_dict(BoolExpr, anon_prefix='anon_constr')
    self._inits = IdentityDict[Tuple[Refable, str], BoolExpr]()  # need to delay init constraint binding until after things are named

  def _post_init(self):
    assert self._elaboration_state == BlockElaborationState.init
    self._elaboration_state = BlockElaborationState.post_init

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

  @classmethod
  def _get_block_bases(cls) -> List[Type['BaseBlock']]:
    return [bcls for bcls in cls.__bases__
            if issubclass(bcls, BaseBlock) and (bcls, 'non_library') not in bcls._elt_properties]

  # TODO: can we unify PortBridge into ProtoType? Differnce seems to be in meta and repeated superclasses
  ProtoType = TypeVar('ProtoType', bound=edgir.BlockLikeTypes)
  def _populate_def_proto_block_base(self, pb: ProtoType) -> ProtoType:
    """Populates the structural parts of a block proto: parameters, ports, superclasses"""
    assert self._elaboration_state == BlockElaborationState.post_contents or \
           self._elaboration_state == BlockElaborationState.post_generate

    self._parameters.finalize()
    self._params_order = self.Metadata({str(idx): name for idx, name in enumerate(self._parameters.keys_ordered())})

    self._ports.finalize()
    self._ports_order = self.Metadata({str(idx): name for idx, name in enumerate(self._ports.keys_ordered())})

    if (self.__class__, 'abstract') in self._elt_properties:
      self.abstract = self.Metadata('abstract')

    for cls in self._get_block_bases():
      super_pb = pb.superclasses.add()
      super_pb.target.name = cls._static_def_name()

    for (name, param) in self._parameters.items():
      assert isinstance(param.binding, ParamBinding)
      pb.params[name].CopyFrom(param._decl_to_proto())

    for (name, port) in self._ports.items():
      pb.ports[name].CopyFrom(port._instance_to_proto())

    self._constraints.finalize()  # needed for source locator generation

    ref_map = self._get_ref_map(edgir.LocalPath())
    pb.meta.CopyFrom(self._metadata_to_proto(self._metadata, [], ref_map))  # needed for block ordering; TODO maybe should be in contents?

    return pb

  def _populate_def_proto_block_contents(self, pb: ProtoType) -> ProtoType:
    """Populates the contents of a block proto: constraints"""
    assert self._elaboration_state == BlockElaborationState.post_contents or \
           self._elaboration_state == BlockElaborationState.post_generate

    self._constraints.finalize()

    ref_map = self._get_ref_map(edgir.LocalPath())

    for (name, constraint) in self._constraints.items():
      pb.constraints[name].CopyFrom(constraint._expr_to_proto(ref_map))

    for ((target, prefix), constraint) in self._inits.items():
      if not constraint._is_true_lit():
        pb.constraints[prefix + self._name_of(target)].CopyFrom(constraint._expr_to_proto(ref_map))

    return pb

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    return super()._get_ref_map(prefix) + IdentityDict(
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

  def _check_constraint(self, constraint: BoolExpr) -> None:
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

  def constrain(self, constraint: BoolExpr, name: Optional[str] = None, *, unchecked: bool=False) -> BoolExpr:
    if not isinstance(constraint, BoolExpr):
      raise TypeError(f"constraint to constrain(...) must be BoolExpr, got {constraint} of type {type(constraint)}")
    if not isinstance(name, (str, type(None))):
      raise TypeError(f"name to constrain(...) must be str or None, got {name} of type {type(name)}")

    if not unchecked:  # before we have const prop need to manually set nested params
      self._check_constraint(constraint)

    self._constraints.register(constraint)

    if name:  # TODO unify naming API with everything else?
      self.manager.add_element(name, constraint)
    if not builder.stack or builder.stack[0] is self:
      self._sourcelocator[constraint] = self._get_calling_source_locator()

    return constraint

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, *, optional: bool = False, desc: Optional[str] = None, _no_init: bool = False) -> T:
    """Registers a port for this Block"""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can't call Port(...) outside __init__",
                                 "call Port(...) inside __init__ only, and remember to call super().__init__()")
    if not isinstance(tpe, BasePort):
      raise TypeError(f"param to Port(...) must be Port, got {tpe} of type {type(tpe)}")

    elt = tpe._bind(self)
    self._ports.register(elt)
    if isinstance(tpe, Port) and not _no_init:
      self._inits[elt, '(init)'] = tpe._initializer_to(elt)
    if not optional:
      self._inits[elt, '(reqd)'] = elt.is_connected()
      self._required_ports.add(elt)

    if not builder.stack or builder.stack[0] is self:
      if desc is not None:
        self._edgdoc[elt] = desc
      self._sourcelocator[elt] = self._get_calling_source_locator()

    return elt

  U = TypeVar('U', bound=ConstraintExpr)
  def Parameter(self, tpe: U, *, desc: Optional[str] = None) -> U:
    """Registers a parameter for this Block"""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can't call Parameter(...) outside __init__",
                                 "call Parameter(...) inside __init__ only, and remember to call super().__init__()")
    if not isinstance(tpe, ConstraintExpr):
      raise TypeError(f"param to Parameter(...) must be ConstraintExpr, got {tpe} of type {type(tpe)}")

    elt = tpe._bind(ParamBinding(self))
    self._parameters.register(elt)
    init_expr = tpe._initializer_to(elt)
    self._check_constraint(init_expr)
    self._inits[elt, '(init)'] = init_expr

    if not builder.stack or builder.stack[0] is self:
      if desc is not None:
        self._edgdoc[elt] = desc
      self._sourcelocator[elt] = self._get_calling_source_locator()

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

  def _def_to_proto(self) -> edgir.Link:
    for cls in self._get_block_bases():
      assert issubclass(cls, Link)

    pb = self._populate_def_proto_block_base(edgir.Link())
    pb = self._populate_def_proto_block_contents(pb)

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

    return pb

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, **kwargs) -> T:  # for links only, ports can be the less restrictive BasePort type
    # TODO better fix to get rid of type ignore
    # TODO assert can't mix vector and non-vector types of port
    return super().Port(tpe, **kwargs)  # type: ignore
