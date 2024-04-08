from typing import List, Tuple, Dict

import edgir
from edg_core import BaseBackend, CompiledDesign
from .NetlistGenerator import NetlistTransform


class SvgPcbBackend(BaseBackend):
  """Backend that generates SVG-PCB (https://github.com/leomcelroy/svg-pcb) layout code for a board,
  using block templates (if available) or bare footprints for other components.
  """
  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    netlist = NetlistTransform(design, refdes_mode="pathName").run()

    return [
      (edgir.LocalPath(), "")
    ]
