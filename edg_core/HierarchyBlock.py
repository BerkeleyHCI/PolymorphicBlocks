from __future__ import annotations

from functools import reduce
from typing import *

import edgir
from . import ArrayStringExpr, ArrayRangeExpr, ArrayFloatExpr, ArrayIntExpr, ArrayBoolExpr, ArrayBoolLike, ArrayIntLike, \
  ArrayFloatLike, ArrayRangeLike, ArrayStringLike
from .Array import BaseVector, Vector
from .Binding import InitParamBinding, AssignBinding
from .Blocks import BaseBlock, Connection, BlockElaborationState, AbstractBlockProperty
from .ConstraintExpr import BoolLike, FloatLike, IntLike, RangeLike, StringLike
from .ConstraintExpr import ConstraintExpr, BoolExpr, FloatExpr, IntExpr, RangeExpr, StringExpr
from .Core import Refable, non_library
from .HdlUserExceptions import *
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet
from .PortTag import PortTag, Input, Output, InOut
from .Ports import BasePort, Port

if TYPE_CHECKING:
  from .BlockInterfaceMixin import BlockInterfaceMixin


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

    self._mixins: List['BlockInterfaceMixin'] = []

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
    ref_map = super()._get_ref_map(prefix) + IdentityDict(
      *[block._get_ref_map(edgir.localpath_concat(prefix, name)) for (name, block) in self._blocks.items()]
    )
    mixin_ref_maps = list(map(lambda mixin: mixin._get_ref_map(prefix), self._mixins))
    if mixin_ref_maps:
      mixin_ref_map = reduce(lambda a, b: a+b, mixin_ref_maps)
      ref_map += mixin_ref_map

    return ref_map

  def _get_init_params_values(self) -> Dict[str, Tuple[ConstraintExpr, Optional[ConstraintExpr]]]:
    if self._mixins:
      combined_dict = self._init_params_value.copy()
      for mixin in self._mixins:
        combined_dict.update(mixin._get_init_params_values())
      return combined_dict
    else:
      return self._init_params_value

  def _populate_def_proto_block_base(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    pb = super()._populate_def_proto_block_base(pb)

    # generate param defaults
    for param_name, (param, param_value) in self._get_init_params_values().items():
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
      new_block_lib = edgir.add_pair(pb.blocks, name).lib_elem
      new_block_lib.base.target.name = block._get_def_name()
      for mixin in block._mixins:
        new_block_lib.mixins.add().target.name = mixin._get_def_name()

    # actually generate the links and connects
    link_chain_names = IdentityDict[Connection, List[str]]()  # prefer chain name where applicable
    # TODO generate into primary data structures
    for name, chain in self._chains.items_ordered():
      for i, connect in enumerate(chain.links):
        link_chain_names.setdefault(connect, []).append(f"{name}_{i}")

    for name, connect in self._connects.items_ordered():
      connect_elts = connect.make_connection()

      if name.startswith('anon_'):  # infer a non-anon name if possible
        if connect in link_chain_names and not link_chain_names[connect][0].startswith('anon_'):
          name = link_chain_names[connect][0]  # arbitrarily pick the first chain name
        elif isinstance(connect_elts, Connection.Export):
          port_pathname = connect_elts.external_port._name_from(self).replace('.', '_')
          name = f'_{port_pathname}_link'
        elif isinstance(connect_elts, Connection.ConnectedLink) and connect_elts.bridged_connects:
          port_pathname = connect_elts.bridged_connects[0][0]._name_from(self).replace('.', '_')
          name = f'_{port_pathname}_link'
        elif isinstance(connect_elts, Connection.ConnectedLink) and connect_elts.link_connects:
          port_pathname = connect_elts.link_connects[0][0]._name_from(self).replace('.', '_')
          name = f'_{port_pathname}_link'
        elif connect in link_chain_names:  # if there's really nothing better, anon_chain is better than nothing
          name = link_chain_names[connect][0]

      if connect_elts is None:  # single port net - effectively discard
        pass
      elif isinstance(connect_elts, Connection.Export):  # generate direct export
        constraint_pb = edgir.add_pair(pb.constraints, f"(conn){name}")
        if connect_elts.is_array:
          constraint_pb.exportedArray.exterior_port.ref.CopyFrom(ref_map[connect_elts.external_port])
          constraint_pb.exportedArray.internal_block_port.ref.CopyFrom(ref_map[connect_elts.internal_port])
        else:
          constraint_pb.exported.exterior_port.ref.CopyFrom(ref_map[connect_elts.external_port])
          constraint_pb.exported.internal_block_port.ref.CopyFrom(ref_map[connect_elts.internal_port])

      elif isinstance(connect_elts, Connection.ConnectedLink):  # generate link
        link_path = edgir.localpath_concat(edgir.LocalPath(), name)
        link_pb = edgir.add_pair(pb.links, name)
        if connect_elts.is_link_array:
          link_pb.array.self_class.target.name = connect_elts.link_type._static_def_name()
        else:
          link_pb.lib_elem.target.name = connect_elts.link_type._static_def_name()

        for idx, (self_port, link_port_path) in enumerate(connect_elts.bridged_connects):
          assert isinstance(self_port, Port)
          assert not connect_elts.is_link_array, "bridged arrays not supported"
          assert self_port.bridge_type is not None

          port_name = self_port._name_from(self)
          edgir.add_pair(pb.blocks, f"(bridge){port_name}").lib_elem.base.target.name = self_port.bridge_type._static_def_name()
          bridge_path = edgir.localpath_concat(edgir.LocalPath(), f"(bridge){port_name}")

          bridge_constraint_pb = edgir.add_pair(pb.constraints, f"(bridge){name}_b{idx}")
          bridge_constraint_pb.exported.exterior_port.ref.CopyFrom(ref_map[self_port])
          bridge_constraint_pb.exported.internal_block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'outer_port'))

          connect_constraint_pb = edgir.add_pair(pb.constraints, f"(conn){name}_b{idx}")
          connect_constraint_pb.connected.block_port.ref.CopyFrom(edgir.localpath_concat(bridge_path, 'inner_link'))
          connect_constraint_pb.connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))

        for idx, (subelt_port, link_port_path) in enumerate(connect_elts.link_connects):
          connect_constraint_pb = edgir.add_pair(pb.constraints, f"(conn){name}_d{idx}")
          if connect_elts.is_link_array:
            connect_constraint_pb.connectedArray.block_port.ref.CopyFrom(ref_map[subelt_port])
            connect_constraint_pb.connectedArray.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))
          else:
            connect_constraint_pb.connected.block_port.ref.CopyFrom(ref_map[subelt_port])
            connect_constraint_pb.connected.link_port.ref.CopyFrom(edgir.localpath_concat(link_path, link_port_path))
      else:
        raise ValueError("unknown connect type")

    # generate block initializers
    for (block_name, block) in self._blocks.items():
      for (block_param_name, (block_param, block_param_value)) in block._get_init_params_values().items():
        if block_param_value is not None:
          edgir.add_pair(pb.constraints, f'(init){block_name}.{block_param_name}').CopyFrom(  # TODO better name
            AssignBinding.make_assign(block_param, block_param._to_expr_type(block_param_value), ref_map)
          )

    return pb

  # TODO make this non-overriding?
  def _def_to_proto(self) -> edgir.HierarchyBlock:
    assert not self._mixins  # blocks with mixins can only be instantiated anonymously

    pb = edgir.HierarchyBlock()
    pb.prerefine_class.target.name = self._get_def_name()  # TODO integrate with a non-link populate_def_proto_block...
    pb = self._populate_def_proto_block_base(pb)
    pb = self._populate_def_proto_port_init(pb)

    for (name, (param, param_value)) in self._get_init_params_values().items():
      assert param.initializer is None, f"__init__ argument param {name} has unexpected initializer"
    pb = self._populate_def_proto_param_init(pb)

    pb = self._populate_def_proto_hierarchy(pb)
    pb = self._populate_def_proto_block_contents(pb)
    pb = self._populate_def_proto_description(pb)

    return pb

  MixinType = TypeVar('MixinType', bound='BlockInterfaceMixin')
  def with_mixin(self, tpe: MixinType) -> MixinType:
    """Adds an interface mixin for this Block. Mainly useful for abstract blocks, e.g. IoController with HasI2s."""
    from .BlockInterfaceMixin import BlockInterfaceMixin
    if not (isinstance(tpe, BlockInterfaceMixin) and tpe._is_mixin()):
      raise TypeError("param to with_mixin must be a BlockInterfaceMixin")
    if isinstance(self, BlockInterfaceMixin) and self._is_mixin():
      raise BlockDefinitionError(self, "mixins can not have with_mixin")
    if (self.__class__, AbstractBlockProperty) not in self._elt_properties:
      raise BlockDefinitionError(self, "mixins can only be added to abstract classes")
    if not isinstance(self, tpe._get_mixin_base()):
      raise TypeError(f"block {self.__class__.__name__} not an instance of mixin base {tpe._get_mixin_base().__name__}")
    assert self._parent is not None

    elt = tpe._bind(self._parent)
    self._parent.manager.add_alias(elt, self)
    self._mixins.append(elt)

    return elt

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
      elt = assert_cast(elt, (Block), f"middle arguments elts[{i}] to chain")
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
    if not isinstance(param.binding, InitParamBinding):
      raise TypeError(f"param to ArgParameter(...) must be __init__ argument with @init_in_parent")
    return param

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, tags: Iterable[PortTag]=[], *, optional: bool = False) -> T:
    """Registers a port for this Block"""
    if not isinstance(tpe, (Port, Vector)):
      raise NotImplementedError("Non-Port (eg, Vector) ports not (yet?) supported")
    for tag in tags:
      assert_cast(tag, PortTag, "tag for Port(...)")

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
    from .BlockInterfaceMixin import BlockInterfaceMixin
    from .DesignTop import DesignTop
    if not isinstance(tpe, Block):
      raise TypeError(f"param to Block(...) must be Block, got {tpe} of type {type(tpe)}")
    if isinstance(tpe, BlockInterfaceMixin) and tpe._is_mixin():
      raise TypeError("param to Block(...) must not be BlockInterfaceMixin")
    if isinstance(tpe, DesignTop):
      raise TypeError(f"param to Block(...) may not be DesignTop")
    if self._elaboration_state not in \
        [BlockElaborationState.init, BlockElaborationState.contents, BlockElaborationState.generate]:
      raise BlockDefinitionError(self, "can only define blocks in init, contents, or generate")

    elt = tpe._bind(self)
    self._blocks.register(elt)

    return elt


AbstractBlockType = TypeVar('AbstractBlockType', bound=Type[Block])
def abstract_block(decorated: AbstractBlockType) -> AbstractBlockType:
  """Defines the decorated block as abstract, a supertype block missing an implementation and
  should be refined by a subclass in a final design.
  If this block is present (unrefined) in a final design, causes an error."""
  from .BlockInterfaceMixin import BlockInterfaceMixin
  if isinstance(decorated, BlockInterfaceMixin) and decorated._is_mixin():
    raise BlockDefinitionError(decorated, "BlockInterfaceMixin @abstract_block definition is redundant")
  decorated._elt_properties[(decorated, AbstractBlockProperty)] = None
  return decorated


def abstract_block_default(target: Callable[[], Type[Block]]) -> Callable[[AbstractBlockType], AbstractBlockType]:
  """Similar to the abstract_block decorator, but specifies a default refinement.
  The argument is a lambda since the default refinement is going to be a subclass of the class being defined,
  it will not be defined yet when the base class is being evaluated, so evaluation needs to be delayed."""
  def inner(decorated: AbstractBlockType) -> AbstractBlockType:
    from .BlockInterfaceMixin import BlockInterfaceMixin
    if isinstance(decorated, BlockInterfaceMixin) and decorated._is_mixin():
      raise BlockDefinitionError(decorated, "BlockInterfaceMixin @abstract_block definition is redundant")
    decorated._elt_properties[(decorated, AbstractBlockProperty)] = target
    return decorated
  return inner
