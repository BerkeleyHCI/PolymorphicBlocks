from __future__ import annotations

from typing import *

KeyType = TypeVar('KeyType', bound=Hashable)
ValueType = TypeVar('ValueType', bound=Hashable)

class MultiBiDict(Generic[KeyType, ValueType]):
  def __init__(self):
    self.dict: Dict[KeyType, Set[ValueType]] = {}
    self.inverse_dict: Dict[ValueType, Set[KeyType]] = {}

  def add(self, key: KeyType, value: ValueType):
    self.dict.setdefault(key, set()).add(value)
    self.inverse_dict.setdefault(value, set()).add(key)

  def __contains__(self, key: KeyType) -> bool:
    return len(self.dict.get(key, set())) > 0

  def __getitem__(self, key: KeyType) -> ValueType:
    value_set = self.dict.get(key, set())
    if len(value_set) != 1:
      raise ValueError(f"MultiBiDict at key {key} has non-one value(s) {value_set}")
    else:
      return value_set.copy().pop()

  def contains_value(self, value: ValueType) -> bool:
    return len(self.inverse_dict.get(value, set())) > 0

  def get(self, key: KeyType) -> Set[ValueType]:
    return self.dict.get(key, set()).copy()

  def get_by_value(self, value: ValueType) -> Set[KeyType]:  # TODO better name
    return self.inverse_dict.get(value, set()).copy()

  def get_only_by_value(self, value: ValueType) -> KeyType:  # TODO better name
    key_set = self.inverse_dict.get(value, set())
    if len(key_set) != 1:
      raise ValueError(f"MultiBiDict at value {value} has non-one key(s) {key_set}")
    else:
      return key_set.copy().pop()

  def clear(self):
    self.dict = {}
    self.inverse_dict = {}
