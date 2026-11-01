from __future__ import annotations

import inspect
from types import FrameType, FunctionType
from typing import *
from abc import abstractmethod

from typing_extensions import override

from .HdlUserExceptions import ElementNamingError
from .. import edgir
from .Builder import builder
from .IdentityDict import IdentityDict

ElementType = TypeVar("ElementType")


class SourceLocator:
    """Object that can be used to locate the source of a library element, for error reporting."""

    def __init__(self, top_frame: Optional[FrameType], depth: int) -> None:
        frame = top_frame
        assert frame is not None
        for i in range(depth):
            frame = frame.f_back
            assert frame is not None
        self._filename = frame.f_code.co_filename
        self._line = frame.f_lineno

    @classmethod
    def from_caller(cls) -> SourceLocator:
        # returns the source locator for the calling frame of the caller
        return cls(inspect.currentframe(), 2)

    @override
    def __repr__(self) -> str:
        return f"{self._filename}:{self._line}"


class NamespaceManager:
    """Manages names of objects in a naming container.
    Supports source locators via inspect, before an object is given a name.
    Supports delayed naming via callables, allowing names to depend on other names that may not yet be assigned.
    """

    def __init__(self, parent: Any) -> None:
        self._parent = parent
        self._base_names = IdentityDict[Any, Union[SourceLocator, str, Callable[[], str]]]()
        self._default_names = IdentityDict[Any, str]()
        self._default_name_prefix_count: Dict[str, int] = {}
        self._assigned_names: Set[str] = set()
        self._aliases = IdentityDict[Any, Any]()

    def __contains__(self, item: Any) -> bool:
        if item in self._aliases:
            return self._aliases[item] in self

        return item in self._base_names

    def resolve_names(self) -> None:
        # asserts that all names are given and valid and resolves anonymous names
        missing_names: List[str] = []
        error_names: List[Any] = []
        for obj, name in self._base_names.items():
            if isinstance(name, SourceLocator):
                default_name = self._default_names.get(obj, None)
                if default_name is not None:
                    self._base_names.update(obj, default_name)
                    if default_name in self._assigned_names:
                        raise ElementNamingError(type(self._parent), f"duplicate name {default_name}")
                    self._assigned_names.add(default_name)
                else:
                    missing_names.append(f"{obj} @ {name}")
            else:
                pass  # has valid name

        if missing_names:
            raise ElementNamingError(type(self._parent), f"no name for objects {missing_names}")
        if error_names:  # errors may be due to missing names, so check after missing names are resolved
            raise ElementNamingError(type(self._parent), f"error generating names for objects {error_names}")

    def add_alias(self, src: Any, target: Any) -> None:
        self._aliases[src] = target

    def add_expected(self, item: Any, source_locator: SourceLocator, *, default_prefix: Optional[str] = None) -> None:
        self._base_names[item] = source_locator
        if default_prefix:
            count = self._default_name_prefix_count.get(default_prefix, 0)
            self._default_name_prefix_count[default_prefix] = count + 1
            self._default_names[item] = f"{default_prefix}{count}"

    def add_name(self, item: Any, name: Union[str, Callable[[], str]]) -> None:
        existing = self._base_names.get(item, None)
        if existing is None:
            if isinstance(item, ElementDict):
                item._set_parent(self)
                self._base_names[item] = name
            else:
                return  # not expected, ignore
        elif isinstance(existing, SourceLocator):
            if name in self._assigned_names:
                raise ElementNamingError(type(self._parent), f"duplicate name {name}")
            if isinstance(name, str):
                self._assigned_names.add(name)

            self._base_names.update(item, name)
        elif existing is not None:
            return  # reassignments, eg for aliasing for deprecation, ignored; first one takes
        else:
            raise ValueError("unexpected name entry type")

    def name(self, item: Any, *, debug: bool = False) -> str:
        """Returns the name of an item.
        If debug, returns a debugging name if the final name is not resolved, otherwise raises."""
        if item in self._aliases:
            return self.name(self._aliases[item], debug=debug)

        name = self._base_names.get(item, None)
        if isinstance(name, str):
            return name
        elif isinstance(name, FunctionType):
            name = name()
            assert isinstance(name, str)
            self._base_names.update(item, name)
            if name in self._assigned_names:
                raise ElementNamingError(type(self._parent), f"duplicate name {name}")
            self._assigned_names.add(name)
            return name
        elif isinstance(name, SourceLocator):
            if debug:
                return f"(unnamed {item}@{name})"
            else:
                raise ValueError(f"no name for {item}")
        else:
            raise ValueError(f"no name for unexpected {item} (internal consistency error)")


class ElementDict(Generic[ElementType]):
    """Dict that contains sub-elements, basically a dict with a hook that notifies its parent when items are added."""

    # TODO also have a KeyType? Perhaps enforce type bounds, eg must be str-able?
    def __init__(self) -> None:
        self.container: Dict[Union[str, int], ElementType] = {}
        self._parent: Optional[NamespaceManager] = None  # name prefix, pointer to top level

    def _set_parent(self, parent: NamespaceManager) -> None:
        self._parent = parent

    def __setitem__(self, key: Union[str, int], value: ElementType) -> None:
        assert self._parent is not None
        self._parent.add_name(value, lambda: f"{self._parent.name(self)}[{key}]")  # type: ignore[union-attr]
        self.container[key] = value

    def __getitem__(self, item: Union[str, int]) -> ElementType:
        return self.container[item]

    def items(self) -> ItemsView[Union[str, int], ElementType]:
        return self.container.items()

    def values(self) -> ValuesView[ElementType]:
        return self.container.values()


class Refable:
    """Object that could be referenced into a edgir.LocalPath"""

    RefMapType = IdentityDict["Refable", edgir.LocalPath]

    @override
    def __repr__(self) -> str:
        return "%s@%02x" % (self.__class__.__name__, (id(self) // 4) & 0xFF)

    @override
    def __eq__(self, other: Any) -> None:  # type: ignore
        raise NotImplementedError(f"__eq__ reserved for DSL, attempted to compare {self} and {other}")

    def __bool__(self) -> bool:
        raise ValueError(
            "bool-ing a Refable is almost certainly a mistake. "
            "Note: 'and' and 'or' do not work on BoolExpr, use '&' or '|' instead."
        )

    def _create_ref_map(self, prefix: edgir.LocalPath = edgir.LocalPath()) -> RefMapType:
        """Wrapper around _build_ref_map for top-level refmap construction."""
        ref_map = IdentityDict[Refable, edgir.LocalPath]()
        self._build_ref_map(ref_map, prefix)
        return ref_map

    def _build_ref_map(self, ref_map: Refable.RefMapType, prefix: edgir.LocalPath) -> None:
        """Adds the references contained by this object to the parameter refmap."""
        ref_map[self] = prefix


class EltPropertiesBase:
    """ "Base type for properties associated with a particular block, that do not apply to subtypes"""

    pass


NonLibraryProperty = EltPropertiesBase()
NonLibraryType = TypeVar("NonLibraryType", bound=Type["LibraryElement"])


def non_library(decorated: NonLibraryType) -> NonLibraryType:
    decorated._elt_properties[(decorated, NonLibraryProperty)] = None
    return decorated


@non_library
class LibraryElement(Refable):
    """Defines a library element, which optionally contains other library elements."""

    _elt_properties: Dict[Tuple[Type[LibraryElement], EltPropertiesBase], Any] = {}

    @override
    def __repr__(self) -> str:
        return "%s@%02x" % (self._get_def_name(), (id(self) // 4) & 0xFF)

    BaseType = TypeVar("BaseType", bound="LibraryElement")

    @classmethod
    def _get_bases_of(cls, base_type: Type[BaseType]) -> Tuple[List[Type[BaseType]], List[Type[BaseType]]]:
        """Returns all the base classes of this class, as a list of direct superclasses (including through non_library
        elements) and a list of additional (indirect) superclasses. Direct superclasses are in MRO order, indirect
        superclasses order is not defined (but MRO in current practice).

        mypy currently does not allow passing in abstract types, so generally calls to this need type: ignore."""
        direct_bases: Set[Type[LibraryElement.BaseType]] = set()

        def process_direct_base(bcls: Type[LibraryElement.BaseType]) -> None:
            if not issubclass(bcls, base_type):
                return  # ignore above base_type
            if (bcls, NonLibraryProperty) in bcls._elt_properties:  # non-library, recurse into parents
                for bcls_base in bcls.__bases__:
                    process_direct_base(bcls_base)
            else:  # anything else, directly append if not existing
                direct_bases.add(bcls)

        for bcls in cls.__bases__:
            process_direct_base(bcls)

        ordered_direct_bases: List[Type[LibraryElement.BaseType]] = []
        ordered_indirect_bases: List[Type[LibraryElement.BaseType]] = []
        for mro_base in cls.__mro__[1:]:  # ignore self
            if mro_base in direct_bases:
                ordered_direct_bases.append(mro_base)
            elif issubclass(mro_base, base_type) and (mro_base, NonLibraryProperty) not in mro_base._elt_properties:
                ordered_indirect_bases.append(mro_base)

        return ordered_direct_bases, ordered_indirect_bases

    @classmethod
    def _static_def_name(cls) -> str:
        """If this library element is defined by class (all instances have an equivalent library definition),
        returns the definition name. Otherwise, should crash."""
        return cls.__module__ + "." + cls.__name__

    def _get_def_name(self) -> str:
        """Returns the definition name"""
        return self.__class__._static_def_name()

    @abstractmethod
    def _def_to_proto(self) -> Union[edgir.PortTypes, edgir.BlockLikeTypes]: ...


class NamingContainer:
    """Mixin class for objects that contain and name internal objects"""

    def __init__(self) -> None:
        self._parent: Optional[NamingContainer] = None  # set by binding, None means not bound
        self._namer = NamespaceManager(self)

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_namer"):  # don't access before definition
            self._namer.add_name(value, name)
        super().__setattr__(name, value)

    def _path_of(self, elt: Any, *, debug: bool = False) -> List[str]:
        """Returns the name path of an inner element.
        If debug is true, will return the best-effort name even if it is not yet assigned.
        If debug is false, raises an error for unassigned names."""
        if elt is self:
            return []
        else:
            assert elt._parent is not None, "can't get path / name for non-bound element"
            return self._path_of(elt._parent, debug=debug) + [elt._parent._name_of(elt, debug=debug)]

    def _path_name_of(self, elt: Any, *, debug: bool = False) -> str:
        """Convenience stringify wrapper around _path_of."""
        return ".".join(self._path_of(elt, debug=debug))

    def _name_of(self, elt: Any, *, debug: bool = False) -> str:
        """Returns the name of a contained element, non-recursively."""
        if elt not in self._namer:
            if not debug:
                raise ValueError(f"{self.__class__.__name__} has no {elt}")
            else:
                return f"(unknown {elt.__class__.__name__})"
        else:
            return self._namer.name(elt, debug=debug)


@non_library
class HasMetadata(LibraryElement, NamingContainer):
    """A library element with the metadata dict-like field"""

    def __init__(self) -> None:
        super().__init__()
        self._metadata: List[Any] = []

    MetadataType = TypeVar("MetadataType", bound=Union[str, Mapping[str, Any], IdentityDict[Any, Any]])

    def Metadata(self, value: MetadataType) -> MetadataType:
        """Adds a metadata field to this object. Reference to the value must not change, and reassignment will error.
        Value may be changed until proto generation.
        Utility method for library builders."""
        self._metadata.append(value)
        self._namer.add_expected(value, SourceLocator.from_caller())
        return value

    def _populate_metadata(self, pb: edgir.Metadata, src: Any, ref_map: Refable.RefMapType) -> None:
        """Generate metadata from a given object."""
        if isinstance(src, str):
            pb.text_leaf = src
        elif isinstance(src, bytes):
            pb.bin_leaf = src
        elif isinstance(src, dict) or isinstance(src, IdentityDict):
            for key, val in src.items():
                assert isinstance(key, str), f"must overload _metadata_to_proto for non-str dict key {key}"
                self._populate_metadata(pb.members.node[key], val, ref_map)
        elif isinstance(src, list):
            for idx, val in enumerate(src):
                self._populate_metadata(pb.members.node[str(idx)], val, ref_map)
        else:
            raise ValueError(f"must overload _metadata_to_proto to handle unknown value {src}")
