from typing import List, Tuple, Dict

from .. import edgir
from ..core import *
from . import footprint as kicad
from .NetlistGenerator import NetlistTransform


class NetlistBackend(BaseBackend):
  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    if set(args.keys()) - {'RefdesMode'} != set():
      raise ValueError("Invalid argument found in args")
    refdes_mode_arg = args.get("RefdesMode", "refdesPathNameValue")
    if refdes_mode_arg == 'pathName':
      refdes_mode = kicad.RefdesMode.Pathname
    elif refdes_mode_arg == 'refdes':
      refdes_mode = kicad.RefdesMode.Conventional
    elif refdes_mode_arg == 'refdesPathNameValue':
      refdes_mode = kicad.RefdesMode.PathnameAsValue
    else:
      raise ValueError(f"Invalid valueMode value {refdes_mode_arg}")

    netlist = NetlistTransform(design).run()
    netlist_string = kicad.generate_netlist(netlist, refdes_mode)

    return [
      (edgir.LocalPath(), netlist_string)
    ]
