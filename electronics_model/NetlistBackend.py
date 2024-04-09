from typing import List, Tuple, Dict

import edgir
from edg_core import BaseBackend, CompiledDesign
from . import footprint as kicad
from .NetlistGenerator import NetlistTransform


class NetlistBackend(BaseBackend):
  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    if set(args.keys()) - {'RefdesMode'} != set():
      raise ValueError("Invalid argument found in args")
    refdes_mode = args.get("RefdesMode", "pathName")
    if refdes_mode == 'pathName':
      refdes_pathname = True
    elif refdes_mode == 'refdes':
      refdes_pathname = False
    else:
      raise ValueError(f"Invalid valueMode value {refdes_mode}")

    netlist = NetlistTransform(design).run()
    netlist_string = kicad.generate_netlist(netlist.blocks, netlist.nets, refdes_pathname)

    return [
      (edgir.LocalPath(), netlist_string)
    ]
