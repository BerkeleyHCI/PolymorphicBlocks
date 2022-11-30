from typing import List, Tuple, Dict

import edgir
from edg_core import BaseBackend, CompiledDesign
from . import footprint as kicad
from .NetlistGenerator import NetlistTransform


class NetlistBackend(BaseBackend):
  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    # TODO: add sanitization for arguments. Need to check if arguments are valid and do type conversion.

    netlist = NetlistTransform(design, value_mode=args["valueMode"]).run()
    netlist_string = kicad.generate_netlist(netlist.blocks, netlist.nets)
    return [
      (edgir.LocalPath(), netlist_string)
    ]
