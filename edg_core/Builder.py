from __future__ import annotations

from typing import *
import sys

from . import edgir

if TYPE_CHECKING:
  from .Core import Refable
  from .Blocks import BaseBlock


class Builder:
  def __init__(self) -> None:
    self.stack: List[Refable] = []

  def push_element(self, elt: Refable) -> None:
    self.stack.append(elt)

  def pop_to(self, elt: Optional[Refable]) -> None:
    self.stack.pop()
    assert self.get_curr_context() is elt

  def get_curr_block(self) -> BaseBlock:
    from .Blocks import BaseBlock
    elt = self.stack[-1]
    assert isinstance(elt, BaseBlock)
    return elt

  def get_curr_context(self) -> Optional[Refable]:
    if not self.stack:
      return None
    else:
      return self.stack[-1]

  def elaborate_toplevel(self, block: BaseBlock, exc_prefix: str, *,
                         replace_superclass: bool = True,
                         generate_fn_name: Optional[str] = None,
                         generate_values: Iterable[Tuple[edgir.LocalPath, edgir.LitTypes]] = []) -> edgir.HierarchyBlock:
    assert self.get_curr_context() is None
    self.push_element(block)
    try:
      if generate_fn_name is not None:  # TODO this is kind of nasty =(
        elaborated = block._generated_def_to_proto(generate_fn_name, generate_values)  # type: ignore
      else:  # TODO check is a GeneratorBlock w/o circular imports?
        elaborated = block._elaborated_def_to_proto()

      # since this is the top level, set the superclass to the block itself
      if replace_superclass:
        del elaborated.superclasses[:]  # TODO stack instead of replace superclasses?
        elaborated.superclasses.add().target.name = block._get_def_name()

      return elaborated
    except BaseException as e:
      raise type(e)(f"({exc_prefix}) " + repr(e)) \
        .with_traceback(sys.exc_info()[2])
    finally:
      self.pop_to(None)


builder = Builder()
