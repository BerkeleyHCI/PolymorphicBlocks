from typing import List, Tuple

import edgir
from edg_core import BaseBackend, CompiledDesign
from . import footprint as kicad
from .NetlistGenerator import NetlistTransform


class NetlistBackend(BaseBackend):
  def run(self, design: CompiledDesign) -> List[Tuple[edgir.LocalPath, str]]:
    netlist = NetlistTransform(design).run()
    netlist_string = kicad.generate_netlist(netlist.blocks, netlist.nets)
    return [
      (edgir.LocalPath(), netlist_string)
    ]
