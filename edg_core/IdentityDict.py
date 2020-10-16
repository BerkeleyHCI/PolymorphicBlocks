from __future__ import annotations

from typing import *

KeyType = TypeVar('KeyType')
ValueType = TypeVar('ValueType')
class IdentityDict(Generic[KeyType, ValueType]):  # TODO this should implement Mapping[KeyType, ValueType]
  def __init__(self, *args: Union[Iterable[Tuple[KeyType, ValueType]], IdentityDict[KeyType, ValueType]]):
    self.dict: Dict[int, ValueType] = {}
    self.keys_dict: Dict[int, KeyType] = {}  # allow iteration over items

    for elt in args:
      if isinstance(elt, IdentityDict):
        self.extend(elt.items())
      elif isinstance(elt, Iterable):
        self.extend(elt)

  def __getitem__(self, key: KeyType) -> ValueType:
    key_id = id(key)
    assert key_id in self.dict, "key %s (%s) not found" % (key_id, key)
    return self.dict[key_id]

  GetDefaultType = TypeVar('GetDefaultType')
  def get(self, key: KeyType, default: GetDefaultType) -> Union[ValueType, GetDefaultType]:
    key_id = id(key)
    if key_id not in self.dict:
      return default
    else:
      return self.dict[key_id]

  def setdefault(self, key: KeyType, default: ValueType) -> ValueType:
    key_id = id(key)
    if key_id not in self.dict:
      self.dict[key_id] = default
    return self.dict[key_id]

  def __repr__(self) -> str:
    return "IdentityDict" + str(self.items())

  def __add__(self, other: IdentityDict[KeyType, ValueType]) -> IdentityDict[KeyType, ValueType]:
    return self.extend(other.items())

  def __setitem__(self, key: KeyType, item: ValueType):
    key_id = id(key)
    assert key_id not in self.dict, f"attempted to overwrite {key}={self.dict[key_id]} with new {item}"
    self.dict[key_id] = item
    self.keys_dict[key_id] = key

  def extend(self, items: Iterable[Tuple[KeyType, ValueType]]) -> IdentityDict[KeyType, ValueType]:
    for (key, value) in items:
      self[key] = value
    return self

  def items(self) -> Iterable[Tuple[KeyType, ValueType]]:
    return [(self.keys_dict[key_id], value) for (key_id, value) in self.dict.items()]

  def keys(self) -> Iterable[KeyType]:
    return self.keys_dict.values()

  def values(self) -> Iterable[ValueType]:
    return self.dict.values()

  def __contains__(self, item: KeyType) -> bool:
    return id(item) in self.dict
