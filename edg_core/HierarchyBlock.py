from __future__ import annotations

from typing import *

import edgir
from . import ArrayStringExpr, ArrayRangeExpr, ArrayFloatExpr, ArrayIntExpr, ArrayBoolExpr, ArrayBoolLike, ArrayIntLike, \
  ArrayFloatLike, ArrayRangeLike, ArrayStringLike
from .Array import BaseVector, Vector
from .Binding import InitParamBinding, AssignBinding
from .Blocks import BaseBlock, Connection
from .ConstraintExpr import BoolLike, FloatLike, IntLike, RangeLike, StringLike
from .ConstraintExpr import ConstraintExpr, BoolExpr, FloatExpr, IntExpr, RangeExpr, StringExpr
from .Core import Refable, non_library
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
      if not hasattr(self, '_init_params_value'):
        self._init_params_value = {}

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

        if arg_name in self._init_params_value:  # if previously declared, check it is the prev param and keep as-is
          (prev_param, prev_val) = self._init_params_value[arg_name]
          assert prev_param is arg_val, f"in {fn}, redefinition of initializer {arg_name}={arg_val} over prior {prev_val}"
        else:  # not previously declared, create a new constructor parameter
          if isinstance(arg_val, ConstraintExpr):
            assert arg_val._is_bound() or arg_val.initializer is None,\
              f"in constructor arguments got non-bound default {arg_name}={arg_val}: " +\
              "either leave default empty or pass in a value or uninitialized type " +\
              "(eg, 2.0, FloatExpr(), but NOT FloatExpr(2.0))"

          param_model: ConstraintExpr
          if arg_param.annotation in (BoolLike, "BoolLike", BoolExpr, "BoolExpr"):
            param_model = BoolExpr()
          elif arg_param.annotation in (IntLike, "IntLike", IntExpr, "IntExpr"):
            param_model = IntExpr()
          elif arg_param.annotation in (FloatLike, "FloatLike", FloatExpr, "FloatExpr"):
            param_model = FloatExpr()
          elif arg_param.annotation in (RangeLike, "RangeLike", RangeExpr, "RangeExpr"):
            param_model = RangeExpr()
          elif arg_param.annotation in (StringLike, "StringLike", StringExpr, "StringExpr"):
            param_model = StringExpr()
          elif arg_param.annotation in (ArrayBoolLike, "ArrayBoolLike", ArrayBoolExpr, "ArrayBoolExpr"):
            param_model = ArrayBoolExpr()
          elif arg_param.annotation in (ArrayIntLike, "ArrayIntLike", ArrayIntExpr, "ArrayIntExpr"):
            param_model = ArrayIntExpr()
          elif arg_param.annotation in (ArrayFloatLike, "ArrayFloatLike", ArrayFloatExpr, "ArrayFloatExpr"):
            param_model = ArrayFloatExpr()
          elif arg_param.annotation in (ArrayRangeLike, "ArrayRangeLike", ArrayRangeExpr, "ArrayRangeExpr"):
            param_model = ArrayRangeExpr()
          elif arg_param.annotation in (ArrayStringLike, "ArrayStringLike", ArrayStringExpr, "ArrayStringExpr"):
            param_model = ArrayStringExpr()
          else:
            raise ValueError(f"In {fn}, unknown argument type for {arg_name}: {arg_param.annotation}")

          # Create new parameter in self, and pass through this one instead of the original
          param_bound = param_model._bind(InitParamBinding(self))

          # transform value to standaradize form to ConstraintExpr or None as needed
          if isinstance(arg_val, ConstraintExpr):
            if not arg_val._is_bound():  # TODO: perhaps deprecate the FloatExpr() form as an empty param?
              assert arg_val.initializer is None, f"models may not be passed into __init__ {arg_name}={arg_val}"
              arg_val = None
          elif not isinstance(arg_val, ConstraintExpr) and arg_val is not None:
            arg_val = param_model._to_expr_type(arg_val)
          assert arg_val is None or type(param_model) == type(arg_val), \
            f"type mismatch for {arg_name}: argument type {type(param_model)}, argument value {type(arg_val)}"

          self._init_params_value[arg_name] = (param_bound, arg_val)

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
  def __init__(self, port: Union[Port, Connection], tags: List[PortTag]) -> None:
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

    already_connected_ports = IdentitySet[BasePort]()
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
  def __init__(self, blocks: List[Block], links: List[Connection]):
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

    # name -> (empty param, default argument (if any)), set in @init_in_parent
    self._init_params_value: Dict[str, Tuple[ConstraintExpr, Optional[ConstraintExpr]]]
    if not hasattr(self, '_init_params_value'):
      self._init_params_value = {}
    for param_name, (param, param_value) in self._init_params_value.items():
      self._parameters.register(param)
      self.manager.add_element(param_name, param)

    self._blocks = self.manager.new_dict(Block)  # type: ignore
    self._chains = self.manager.new_dict(ChainConnect, anon_prefix='anon_chain')
    self._port_tags = IdentityDict[BasePort, Set[PortTag[Any]]]()

  def _get_ports_by_tag(self, tags: Set[PortTag]) -> List[BasePort]:
    out = []
    for block_port_name, block_port in self._ports.items():
      assert isinstance(block_port, BasePort)
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
    for param_name, (param, param_value) in self._init_params_value.items():
      if param_value is not None:
        # default values can't depend on anything so the ref_map is empty
        pb.param_defaults[param_name].CopyFrom(param_value._expr_to_proto(IdentityDict()))

    return pb

  def _populate_def_proto_hierarchy(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    self._blocks.finalize()
    self._connects.finalize()
    self._chains.finalize()

    ref_map = self._get_ref_map(edgir.LocalPath())

    for name, block in self._blocks.items():
      pb.blocks[name].lib_elem.target.name = block._get_def_name()

    # actually generate the links and connects
    link_chain_names = IdentityDict[Connection, List[str]]()  # prefer chain name where applicable
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

      connect_elts = connect.make_connection(self)
      if connect_elts is None:  # single port net - effectively discard
        pass

      elif isinstance(connect_elts, Connection.Export):  # generate direct export
        if connect_elts.is_array:
          pb.constraints[f"(conn){name}"].exportedArray.exterior_port.ref.CopyFrom(ref_map[connect_elts.external_port])
          pb.constraints[f"(conn){name}"].exportedArray.internal_block_port.ref.CopyFrom(ref_map[connect_elts.internal_port])
        else:
          pb.constraints[f"(conn){name}"].exported.exterior_port.ref.CopyFrom(ref_map[connect_elts.external_port])
          pb.constraints[f"(conn){name}"].exported.internal_block_port.ref.CopyFrom(ref_map[connect_elts.internal_port])
        self._namespace_order.append(f"(conn){name}")

      elif isinstance(connect_elts, Connection.ConnectedLink):  # generate link
        link_path = edgir.localpath_concat(edgir.LocalPath(), name)

        if connect_elts.is_link_array:
          pb.links[name].array.self_class.target.name = connect_elts.link_type._static_def_name()
        else:
          pb.links[name].lib_elem.target.name = connect_elts.link_type._static_def_name()
        self._namespace_order.append(f"{name}")

        for idx, (self_port, link_port_path) in enumerate(connect_elts.bridged_connects):
          assert isinstance(self_port, Port)
          assert not connect_elts.is_link_array, "bridged arrays not supported"
          assert self_port.bridge_type is not None

          port_name = self_port._name_from(self)
          pb.blocks[f"(bridge){port_name}"].lib_elem.target.name = self_port.bridge_type._static_def_name()
          self._namespace_order.append(f"(bridge){port_name}")
          bridge_path = edgir.localpath_concat(edgir.LocalPath(), f"(bridge){port_name}")

          pb.constraints[f"(bridge){name}_b{idx}"].exported.exterior_port.ref.CopyFrom(ref_map[self_port])
          pb.constraints[f"(bridge){name}_b{idx}"].exported.internal_block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'outer_port'))
          self._namespace_order.append(f"(bridge){name}_b{idx}")

          pb.constraints[f"(conn){name}_b{idx}"].connected.block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'inner_link'))
          pb.constraints[f"(conn){name}_b{idx}"].connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))
          self._namespace_order.append(f"(conn){name}_b{idx}")

        for idx, (subelt_port, link_port_path) in enumerate(connect_elts.link_connects):
          if connect_elts.is_link_array:
            pb.constraints[f"(conn){name}_d{idx}"].connectedArray.block_port.ref.CopyFrom(ref_map[subelt_port])
            pb.constraints[f"(conn){name}_d{idx}"].connectedArray.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))
          else:
            pb.constraints[f"(conn){name}_d{idx}"].connected.block_port.ref.CopyFrom(ref_map[subelt_port])
            pb.constraints[f"(conn){name}_d{idx}"].connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))
          self._namespace_order.append(f"(conn){name}_d{idx}")
      else:
        raise ValueError("unknown connect type")

    # generate block initializers
    for (block_name, block) in self._blocks.items():
      for (block_param_name, (block_param, block_param_value)) in block._init_params_value.items():
        if block_param_value is not None:
          pb.constraints[f'(init){block_name}.{block_param_name}'].CopyFrom(  # TODO better name
            AssignBinding.make_assign(block_param, block_param._to_expr_type(block_param_value), ref_map)
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
      rtn.update(connect.ports())
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
    for (name, (param, param_value)) in self._init_params_value.items():
      assert param.initializer is None, f"__init__ argument param {name} has unexpected initializer"
    pb = self._populate_def_proto_param_init(pb)
    for (port) in self._connected_ports():
      if port._block_parent() is self:
        port_name = self.manager.name_of(port) or "unk"
        assert not port._get_initializers([port_name]), f"connected boundary port {port_name} has unexpected initializer"
    pb = self._populate_def_proto_port_init(pb)

    return pb

  def chain(self, *elts: Union[Connection, BasePort, Block]) -> ChainConnect:
    if not elts:
      return self._chains.register(ChainConnect([], []))
    chain_blocks = []
    chain_links = []

    if isinstance(elts[0], (BasePort, Connection)):
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

  def connect(self, *connects: Union[BasePort, Connection], flatten=False) -> Connection:
    assert not flatten, "flatten only allowed in links"
    return super().connect(*connects, flatten=flatten)

  CastableType = TypeVar('CastableType')
  from .ConstraintExpr import BoolLike, BoolExpr, FloatLike, FloatExpr, RangeLike, RangeExpr
  # type ignore is needed because IntLike overlaps BoolLike
  @overload
  def ArgParameter(self, param: BoolLike) -> BoolExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: IntLike) -> IntExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: FloatLike) -> FloatExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: RangeLike) -> RangeExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: StringLike) -> StringExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayBoolLike) -> ArrayBoolExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayIntLike) -> ArrayIntExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayFloatLike) -> ArrayFloatExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayRangeLike) -> ArrayRangeExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayStringLike) -> ArrayStringExpr: ...  # type: ignore

  def ArgParameter(self, param: CastableType) -> ConstraintExpr[Any, CastableType]:
    """Registers a constructor argument parameter for this Block.
    This doesn't actually do anything, but is needed to help the type system converter the *Like to a *Expr."""
    if not isinstance(param, ConstraintExpr):
      raise TypeError(f"param to ArgParameter(...) must be ConstraintExpr, got {param} of type {type(param)}")
    if param.binding is None:
      raise TypeError(f"param to ArgParameter(...) must have binding")
    return param

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, tags: Iterable[PortTag]=[], *, optional: bool = False) -> T:
    """Registers a port for this Block"""
    if not isinstance(tpe, (Port, Vector)):
      raise NotImplementedError("Non-Port (eg, Vector) ports not (yet?) supported")
    if optional and tags:
      raise BlockDefinitionError(self, "optional ports cannot have implicit connection tags",
                                 "port can either be optional or have implicit connection tags")
    for tag in tags:
      tag = assert_type(tag, PortTag, "tag for Port(...)")

    port = super().Port(tpe, optional=optional)

    self._port_tags[port] = set(tags)
    return port  # type: ignore

  ExportType = TypeVar('ExportType', bound=BasePort)
  def Export(self, port: ExportType, tags: Iterable[PortTag]=[], *, optional: bool = False) -> ExportType:
    """Exports a port of a child block, but does not propagate tags or optional."""
    assert port._is_bound(), "can only export bound type"
    port_parent = port._block_parent()
    assert isinstance(port_parent, Block)
    assert port_parent._parent is self, "can only export ports of contained block"

    if isinstance(port, BaseVector):  # TODO can the vector and non-vector paths be unified?
      assert isinstance(port, Vector)
      new_port: BasePort = self.Port(Vector(port._tpe.empty()),
                                     tags, optional=optional)
    elif isinstance(port, Port):
      new_port = self.Port(type(port).empty(),  # TODO is dropping args safe in all cases?
                           tags, optional=optional)
    else:
      raise NotImplementedError(f"unknown exported port type {port}")

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


AbstractBlockType = TypeVar('AbstractBlockType', bound=Type[Block])
def abstract_block(decorated: AbstractBlockType) -> AbstractBlockType:
  decorated._elt_properties[(decorated, 'abstract')] = None
  return decorated
