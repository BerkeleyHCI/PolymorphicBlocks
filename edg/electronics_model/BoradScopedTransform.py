from abc import abstractmethod
from typing import Optional, Dict, List, cast

from .. import edgir
from ..core import TransformUtil, CompiledDesign
from ..core.TransformUtil import TransformContext


class BoardScopedTransform(TransformUtil.Transform):
    """Transform subclass that handles board scoping for sub-boards and wrappers.
    Board scopes are defined as a Path (root for the "main" board) or None (for sub-board wrappers).
    Subclasses may define additional data structures, indexed by this board scope Path."""

    def __init__(self, design: CompiledDesign) -> None:
        super().__init__()
        self._design = design
        self._board_scopes: Dict[TransformUtil.Path, Optional[TransformUtil.Path]] = {
            TransformUtil.Path.empty(): TransformUtil.Path.empty()
        }  # always initialized in parent

    @abstractmethod
    def visit_block_scoped(
        self, context: TransformUtil.TransformContext, scope: TransformUtil.Path, block: edgir.BlockTypes
    ) -> None:
        raise NotImplementedError

    def visit_block(self, context: TransformContext, block: edgir.HierarchyBlock) -> None:
        scope = self._board_scopes[context.path]

        if "fp_subboard" in block.meta.members.node:
            fp_external_blocks = self._design.get_value(context.path.to_tuple() + ("fp_external_blocks",))
            assert isinstance(fp_external_blocks, list)
            external_blocks: Optional[List[str]] = cast(List[str], fp_external_blocks)
            if "fp_subblocks_ignored" in block.meta.members.node:
                internal_scope = None
            else:
                raise NotImplementedError("support subboard")
        else:
            external_blocks = None
            internal_scope = scope

        for block_pair in block.blocks:
            if external_blocks is not None and block_pair.name not in external_blocks:
                self._board_scopes[context.path.append_block(block_pair.name)] = internal_scope
            else:
                self._board_scopes[context.path.append_block(block_pair.name)] = scope

        self.visit_block_scoped(context, scope, block)
