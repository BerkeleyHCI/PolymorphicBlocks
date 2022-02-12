from __future__ import annotations

import collections
from itertools import chain
from numbers import Number
from typing import *

import edgir
from .Blocks import BaseBlock, BlockElaborationState, ConnectedPorts
from .Binding import ParamBinding, AssignBinding
from .ConstraintExpr import ConstraintExpr, BoolExpr, FloatExpr, IntExpr, RangeExpr, StringExpr
from .ConstraintExpr import BoolLike, FloatLike, IntLike, RangeLike, StringLike
from .Core import Refable, non_library
from .Range import Range
from .Exceptions import *
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet
from .PortTag import PortTag, Input, Output, InOut
from .Ports import BasePort, Port


InitType = TypeVar('InitType', bound=Callable[..., None])
def init_in_parent(fn: InitType) -> InitType:
  """
  This is a wrapper around any Block's __init__ that takes parameters, so arguments passed into the parameters
  generate into parameter assignments in the parent Block scope.

  This also handles default values, which are generated into the Block containing the __init__.

  It is explicitly not supported for a subclass to modify the parameters passed to a super().__init__ call.
  This can interact badly with refinement, since the parameters of super().__init__ could be directly assigned
  in an enclosing block, yet the subclass would also re-assign the same parameter, leading to a conflicting assign.
  These cases should use composition instead of inheritance, by instantiating the "super" Block and so its parameters
  are not made available to the enclosing scope.
  """
  import inspect
  from .Builder import builder

  def wrapped(self: Block, *args_tup, **kwargs) -> Any:
    args = list(args_tup)
    builder_prev = builder.get_curr_context()
    builder.push_element(self)
    try:
      if not hasattr(self, '_init_params'):
        self._init_params = {}

      for arg_index, (arg_name, arg_param) in enumerate(list(inspect.signature(fn).parameters.items())[1:]):  # discard 0=self
        if arg_param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
          continue  # ignore *args and **kwargs, those will get resolved at a lower level

        if arg_name in kwargs:
          arg_val = kwargs[arg_name]
        elif arg_index < len(args):
          arg_val = args[arg_index]
        elif arg_param.default is not inspect._empty:
          arg_val = arg_param.default
        else:
          arg_val = None

        if arg_name in self._init_params:  # if previously declared, check it is the prev param and keep as-is
          prev_val = self._init_params[arg_name]
          assert prev_val is arg_val, f"in {fn}, redefinition of initializer {arg_name}={arg_val} over prior {prev_val}"
        else:  # not previously declared, create a new constructor parameter
          if isinstance(arg_val, ConstraintExpr):
            assert arg_val._is_bound() or arg_val.initializer is None,\
              f"in constructor arguments got non-bound default {arg_name}={arg_val}: " +\
              "either leave default empty or pass in a value or uninitialized type " +\
              "(eg, 2.0, FloatExpr(), but NOT FloatExpr(2.0))"

          param_model: ConstraintExpr
          if arg_param.annotation in (BoolLike, "BoolLike", BoolExpr, "BoolExpr"):
            param_model = BoolExpr(arg_val)
          elif arg_param.annotation in (IntLike, "IntLike", IntExpr, "IntExpr"):
            param_model = IntExpr(arg_val)
          elif arg_param.annotation in (FloatLike, "FloatLike", FloatExpr, "FloatExpr"):
            param_model = FloatExpr(arg_val)
          elif arg_param.annotation in (RangeLike, "RangeLike", RangeExpr, "RangeExpr"):
            param_model = RangeExpr(arg_val)
          elif arg_param.annotation in (StringLike, "StringLike", StringExpr, "StringExpr"):
            param_model = StringExpr(arg_val)
          else:
            raise ValueError(f"In {fn}, unknown argument type for {arg_name}: {arg_param.annotation}")

          # Create new parameter in self, and pass through this one instead of the original
          param_bound = param_model._bind(ParamBinding(self))
          self._init_params[arg_name] = param_bound

          if arg_name in kwargs:
            kwargs[arg_name] = param_bound
          elif arg_index < len(args):
            args[arg_index] = param_bound
          else:
            kwargs[arg_name] = param_bound
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

  def _populate_def_proto_block_base(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    pb = super()._populate_def_proto_block_base(pb)

    # generate param defaults
    for param_name, self_param in self._init_params.items():
      if self_param.initializer is not None:
        # default values can't depend on anything so the ref_map is empty
        pb.param_defaults[param_name].CopyFrom(self_param.initializer._expr_to_proto(IdentityDict()))

    return pb

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

    for name, block in self._blocks.items():
      pb.blocks[name].lib_elem.target.name = block._get_def_name()

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
    for cls in self._get_bases_of(BaseBlock):  # type: ignore  # TODO avoid 'only concrete class' error
      assert issubclass(cls, Block)  # HierarchyBlock can extend (refine) blocks that don't have an implementation

    pb = edgir.HierarchyBlock()
    pb.prerefine_class.target.name = self._get_def_name()  # TODO integrate with a non-link populate_def_proto_block...
    pb = self._populate_def_proto_hierarchy(pb)  # specifically generate connect statements first
    pb = self._populate_def_proto_block_base(pb)
    pb = self._populate_def_proto_block_contents(pb)
    pb = self._populate_def_proto_param_init(pb, IdentitySet(*self._init_params.values()))
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
  def Port(self, tpe: T, tags: Iterable[PortTag]=[], *, optional: bool = False) -> T:
    """Registers a port for this Block"""
    if not isinstance(tpe, Port):
      raise NotImplementedError("Non-Port (eg, Vector) ports not (yet?) supported")
    if optional and tags:
      raise BlockDefinitionError(self, "optional ports cannot have implicit connection tags",
                                 "port can either be optional or have implicit connection tags")
    for tag in tags:
      tag = assert_type(tag, PortTag, "tag for Port(...)")

    port = super().Port(tpe, optional=optional)

    self._port_tags[port] = set(tags)
    return port  # type: ignore

  import edg_core
  ExportType = TypeVar('ExportType', bound=edg_core.Port)  # Block.Port aliases edg_core.Port
  def Export(self, port: ExportType, tags: Iterable[PortTag]=[], *, optional: bool = False) -> ExportType:
    """Exports a port of a child block, but does not propagate tags or optional."""
    port_parent = port._block_parent()
    assert isinstance(port_parent, Block)
    assert port_parent._parent is self, "can only export ports of contained block"
    assert port._is_bound(), "can only export bound type"

    new_port: BasePort = self.Port(type(port)(),  # TODO is dropping args safe in all cases?
                                   tags, optional=optional)
    self.connect(new_port, port)
    return new_port  # type: ignore

  BlockType = TypeVar('BlockType', bound='Block')
  def Block(self, tpe: BlockType) -> BlockType:
    from .DesignTop import DesignTop
    if not isinstance(tpe, Block):
      raise TypeError(f"param to Block(...) must be Block, got {tpe} of type {type(tpe)}")
    if isinstance(tpe, DesignTop):
      raise TypeError(f"param to Block(...) may not be DesignTop")

    elt = tpe._bind(self)
    self._blocks.register(elt)

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
    req_params: Tuple[ConstraintExpr, ...]  # all required params for generator to fire
    req_ports: Tuple[BasePort, ...]  # all required ports for generator to fire
    fn_args: Tuple[ConstraintExpr, ...]  # params to unpack for the generator function

  # DEPRECATED - pending experimentation to see if this can be removed
  # This is an older API that has the .get(...) in the genreator function,
  # instead of handling it in infrastructure and passing results to the generator as args.
  def generator_getfn(self, fn: Callable[[], None], *reqs: ConstraintExpr) -> None:
    assert callable(fn), f"fn {fn} must be a method (callable)"
    fn_name = fn.__name__
    assert hasattr(self, fn_name), f"{self} does not contain {fn_name}"
    assert getattr(self, fn_name) == fn, f"{self}.{fn_name} did not equal fn {fn}"

    assert fn_name not in self._generators, f"redefinition of generator {fn_name}"
    self._generators[fn_name] = GeneratorBlock.GeneratorRecord(reqs, (), ())

  ConstrType1 = TypeVar('ConstrType1', bound=Any)
  ConstrCastable1 = TypeVar('ConstrCastable1', bound=Any)
  ConstrType2 = TypeVar('ConstrType2', bound=Any)
  ConstrCastable2 = TypeVar('ConstrCastable2', bound=Any)
  ConstrType3 = TypeVar('ConstrType3', bound=Any)
  ConstrCastable3 = TypeVar('ConstrCastable3', bound=Any)
  ConstrType4 = TypeVar('ConstrType4', bound=Any)
  ConstrCastable4 = TypeVar('ConstrCastable4', bound=Any)
  ConstrType5 = TypeVar('ConstrType5', bound=Any)
  ConstrCastable5 = TypeVar('ConstrCastable5', bound=Any)
  ConstrType6 = TypeVar('ConstrType6', bound=Any)
  ConstrCastable6 = TypeVar('ConstrCastable6', bound=Any)
  ConstrType7 = TypeVar('ConstrType7', bound=Any)
  ConstrCastable7 = TypeVar('ConstrCastable7', bound=Any)
  ConstrType8 = TypeVar('ConstrType8', bound=Any)
  ConstrCastable8 = TypeVar('ConstrCastable8', bound=Any)
  ConstrType9 = TypeVar('ConstrType9', bound=Any)
  ConstrCastable9 = TypeVar('ConstrCastable9', bound=Any)
  ConstrType10 = TypeVar('ConstrType10', bound=Any)
  ConstrCastable10 = TypeVar('ConstrCastable10', bound=Any)

  # These are super ugly, both in that it's manually enumerating all the possible argument numbers
  # (but there's precedent in how Scala's libraries are written!) and that the generator can't actually take
  # the *Like types (eg, BoolLike - it can only take a BoolExpr), but this is needed to allow the *Like types
  # in constructor argument lists, and avoid piping them through to an explicit parameter.
  # While @init_in_parent remaps the arguments from a *Like type in the input to a *Expr type into the constructor,
  # expressing that function signature remapping isn't quite possible with mypy.
  # So this is the least worst option, a bit more ugliness for the advanced generator functionality rather than
  # for the common case of block definition.
  @overload
  def generator(self, fn: Callable[[], None],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7, ConstrType8], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]],
                req8: Union[ConstrCastable8, ConstraintExpr[ConstrType8, ConstrCastable8]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...

  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7, ConstrType8,
                                    ConstrType9], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]],
                req8: Union[ConstrCastable8, ConstraintExpr[ConstrType8, ConstrCastable8]],
                req9: Union[ConstrCastable9, ConstraintExpr[ConstrType9, ConstrCastable9]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...

  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7, ConstrType8,
                                    ConstrType9, ConstrType10], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]],
                req8: Union[ConstrCastable8, ConstraintExpr[ConstrType8, ConstrCastable8]],
                req9: Union[ConstrCastable9, ConstraintExpr[ConstrType9, ConstrCastable9]],
                req10: Union[ConstrCastable10, ConstraintExpr[ConstrType10, ConstrCastable10]],
                *, req_ports: Iterable[BasePort] = []) -> None: ...

  # TODO don't ignore the type and fix so the typer understands the above are subsumed by this
  def generator(self, fn: Callable[..., None], *reqs: ConstraintExpr,  # type: ignore
                req_ports: Iterable[BasePort] = []) -> None:
    """
    Registers a generator function
    :param fn: function (of self) to invoke, where the parameter list lines up with reqs
    :param reqs: required parameters, the value of which is made available to the generator
    :param req_ports: required ports, which can have their .is_connected() and .link().name() value obtained
    :param targets: list of ports and blocks the generator may connect to, to avoid generating initializers
    """
    assert callable(fn), f"fn {fn} must be a method (callable)"
    fn_name = fn.__name__
    assert hasattr(self, fn_name), f"{self} does not contain {fn_name}"
    assert getattr(self, fn_name) == fn, f"{self}.{fn_name} did not equal fn {fn}"

    assert fn_name not in self._generators, f"redefinition of generator {fn_name}"

    self._generators[fn_name] = GeneratorBlock.GeneratorRecord(reqs, tuple(req_ports), reqs)

  # Generator solved-parameter-access interface
  #
  ConstrType = TypeVar('ConstrType')
  def get(self, param: ConstraintExpr[ConstrType, Any], default: Optional[ConstrType] = None) -> ConstrType:
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
    elif isinstance(param, IntExpr):
      assert isinstance(value, int), f"get({self._name_of(param)}) expected int, got {value}"
    elif isinstance(param, RangeExpr):
      assert isinstance(value, Range), f"get({self._name_of(param)}) expected range, got {value}"
    elif isinstance(param, BoolExpr):
      assert isinstance(value, bool), f"get({self._name_of(param)}) expected bool, got {value}"
    elif isinstance(param, StringExpr):
      assert isinstance(value, str), f"get({self._name_of(param)}) expected str, got {value}"
    else:
      raise NotImplementedError(f"get({self._name_of(param)}) on unknown type, got {value}")
    return value  # type: ignore

  def get_opt(self, param: ConstraintExpr[ConstrType, Any]) -> Optional[ConstrType]:
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
    if self._elaboration_state != BlockElaborationState.post_generate:  # only write generator on the stub definition
      assert len(self._generators) == 1, f"{self} does not have exactly 1 generator"

      pb = edgir.HierarchyBlock()
      ref_map = self._get_ref_map(edgir.LocalPath())
      for (name, record) in self._generators.items():
        pb.generators[name]  # even if rest of the fields are empty, make sure to create a record
        for req_param in record.req_params:
          pb.generators[name].required_params.add().CopyFrom(ref_map[req_param])
        for req_port in record.req_ports:
          pb.generators[name].required_ports.add().CopyFrom(ref_map[req_port])
      pb = self._populate_def_proto_block_base(pb)
      return pb
    else:
      return super()._def_to_proto()

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

    for (name, port) in self._ports.items():
      # TODO cleaner, oddly-stateful, detection of connected_link
      if isinstance(port, Port):
        port.link()  # lazy-initialize connected_link refs so it's ready for params
    self._parse_param_values(generate_values)

    # TODO: support ValueExpr, perhaps by ConstraintExpr matching or eager conversion to ValueExpr
    # or some kind of matching (eg, by index) from generator record to request
    fn_args = [self.get(arg_param)
      for arg_param in self._generators[generate_fn_name].fn_args]

    fn = getattr(self, generate_fn_name)
    fn(*fn_args)

    self._elaboration_state = BlockElaborationState.post_generate

    return self._def_to_proto()

  def generate(self):
    raise RuntimeError("generate deprecated")

AbstractBlockType = TypeVar('AbstractBlockType', bound=Type[Block])
def abstract_block(decorated: AbstractBlockType) -> AbstractBlockType:
  decorated._elt_properties[(decorated, 'abstract')] = None
  return decorated
