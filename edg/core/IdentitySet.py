from __future__ import annotations

from typing import *

EltType = TypeVar('EltType')  # TODO maybe should be covariant? but is mutable so maybe not?
class IdentitySet(Generic[EltType]):  # TODO this should implement some kind of set base class
  def __init__(self, *args: EltType) -> None:
    self.set: Set[int] = set()  # TODO convenience hack, the same data is in self.dict.keys
    self.dict: Dict[int, EltType] = {}

    for elt in args:
      self.add(elt)

  def __iter__(self) -> Iterator[EltType]:
    return iter(self.dict.values())

  def __len__(self) -> int:
    return len(self.set)

  def __repr__(self) -> str:
    return "IdentitySet" + str(self.dict.values())

  def add(self, item: EltType) -> None:
    if id(item) in self.dict:
      assert self.dict[id(item)] is item
    self.set.add(id(item))
    self.dict[id(item)] = item

  def __contains__(self, item: EltType) -> bool:
    return id(item) in self.set and self.dict[id(item)] is item

  def pop(self) -> EltType:
    return self.dict.pop(self.set.pop())

  def difference_update(self, other: IdentitySet[EltType]) -> None:
    self.set.difference_update(other.set)
    for elt_id in [elt_id for elt_id in self.dict.keys() if elt_id not in self.set]:
      self.dict.pop(elt_id)

  def update(self, other: Iterable[EltType]) -> None:
    for elt in other:
      self.add(elt)

  def get_only(self) -> EltType:  # sadly there's no equivalent in Python base set
    assert len(self.set) == 1
    return self.dict[next(iter(self.set))]

  def remove(self, element: EltType) -> None:
    self.set.remove(id(element))
    self.dict.pop(id(element))
