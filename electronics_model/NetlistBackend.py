from typing import List, Tuple, Dict

import edgir
from edg_core import BaseBackend, CompiledDesign
from . import footprint as kicad
from .NetlistGenerator import NetlistTransform

class NetlistBackend(BaseBackend):
  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    if set(args.keys()) != {'RefdesMode'}:
      raise ValueError("Invalid argument found in args")

    netlist = NetlistTransform(design, refdes_mode=args["RefdesMode"]).run()
    netlist_string = kicad.generate_netlist(netlist.blocks, netlist.nets)

    return [
      (edgir.LocalPath(), netlist_string)
    ]
