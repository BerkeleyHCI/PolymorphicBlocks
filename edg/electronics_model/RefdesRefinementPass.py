from typing import List, Tuple, Dict, Set, Optional

from .. import edgir
from ..core import CompiledDesign, TransformUtil
from ..core.BaseRefinementPass import BaseRefinementPass


class RefdesRefinementPass(BaseRefinementPass):
  def run(self, design: CompiledDesign) -> List[Tuple[edgir.LocalPath, edgir.ValueLit]]:
    block_refdes_list = RefdesTransform(design).run()
    return [(block_path.append_param('fp_refdes').to_local_path(), edgir.lit_to_valuelit(block_refdes))
            for (block_path, block_refdes) in block_refdes_list]


class RefdesTransform(TransformUtil.Transform):
  def __init__(self, design: CompiledDesign):
    self.design = design

    board_refdes_prefix = self.design.get_value(('refdes_prefix',))
    if board_refdes_prefix is None:
      self.board_refdes_prefix = ''
    else:
      assert isinstance(board_refdes_prefix, str)
      self.board_refdes_prefix = board_refdes_prefix

    self.scopes: Dict[TransformUtil.Path, Optional[TransformUtil.Path]] = {
      TransformUtil.Path.empty(): TransformUtil.Path.empty()
    }

    self.block_refdes_list: List[Tuple[TransformUtil.Path, str]] = []  # populated in traversal order
    self.refdes_last: Dict[(TransformUtil.Path, str), int] = {}  # (scope, prefix) -> num

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
    scope = self.scopes[context.path]
    internal_scope = scope
    if 'fp_is_wrapper' in block.meta.members.node:  # wrapper internal blocks ignored
      internal_scope = None

    for block_pair in block.blocks:
      self.scopes[context.path.append_block(block_pair.name)] = internal_scope

    if 'fp_is_footprint' in block.meta.members.node and scope is not None:
      refdes_prefix = self.design.get_value(context.path.to_tuple() + ('fp_refdes_prefix',))
      assert isinstance(refdes_prefix, str)

      refdes_id = self.refdes_last.get((scope, refdes_prefix), 0) + 1
      self.refdes_last[(scope, refdes_prefix)] = refdes_id
      self.block_refdes_list.append((context.path, self.board_refdes_prefix + refdes_prefix + str(refdes_id)))

  def run(self) -> List[Tuple[TransformUtil.Path, str]]:
    self.transform_design(self.design.design)
    return self.block_refdes_list
