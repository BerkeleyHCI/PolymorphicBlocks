from __future__ import annotations

from numbers import Number
from typing import *
from itertools import chain
import sys

from . import edgir
from .Exception import *
from .Array import Vector
from .Builder import builder
from .Blocks import BaseBlock, Link, BlockElaborationState, ConnectedPorts
from .ConstraintExpr import ConstraintExpr, BoolExpr, FloatExpr, RangeExpr, StringExpr, ParamBinding, AssignBinding
from .Core import Refable, non_library
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet
from .Ports import BasePort, Port, Bundle
from .PortTag import PortTag, Input, Output, InOut


InitType = TypeVar('InitType', bound=Callable[..., None])
def init_in_parent(fn: InitType) -> InitType:
  import inspect
  from .Builder import builder

  param_types = (bool, float, int, tuple, str, ConstraintExpr)
  float_like_types = (float, int, FloatExpr)

  def wrapped(self: Block, *args_tup, **kwargs) -> Any:
    args = list(args_tup)
    builder_prev = builder.get_curr_context()
    builder.push_element(self)
    try:
      if not hasattr(self, '_init_params'):
        self._init_params = {}

      for arg_index, (arg_name, arg_param) in enumerate(list(inspect.signature(fn).parameters.items())[1:]):  # discard 0=self
        arg_default = arg_param.default
        if arg_name in kwargs:
          arg_val = kwargs[arg_name]
        elif arg_index < len(args):
          arg_val = args[arg_index]
        else:
          arg_val = arg_default

        if isinstance(arg_val, ConstraintExpr) and not arg_val._is_bound():
          assert arg_val.initializer is None, f"in got non-bound {arg_name} but initialized with {arg_val.initializer}"
          arg_val = None

        if isinstance(arg_default, param_types):  # only care about ConstraintExpr-like args
          # TODO unify w/ ConstraintExpr Union-type
          # TODO check arg_val type
          if isinstance(arg_default, (bool, BoolExpr)):
            param_model: ConstraintExpr = BoolExpr()
          elif isinstance(arg_default, (float, int, FloatExpr)):
            param_model = FloatExpr()
          elif isinstance(arg_default, RangeExpr) or (isinstance(arg_default, tuple) and
              isinstance(arg_default[0], float_like_types) and isinstance(arg_default[0], float_like_types)):
            param_model = RangeExpr()
          elif isinstance(arg_default, (str, StringExpr)):
            param_model = StringExpr()
          else:
            raise ValueError(f"Unknown Constraint-like argument to name={arg_name} with default={arg_default} of type={type(arg_default)}")

          # Create new parameter in self
          # TODO internal initializers (subclass fixing superclass initializers) need to be supported properly
          param_name = '(constr)' + arg_name
          if param_name in self._init_params:
            param_bound = self._init_params[param_name][0]
            assert arg_val is param_bound, f"in {fn}, top level remapped name={arg_name} but got different value passed through"
          else:
            param_bound = param_model._bind(ParamBinding(self))
            self._init_params[param_name] = (param_bound, arg_val)

          # Modify the arguments passed through
          if arg_name in kwargs:
            kwargs[arg_name] = param_bound
          elif arg_index < len(args):
            args[arg_index] = param_bound
          else:
            kwargs[arg_name] = param_bound

        elif isinstance(arg_default, (BaseBlock, BasePort)):
          raise NotImplementedError(f"argument passing for Block and Port types not implemented: {arg_default}")
        elif arg_default is inspect._empty:  # type: ignore
          pass
        else:
          raise NotImplementedError(f"unrecognized argument to Block: {arg_default} of type {type(arg_default)}")
    finally:
      builder.pop_to(builder_prev)

    return fn(self, *args, **kwargs)

  # TODO check fn is constructor?

  return cast(InitType, wrapped)


# TODO not statically type checked, since the port may be externally facing. TODO: maybe PortTags should be bridgeable?
class ImplicitConnect:
  """Implicit connect definition. a port and all the implicit connect tags it supports.
  To implicitly connect to a sub-block's port, this tags list must be a superset of the sub-block port's tag list."""
  def __init__(self, port: Port, tags: List[PortTag]) -> None:
    self.port = port
    self.tags = set(tags)


class ImplicitScope:
  def __init__(self, parent: Block, implicits: Iterable[ImplicitConnect]) -> None:
    self.open: Optional[bool] = None
    self.parent = parent
    self.implicits = tuple(implicits)

  BlockType = TypeVar('BlockType', bound='Block')
  def Block(self, tpe: BlockType) -> BlockType:
    """Instantiates a block and performs implicit connections."""
    if self.open is None:
      raise EdgContextError("can only use ImplicitScope.Block(...) in a Python with context")
    elif self.open == False:
      raise EdgContextError("can't use ImplicitScope.Block(...) after a Python with context")

    block = self.parent.Block(tpe)

    already_connected_ports = IdentitySet[Port]()
    for implicit in self.implicits:
      # for all ports, only the first connectable implicit should connect
      for tag in implicit.tags:
        for port in block._get_ports_by_tag({tag}):
          if port not in already_connected_ports:
            self.parent.connect(implicit.port, port)
            already_connected_ports.add(port)

    return block

  def __enter__(self) -> ImplicitScope:
    self.open = True
    return self

  def __exit__(self, exc_type, exc_val, exc_tb) -> None:
    self.open = False


class ChainConnect:
  """Return type of chain connect operation, that can't be used in EDG operations except assignment to instance
  variable for naming.
  """
  def __init__(self, blocks: List[Block], links: List[ConnectedPorts]):
    self.blocks = blocks
    self.links = links

  def __iter__(self):
    return iter((tuple(self.blocks), self))


@non_library
class Block(BaseBlock[edgir.HierarchyBlock]):
  """Part with a statically-defined subcircuit.
  Relations between contained parameters may only be expressed in the given constraint language.
  """
  def __init__(self) -> None:
    super().__init__()

    self._init_params: Dict[str, Tuple[ConstraintExpr, Any]]  # name -> (bound parameter, raw arg value), set in @init_in_parent
    if hasattr(self, '_init_params'):
      for param_name, (self_param, parent_init) in self._init_params.items():
        self._parameters.register(self_param)
        self.manager.add_element(param_name, self_param)
    else:
      self._init_params = {}

    self.parent = None

    self._blocks = self.manager.new_dict(Block)  # type: ignore
    self._chains = self.manager.new_dict(ChainConnect, anon_prefix='anon_chain')
    self._port_tags = IdentityDict[Port, Set[PortTag[Any]]]()

  def _get_ports_by_tag(self, tags: Set[PortTag]) -> List[Port]:
    out = []
    for block_port_name, block_port in self._ports.items():
      assert isinstance(block_port, Port)
      port_tags: Set[PortTag[Any]] = self._port_tags.get(block_port, set())
      if port_tags.issuperset(tags):
        out.append(block_port)
    return out

  def _initializers(self) -> IdentityDict[ConstraintExpr, ConstraintExpr]:
    # TODO unify w/ _initializer_to?
    return IdentityDict([(self_param, self_param_init)
                         for name, (self_param, self_param_init) in self._init_params.items()
                         if self_param_init is not None])

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    return super()._get_ref_map(prefix) + IdentityDict(
      *[block._get_ref_map(edgir.localpath_concat(prefix, name)) for (name, block) in self._blocks.items()]
    )

  def _populate_def_proto_hierarchy(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    self._blocks.finalize()
    self._connects.finalize()
    self._chains.finalize()

    ref_map = self._get_ref_map(edgir.LocalPath())

    # opportunistic check in the frontend that all internal ports marked connected are connected
    all_connected_ports = IdentitySet[BasePort]()
    for name, connect in self._connects.items():
      if len(connect.ports) > 1:
        all_connected_ports.update(connect.ports)

    unconnected_required_ports: List[str] = []  # aggregate report all unconnected ports
    for name, block in self._blocks.items():
      # make sure all the blocks internal required ports are connected
      for block_port in block._required_ports:
        if block_port not in all_connected_ports:
          unconnected_required_ports.append(name + '.' + block._name_of(block_port))
      pb.blocks[name].lib_elem.target.name = block._get_def_name()

    self._blocks_order = self.Metadata({str(idx): name for idx, name in enumerate(self._blocks.keys_ordered())})

    if unconnected_required_ports:
      required_ports = ', '.join(unconnected_required_ports)
      raise UnconnectedRequiredPortError(
        f"In blocks in {type(self)}, "
        f"required ports {required_ports} not connected")

    # actually generate the links and connects
    link_chain_names = IdentityDict[ConnectedPorts, List[str]]()  # prefer chain name where applicable
    for name, chain in self._chains.items_ordered():
      for i, connect in enumerate(chain.links):
        link_chain_names.setdefault(connect, []).append(f"{name}_{i}")

    self._links_order: Dict[str, str] = self.Metadata({})
    for name, connect in self._connects.items_ordered():
      if connect in link_chain_names:
        if not name.startswith('anon_'):
          pass  # prefer a named link above all else
        else:
          name = link_chain_names[connect][0]  # arbitrarily pick the first one for now, TODO disambiguate?

      connect_elts = connect.generate_connections()
      if connect_elts is None:  # single port net - effectively discard
        pass
      elif connect_elts.link_type is None:  # generate direct export
        pb.constraints[f"(conn){name}"].exported.exterior_port.ref.CopyFrom(ref_map[connect_elts.bridged_connects[0][0]])
        pb.constraints[f"(conn){name}"].exported.internal_block_port.ref.CopyFrom(ref_map[connect_elts.direct_connects[0][0]])
      else:  # generate link
        link_path = edgir.localpath_concat(edgir.LocalPath(), name)

        self._links_order[str(len(self._links_order))] = f"{name}"
        pb.links[name].lib_elem.target.name = connect_elts.link_type._static_def_name()

        for idx, (self_port, link_port_path) in enumerate(connect_elts.bridged_connects):
          assert isinstance(self_port, Port)
          assert self_port.bridge_type is not None

          port_name = self._name_of(self_port)
          pb.blocks[f"(bridge){port_name}"].lib_elem.target.name = self_port.bridge_type._static_def_name()
          self._blocks_order[str(len(self._blocks_order))] = f"(bridge){port_name}"  # TODO unify w/ block instantiation?
          bridge_path = edgir.localpath_concat(edgir.LocalPath(), f"(bridge){port_name}")

          pb.constraints[f"(bridge){name}_b{idx}"].exported.exterior_port.ref.CopyFrom(ref_map[self_port])
          pb.constraints[f"(bridge){name}_b{idx}"].exported.internal_block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'outer_port'))

          pb.constraints[f"(conn){name}_b{idx}"].connected.block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'inner_link'))
          pb.constraints[f"(conn){name}_b{idx}"].connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))

        for idx, (subelt_port, link_port_path) in enumerate(connect_elts.direct_connects):
          pb.constraints[f"(conn){name}_d{idx}"].connected.block_port.ref.CopyFrom(ref_map[subelt_port])
          pb.constraints[f"(conn){name}_d{idx}"].connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))

    # generate block initializers
    for (name, block) in self._blocks.items():
      for (block_param, block_param_init) in block._initializers().items():
        pb.constraints[f'(init){name}{block_param}'].CopyFrom(  # TODO better name
          AssignBinding.make_assign(block_param, block_param._to_expr_type(block_param_init), ref_map)
          # AssignBinding.make_assign(block_param, block_param._to_expr_type(block_param.initializer), ref_map)
        )

    return pb

  def _def_to_proto(self) -> edgir.HierarchyBlock:
    for cls in self._get_block_bases():
      assert issubclass(cls, Block)  # HierarchyBlock can extend (refine) blocks that don't have an implementation

    pb = self._populate_def_proto_hierarchy(edgir.HierarchyBlock())  # specifically generate connect statements first
    pb = self._populate_def_proto_block_base(pb)
    pb = self._populate_def_proto_block_contents(pb)

    return pb

  def chain(self, *elts: Union[BasePort, Block]) -> ChainConnect:
    if not elts:
      return self._chains.register(ChainConnect([], []))
    chain_blocks = []
    chain_links = []

    if isinstance(elts[0], BasePort):
      current_port = elts[0]
    elif isinstance(elts[0], Block):
      outable_ports = elts[0]._get_ports_by_tag({Output}) + elts[0]._get_ports_by_tag({InOut})
      if len(outable_ports) > 1:
        raise BlockDefinitionError(elts[0], f"first element 0 to chain {type(elts[0])} does not have exactly one InOut or Output port: {outable_ports}")
      current_port = outable_ports[0]
      chain_blocks.append(elts[0])
    else:
      raise EdgTypeError(f"first element 0 to chain", elts[0], (BasePort, Block))

    for i, elt in list(enumerate(elts))[1:-1]:
      elt = assert_type(elt, (Block), f"middle arguments elts[{i}] to chain")
      if elt._get_ports_by_tag({Input}) and elt._get_ports_by_tag({Output}):
        in_ports = elt._get_ports_by_tag({Input})
        out_ports = elt._get_ports_by_tag({Output})
        if len(in_ports) != 1:
          raise ChainError(self, f"element {i} to chain {type(elt)} does not have exactly one Input port: {in_ports}")
        elif len(out_ports) != 1:
          raise ChainError(self, f"element {i} to chain {type(elt)} does not have exactly one Output port: {out_ports}")
        chain_links.append(self.connect(current_port, in_ports[0]))
        chain_blocks.append(elt)
        current_port = out_ports[0]
      elif elt._get_ports_by_tag({InOut}):
        ports = elt._get_ports_by_tag({InOut})
        if len(ports) != 1:
          raise ChainError(self, f"element {i} to chain {type(elt)} does not have exactly one InOut port: {ports}")
        self.connect(current_port, ports[0])
        chain_blocks.append(elt)
      else:
        raise ChainError(self, f"element {i} to chain {type(elt)} has no Input and Output, or InOut ports")

    if isinstance(elts[-1], BasePort):
      chain_links.append(self.connect(current_port, elts[-1]))
    elif isinstance(elts[-1], Block):
      inable_ports = elts[-1]._get_ports_by_tag({Input}) + elts[-1]._get_ports_by_tag({InOut})
      if len(inable_ports) != 1:
        raise BlockDefinitionError(elts[-1], f"last element {len(elts) - 1} to chain {type(elts[-1])} does not have exactly one InOut or Input port: {inable_ports}")
      chain_blocks.append(elts[-1])
      chain_links.append(self.connect(current_port, inable_ports[0]))
    else:
      raise EdgTypeError(f"last argument {len(elts) - 1} to chain", elts[-1], (BasePort, Block))

    return self._chains.register(ChainConnect(chain_blocks, chain_links))

  def implicit_connect(self, *implicits: ImplicitConnect) -> ImplicitScope:
    for implicit in implicits:
      if not isinstance(implicit, ImplicitConnect):
        raise TypeError(f"param to implicit_connect(...) must be ImplicitConnect, "
                        f"got {implicit} of type {type(implicit)}")

    return ImplicitScope(self, implicits)

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, tags: Iterable[PortTag]=[], *, optional: bool = False, **kwargs) -> T:
    """Registers a port for this Block"""
    if not isinstance(tpe, Port):
      raise NotImplementedError("Non-Port (eg, Vector) ports not (yet?) supported")
    if optional and tags:
      raise BlockDefinitionError(self, "optional ports cannot have implicit connection tags",
                                 "port can either be optional or have implicit connection tags")
    for tag in tags:
      tag = assert_type(tag, PortTag, "tag for Port(...)")

    port = super().Port(tpe, optional=optional, **kwargs)

    self._port_tags[port] = set(tags)
    return port  # type: ignore

  import edg_core
  ExportType = TypeVar('ExportType', bound=edg_core.Port)  # Block.Port aliases edg_core.Port
  def Export(self, port: ExportType, tags: Iterable[PortTag]=[], *, optional: Optional[bool] = None) -> ExportType:
    """Exports a port of a child block, tags and optional"""
    port_parent = port._block_parent()
    assert isinstance(port_parent, Block)
    assert port_parent._parent is self, "can only export ports of contained block"
    assert port._is_bound(), "can only export bound type"

    if optional is None:
      optional = port not in port_parent._required_ports

    new_port: BasePort = self.Port(type(port)(),  # TODO is dropping args safe in all cases?
                                   list(tags) + list(port_parent._port_tags[port]),
                                   optional=optional)
    self.connect(new_port, port)
    return new_port  # type: ignore

  BlockType = TypeVar('BlockType', bound='Block')
  def Block(self, tpe: BlockType) -> BlockType:
    if not isinstance(tpe, Block):
      raise TypeError(f"param to Block(...) must be Block, got {tpe} of type {type(tpe)}")

    elt = tpe._bind(self)
    self._blocks.register(elt)

    if not builder.stack or builder.stack[0] is self:
      self._sourcelocator[elt] = self._get_calling_source_locator()

    return elt

  def connect(self, *ports: BasePort) -> ConnectedPorts:
    for port in ports:
      if not isinstance(port, Port):
        raise TypeError(f"param to connect(...) must be Port, got {port} of type {type(port)}")

    return super().connect(*ports)


@non_library
class GeneratorBlock(Block):
  """Part which generates into a subcircuit, given fully resolved parameters.
  Generation happens after a solver run.
  Allows much more power and customization in the elaboration of a subcircuit.
  """
  def __init__(self):
    super().__init__()
    self.param_values: Optional[IdentityDict[ConstraintExpr, edgir.LitTypes]] = None

    self.generator = self.Metadata({
      'module': self.__class__.__module__,
      'class': self.__class__.__name__,
    })

  def _parse_from_proto(self, pb: edgir.HierarchyBlock, additional_constraints: Dict[str, edgir.ValueExpr]={}) -> None:
    """Reads concrete parameter values (including those of contained ports and attached links) from a protobuffer.
    Does not parse data for internal blocks, links, or ports, because those would not have been instantiated."""
    # Sanity check the incoming proto
    assert pb.superclasses[0].target.name == self.ref_to_proto(), f"proto superclass mismatch {pb.superclasses} in {type(self)}"
    # TODO: maybe check structural definitions too (ports and params)

    # Read through constraints and create a parameter value map
    self.param_values = IdentityDict()

    def resolve_path(starting: Union[Block, Port, Link, ConstraintExpr], path: List[edgir.LocalStep]) \
        -> Optional[Union[ConstraintExpr, Block, Port, Link]]:
      if not path:
        return starting
      elif isinstance(starting, Block):
        if path[0].name in starting._ports:
          port = starting._ports[path[0].name]
          assert isinstance(port, Port)
          return resolve_path(port, path[1:])
        elif path[0].name in starting._parameters:
          return starting._parameters[path[0].name]
        else:
          raise ValueError(f"no path {path} in {starting}")
      elif isinstance(starting, Port):
        if path[0].HasField('reserved_param') and path[0].reserved_param == edgir.CONNECTED_LINK:
          return resolve_path(starting.link(), path[1:])
        elif path[0].HasField('reserved_param') and path[0].reserved_param == edgir.IS_CONNECTED:
          return resolve_path(starting.is_connected(), path[1:])
        elif isinstance(starting, Bundle) and path[0].HasField('name') and path[0].name in starting._ports:
          return resolve_path(starting._ports[path[0].name], path[1:])
        elif path[0].HasField('name') and path[0].name in starting._parameters:
          return starting._parameters[path[0].name]
        else:
          raise ValueError(f"no path {path} in {starting}")
      elif isinstance(starting, Link):
        if path[0].name in starting._parameters:
          return starting._parameters[path[0].name]
        if path[0].name in starting._ports:
          raise ValueError(f"can't resolve into ports in array {path} in {starting}")
        else:
          raise ValueError(f"no path {path} in {starting}")
      else:
        return None  # failed to parse

    # TODO: maybe better name tracking w/ additional_constraints
    for name, constraint in chain(pb.constraints.items(), additional_constraints.items()):
      try:
        if constraint.HasField('binary') and constraint.binary.op == edgir.BinaryExpr.EQ:
          # Only parse constraints of the type [parameter] = [literal]
          param = resolve_path(self, list(constraint.binary.lhs.ref.steps))
          lit_val = edgir.lit_from_expr(constraint.binary.rhs)
          if isinstance(param, ConstraintExpr) and lit_val is not None:
            if param not in self.param_values or self.param_values[param] != lit_val:
              # reassignment errors in IdentityDict
              self.param_values[param] = lit_val
              if isinstance(param, RangeExpr) and isinstance(lit_val, tuple):
                self.param_values[param.lower()] = lit_val[0]
                self.param_values[param.upper()] = lit_val[1]
      except Exception as e:
        raise type(e)(f"(while parsing constraint {name} = {constraint}) " + str(e)) \
          .with_traceback(sys.exc_info()[2])

    for port in self._ports.values():
      assert isinstance(port, Port)  # TODO self.ports is of type BasePort, maybe fix to Port?
      if port.is_connected() not in self.param_values:
        self.param_values[port.is_connected()] = False

  ParamGetType = TypeVar('ParamGetType')
  def get(self, param: ConstraintExpr[Any, Any, ParamGetType], default: Optional[ParamGetType] = None) -> ParamGetType:
    if self._elaboration_state != BlockElaborationState.generate:
      raise BlockDefinitionError(self, "can't call get(... outside generate",
                                 "call get(...) inside generate only, and remember to call super().generate()")
    if not isinstance(param, ConstraintExpr):
      raise TypeError(f"param to get(...) must be ConstraintExpr, got {param} of type {type(param)}")
    assert self.param_values is not None

    if param not in self.param_values:  # TODO disambiguate between inaccessible and failed const prop
      if default is not None:
        return default
      else:
        raise NotImplementedError(f"get({self._name_of(param)}) did not find a value, either the variable is inaccessible or an internal error")

    value = cast(Any, self.param_values[param])
    if isinstance(param, FloatExpr):
      assert isinstance(value, Number), f"get({self._name_of(param)}) expected float, got {value}"
    elif isinstance(param, RangeExpr):
      assert isinstance(value[0], Number) and isinstance(value[1], Number), f"get({self._name_of(param)}) expected range, got {value}"
    elif isinstance(param, BoolExpr):
      assert isinstance(value, bool), f"get({self._name_of(param)}) expected bool, got {value}"
    elif isinstance(param, StringExpr):
      assert isinstance(value, str), f"get({self._name_of(param)}) expected str, got {value}"
    else:
      raise NotImplementedError(f"get({self._name_of(param)}) on unknown type, got {value}")
    return value  # type: ignore

  def get_opt(self, param: ConstraintExpr[Any, Any, ParamGetType]) -> Optional[ParamGetType]:
    # TODO can this be unified with get() without a default? type inference seems to choke
    if self._has(param):
      return self.get(param)
    else:
      return None

  def _has(self, param: ConstraintExpr) -> bool:  # temporary, hack: all ConstraintExpr should be solved with const prop
    assert self.param_values is not None, "Can't call _has(...) outside generate()"
    return param in self.param_values

  # TODO maybe disallow Block from being called in contents() ?

  # generate should be overloaded to instantiate subparts and connect them together
  def generate(self) -> None:
    pass


  def _def_to_proto(self) -> edgir.HierarchyBlock:
    # TODO dedup w/ HierarchyBlock._def_to_proto
    for cls in self._get_block_bases():
      assert issubclass(cls, Block)

    pb = edgir.HierarchyBlock()
    if self._elaboration_state == BlockElaborationState.post_generate:  # don't write contents before generate
      pb = self._populate_def_proto_hierarchy(pb)  # specifically generate connect statements first TODO why?
      pb = self._populate_def_proto_block_base(pb)
      pb = self._populate_def_proto_block_contents(pb)
    else:
      pb = self._populate_def_proto_block_base(pb)
      pb = self._populate_def_proto_block_contents(pb)  # constraints need to be written and propagated
    return pb


  def _generated_def_to_proto(self) -> edgir.HierarchyBlock:
    assert self._elaboration_state == BlockElaborationState.post_init  # TODO dedup w/ elaborated_def_to_proto
    self._elaboration_state = BlockElaborationState.contents
    self.contents()
    self._elaboration_state = BlockElaborationState.generate
    self.generate()
    self.generator['done'] = 'done'
    self._elaboration_state = BlockElaborationState.post_generate
    return self._def_to_proto()


AbstractBlockType = TypeVar('AbstractBlockType', bound=Type[Block])
def abstract_block(decorated: AbstractBlockType) -> AbstractBlockType:
  decorated._elt_properties[(decorated, 'abstract')] = None
  return decorated
