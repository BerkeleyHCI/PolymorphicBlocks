from __future__ import annotations

from typing import *

from deprecated import deprecated

from .HdlUserExceptions import EdgContextError
from .. import edgir

if TYPE_CHECKING:
    from .Blocks import BaseBlock
    from .Link import Link
    from .HierarchyBlock import Block


class Builder:
    def __init__(self) -> None:
        self.stack: List[BaseBlock] = []

    def _current_block(self) -> Optional[BaseBlock]:
        if not self.stack:
            return None
        else:
            return self.stack[-1]

    def push_element(self, elt: BaseBlock) -> Optional[BaseBlock]:
        """Pushes a new element onto the context stack, returning the previous top element.
        Ignores if the element is already on top of the stack."""
        prev_elt = self._current_block()
        if not self.stack or self.stack[-1] is not elt:  # prevent double-pushing
            self.stack.append(elt)
        return prev_elt

    def pop_to(self, prev: Optional[BaseBlock]) -> None:
        """Pops at most one element from stack, expecting prev to be at the top of the stack.
        The pattern should be one pop for one push, and allowing that duplicate pushes are ignored."""
        if (prev is None and not self.stack) or (prev is not None and self.stack[-1] is prev):
            return

        self.stack.pop()
        assert (prev is None and not self.stack) or (prev is not None and self.stack[-1] is prev)

    def block(self) -> BaseBlock:
        """Returns the current block context, throwing an error if there is no block context."""
        current_block = self._current_block()
        if current_block is None:
            raise EdgContextError("no block context")
        return current_block

    @deprecated("use asserting block() instead")
    def get_enclosing_block(self) -> Optional[BaseBlock]:
        return self._current_block()

    @deprecated("use block() instead, context frames can only be blocks now")
    def get_curr_context(self) -> Optional[BaseBlock]:
        return self._current_block()

    @overload
    def elaborate_toplevel(
        self,
        block: Block,
        *,
        is_generator: bool = False,
        generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]] = [],
    ) -> edgir.HierarchyBlock: ...

    @overload
    def elaborate_toplevel(
        self,
        block: Link,
        *,
        is_generator: bool = False,
        generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]] = [],
    ) -> edgir.Link: ...

    def elaborate_toplevel(
        self,
        block: BaseBlock,
        *,
        is_generator: bool = False,
        generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]] = [],
    ) -> edgir.BlockLikeTypes:
        try:
            if is_generator:  # TODO this is kind of nasty =(
                from .Generator import GeneratorBlock

                assert isinstance(block, GeneratorBlock)
                elaborated: edgir.BlockLikeTypes = block._generated_def_to_proto(generate_values)
            else:  # TODO check is a GeneratorBlock w/o circular imports?
                elaborated = block._elaborated_def_to_proto()

            return elaborated
        except Exception as e:
            raise Exception(f"While elaborating {block.__class__}") from e


builder = Builder()
