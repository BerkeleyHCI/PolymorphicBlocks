from __future__ import annotations

from typing import *
from abc import abstractmethod
import inspect

from . import edgir
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
    self.dicts: List[Tuple[Type, SubElementDict]] = []

  def new_dict(self, filter_type: Type[ElementType], anon_prefix: Optional[str] = None) -> SubElementDict[ElementType]:
    sub_dict = SubElementDict[ElementType](anon_prefix)
    self.dicts.append((filter_type, sub_dict))
    return sub_dict

  def add_element(self, name: str, item: Any) -> None:
    if isinstance(item, ElementDict):
      item._set_parent((name, self))
    else:
      assigned = []
      for (tpe, dict) in self.dicts:
        if item in dict.anons:
          dict.add_element(name, item)
          assigned.append(dict)
      assert len(assigned) <= 1, f"assigned {item} to multiple SubElementDict {assigned}"

  def _name_of(self, item: Any) -> Optional[str]:
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
    self._parent[1].add_element(f"{self._parent[0]}_{key}", value)  # TODO perhaps some kind of check to make sure this is required?
    self.container[key] = value

  def __getitem__(self, item: Union[str, int]) -> ElementType:
    return self.container[item]

  def items(self) -> ItemsView[Union[str, int], ElementType]:
    return self.container.items()


class ElementMeta(type):
  def __call__(cls, *args, **kwargs):
    parent = builder.get_curr_context()
    try:
      obj = type.__call__(cls, *args, **kwargs)
      obj._initializer_args = (args, kwargs)
      obj._parent = parent
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
                     "Note: remember to wrap parameters in self.get(...) if accessing values in generators. "
                     "Note: 'and' and 'or' do not work on BoolExpr, use '&' or '|' instead.")

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict['Refable', edgir.LocalPath]:
    return IdentityDict([(self, prefix)])


NonLibraryFlag = object()
NonLibraryType = TypeVar('NonLibraryType', bound=Type['LibraryElement'])
def non_library(decorated: NonLibraryType) -> NonLibraryType:
  decorated._elt_properties[(decorated, 'non_library')] = None
  return decorated


@non_library
class LibraryElement(Refable, metaclass=ElementMeta):
  """Defines a library element, which optionally contains other library elements."""
  _elt_properties: Dict[Any, Any] = {}  # TODO can this be restricted further?

  def __repr__(self) -> str:
    return "%s@%02x" % (self._get_def_name(), (id(self) // 4) & 0xff)

  def __init__(self) -> None:
    self._parent: Optional[Refable]  # set by metaclass
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

  def _name_of(self, subelt: Any) -> str:
    self_name = self.manager._name_of(subelt)
    if self_name is not None:
      return self_name
    elif isinstance(subelt, LibraryElement):
      return subelt._name_to(self)
    else:
      raise NotImplementedError(f"no name for {subelt}")

  def _name_to(self, base: LibraryElement) -> str:
    # TODO requires self._parent is set properly, when we really need self.parent (binding)
    # TODO this algorithm could probably be better
    if base is self:
      return ""
    else:
      if not isinstance(self._parent, LibraryElement):
        return "???"
      else:  # TODO refactor to avoid potential infinite recursion w/ _name_of
        return self._parent._name_to(base) + "." + self._parent._name_of(self)  # TODO this adds extra leading dot

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


class HasMetadata(LibraryElement):
  """A library element with the metadata dict-like field"""
  def __init__(self) -> None:
    super().__init__()
    self._metadata: SubElementDict[Any] = self.manager.new_dict(Any)  # type: ignore

    if not builder.stack or builder.stack[0] is self:  # these are performance-intensive, avoid generating internally
      self._edgdoc = self.Metadata(IdentityDict[Refable, str]())
      selfdoc = inspect.getdoc(self)
      if selfdoc:
        self._edgdoc[self] = selfdoc

      self._sourcelocator = self.Metadata(IdentityDict[Refable, str]())
      self._sourcelocator[self] = self._get_class_line()

  def _get_class_line(self) -> str:
    """Returns the source locator for own class definition
    TODO: line number is broken - there doesn't seem to be a good way of getting a line number
      this used to return the source locator for the last function of the same name in the same object, but this
      didn't work for classes since not everyone defines its own __init__
    TODO: maybe return a more structured type?
    """
    return f"{inspect.getsourcefile(self.__class__)}: 0"

  def _get_calling_source_locator(self) -> str:
    """Returns the source locator (as a string for now) of the line calling the function this is being called from,
    accounting for inheritance (superclass calls to a function of the same name in the same object).
    TODO: maybe return a more structured type?
    """
    stack = inspect.stack()
    ref_frame = stack[1]  # calling frame
    func_name = ref_frame[0].f_code.co_name

    for candidate_frame in stack[2:]:  # iterate through to the first frame with a different function name
      # TODO this used to check for different self object
      # ('self' not in candidate_frame[0].f_locals or candidate_frame[0].f_locals['self'] is not self)
      # but this would trip up on chained calls, eg imp.Block(...)
      # needs a better way to track through these objects?
      if candidate_frame[0].f_code.co_name != func_name:
        break
    return f"{candidate_frame[0].f_code.co_filename}: {candidate_frame[0].f_lineno}"

  MetadataType = TypeVar('MetadataType', bound=Union[str, Mapping[str, Any], SubElementDict[Any], IdentityDict[Any, Any]])
  def Metadata(self, value: MetadataType) -> MetadataType:
    """Adds a metadata field to this object. Reference to the value must not change, and reassignment will error.
    Value may be changed until proto generation.
    Utility method for library builders."""
    self._metadata.register(value)
    return value

  def _metadata_to_proto(self, src: Any, path: List[str],
                         ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.Metadata:
    """Generate metadata from a given object."""
    pb = edgir.Metadata()
    if isinstance(src, str):
      pb.text_leaf = src
    elif isinstance(src, bytes):
      pb.bin_leaf = src
    elif isinstance(src, dict) or isinstance(src, SubElementDict) or isinstance(src, IdentityDict):
      if isinstance(src, SubElementDict):  # used at the top-level, for Metadata(...)
        src.finalize()  # TODO should this be here?
      if isinstance(src, IdentityDict) and path in [['_edgdoc'], ['_sourcelocator']]:
        for key, val in src.items():
          assert isinstance(val, str)
          if key is self:
            pb.members.node['self'].text_leaf = val
          else:
            pb.members.node[self._name_of(key)].text_leaf = val
      else:
        for key, val in src.items():
          assert isinstance(key, str), f'must overload _metadata_to_proto for non-str dict key {key} at {path}'
          pb.members.node[key].CopyFrom(self._metadata_to_proto(val, path + [key], ref_map))
    elif isinstance(src, list):
      for idx, val in enumerate(src):
        pb.members.node[str(idx)].CopyFrom(self._metadata_to_proto(val, path + [str(idx)], ref_map))
    else:
      raise ValueError(f'must overload _metadata_to_proto to handle unknown value {src} at {path}')
    return pb
