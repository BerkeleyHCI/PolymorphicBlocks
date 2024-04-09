import importlib
import inspect
from typing import List, Tuple, Dict, NamedTuple
from . import footprint as kicad

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil
from .NetlistGenerator import NetlistTransform
from .SvgPcbTemplateBlock import SvgPcbTemplateBlock


class SvgPcbBackend(BaseBackend):
  """Backend that generates SVG-PCB (https://github.com/leomcelroy/svg-pcb) layout code for a board,
  using block templates (if available) or bare footprints for other components.
  """
  @classmethod
  def _block_matches_prefixes(cls, block: kicad.Block, prefixes: List[List[str]]):
    for prefix in prefixes:
      if block.path[0:min(len(block.path), len(prefix))] == prefix:
        return True
    return False

  @classmethod
  def _filter_blocks_by_pathname(cls, blocks: Dict[str, kicad.Block], exclude_prefixes: List[List[str]]) ->\
          Dict[str, kicad.Block]:
    return {name: block for name, block in blocks.items()
            if not cls._block_matches_prefixes(block, exclude_prefixes)}

  @classmethod
  def _pathname_to_svbpcb(cls, path: TransformUtil.Path) -> str:
    return '_'.join(path.to_tuple())

  @classmethod
  def _footprint_to_svgpcb(cls, footprint: str) -> str:
    # TODO needs to be consistent w/ svgpcb rules
    return footprint.split(':')[-1].replace('-', '_').replace(' ', '_').replace('.', '_')

  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    svgpcb_blocks = SvgPcbTransform(design).run()
    svgpcb_block_prefixes = [list(path.to_tuple()) for path, block in svgpcb_blocks]
    netlist = NetlistTransform(design, refdes_mode="pathName").run()
    other_blocks = self._filter_blocks_by_pathname(netlist.blocks, svgpcb_block_prefixes)

    functions_definitions = '\n'.join([block.svgpcb_code for path, block in svgpcb_blocks])
    svgpcb_block_instantiations = ''.join([
      f"const {self._pathname_to_svbpcb(path)} = {block.fn_name}(pt(0, 0))\n"
      for path, block in svgpcb_blocks
    ])
    other_block_instantiations = ''.join([
      # TODO path from NetlistTransform should preserve LocalPath type
      f"""\
const {path.replace('.', '_')} = board.add({self._footprint_to_svgpcb(block.footprint)}, {{
  translate: pt(0, 0), rotate: 0,
  id: '{path.replace('.', '_')}'
}})\n"""
      for path, block in other_blocks.items()
    ])

    nets_pins_code = {name: ', '.join([
      f"""["{pin.block_name.replace('.', '_')}", "{pin.pin_name}"]"""
      for pin in pins
    ])
      for name, pins in netlist.nets.items()}
    nets_code = [f"""\
  {{
    name: "{name}",
    pads: [{net_code}]
  }}"""
            for name, net_code in nets_pins_code.items()]
    sep = ',\n'  # get past backslashes not allowed in f-strings
    netlist_code = f"""\
board.setNetlist([
{sep.join(nets_code)}
])
"""

    return [
      (edgir.LocalPath(), functions_definitions),
      (edgir.LocalPath(), svgpcb_block_instantiations + other_block_instantiations),
      (edgir.LocalPath(), netlist_code),
    ]


class SvgPcbGeneratedBlock(NamedTuple):
  fn_name: str
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
      generator_obj._svgpcb_init(context.path, self.design)
      self._svgpcb_blocks.append((context.path,
                                  SvgPcbGeneratedBlock(
                                    generator_obj._svgpcb_fn_name(),
                                    generator_obj._svgpcb_template(),
                                  )))
    else:
      pass

  def run(self) -> List[Tuple[TransformUtil.Path, SvgPcbGeneratedBlock]]:
    self.transform_design(self.design.design)
    return self._svgpcb_blocks
