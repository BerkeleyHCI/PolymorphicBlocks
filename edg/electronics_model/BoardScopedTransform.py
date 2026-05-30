from typing import Optional, Dict, List, cast
from typing_extensions import override

from .. import edgir
from ..core import TransformUtil, CompiledDesign
from ..core.TransformUtil import TransformContext


class BoardScopedTransform(TransformUtil.Transform):
    """Transform subclass that handles board scoping for sub-boards and wrappers.
    Board scopes are defined as a Path (root for the "main" board) or None (for sub-board wrappers
    that discard their implementation).
    Subclasses may define additional data structures, indexed by this board scope Path."""

    def __init__(self, design: CompiledDesign) -> None:
        super().__init__()
        self._design = design
        self._board_parent_scopes: Dict[TransformUtil.Path, Optional[TransformUtil.Path]] = {
            TransformUtil.Path.empty(): TransformUtil.Path.empty()
        }  # always initialized in parent
        self._board_scopes: Dict[TransformUtil.Path, Optional[TransformUtil.Path]] = {}

    def visit_block_scoped(
        self, context: TransformUtil.TransformContext, scope: Optional[TransformUtil.Path], block: edgir.BlockTypes
    ) -> None:
        pass

    def visit_link_scoped(
        self, context: TransformUtil.TransformContext, scope: Optional[TransformUtil.Path], link: edgir.Link
    ) -> None:
        pass

    def visit_linkarray_scoped(
        self, context: TransformUtil.TransformContext, scope: Optional[TransformUtil.Path], link: edgir.LinkArray
    ) -> None:
        pass

    @override
    def visit_block(self, context: TransformContext, block: edgir.HierarchyBlock) -> None:
        parent_scope = self._board_parent_scopes[context.path]

        if "fp_subboard" in block.meta.members.node or "fp_subboard_connector_pair" in block.meta.members.node:
            fp_external_blocks = self._design.get_value(context.path.to_tuple() + ("fp_external_blocks",))
            if fp_external_blocks is None:
                fp_external_blocks = []
            assert isinstance(fp_external_blocks, list)
            external_blocks: Optional[List[str]] = cast(List[str], fp_external_blocks)
            if "fp_subblocks_ignored" in block.meta.members.node:
                internal_scope = None
            elif "fp_subboard_connector_pair" in block.meta.members.node:
                internal_scope = self._board_scopes[TransformUtil.Path.empty().append_block(*context.path.blocks[:-1])]
            else:
                internal_scope = context.path
        else:
            external_blocks = None
            internal_scope = parent_scope

        self._board_scopes[context.path] = internal_scope

        for block_pair in block.blocks:
            if external_blocks is not None and block_pair.name not in external_blocks:
                self._board_parent_scopes[context.path.append_block(block_pair.name)] = internal_scope
            else:
                self._board_parent_scopes[context.path.append_block(block_pair.name)] = parent_scope

        self.visit_block_scoped(context, internal_scope, block)

    @override
    def visit_link(self, context: TransformContext, link: edgir.Link) -> None:
        self.visit_link_scoped(context, self._board_scopes[context.path.block_component()], link)

    @override
    def visit_linkarray(self, context: TransformContext, link: edgir.LinkArray) -> None:
        self.visit_linkarray_scoped(context, self._board_scopes[context.path.block_component()], link)
