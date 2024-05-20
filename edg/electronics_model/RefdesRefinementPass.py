from typing import List, Tuple, Dict, Set

import edgir
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

    self.block_refdes_list: List[Tuple[TransformUtil.Path, str]] = []  # populated in traversal order
    self.seen_blocks: Set[TransformUtil.Path] = set()
    self.refdes_last: Dict[str, int] = {}

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
    if 'fp_is_footprint' in block.meta.members.node:
      refdes_prefix = self.design.get_value(context.path.to_tuple() + ('fp_refdes_prefix',))
      assert isinstance(refdes_prefix, str)

      refdes_id = self.refdes_last.get(refdes_prefix, 0) + 1
      self.refdes_last[refdes_prefix] = refdes_id
      assert context.path not in self.seen_blocks
      self.block_refdes_list.append((context.path, self.board_refdes_prefix + refdes_prefix + str(refdes_id)))

  def run(self) -> List[Tuple[TransformUtil.Path, str]]:
    self.transform_design(self.design.design)
    return self.block_refdes_list
