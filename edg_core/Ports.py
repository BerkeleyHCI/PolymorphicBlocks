from __future__ import annotations

from typing import *
from abc import abstractmethod
from itertools import chain

from . import edgir
from .Core import Refable, HasMetadata, SubElementDict, non_library
from .IdentityDict import IdentityDict
from .ConstraintExpr import ConstraintExpr, RangeExpr, ParamBinding, BoolExpr, IsConnectedBinding, ParamVariableBinding
from .Builder import builder
from .Exception import *
if TYPE_CHECKING:
  from .Blocks import BaseBlock, Link
  from .PortBlocks import PortBridge, PortAdapter


PortParentTypes = Union['BaseContainerPort', 'BaseBlock']
@non_library
class BasePort(HasMetadata):
  SelfType = TypeVar('SelfType', bound='BasePort')

  def __init__(self) -> None:
    """Abstract Base Class for ports"""
    self._parent: Optional[Refable]  # set by metaclass
    self._initializer_args: Tuple[Tuple[Any, ...], Dict[str, Any]]  # set by metaclass

    super().__init__()

    self.parent: Optional[PortParentTypes] = None  # set during binding

  def _block_parent(self) -> Optional[BaseBlock]:
    from .Blocks import BaseBlock
    if isinstance(self.parent, BasePort):
      return self.parent._block_parent()
    elif isinstance(self.parent, BaseBlock):
      return self.parent
    elif self.parent is None:
      return None
    else:
      raise ValueError(f"Unknown parent type {self.parent}")

  @abstractmethod
  def is_connected(self) -> BoolExpr: ...

  @abstractmethod
  def _def_to_proto(self) -> edgir.PortTypes:  # TODO: this might not be valid for Vector types?
    raise NotImplementedError

  @abstractmethod
  def _type_of(self) -> Hashable: ...

  """Returns the proto of an instance of this object"""
  @abstractmethod
  def _instance_to_proto(self) -> edgir.PortLike:
    raise NotImplementedError

  def _bind_in_place(self, parent: PortParentTypes):
    self.parent = parent

  def _bind(self: SelfType, parent: PortParentTypes, *, ignore_context=False) -> SelfType:
    """Returns a clone of this object with the specified binding. This object must be unbound."""
    assert self.parent is None, "can't clone bound block"
    if not ignore_context:
      assert builder.get_curr_context() is self._parent, "can't clone to different context"
    clone = type(self)(*self._initializer_args[0], **self._initializer_args[1])  # type: ignore
    clone._bind_in_place(parent)
    return clone

  def _is_bound(self):
    def impl(elt: Optional[PortParentTypes]) -> bool:
      if elt is None:
        return False
      elif isinstance(elt, BasePort):
        return impl(elt.parent)
      else:
        return True
    return impl(self.parent)


@non_library
class BaseContainerPort(BasePort):  # TODO can this be removed?
  pass


PortLinkType = TypeVar('PortLinkType', bound='Link', covariant=True)  # TODO: this breaks w/ selftypes
@non_library
class Port(BasePort, Generic[PortLinkType]):
  """Constructor for ports, structural information (parameters, fields) should be defined here
  with optional initialization (for parameter defaults).
  All arguments must be optional with sane (empty) defaults (for cloneability).
  TODO: is this a reasonable restriction?"""
  def __init__(self) -> None:
    """Abstract Base Class for ports"""
    super().__init__()

    self.link_type: Type[PortLinkType]
    self._link_instance: Optional[PortLinkType] = None
    self.bridge_type: Optional[Type[PortBridge]] = None
    self._bridge_instance: Optional[PortBridge] = None  # internal only
    self.adapter_types: List[Type[PortAdapter]] = []

    # TODO delete type ignore after https://github.com/python/mypy/issues/5374
    self._parameters: SubElementDict[ConstraintExpr] = self.manager.new_dict(ConstraintExpr)  # type: ignore

    self.manager_ignored.update(['_is_connected'])
    self._is_connected = BoolExpr()._bind(ParamVariableBinding(IsConnectedBinding(self)))

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
    if block_parent is None or block_parent.parent is None:
      raise UnconnectableError(f"{self} must be bound to instantiate an adapter")

    enclosing_block = block_parent.parent
    if enclosing_block is not builder.get_curr_block():
      raise UnconnectableError(f"can only create adapters on ports of subblocks")
    assert isinstance(enclosing_block, Block)

    adapter_inst = enclosing_block.Block(adapter)
    enclosing_block.manager.add_element(
      f"(adapter){enclosing_block._name_of(block_parent)}.{block_parent._name_of(self)}",
      adapter_inst)
    enclosing_block.connect(self, adapter_inst.src)  # we don't name it to avoid explicit name conflicts
    return adapter_inst.dst

  def _initializers(self) -> IdentityDict[ConstraintExpr, ConstraintExpr]:
    # TODO unify w/ _initializer_to?
    return IdentityDict([(param, param.initializer)
                         for param in self._parameters.values() if param.initializer is not None])

  def _initializer_to(self, target: BasePort) -> BoolExpr:
    assert not self._is_bound(), f"model for initializer must be literal-like and not be bound"
    assert isinstance(target, type(self)), "target of initializer must be same type"  # TODO should be type equivalent, but breaks type checkers
    assert target._is_bound(), "target for initializer must be bound"

    param_init_exprs = [self_param._initializer_to(target._parameters[name])
                        for name, self_param in self._parameters.items()]
    return BoolExpr._combine_and(param_init_exprs)

  def _instance_to_proto(self) -> edgir.PortLike:
    pb = edgir.PortLike()
    pb.lib_elem.target.name = self._get_def_name()
    return pb

  def _def_to_proto(self) -> edgir.PortTypes:
    self._parameters.finalize()
    self._params_order = self.Metadata({str(idx): name for idx, name in enumerate(self._parameters.keys_ordered())})

    pb = edgir.Port()

    bases = [bcls for bcls in self.__class__.__bases__
             if issubclass(bcls, Port) and (bcls, 'non_library') not in bcls._elt_properties]
    for cls in bases:
      super_pb = pb.superclasses.add()
      super_pb.target.name = cls._static_def_name()

    for (name, param) in self._parameters.items():
      pb.params[name].CopyFrom(param._decl_to_proto())

    pb.meta.CopyFrom(self._metadata_to_proto(self._metadata, [], IdentityDict()))  # TODO use ref map

    return pb

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    if self._link_instance is not None:
      link_refs = self._link_instance._get_ref_map(edgir.localpath_concat(prefix, edgir.CONNECTED_LINK))
    else:
      link_refs = IdentityDict([])
    return super()._get_ref_map(prefix) + IdentityDict(
      [(self.is_connected(), edgir.localpath_concat(prefix, edgir.IS_CONNECTED))],
      *[param._get_ref_map(edgir.localpath_concat(prefix, name)) for name, param in self._parameters.items()]
    ) + link_refs

  def _type_of(self) -> Hashable:
    return type(self)

  def is_connected(self) -> BoolExpr:
    return self._is_connected

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
  def __init__(self) -> None:
    super().__init__()

    self._ports: SubElementDict[Port] = self.manager.new_dict(Port)

  def _initializers(self) -> IdentityDict[ConstraintExpr, ConstraintExpr]:
    # TODO unify w/ _initializer_to?
    return IdentityDict(chain(*[super()._initializers().items()],
                              *[port._initializers().items() for port in self._ports.values()]
                              ))

  def _initializer_to(self, target: BasePort) -> BoolExpr:
    assert isinstance(target, type(self)), "initializer must be of same type as target"  # TODO should be type equivalent, but breaks type checkers
    param_exprs = super()._initializer_to(target)
    port_init_exprs = [self_port._initializer_to(target._ports[name])
                       for name, self_port in self._ports.items()]
    return BoolExpr._combine_and([param_exprs] + port_init_exprs)

  def _def_to_proto(self) -> edgir.Bundle:
    self._parameters.finalize()
    self._params_order = self.Metadata({str(idx): name for idx, name in enumerate(self._parameters.keys_ordered())})

    self._ports.finalize()
    self._ports_order = self.Metadata({str(idx): name for idx, name in enumerate(self._ports.keys_ordered())})

    pb = edgir.Bundle()

    bases = [bcls for bcls in self.__class__.__bases__
             if issubclass(bcls, Port) and (bcls, 'non_library') not in bcls._elt_properties]
    for cls in bases:
      assert issubclass(cls, Bundle)  # TODO move elsewhere, but Bundle subtypes must only inherit from Bundle
      super_pb = pb.superclasses.add()
      super_pb.target.name = cls._static_def_name()

    for (name, param) in self._parameters.items():
      pb.params[name].CopyFrom(param._decl_to_proto())
    for (name, port) in self._ports.items():
      pb.ports[name].CopyFrom(port._instance_to_proto())

    pb.meta.CopyFrom(self._metadata_to_proto(self._metadata, [], IdentityDict()))  # TODO use ref map

    return pb

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    return super()._get_ref_map(prefix) + IdentityDict(
      *[field._get_ref_map(edgir.localpath_concat(prefix, name)) for (name, field) in self._ports.items()]
    )

  T = TypeVar('T', bound=Port)
  def Port(self, tpe: T, *, desc: Optional[str] = None) -> T:
    """Registers a field for this Bundle"""
    if not isinstance(tpe, Port):
      raise TypeError(f"param to Field(...) must be Port, got {tpe} of type {type(tpe)}")

    elt = tpe._bind(self)
    self._ports.register(elt)

    if not builder.stack or builder.stack[0] is self:
      self._sourcelocator[elt] = self._get_calling_source_locator()

    return elt
