import importlib
import inspect
from typing import List, Tuple, Dict, NamedTuple

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil
from .NetlistGenerator import NetlistTransform
from .SvgPcbTemplateBlock import SvgPcbTemplateBlock


class SvgPcbBackend(BaseBackend):
  """Backend that generates SVG-PCB (https://github.com/leomcelroy/svg-pcb) layout code for a board,
  using block templates (if available) or bare footprints for other components.
  """
  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    netlist = NetlistTransform(design, refdes_mode="pathName").run()
    print(str(netlist).encode('utf-8'))
    svgpcb_blocks = SvgPcbTransform(design).run()
    print(svgpcb_blocks)

    return [
      (edgir.LocalPath(), "")
    ]


class SvgPcbGeneratedBlock(NamedTuple):
  name: str
  svgpcb_code: str


class SvgPcbTransform(TransformUtil.Transform):
  """Collects all SVGPCB blocks and initializes them."""
  def __init__(self, design: CompiledDesign):
    self.design = design
    self._svgpcb_blocks: List[Tuple[TransformUtil.Path, SvgPcbGeneratedBlock]] = []

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
    # TODO: dedup w/ class_from_library in edg_hdl_server
    elt_split = block.self_class.target.name.split('.')
    elt_module = importlib.import_module('.'.join(elt_split[:-1]))
    assert inspect.ismodule(elt_module)
    cls = getattr(elt_module, elt_split[-1])
    if issubclass(cls, SvgPcbTemplateBlock):
      generator_obj = cls()
      generator_obj._svgpcb_init()
      self._svgpcb_blocks.append((context.path,
                                  SvgPcbGeneratedBlock(
                                    generator_obj._svgpcb_fn_name(),
                                    generator_obj._svgpcb_template(),
                                  )))
    else:
      pass

  def run(self) -> List[Tuple[TransformUtil.Path, SvgPcbTemplateBlock]]:
    self.transform_design(self.design.design)
    return self._svgpcb_blocks
