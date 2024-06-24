from __future__ import annotations

from typing import *
from abc import abstractmethod

from .. import edgir
from .Builder import builder
from .IdentityDict import IdentityDict
from .IdentitySet import IdentitySet


ElementType = TypeVar('ElementType')
class SubElementDict(Generic[ElementType]):
  def __init__(self, anon_prefix: Optional[str]=None) -> None:
    self.anons = IdentitySet[ElementType]()  # TODO this should be order-preserving?
    self.anon_prefix = anon_prefix
    self.container: Dict[str, ElementType] = {}
    self.names = IdentityDict[ElementType, str]()  # TODO unify w/ container?
    self.keys_list: List = []
    self.closed = False

  def register(self, item: ElementType) -> ElementType:
    assert not self.closed, "adding items after closed"
    self.anons.add(item)
    return item

  def add_element(self, name: str, item: Any) -> None:
    assert not self.closed, "naming items after closed"
    assert item in self.anons, f"attempted to add {name}={item}, but did not pre-register"
    self.anons.remove(item)
    assert name not in self.container, f"attempted to reassign {name}={item}"

    self.container[name] = item
    self.names[item] = name
    self.keys_list.append(name)

  # TODO should this be automatically called?
  def finalize(self):
    if self.closed:
      return
    if self.anon_prefix is None:
      assert not self.anons, f"can't have unnamed objects: {self.anons}"
    else:
      for id, elt in enumerate(self.anons):
        name = f'{self.anon_prefix}_{id}'
        assert name not in self.container, f"duplicate name {name}"
        self.container[name] = elt
        self.names[elt] = name
        self.keys_list.append(name)
      self.anons = IdentitySet[ElementType]()  # TODO needs clear operation

  def all_values_temp(self) -> Iterable[ElementType]:  # TODO needs better API name, reconcile w/ values?
    return list(self.container.values()) + list(self.anons)

  # TODO the below allows this to be used like a dict, is this a good idea?
  # TODO should these make sure the dict is closed?
  def items(self) -> ItemsView[str, ElementType]:
    return self.container.items()

  def items_ordered(self) -> Iterable[Tuple[str, ElementType]]:
    return [(key, self.container[key]) for key in self.keys_list]

  def keys_ordered(self) -> Iterable[str]:  # TODO should this clone?
    return self.keys_list

  def values(self) -> ValuesView[ElementType]:
    return self.container.values()

  def __getitem__(self, item: str) -> ElementType:
    return self.container[item]

  def __contains__(self, item: str) -> bool:
    return item in self.container

  def name_of(self, elt: ElementType) -> Optional[str]:
    if elt in self.names:
      return self.names[elt]
    else:
      return None

class SubElementManager:
  def __init__(self) -> None:
    self.dicts: List[Tuple[Union[Type, Tuple[Type, ...]], SubElementDict]] = []
    self.aliases = IdentityDict[Any, Any]()

  def new_dict(self, filter_type: Union[Type[ElementType], Tuple[Type[ElementType], ...]],
               anon_prefix: Optional[str] = None) -> SubElementDict[ElementType]:
    sub_dict = SubElementDict[ElementType](anon_prefix)
    self.dicts.append((filter_type, sub_dict))
    return sub_dict

  def add_alias(self, src: Any, target: Any):
    self.aliases[src] = target

  def add_element(self, name: str, item: Any) -> None:
    if isinstance(item, ElementDict):
      item._set_parent((name, self))
    else:
      assigned = []
      for (tpe, dict) in self.dicts:
        if item in dict.anons:
          dict.add_element(name, item)
          assigned.append(dict)
        else:  # require not conflicting name, or direct reassignment
          assert name not in dict.container or dict.names.get(item, None) == name, f"duplicate name {name}"
      assert len(assigned) <= 1, f"assigned {item} to multiple SubElementDict {assigned}"

  def name_of(self, item: Any) -> Optional[str]:
    if item in self.aliases:
      item = self.aliases[item]
    name_candidates = [sub_dict.name_of(item) for sub_dict_type, sub_dict in self.dicts]
    name_candidates_filtered = [name_candidate for name_candidate in name_candidates if name_candidate is not None]
    assert len(name_candidates_filtered) <= 1, f"more than 1 name candidates {name_candidates} for {item}"
    if not name_candidates_filtered:
      return None
    else:
      return name_candidates_filtered[0]


class ElementDict(Generic[ElementType]):
  """Dict that contains sub-elements, basically a dict with a hook that notifies its parent when items are added."""
  # TODO also have a KeyType? Perhaps enforce type bounds, eg must be str-able?
  def __init__(self) -> None:
    self.container: Dict[Union[str, int], ElementType] = {}
    self._parent: Optional[Tuple[str, SubElementManager]] = None  # name prefix, pointer to top level

  def _set_parent(self, parent: Tuple[str, SubElementManager]) -> None:
    self._parent = parent

  def __setitem__(self, key: Union[str, int], value: ElementType) -> None:
    assert self._parent is not None
    self._parent[1].add_element(f"{self._parent[0]}[{key}]", value)  # TODO perhaps some kind of check to make sure this is required?
    self.container[key] = value

  def __getitem__(self, item: Union[str, int]) -> ElementType:
    return self.container[item]

  def items(self) -> ItemsView[Union[str, int], ElementType]:
    return self.container.items()

  def values(self) -> ValuesView[ElementType]:
    return self.container.values()


class ElementMeta(type):
  def __call__(cls, *args, **kwargs):
    parent = builder.get_curr_context()
    block_context = builder.get_enclosing_block()
    try:
      obj = type.__call__(cls, *args, **kwargs)
      obj._initializer_args = (args, kwargs)
      obj._lexical_parent = parent
      obj._block_context = block_context
      obj._post_init()
    finally:
      if builder.get_curr_context() is not parent:  # in case the constructor skipped internal element init
        builder.pop_to(parent)

    return obj


class Refable():
  """Object that could be referenced into a edgir.LocalPath"""
  def __repr__(self) -> str:
    return "%s@%02x" % (self.__class__.__name__, (id(self)//4)&0xff)

  def __eq__(self, other: Any) -> None:  # type: ignore
    raise NotImplementedError(f"__eq__ reserved for DSL, attempted to compare {self} and {other}")

  def __bool__(self) -> bool:
    raise ValueError("bool-ing a Refable is almost certainly a mistake. "
                     "Note: 'and' and 'or' do not work on BoolExpr, use '&' or '|' instead.")

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict['Refable', edgir.LocalPath]:
    return IdentityDict([(self, prefix)])


class EltPropertiesBase:
  """"Base type for properties associated with a particular block, that do not apply to subtypes"""
  pass


NonLibraryProperty = EltPropertiesBase()
NonLibraryType = TypeVar('NonLibraryType', bound=Type['LibraryElement'])
def non_library(decorated: NonLibraryType) -> NonLibraryType:
  decorated._elt_properties[(decorated, NonLibraryProperty)] = None
  return decorated


@non_library
class LibraryElement(Refable, metaclass=ElementMeta):
  """Defines a library element, which optionally contains other library elements."""
  _elt_properties: Dict[Tuple[Type[LibraryElement], EltPropertiesBase], Any] = {}

  def __repr__(self) -> str:
    return "%s@%02x" % (self._get_def_name(), (id(self) // 4) & 0xff)

  def __init__(self) -> None:
    self._lexical_parent: Optional[LibraryElement]  # set by metaclass
    self._parent: Optional[LibraryElement] = None  # set by binding, None means not bound
    self._initializer_args: Tuple[Tuple[Any, ...], Dict[str, Any]]  # set by metaclass

    builder.push_element(self)

    self.manager = SubElementManager()
    self.manager_ignored: Set[str] = set(['_parent'])

  """Optionally overloaded to run anything post-__init__"""
  def _post_init(self):
    pass

  def __setattr__(self, name: str, value: Any) -> None:
    if hasattr(self, 'manager_ignored') and name not in self.manager_ignored:
      self.manager.add_element(name, value)
    super().__setattr__(name, value)

  def _name_of_child(self, subelt: Any, allow_unknown: bool = False) -> str:
    self_name = self.manager.name_of(subelt)
    if self_name is not None:
      return self_name
    else:
      if allow_unknown:
        return f"(unknown {subelt.__class__.__name__})"
      else:
        raise ValueError(f"no name for {subelt}")

  def _path_from(self, base: LibraryElement, allow_unknown: bool = False) -> List[str]:
    if base is self:
      return []
    else:
      assert self._parent is not None, "can't get path / name for non-bound element"
      return self._parent._path_from(base, allow_unknown) + [self._parent._name_of_child(self, allow_unknown)]

  def _name_from(self, base: LibraryElement, allow_unknown: bool = False) -> str:
    """Returns the path name to (inclusive) this element from some starting point.
    allow_unknown allows elements that haven't been assigned a name yet to not crash,
    this is useful when called from an error so the _name_from error doesn't stomp the real error."""
    return '.'.join(self._path_from(base, allow_unknown))

  @classmethod
  def _static_def_name(cls) -> str:
    """If this library element is defined by class (all instances have an equivalent library definition),
    returns the definition name. Otherwise, should crash."""
    if cls.__module__ == "__main__":
      # when the top-level design is run as main, the module name is __main__ which is meaningless
      # and breaks when the HDL server tries to resolve the __main__ reference (to itself),
      # so this needs to resolve the correct name
      import inspect
      import os
      module = os.path.splitext(os.path.basename(inspect.getfile(cls)))[0]
    else:
      module = cls.__module__
    return module + "." + cls.__name__

  def _get_def_name(self) -> str:
    """Returns the definition name"""
    return self.__class__._static_def_name()

  @abstractmethod
  def _def_to_proto(self) -> Union[edgir.PortTypes, edgir.BlockLikeTypes]: ...


class StructuredMetadata():
  """Base class for metadata that is structured (as a class in Python)"""
  @abstractmethod
  def _to_proto(self, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.Metadata:
    raise NotImplementedError


@non_library
class HasMetadata(LibraryElement):
  """A library element with the metadata dict-like field"""
  def __init__(self) -> None:
    super().__init__()
    self._metadata: SubElementDict[Any] = self.manager.new_dict(Any)  # type: ignore

  MetadataType = TypeVar('MetadataType', bound=Union[StructuredMetadata, str, Mapping[str, Any], SubElementDict[Any], IdentityDict[Any, Any]])
  def Metadata(self, value: MetadataType) -> MetadataType:
    """Adds a metadata field to this object. Reference to the value must not change, and reassignment will error.
    Value may be changed until proto generation.
    Utility method for library builders."""
    self._metadata.register(value)
    return value

  BaseType = TypeVar('BaseType', bound='HasMetadata')
  @classmethod
  def _get_bases_of(cls, base_type: Type[BaseType]) -> Tuple[List[Type[BaseType]], List[Type[BaseType]]]:
    """Returns all the base classes of this class, as a list of direct superclasses (including through non_library
    elements) and a list of additional (indirect) superclasses. Direct superclasses are in MRO order, indirect
    superclasses order is not defined (but MRO in current practice).

    mypy currently does not allow passing in abstract types, so generally calls to this need type: ignore."""
    direct_bases: Set[Type] = set()
    def process_direct_base(bcls: Type[HasMetadata.BaseType]):
      if not issubclass(bcls, base_type):
        return  # ignore above base_type
      if (bcls, NonLibraryProperty) in bcls._elt_properties:  # non-library, recurse into parents
        for bcls_base in bcls.__bases__:
          process_direct_base(bcls_base)
      else:  # anything else, directly append if not existing
        direct_bases.add(bcls)
    for bcls in cls.__bases__:
      process_direct_base(bcls)

    ordered_direct_bases: List[Type[HasMetadata.BaseType]] = []
    ordered_indirect_bases: List[Type[HasMetadata.BaseType]] = []
    for mro_base in cls.__mro__[1:]:  # ignore self
      if mro_base in direct_bases:
        ordered_direct_bases.append(mro_base)
      elif issubclass(mro_base, base_type) and (mro_base, NonLibraryProperty) not in mro_base._elt_properties:
        ordered_indirect_bases.append(mro_base)

    return ordered_direct_bases, ordered_indirect_bases

  def _populate_metadata(self, pb: edgir.Metadata, src: Any,
                         ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.Metadata:
    """Generate metadata from a given object."""
    if isinstance(src, StructuredMetadata):
      pb.CopyFrom(src._to_proto(ref_map))
    elif isinstance(src, str):
      pb.text_leaf = src
    elif isinstance(src, bytes):
      pb.bin_leaf = src
    elif isinstance(src, dict) or isinstance(src, SubElementDict) or isinstance(src, IdentityDict):
      if isinstance(src, SubElementDict):  # used at the top-level, for Metadata(...)
        src.finalize()  # TODO should this be here?
      for key, val in src.items():
        assert isinstance(key, str), f'must overload _metadata_to_proto for non-str dict key {key}'
        self._populate_metadata(pb.members.node[key], val, ref_map)
    elif isinstance(src, list):
      for idx, val in enumerate(src):
        self._populate_metadata(pb.members.node[str(idx)], val, ref_map)
    else:
      raise ValueError(f'must overload _metadata_to_proto to handle unknown value {src}')
    return pb
