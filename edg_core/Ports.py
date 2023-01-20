from __future__ import annotations

import itertools
from abc import abstractmethod
from typing import *

import edgir
from .Binding import ParamBinding, IsConnectedBinding, NameBinding
from .Builder import builder
from .ConstraintExpr import ConstraintExpr, BoolExpr, StringExpr
from .Core import Refable, HasMetadata, SubElementDict, non_library
from .HdlUserExceptions import *
from .IdentityDict import IdentityDict

if TYPE_CHECKING:
  from .Blocks import BaseBlock
  from .Link import Link
  from .PortBlocks import PortBridge, PortAdapter


PortParentTypes = Union['BaseContainerPort', 'BaseBlock']
@non_library
class BasePort(HasMetadata):
  SelfType = TypeVar('SelfType', bound='BasePort')

  def __init__(self) -> None:
    """Abstract Base Class for ports"""
    self._parent: Optional[PortParentTypes]  # refined from Optional[Refable] in base LibraryElement
    self._block_context: Optional[BaseBlock]  # set by metaclass, as lexical scope available pre-binding
    self._initializer_args: Tuple[Tuple[Any, ...], Dict[str, Any]]  # set by metaclass

    super().__init__()

  def _block_parent(self) -> Optional[BaseBlock]:
    from .Blocks import BaseBlock
    if isinstance(self._parent, BasePort):
      return self._parent._block_parent()
    elif isinstance(self._parent, BaseBlock):
      return self._parent
    elif self._parent is None:
      return None
    else:
      raise ValueError(f"Unknown parent type {self._parent}")

  @abstractmethod
  def _def_to_proto(self) -> edgir.PortTypes:  # TODO: this might not be valid for Vector types?
    raise NotImplementedError

  @abstractmethod
  def _type_of(self) -> Hashable: ...

  @abstractmethod
  def _instance_to_proto(self) -> edgir.PortLike:
    """Returns the proto of an instance of this object"""
    raise NotImplementedError

  def _bind_in_place(self, parent: PortParentTypes):
    self._parent = parent

  def _clone(self: SelfType) -> SelfType:
    """Returns a fresh clone of this object, with fresh references but preserving user-specified state like
    parameter initializers."""
    assert self._parent is None, "can't clone bound block"
    # TODO: this might be more efficient (but trickier) with copy.copy
    cloned = type(self)(*self._initializer_args[0], **self._initializer_args[1])  # type: ignore
    cloned._cloned_from(self)
    return cloned

  def _cloned_from(self: SelfType, other: SelfType) -> None:
    """Copies user-specified initializers from other."""
    pass

  def _bind(self: SelfType, parent: PortParentTypes) -> SelfType:
    """Returns a clone of this object with the specified binding. This object must be unbound."""
    assert builder.get_enclosing_block() is self._block_context, f"can't clone to different context, {builder.get_enclosing_block()} -> {self._block_context}"
    clone = self._clone()
    clone._bind_in_place(parent)
    return clone

  def _is_bound(self):
    def impl(elt: Optional[PortParentTypes]) -> bool:
      if elt is None:
        return False
      elif isinstance(elt, BasePort):
        return impl(elt._parent)
      else:
        return True
    return impl(self._parent)

  @abstractmethod
  def _get_initializers(self, path_prefix: List[str]) -> \
      List[Tuple[ConstraintExpr, List[str], ConstraintExpr]]:
    """Returns all the initializers of contained parameters, as tuples of (parameter, path, initializer value).
    Parameters without initializers are skipped."""
    raise NotImplementedError


@non_library
class BaseContainerPort(BasePort):  # TODO can this be removed?
  pass


PortLinkType = TypeVar('PortLinkType', bound='Link', covariant=True)  # TODO: this breaks w/ selftypes
@non_library
class Port(BasePort, Generic[PortLinkType]):
  """Abstract Base Class for ports"""

  SelfType = TypeVar('SelfType', bound='Port')

  @classmethod
  def empty(cls: Type[SelfType]) -> SelfType:
    """Automatically generated empty constructor, that creates a port with all parameters None."""
    # This is kind of a really nasty hack that overwrites initializers :s
    new_model = cls()
    new_model._clear_initializers()
    return new_model

  def __init__(self) -> None:
    """Constructor for ports, structural information (parameters, fields) should be defined here
    with optional initialization (for parameter defaults).
    All arguments must be optional with sane (empty) defaults (for cloneability).
    TODO: is this a reasonable restriction?"""
    super().__init__()

    self.link_type: Type[PortLinkType]
    # This needs to be lazy-initialized to avoid building ports with links with ports, and so on
    # TODO: maybe a cleaner solution is to mark port constructors in a Block context or Link context?
    self._link_instance: Optional[PortLinkType] = None
    self.bridge_type: Optional[Type[PortBridge]] = None
    self._bridge_instance: Optional[PortBridge] = None  # internal only

    # TODO delete type ignore after https://github.com/python/mypy/issues/5374
    self._parameters: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr)  # type: ignore

    self.manager_ignored.update(['_is_connected', '_name'])
    self._is_connected = BoolExpr()._bind(IsConnectedBinding(self))
    self._name = StringExpr()._bind(NameBinding(self))

  def _clear_initializers(self) -> None:
    self._parameters.finalize()
    for (name, param) in self._parameters.items():
      param.initializer = None

  def _cloned_from(self: SelfType, other: SelfType) -> None:
    super()._cloned_from(other)
    self._parameters.finalize()
    for (name, param) in self._parameters.items():
      other_param = other._parameters[name]
      assert isinstance(other_param, type(param))
      param.initializer = other_param.initializer

  def init_from(self: SelfType, other: SelfType):
    assert self._parent is not None, "may only init_from on an bound port"
    assert not self._get_initializers([]), "may only init_from an empty model"
    self._cloned_from(other)

  def _bridge(self) -> Optional[PortBridge]:
    """Creates a (unbound) bridge and returns it."""
    if self.bridge_type is None:
      return None
    if self._bridge_instance is not None:
      return self._bridge_instance
    assert self._is_bound(), "not bound, can't create bridge"

    self._bridge_instance = self.bridge_type()
    return self._bridge_instance

  ConvertTargetType = TypeVar('ConvertTargetType', bound='Port')
  def _convert(self, adapter: PortAdapter[ConvertTargetType]) -> ConvertTargetType:
    """Given an Adapter block, """
    from .HierarchyBlock import Block

    block_parent = self._block_parent()
    if block_parent is None or block_parent._parent is None:
      raise UnconnectableError(f"{self} must be bound to instantiate an adapter")

    enclosing_block = block_parent._parent
    if enclosing_block is not builder.get_enclosing_block():
      raise UnconnectableError(f"can only create adapters on ports of subblocks")
    assert isinstance(enclosing_block, Block)

    adapter_inst = enclosing_block.Block(adapter)
    enclosing_block.manager.add_element(
      f"(adapter){block_parent._name_from(enclosing_block)}.{self._name_from(block_parent)}",
      adapter_inst)
    enclosing_block.connect(self, adapter_inst.src)  # we don't name it to avoid explicit name conflicts
    return adapter_inst.dst

  def _instance_to_proto(self) -> edgir.PortLike:
    pb = edgir.PortLike()
    pb.lib_elem.target.name = self._get_def_name()
    return pb

  def _def_to_proto(self) -> edgir.PortTypes:
    self._parameters.finalize()

    pb = edgir.Port()

    pb.self_class.target.name = self._get_def_name()

    for cls in self._get_bases_of(Port):
      super_pb = pb.superclasses.add()
      super_pb.target.name = cls._static_def_name()

    for (name, param) in self._parameters.items():
      edgir.add_pair(pb.params, name).CopyFrom(param._decl_to_proto())

    self._populate_metadata(pb.meta, self._metadata, IdentityDict())  # TODO use ref map

    return pb

  def _type_of(self) -> Hashable:
    return type(self)

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    if self._link_instance is not None:
      link_refs = self._link_instance._get_ref_map(edgir.localpath_concat(prefix, edgir.CONNECTED_LINK))
    else:
      link_refs = IdentityDict([])
    return super()._get_ref_map(prefix) + IdentityDict[Refable, edgir.LocalPath](
      [(self.is_connected(), edgir.localpath_concat(prefix, edgir.IS_CONNECTED)),
       (self.name(), edgir.localpath_concat(prefix, edgir.NAME))],
      *[param._get_ref_map(edgir.localpath_concat(prefix, name)) for name, param in self._parameters.items()]
    ) + link_refs

  def _get_initializers(self, path_prefix: List[str]) -> List[Tuple[ConstraintExpr, List[str], ConstraintExpr]]:
    self._parameters.finalize()
    return [(param, path_prefix + [name], param.initializer) for (name, param) in self._parameters.items()
            if param.initializer is not None]

  def is_connected(self) -> BoolExpr:
    return self._is_connected

  def name(self) -> StringExpr:
    return self._name

  def link(self) -> PortLinkType:
    """Returns the link connected to this port, if this port is bound."""
    # TODO: with some magic, this can be implemented w/o the function call by hiding logic in getattr
    if self._link_instance is not None:
      return self._link_instance
    assert self._is_bound(), "not bound, can't create link"

    self._link_instance = self.link_type()
    self._link_instance._bind_in_place(self)
    return self._link_instance

  U = TypeVar('U', bound=ConstraintExpr)
  def Parameter(self, tpe: U) -> U:
    """Registers a parameter for this Port"""
    elt = tpe._bind(ParamBinding(self))
    self._parameters.register(elt)
    return elt


@non_library
class Bundle(Port[PortLinkType], BaseContainerPort, Generic[PortLinkType]):
  SelfType = TypeVar('SelfType', bound='Bundle')

  def __init__(self) -> None:
    super().__init__()

    self._ports: SubElementDict[Port] = self.manager.new_dict(Port)

  def _clear_initializers(self) -> None:
    super()._clear_initializers()
    self._ports.finalize()
    for (name, port) in self._ports.items():
      port._clear_initializers()

  def _cloned_from(self: SelfType, other: SelfType) -> None:
    super()._cloned_from(other)
    for (name, port) in self._ports.items():
      other_port = other._ports[name]
      assert isinstance(other_port, type(port))
      port._cloned_from(other_port)

  def with_elt_initializers(self: SelfType, replace_elts: dict[str, Port]) -> SelfType:
    """Clones model-typed self, except adding initializers to elements from the input dict.
    Those elements must be empty."""
    assert self._parent is None, "self must not be bound"
    cloned = self._clone()
    for (name, replace_port) in replace_elts.items():
      assert replace_port._parent is None, "replace_elts must not be bound"
      cloned_port = cloned._ports[name]
      assert isinstance(replace_port, type(cloned_port))
      assert not cloned_port._get_initializers([]), f"replace_elts sub-port {name} was not empty"
      cloned_port._cloned_from(replace_port)
    return cloned

  def _def_to_proto(self) -> edgir.Bundle:
    self._parameters.finalize()
    self._ports.finalize()

    pb = edgir.Bundle()

    pb.self_class.target.name = self._get_def_name()

    for cls in self._get_bases_of(Bundle):
      super_pb = pb.superclasses.add()
      super_pb.target.name = cls._static_def_name()

    for (name, param) in self._parameters.items():
      edgir.add_pair(pb.params, name).CopyFrom(param._decl_to_proto())
    for (name, port) in self._ports.items():
      edgir.add_pair(pb.ports, name).CopyFrom(port._instance_to_proto())

    self._populate_metadata(pb.meta, self._metadata, IdentityDict())  # TODO use ref map

    return pb

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    return super()._get_ref_map(prefix) + IdentityDict(
      *[field._get_ref_map(edgir.localpath_concat(prefix, name)) for (name, field) in self._ports.items()]
    )

  def _get_initializers(self, path_prefix: List[str]) -> List[Tuple[ConstraintExpr, List[str], ConstraintExpr]]:
    self_initializers = super()._get_initializers(path_prefix)
    self._ports.finalize()
    return list(itertools.chain(
      self_initializers,
      *[port._get_initializers(path_prefix + [name]) for (name, port) in self._ports.items()]
    ))

  T = TypeVar('T', bound=Port)
  def Port(self, tpe: T, *, desc: Optional[str] = None) -> T:
    """Registers a field for this Bundle"""
    if not isinstance(tpe, Port):
      raise TypeError(f"param to Field(...) must be Port, got {tpe} of type {type(tpe)}")

    elt = tpe._bind(self)
    self._ports.register(elt)

    return elt

