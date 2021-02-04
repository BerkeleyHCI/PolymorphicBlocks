from __future__ import annotations

from numbers import Number
from typing import *
from itertools import chain
import collections
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
          # TODO check arg_val type, so a better error message is generated
          if isinstance(arg_default, (bool, BoolExpr)):
            param_model: ConstraintExpr = BoolExpr(arg_val)
          elif isinstance(arg_default, (float, int, FloatExpr)):
            param_model = FloatExpr(arg_val)
          elif isinstance(arg_default, RangeExpr) or (isinstance(arg_default, tuple) and
              isinstance(arg_default[0], float_like_types) and isinstance(arg_default[0], float_like_types)):
            param_model = RangeExpr(arg_val)
          elif isinstance(arg_default, (str, StringExpr)):
            param_model = StringExpr(arg_val)
          else:
            raise ValueError(f"Unknown Constraint-like argument to name={arg_name} with default={arg_default} of type={type(arg_default)}")

          # Create new parameter in self
          # TODO internal initializers (subclass fixing superclass initializers) need to be supported properly
          param_name = '(constr)' + arg_name
          assert param_name not in self._init_params, f"in {fn}, redefinition of initializer {arg_name}"
          param_bound = param_model._bind(ParamBinding(self))
          self._init_params[param_name] = param_bound

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

    self._init_params: Dict[str, ConstraintExpr]  # name -> bound param (with initializer set), set in @init_in_parent
    if hasattr(self, '_init_params'):
      for param_name, self_param in self._init_params.items():
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

    if unconnected_required_ports:
      required_ports = ', '.join(unconnected_required_ports)
      raise UnconnectedRequiredPortError(
        f"In blocks in {type(self)}, "
        f"required ports {required_ports} not connected")

    # actually generate the links and connects
    link_chain_names = IdentityDict[ConnectedPorts, List[str]]()  # prefer chain name where applicable
    # TODO generate into primary data structures
    for name, chain in self._chains.items_ordered():
      for i, connect in enumerate(chain.links):
        link_chain_names.setdefault(connect, []).append(f"{name}_{i}")

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
        self._namespace_order.append(f"(conn){name}")
      else:  # generate link
        link_path = edgir.localpath_concat(edgir.LocalPath(), name)

        self._namespace_order.append(f"{name}")
        pb.links[name].lib_elem.target.name = connect_elts.link_type._static_def_name()

        for idx, (self_port, link_port_path) in enumerate(connect_elts.bridged_connects):
          assert isinstance(self_port, Port)
          assert self_port.bridge_type is not None

          port_name = self._name_of(self_port)
          pb.blocks[f"(bridge){port_name}"].lib_elem.target.name = self_port.bridge_type._static_def_name()
          self._namespace_order.append(f"(bridge){port_name}")
          bridge_path = edgir.localpath_concat(edgir.LocalPath(), f"(bridge){port_name}")

          pb.constraints[f"(bridge){name}_b{idx}"].exported.exterior_port.ref.CopyFrom(ref_map[self_port])
          pb.constraints[f"(bridge){name}_b{idx}"].exported.internal_block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'outer_port'))
          self._namespace_order.append(f"(bridge){name}_b{idx}")

          pb.constraints[f"(conn){name}_b{idx}"].connected.block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'inner_link'))
          pb.constraints[f"(conn){name}_b{idx}"].connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))
          self._namespace_order.append(f"(conn){name}_b{idx}")

        for idx, (subelt_port, link_port_path) in enumerate(connect_elts.direct_connects):
          pb.constraints[f"(conn){name}_d{idx}"].connected.block_port.ref.CopyFrom(ref_map[subelt_port])
          pb.constraints[f"(conn){name}_d{idx}"].connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))
          self._namespace_order.append(f"(conn){name}_d{idx}")

    # generate block initializers
    for (block_name, block) in self._blocks.items():
      for (block_param_name, block_param) in block._init_params.items():
        if block_param.initializer is not None:
          pb.constraints[f'(init){block_name}.{block_param_name}'].CopyFrom(  # TODO better name
            AssignBinding.make_assign(block_param, block_param._to_expr_type(block_param.initializer), ref_map)
          )
          self._namespace_order.append(f'(init){block_name}.{block_param_name}')

    # generate H-block-specific order
    for name in self._blocks.keys_ordered():
      self._namespace_order.append(name)

    return pb

  def _connected_ports(self) -> IdentitySet[BasePort]:
    """Returns an IdentitySet of all ports (boundary and interior) involved in a connect or export."""
    rtn = IdentitySet[BasePort]()
    for name, connect in self._connects.items_ordered():
      rtn.update(connect.ports)
    return rtn

  # TODO make this non-overriding?
  def _def_to_proto(self) -> edgir.HierarchyBlock:
    for cls in self._get_block_bases():
      assert issubclass(cls, Block)  # HierarchyBlock can extend (refine) blocks that don't have an implementation

    pb = self._populate_def_proto_hierarchy(edgir.HierarchyBlock())  # specifically generate connect statements first
    pb = self._populate_def_proto_block_base(pb)
    pb = self._populate_def_proto_block_contents(pb)
    pb = self._populate_def_proto_param_init(pb)
    pb = self._populate_def_proto_port_init(pb, self._connected_ports())

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
    self._param_values: Optional[IdentityDict[ConstraintExpr, edgir.LitTypes]] = None
    self._generators: collections.OrderedDict[str, GeneratorBlock.GeneratorRecord] = collections.OrderedDict()

  # Generator dependency data
  #
  class GeneratorRecord(NamedTuple):
    reqs: Tuple[ConstraintExpr, ...]
    fn_args: Tuple[ConstraintExpr, ...]

  # DEPRECATED - pending experimentation to see if this can be removed
  # This is an older API that has the .get(...) in the genreator function,
  # instead of handling it in infrastructure and passing results to the generator as args.
  def generator_getfn(self, fn: Callable[[], None], *reqs: ConstraintExpr) -> None:
    assert callable(fn), f"fn {fn} must be a method (callable)"
    fn_name = fn.__name__
    assert hasattr(self, fn_name), f"{self} does not contain {fn_name}"
    assert getattr(self, fn_name) == fn, f"{self}.{fn_name} did not equal fn {fn}"

    assert fn_name not in self._generators, f"redefinition of generator {fn_name}"
    self._generators[fn_name] = GeneratorBlock.GeneratorRecord(reqs, ())

  ConstrGet1 = TypeVar('ConstrGet1', bound=Any)
  ConstrGet2 = TypeVar('ConstrGet2', bound=Any)
  ConstrGet3 = TypeVar('ConstrGet3', bound=Any)
  ConstrGet4 = TypeVar('ConstrGet4', bound=Any)
  ConstrGet5 = TypeVar('ConstrGet5', bound=Any)

  @overload
  def generator(self, fn: Callable[[], None]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrGet1], None],
                req1: ConstraintExpr[Any, Any, ConstrGet1]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrGet1, ConstrGet2], None],
                req1: ConstraintExpr[Any, Any, ConstrGet1],
                req2: ConstraintExpr[Any, Any, ConstrGet2]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrGet1, ConstrGet2, ConstrGet3], None],
                req1: ConstraintExpr[Any, Any, ConstrGet1],
                req2: ConstraintExpr[Any, Any, ConstrGet2],
                req3: ConstraintExpr[Any, Any, ConstrGet3]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrGet1, ConstrGet2, ConstrGet3, ConstrGet4], None],
                req1: ConstraintExpr[Any, Any, ConstrGet1],
                req2: ConstraintExpr[Any, Any, ConstrGet2],
                req3: ConstraintExpr[Any, Any, ConstrGet3],
                req4: ConstraintExpr[Any, Any, ConstrGet4]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrGet1, ConstrGet2, ConstrGet3, ConstrGet4, ConstrGet5], None],
                req1: ConstraintExpr[Any, Any, ConstrGet1],
                req2: ConstraintExpr[Any, Any, ConstrGet2],
                req3: ConstraintExpr[Any, Any, ConstrGet3],
                req4: ConstraintExpr[Any, Any, ConstrGet4],
                req5: ConstraintExpr[Any, Any, ConstrGet5]) -> None: ...

  # TODO don't ignore the type and fix so the typer understands the above are subsumed by this
  def generator(self, fn: Callable[..., None], *reqs: ConstraintExpr) -> None:  # type: ignore
    assert callable(fn), f"fn {fn} must be a method (callable)"
    fn_name = fn.__name__
    assert hasattr(self, fn_name), f"{self} does not contain {fn_name}"
    assert getattr(self, fn_name) == fn, f"{self}.{fn_name} did not equal fn {fn}"

    assert fn_name not in self._generators, f"redefinition of generator {fn_name}"
    self._generators[fn_name] = GeneratorBlock.GeneratorRecord(reqs, reqs)

  # Generator solved-parameter-access interface
  #
  ParamGetType = TypeVar('ParamGetType')
  def get(self, param: ConstraintExpr[Any, Any, ParamGetType], default: Optional[ParamGetType] = None) -> ParamGetType:
    if self._elaboration_state != BlockElaborationState.generate:
      raise BlockDefinitionError(self, "can't call get(... outside generate",
                                 "call get(...) inside generate only, and remember to call super().generate()")
    if not isinstance(param, ConstraintExpr):
      raise TypeError(f"param to get(...) must be ConstraintExpr, got {param} of type {type(param)}")
    assert self._param_values is not None

    if param not in self._param_values:  # TODO disambiguate between inaccessible and failed const prop
      if default is not None:
        return default
      else:
        raise NotImplementedError(f"get({self._name_of(param)}) did not find a value, either the variable is inaccessible or an internal error")

    value = cast(Any, self._param_values[param])
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
    assert self._param_values is not None, "Can't call _has(...) outside generate()"
    return param in self._param_values

  # TODO maybe disallow Block from being called in contents() ?

  # Generator serialization and parsing
  #
  def _def_to_proto(self) -> edgir.HierarchyBlock:
    # TODO dedup w/ HierarchyBlock._def_to_proto
    for cls in self._get_block_bases():
      assert issubclass(cls, Block)

    pb = edgir.HierarchyBlock()
    if self._elaboration_state == BlockElaborationState.post_generate:  # don't write contents before generate
      pb = self._populate_def_proto_hierarchy(pb)  # specifically generate connect statements first TODO why?
      pb = self._populate_def_proto_block_base(pb)
      pb = self._populate_def_proto_block_contents(pb)
      pb = self._populate_def_proto_param_init(pb, IdentitySet(*self._init_params.values()))
      pb = self._populate_def_proto_port_init(pb, self._connected_ports())
    else:
      pb = self._populate_def_proto_block_base(pb)
      pb = self._populate_def_proto_block_contents(pb)  # constraints need to be written and propagated
      pb = self._populate_def_proto_param_init(pb, IdentitySet(*self._init_params.values()))
      pb = self._populate_def_proto_port_init(pb, self._connected_ports())
      pb = self._populate_def_proto_block_generator(pb)
    return pb

  def _populate_def_proto_block_generator(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    assert self._generators, f"{self} did not define any generator functions"

    ref_map = self._get_ref_map(edgir.LocalPath())
    for (name, record) in self._generators.items():
      pb.generators[name].fn = name
      conditions = pb.generators[name].conditions.add()
      for req in record.reqs:
        conditions.prereqs.add().CopyFrom(ref_map[req])
    return pb

  def _parse_param_values(self, values: Iterable[Tuple[edgir.LocalPath, edgir.LitTypes]]) -> None:
    ref_map = self._get_ref_map(edgir.LocalPath())
    reverse_ref_map = { path.SerializeToString(): refable
      for refable, path in ref_map.items() }
    self._param_values = IdentityDict()
    for (path, value) in values:
      path_expr = reverse_ref_map[path.SerializeToString()]
      assert isinstance(path_expr, ConstraintExpr)
      self._param_values[path_expr] = value

  def _generated_def_to_proto(self, generate_fn_name: str,
                              generate_values: Iterable[Tuple[edgir.LocalPath, edgir.LitTypes]]) -> edgir.HierarchyBlock:
    assert self._elaboration_state == BlockElaborationState.post_init  # TODO dedup w/ elaborated_def_to_proto
    self._elaboration_state = BlockElaborationState.contents
    self.contents()
    self._elaboration_state = BlockElaborationState.generate
    self._parse_param_values(generate_values)

    # TODO: support ValueExpr, perhaps by ConstraintExpr matching or eager conversion to ValueExpr
    # or some kind of matching (eg, by index) from generator record to request
    fn_args = [self.get(arg_param)
      for arg_param in self._generators[generate_fn_name].fn_args]

    try:
      fn = getattr(self, generate_fn_name)
      fn(*fn_args)
      self._elaboration_state = BlockElaborationState.post_generate
      return self._def_to_proto()
    except BaseException as e:
      import traceback
      pb = edgir.HierarchyBlock()
      values_str = ", ".join([f"{edgir.local_path_to_str(path)}={edgir.lit_to_string(value)}"
                              for (path, value) in generate_values])
      err_meta = pb.meta.members.node[f'GenerateError_{generate_fn_name}'].error
      err_meta.message = repr(e) + "\n" + f"with values: {values_str}"
      err_meta.traceback = traceback.format_exc()
      # TODO ideally discard this stack frame, since it's not helpful
      return pb

  def generate(self):
    raise RuntimeError("generate deprecated")

AbstractBlockType = TypeVar('AbstractBlockType', bound=Type[Block])
def abstract_block(decorated: AbstractBlockType) -> AbstractBlockType:
  decorated._elt_properties[(decorated, 'abstract')] = None
  return decorated
