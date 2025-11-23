from __future__ import annotations

import functools
import inspect
import warnings
from functools import reduce
from typing import *

from .. import edgir
from .Builder import builder
from . import ArrayStringExpr, ArrayRangeExpr, ArrayFloatExpr, ArrayIntExpr, ArrayBoolExpr, ArrayBoolLike, ArrayIntLike, \
  ArrayFloatLike, ArrayRangeLike, ArrayStringLike
from .Array import BaseVector, Vector
from .Binding import InitParamBinding, AssignBinding
from .Blocks import BaseBlock, Connection, BlockElaborationState, AbstractBlockProperty, BaseBlockMeta
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


def init_in_parent(fn: Any) -> Any:
  warnings.warn(
    f"in {fn}, @init_in_parent is no longer needed, the annotation can be removed without replacement",
    DeprecationWarning,
    stacklevel=2
  )

  @functools.wraps(fn)
  def wrapped(self: Block, *args, **kwargs) -> Any:
    # in concept, the outer deprecation should fire, but it doesn't consistently, so this is added for redundancy
    warnings.warn(
      f"in {fn}, @init_in_parent is no longer needed, the annotation can be removed without replacement",
      DeprecationWarning
    )
    return fn(self, *args, **kwargs)
  return wrapped


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


BlockPrototypeType = TypeVar('BlockPrototypeType', bound='Block')
class BlockPrototype(Generic[BlockPrototypeType]):
  """A block prototype, that contains a type and arguments, but without constructing the entire block
  and running its (potentially quite expensive) __init__.

  This class is automatically created on Block instantiations by the BlockMeta metaclass __init__ hook."""
  def __init__(self, tpe: Type[BlockPrototypeType], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
    self._tpe = tpe
    self._args = args
    self._kwargs = kwargs

  def __repr__(self) -> str:
    return f"{self.__class__.__name__}({self._tpe}, args={self._args}, kwargs={self._kwargs})"

  def _bind(self, parent: Union[BaseBlock, Port]) -> BlockPrototypeType:
    """Binds the prototype into an actual Block instance."""
    Block._next_bind = self._tpe
    block = self._tpe(*self._args, **self._kwargs)  # type: ignore
    block._bind_in_place(parent)
    return block

  def __getattribute__(self, item: str) -> Any:
    if item.startswith("_"):
      return super().__getattribute__(item)
    else:
      raise AttributeError(f"{self.__class__.__name__} has no attributes, must bind to get a concrete instance, tried to get {item}")

  def __setattr__(self, key: str, value: Any) -> None:
    if key.startswith("_"):
      super().__setattr__(key, value)
    else:
      raise AttributeError(f"{self.__class__.__name__} has no attributes, must bind to get a concrete instance, tried to set {key}")


class BlockMeta(BaseBlockMeta):
  """This provides a hook on __init__ that replaces argument values with empty ConstraintExpr
  based on the type annotation and stores the supplied argument to the __init__ (if any) in the binding.

  The supplied argument is cast to its target type and stored in the binding, in its parent context.
  The binding itself is in the new object's context.

  This performs two functions:
  - Allows blocks to compile at the top-level where required parameters have no values and there is no
  context that provides those values
  - Standardize the type of objects passed to self.ArgParameter, so the result is properly typed.

  This is applied to every class that inherits this metaclass, and hooks every super().__init__ call."""

  _ANNOTATION_EXPR_MAP: Dict[Any, Type[ConstraintExpr]] = {
    BoolLike: BoolExpr,
    "BoolLike": BoolExpr,
    IntLike: IntExpr,
    "IntLike": IntExpr,
    FloatLike: FloatExpr,
    "FloatLike": FloatExpr,
    RangeLike: RangeExpr,
    "RangeLike": RangeExpr,
    StringLike: StringExpr,
    "StringLike": StringExpr,
    ArrayBoolLike: ArrayBoolExpr,
    "ArrayBoolLike": ArrayBoolExpr,
    ArrayIntLike: ArrayIntExpr,
    "ArrayIntLike": ArrayIntExpr,
    ArrayFloatLike: ArrayFloatExpr,
    "ArrayFloatLike": ArrayFloatExpr,
    ArrayRangeLike: ArrayRangeExpr,
    "ArrayRangeLike": ArrayRangeExpr,
    ArrayStringLike: ArrayStringExpr,
    "ArrayStringLike": ArrayStringExpr,
  }

  def __new__(cls, *args: Any, **kwargs: Any) -> Any:
    new_cls = super().__new__(cls, *args, **kwargs)

    if '__init__' in new_cls.__dict__:
      orig_init = new_cls.__dict__['__init__']

      # collect and pre-process argument data
      arg_data: List[Tuple[str, inspect.Parameter, Type[ConstraintExpr]]] = []
      # discard param 0 (self)
      for arg_name, arg_param in list(inspect.signature(orig_init).parameters.items())[1:]:
        if arg_param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
          continue  # pass through of *args, **kwargs handled later
        param_expr_type = BlockMeta._ANNOTATION_EXPR_MAP.get(arg_param.annotation, None)
        if param_expr_type is None:
          raise BlockDefinitionError(new_cls, f"in {new_cls}.__init__, unknown annotation type for {arg_name}: {arg_param.annotation}")

        arg_data.append((arg_name, arg_param, param_expr_type))

      def wrapped_init(self, *args, **kwargs) -> None:
        if not hasattr(self, '_init_params'):  # used to communicate to the block the added init params
          self._init_params = {}

        def remap_arg(arg_name: str, arg_type: Type[ConstraintExpr], arg_value: Any) -> ConstraintExpr:
          if isinstance(arg_value, ConstraintExpr):
            if isinstance(arg_value.binding, InitParamBinding) and arg_value.binding.parent is self:
              return arg_value  # pass through arg that has been previously transformed

          if isinstance(arg_value, ConstraintExpr):  # otherwise, create a new arg
            if arg_value._is_bound():
              typed_arg_value: Optional[ConstraintExpr] = arg_value
            elif arg_value.initializer is None:
              typed_arg_value = None
            else:
              raise BlockDefinitionError(self,
                                         f"in constructor arguments got non-bound value {arg_name}={arg_value}: " + \
                                         "either leave default empty or pass in a value or uninitialized type " + \
                                         "(eg, 2.0, FloatExpr(), but NOT FloatExpr(2.0))")
          elif arg_value is not None:
            typed_arg_value = arg_value
          else:
            typed_arg_value = None

          return arg_type()._bind(InitParamBinding(self, typed_arg_value))

        builder_prev = builder.push_element(self)
        try:
          # rebuild args and kwargs by traversing the args list
          new_args: List[Any] = []
          new_kwargs: Dict[str, Any] = {}
          for arg_pos, (arg_name, arg_param, param_expr_type) in enumerate(arg_data):
            if arg_pos < len(args) and arg_param.kind in (inspect.Parameter.POSITIONAL_ONLY,
                                                            inspect.Parameter.POSITIONAL_OR_KEYWORD):  # present positional arg
              new_arg = remap_arg(arg_name, param_expr_type, args[arg_pos])
              new_args.append(new_arg)
              self._init_params[arg_name] = new_arg
            elif arg_pos >= len(args) and arg_param.kind in (inspect.Parameter.POSITIONAL_ONLY, ):  # non-present positional arg
              if len(builder.stack) == 1:  # at top-level, fill in all args
                new_arg = remap_arg(arg_name, param_expr_type, None)
                new_args.append(new_arg)
                self._init_params[arg_name] = new_arg
            elif arg_name in kwargs and arg_param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                                           inspect.Parameter.KEYWORD_ONLY):  # present kwarg
              new_arg = remap_arg(arg_name, param_expr_type, kwargs[arg_name])
              new_kwargs[arg_name] = new_arg
              self._init_params[arg_name] = new_arg
            elif arg_name not in kwargs and arg_param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                                               inspect.Parameter.KEYWORD_ONLY):  # non-present kwarg
              if arg_param.default is not inspect._empty:  # default values do show up in kwargs, add them to transform them
                new_arg = remap_arg(arg_name, param_expr_type, arg_param.default)
                new_kwargs[arg_name] = new_arg
                self._init_params[arg_name] = new_arg
              elif len(builder.stack) == 1:  # at top-level, fill in all args
                new_arg = remap_arg(arg_name, param_expr_type, None)
                new_kwargs[arg_name] = new_arg
                self._init_params[arg_name] = new_arg

          # unconditionally pass through all args and kwargs
          new_args.extend(args[len(new_args):])
          for arg_name in kwargs:
            if arg_name not in new_kwargs:
              new_kwargs[arg_name] = kwargs[arg_name]

          orig_init(self, *new_args, **new_kwargs)
        finally:
          builder.pop_to(builder_prev)

      new_cls.__init__ = functools.update_wrapper(wrapped_init, orig_init)

    return new_cls


@non_library
class Block(BaseBlock[edgir.HierarchyBlock], metaclass=BlockMeta):
  """Part with a statically-defined subcircuit.
  Relations between contained parameters may only be expressed in the given constraint language.
  """
  _next_bind: Optional[Type[Block]] = None  # set when binding, to avoid creating a prototype

  def __new__(cls, *args: Any, **kwargs: Any) -> Block:
    if Block._next_bind is not None:
      assert Block._next_bind is cls
      Block._next_bind = None
      return super().__new__(cls)
    elif builder.get_enclosing_block() is None:  # always construct if top-level
      return super().__new__(cls)
    else:
      return BlockPrototype(cls, args, kwargs)  # type: ignore

  SelfType = TypeVar('SelfType', bound='BaseBlock')
  def _bind(self: SelfType, parent: Union[BaseBlock, Port]) -> SelfType:
    # for type checking only
    raise TypeError("_bind should be called from BlockPrototype")

  def __init__(self) -> None:
    super().__init__()

    if hasattr(self, '_init_params'):  # used to propagate params generated in the metaclass __init__ hook
      for param_name, param in cast(Dict, self._init_params).items():
        self._parameters.register(param)
        self.manager.add_element(param_name, param)
      delattr(self, '_init_params')

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

  def _build_ref_map(self, refmap: IdentityDict['Refable', edgir.LocalPath], prefix: edgir.LocalPath) -> None:
    super()._build_ref_map(refmap, prefix)
    for name, block in self._blocks.items():
      block._build_ref_map(refmap, edgir.localpath_concat(prefix, name))
    for mixin in self._mixins:
      mixin._build_ref_map(refmap, prefix)

  def _populate_def_proto_block_base(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    pb = super()._populate_def_proto_block_base(pb)

    # generate param defaults
    for param_name, param in self._parameters.items():
      if isinstance(param.binding, InitParamBinding) and param.binding.value is not None:
        # default values can't depend on anything so the ref_map is empty
        param_typed_value = param._to_expr_type(param.binding.value)
        pb.param_defaults[param_name].CopyFrom(param_typed_value._expr_to_proto(IdentityDict()))

    return pb

  def _populate_def_proto_hierarchy(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    self._blocks.finalize()
    self._connects.finalize()
    self._chains.finalize()

    ref_map = self._create_ref_map()

    for name, block in self._blocks.items():
      new_block_lib = edgir.add_pair(pb.blocks, name).lib_elem
      new_block_lib.base.target.name = block._get_def_name()
      for mixin in block._mixins:
        new_block_lib.mixins.add().target.name = mixin._get_def_name()

    # actually generate the links and connects
    link_chain_names = IdentityDict[Connection, List[str]]()  # prefer chain name where applicable
    # TODO generate into primary data structures
    for name, chain in self._chains.items_ordered():  # TODO work with net join
      for i, connect in enumerate(chain.links):
        link_chain_names.setdefault(connect, []).append(f"{name}_{i}")

    delegated_connects = self._all_delegated_connects()
    for name, connect in self._connects.items_ordered():
      if connect in delegated_connects:
        continue
      connect_names_opt = [self._connects.name_of(c) for c in self._all_connects_of(connect)]
      connect_names = [c for c in connect_names_opt if c is not None and not c.startswith('anon_')]
      if len(connect_names) > 1:
        raise UnconnectableError(f"Multiple names {connect_names} for connect")
      elif len(connect_names) == 1:
        name = connect_names[0]

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
      all_block_params = dict(block._parameters.items())
      for mixin in block._mixins:
        all_block_params.update(mixin._parameters.items())
      for (block_param_name, block_param) in all_block_params.items():
        if isinstance(block_param.binding, InitParamBinding) and block_param.binding.value is not None:
          param_typed_value = block_param._to_expr_type(block_param.binding.value)
          edgir.add_pair(pb.constraints, f'(init){block_name}.{block_param_name}').CopyFrom(  # TODO better name
            AssignBinding.make_assign(block_param, param_typed_value, ref_map)
          )

    return pb

  # TODO make this non-overriding?
  def _def_to_proto(self) -> edgir.HierarchyBlock:
    assert not self._mixins  # blocks with mixins can only be instantiated anonymously

    pb = edgir.HierarchyBlock()
    pb.prerefine_class.target.name = self._get_def_name()  # TODO integrate with a non-link populate_def_proto_block...
    pb = self._populate_def_proto_block_base(pb)
    pb = self._populate_def_proto_port_init(pb)

    pb = self._populate_def_proto_param_init(pb)

    pb = self._populate_def_proto_hierarchy(pb)
    pb = self._populate_def_proto_block_contents(pb)
    pb = self._populate_def_proto_description(pb)

    return pb

  MixinType = TypeVar('MixinType', bound='BlockInterfaceMixin')
  def with_mixin(self, tpe: MixinType) -> MixinType:
    """Adds an interface mixin for this Block. Mainly useful for abstract blocks, e.g. IoController with HasI2s."""
    from .BlockInterfaceMixin import BlockInterfaceMixin
    if isinstance(tpe, BlockPrototype):
      tpe_cls = tpe._tpe
    else:
      tpe_cls = tpe.__class__

    if not (issubclass(tpe_cls, BlockInterfaceMixin) and tpe_cls._is_mixin()):
      raise TypeError("param to with_mixin must be a BlockInterfaceMixin")
    if isinstance(self, BlockInterfaceMixin) and self._is_mixin():
      raise BlockDefinitionError(self, "mixins can not have with_mixin")
    if (self.__class__, AbstractBlockProperty) not in self._elt_properties:
      raise BlockDefinitionError(self, "mixins can only be added to abstract classes")
    if not isinstance(self, tpe_cls._get_mixin_base()):
      raise TypeError(f"block {self.__class__.__name__} not an instance of mixin base {tpe_cls._get_mixin_base().__name__}")
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
      raise EdgTypeError(f"first element 0 to chain", elts[0], (BasePort, Connection, Block))

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

    if isinstance(elts[-1], (BasePort, Connection)):
      chain_links.append(self.connect(current_port, elts[-1]))
    elif isinstance(elts[-1], Block):
      inable_ports = elts[-1]._get_ports_by_tag({Input}) + elts[-1]._get_ports_by_tag({InOut})
      if len(inable_ports) != 1:
        raise BlockDefinitionError(elts[-1], f"last element {len(elts) - 1} to chain {type(elts[-1])} does not have exactly one InOut or Input port: {inable_ports}")
      chain_blocks.append(elts[-1])
      chain_links.append(self.connect(current_port, inable_ports[0]))
    else:
      raise EdgTypeError(f"last argument {len(elts) - 1} to chain", elts[-1], (BasePort, Connection, Block))

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
  def ArgParameter(self, param: BoolLike, *, doc: Optional[str] = None) -> BoolExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: IntLike, *, doc: Optional[str] = None) -> IntExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: FloatLike, *, doc: Optional[str] = None) -> FloatExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: RangeLike, *, doc: Optional[str] = None) -> RangeExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: StringLike, *, doc: Optional[str] = None) -> StringExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayBoolLike, *, doc: Optional[str] = None) -> ArrayBoolExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayIntLike, *, doc: Optional[str] = None) -> ArrayIntExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayFloatLike, *, doc: Optional[str] = None) -> ArrayFloatExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayRangeLike, *, doc: Optional[str] = None) -> ArrayRangeExpr: ...  # type: ignore
  @overload
  def ArgParameter(self, param: ArrayStringLike, *, doc: Optional[str] = None) -> ArrayStringExpr: ...  # type: ignore

  def ArgParameter(self, param: CastableType, *, doc: Optional[str] = None) -> ConstraintExpr[Any, CastableType]:
    """Registers a constructor argument parameter for this Block.
    This doesn't actually do anything, but is needed to help the type system converter the *Like to a *Expr."""
    if not isinstance(param, ConstraintExpr):
      raise TypeError(f"param to ArgParameter(...) must be ConstraintExpr, got {param} of type {type(param)}")
    if param.binding is None:
      raise TypeError(f"param to ArgParameter(...) must have binding")
    if not isinstance(param.binding, InitParamBinding):
      raise TypeError(f"param to ArgParameter(...) must be __init__ argument")

    if doc is not None:
      self._param_docs[param] = doc

    return param

  T = TypeVar('T', bound=BasePort)
  def Port(self, tpe: T, tags: Iterable[PortTag]=[], *, optional: bool = False, doc: Optional[str] = None) -> T:
    """Registers a port for this Block"""
    if not isinstance(tpe, (Port, Vector)):
      raise NotImplementedError("Non-Port (eg, Vector) ports not (yet?) supported")
    for tag in tags:
      assert_cast(tag, PortTag, "tag for Port(...)")

    port = super().Port(tpe, optional=optional, doc=doc)

    self._port_tags[port] = set(tags)
    return port  # type: ignore

  ExportType = TypeVar('ExportType', bound=BasePort)
  def Export(self, port: ExportType, tags: Iterable[PortTag]=[], *, optional: bool = False, doc: Optional[str] = None,
             _connect = True) -> ExportType:
    """Exports a port of a child block, but does not propagate tags or optional."""
    assert port._is_bound(), "can only export bound type"
    port_parent = port._block_parent()
    assert isinstance(port_parent, Block)
    assert port_parent._parent is self, "can only export ports of contained block"

    if isinstance(port, BaseVector):  # TODO can the vector and non-vector paths be unified?
      assert isinstance(port, Vector)
      new_port: BasePort = self.Port(Vector(port._tpe.empty()),
                                     tags, optional=optional, doc=doc)
    elif isinstance(port, Port):
      new_port = self.Port(type(port).empty(),  # TODO is dropping args safe in all cases?
                           tags, optional=optional, doc=doc)
    else:
      raise NotImplementedError(f"unknown exported port type {port}")

    if _connect:
      self.connect(new_port, port)

    return new_port  # type: ignore

  BlockType = TypeVar('BlockType', bound='Block')
  def Block(self, tpe: BlockType) -> BlockType:
    from .BlockInterfaceMixin import BlockInterfaceMixin
    from .DesignTop import DesignTop

    if self._elaboration_state not in \
            [BlockElaborationState.init, BlockElaborationState.contents, BlockElaborationState.generate]:
      raise BlockDefinitionError(self, "can only define blocks in init, contents, or generate")

    if isinstance(tpe, BlockPrototype):
      tpe_cls = tpe._tpe
    else:
      tpe_cls = tpe.__class__

    if not issubclass(tpe_cls, Block):
      raise TypeError(f"param to Block(...) must be Block, got {tpe_cls}")
    if issubclass(tpe_cls, BlockInterfaceMixin) and tpe_cls._is_mixin():
      raise TypeError("param to Block(...) must not be BlockInterfaceMixin")
    if issubclass(tpe_cls, DesignTop):
      raise TypeError(f"param to Block(...) may not be DesignTop")

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
