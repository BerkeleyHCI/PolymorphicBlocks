from __future__ import annotations

import itertools
from abc import abstractmethod
from typing import Generic, Optional, Dict, Hashable, List

from deprecated import deprecated
from typing_extensions import TypeVar, override

from .Binding import ParamBinding, IsConnectedBinding, NameBinding
from .Builder import builder
from .ConstraintExpr import ConstraintExpr, BoolExpr, StringExpr
from .Core import Refable, HasMetadata, non_library, NamingContainer, SourceLocator
from .HdlUserExceptions import *
from .IdentityDict import IdentityDict
from .. import edgir

if TYPE_CHECKING:
    from .Blocks import BaseBlock
    from .Array import Vector
    from .Link import Link
    from .PortBlocks import PortBridge, PortAdapter


class InitializerContextMeta(type):
    @override
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Hook on construction to store some metadata about its creation.
        This hooks the top-level __init__ only."""
        obj = type.__call__(cls, *args, **kwargs)
        obj._initializer_args = (args, kwargs)  # stores args so it is clone-able
        return obj


PortParentTypes = Union["Port", "Vector[Any]", "BaseBlock"]


@non_library
class BasePort(HasMetadata, NamingContainer, metaclass=InitializerContextMeta):
    SelfType = TypeVar("SelfType", bound="BasePort")

    def __init__(self) -> None:
        """Abstract Base Class for ports"""
        self._parent: Optional[PortParentTypes]  # refined from Optional[Refable] in base LibraryElement
        self._block_context: Optional["Refable"]  # set by metaclass, as lexical scope available pre-binding
        self._initializer_args: Tuple[Tuple[Any, ...], Dict[str, Any]]  # set by metaclass
        self._block_context = builder._current_block()

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
    @override
    def _def_to_proto(self) -> edgir.PortTypes:  # TODO: this might not be valid for Vector types?
        raise NotImplementedError

    @abstractmethod
    def _type_of(self) -> Hashable: ...

    @abstractmethod
    def _populate_portlike_proto(self, pb: edgir.PortLike) -> None:
        """Populates the proto of an instance of this object"""
        raise NotImplementedError

    def _bind_in_place(self, parent: PortParentTypes) -> None:
        self._parent = parent

    def _clone(self: SelfType) -> SelfType:
        """Returns a fresh clone of this object, with fresh references but preserving user-specified state like
        parameter initializers."""
        assert self._parent is None, "can't clone bound block"
        # TODO: this might be more efficient (but trickier) with copy.copy
        cloned = type(self)(*self._initializer_args[0], **self._initializer_args[1])
        cloned._cloned_from(self)
        return cloned

    def _cloned_from(self: SelfType, other: SelfType) -> None:
        """Copies user-specified initializers from other."""
        pass

    def _bind(self: SelfType, parent: PortParentTypes) -> SelfType:
        """Returns a clone of this object with the specified binding. This object must be unbound."""
        assert (
            self._block_context is None or builder.block() is self._block_context
        ), f"can't clone to different context, {builder.block()} -> {self._block_context}"
        clone = self._clone()
        clone._bind_in_place(parent)
        return clone

    def _is_bound(self) -> bool:
        def impl(elt: Optional[PortParentTypes]) -> bool:
            if elt is None:
                return False
            elif isinstance(elt, BasePort):
                return impl(elt._parent)
            else:
                return True

        return impl(self._parent)

    @abstractmethod
    def _get_initializers(self, path_prefix: List[str]) -> List[Tuple[ConstraintExpr, List[str], ConstraintExpr]]:
        """Returns all the initializers of contained parameters, as tuples of (parameter, path, initializer value).
        Parameters without initializers are skipped."""
        raise NotImplementedError


PortLinkType = TypeVar("PortLinkType", bound="Link", covariant=True, default="Link")  # TODO: this breaks w/ selftypes


@non_library
class Port(BasePort, Generic[PortLinkType]):
    """Abstract Base Class for ports"""

    SelfType = TypeVar("SelfType", bound="Port")

    link_type: Type[PortLinkType]
    bridge_type: Optional[Type[PortBridge]] = None

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

        # This needs to be lazy-initialized to avoid building ports with links with ports, and so on
        # TODO: maybe a cleaner solution is to mark port constructors in a Block context or Link context?
        self._link_instance: Optional[PortLinkType] = None
        self._bridge_instance: Optional[PortBridge] = None  # internal only
        self._adapter_count: int = 0

        self._parameters: List[ConstraintExpr] = []
        self._ports: List[Port] = []

        self._manager_ignored.update(["_is_connected", "_name"])
        self._is_connected = BoolExpr()._bind(IsConnectedBinding(self))
        self._name = StringExpr()._bind(NameBinding(self))

    def _clear_initializers(self) -> None:
        for param in self._parameters:
            param.initializer = None
        for port in self._ports:
            port._clear_initializers()

    @override
    def _cloned_from(self: SelfType, other: SelfType) -> None:
        super()._cloned_from(other)
        assert len(other._parameters) == len(self._parameters)
        for self_param, other_param in zip(self._parameters, other._parameters):
            assert type(other_param) is type(self_param)
            self_param.initializer = other_param.initializer
        assert len(other._ports) == len(self._ports)
        for self_port, other_port in zip(self._ports, other._ports):
            assert type(other_port) is type(self_port)
            self_port._cloned_from(other_port)

    def init_from(self: SelfType, other: SelfType) -> None:
        assert self._parent is not None, "may only init_from on an bound port"
        assert not self._get_initializers([]), "may only init_from an empty model"
        self._cloned_from(other)

    def _bridge(self) -> Optional[PortBridge]:
        """Creates a (unbound) bridge and returns it."""
        from .HierarchyBlock import Block

        if self.bridge_type is None:
            return None
        if self._bridge_instance is not None:
            return self._bridge_instance
        assert self._is_bound(), "not bound, can't create bridge"

        Block._next_bind = self.bridge_type
        self._bridge_instance = self.bridge_type()
        return self._bridge_instance

    ConvertTargetType = TypeVar("ConvertTargetType", bound="Port")

    def _convert(self, adapter: PortAdapter[ConvertTargetType]) -> ConvertTargetType:
        """Given an Adapter block,"""
        from .HierarchyBlock import Block

        block_parent = self._block_parent()
        if block_parent is None:
            raise UnconnectableError(f"{self} must be bound to instantiate an adapter")

        enclosing_block = builder.block()
        assert isinstance(enclosing_block, Block)
        if (block_parent is not enclosing_block) and (block_parent._parent is not enclosing_block):
            raise UnconnectableError(f"can only create adapters on own ports or subblock ports")

        # TODO proper programmatic naming API
        adapter_inst = enclosing_block.Block(adapter)
        adapter_name_suffix = f"_{self._adapter_count}" if self._adapter_count > 0 else ""
        enclosing_block._namer.add_name(
            adapter_inst, f"(adapter){enclosing_block._path_name_of(self)}{adapter_name_suffix}"
        )
        enclosing_block.connect(self, adapter_inst.src)  # we don't name it to avoid explicit name conflicts
        self._adapter_count += 1
        return adapter_inst.dst

    @override
    def _populate_portlike_proto(self, pb: edgir.PortLike) -> None:
        pb.lib_elem.target.name = self._get_def_name()

    @override
    def _def_to_proto(self) -> edgir.Port:
        self._namer.validate_names()

        pb = edgir.Port()

        pb.self_class.target.name = self._get_def_name()

        direct_bases, indirect_bases = self._get_bases_of(Port)
        for cls in direct_bases:
            pb.superclasses.add().target.name = cls._static_def_name()
        for cls in indirect_bases:
            pb.super_superclasses.add().target.name = cls._static_def_name()

        for param in self._parameters:
            param._populate_decl_proto(edgir.add_pair(pb.params, self._name_of(param)))
        for port in self._ports:
            port._populate_portlike_proto(edgir.add_pair(pb.ports, self._name_of(port)))

        named_metadata = {self._name_of(metadata): metadata for metadata in self._metadata}
        self._populate_metadata(pb.meta, named_metadata, IdentityDict())
        return pb

    @override
    def _type_of(self) -> Hashable:
        return type(self)

    @override
    def _build_ref_map(self, ref_map: Refable.RefMapType, prefix: edgir.LocalPath) -> None:
        super()._build_ref_map(ref_map, prefix)
        ref_map[self.is_connected()] = edgir.localpath_concat(prefix, edgir.IS_CONNECTED)
        ref_map[self.name()] = edgir.localpath_concat(prefix, edgir.NAME)
        for param in self._parameters:
            param._build_ref_map(ref_map, edgir.localpath_concat(prefix, self._name_of(param)))
        for port in self._ports:
            port._build_ref_map(ref_map, edgir.localpath_concat(prefix, self._name_of(port)))
        if self._link_instance is not None:
            self._link_instance._build_ref_map(ref_map, edgir.localpath_concat(prefix, edgir.CONNECTED_LINK))

    @override
    def _get_initializers(self, path_prefix: List[str]) -> List[Tuple[ConstraintExpr, List[str], ConstraintExpr]]:
        initializers: List[Tuple[ConstraintExpr, List[str], ConstraintExpr]] = [
            (param, path_prefix + [self._name_of(param)], param.initializer)
            for param in self._parameters
            if param.initializer is not None
        ]
        for port in self._ports:
            initializers.extend(port._get_initializers(path_prefix + [self._name_of(port)]))
        return initializers

    def _with_elt_initializers(self: SelfType, replace_elts: dict[str, "Port"]) -> SelfType:
        """Clones model-typed self, except adding initializers to elements from the input dict.
        Those elements must be empty."""
        assert self._parent is None, "self must not be bound"
        cloned = self._clone()
        for name, replace_port in replace_elts.items():
            assert replace_port._parent is None, "replace_elts must not be bound"
            cloned_port = getattr(cloned, name)
            assert isinstance(replace_port, type(cloned_port))
            assert not cloned_port._get_initializers([]), f"replace_elts sub-port {name} was not empty"
            cloned_port._cloned_from(replace_port)
        return cloned

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

    U = TypeVar("U", bound=ConstraintExpr)

    def Parameter(self, tpe: U) -> U:
        """Registers a parameter for this Port"""
        elt = tpe._bind(ParamBinding(self))
        self._parameters.append(elt)
        self._namer.add_expected(elt, SourceLocator.from_caller())
        return elt

    T = TypeVar("T", bound="Port")

    def Port(self, tpe: T, *, desc: Optional[str] = None) -> T:
        """Registers a sub-Port for this Port"""
        if not isinstance(tpe, Port):
            raise EdgTypeError(f"param to Port(...)", tpe, Port)

        elt = tpe._bind(self)
        self._ports.append(elt)
        self._namer.add_expected(elt, SourceLocator.from_caller())

        return elt


@non_library
@deprecated(reason="merged with Port, use Port instead")
class Bundle(Port[PortLinkType], Generic[PortLinkType]):
    SelfType = TypeVar("SelfType", bound="Bundle")
