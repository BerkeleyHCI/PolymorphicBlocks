from typing import List, Tuple, Dict

from typing_extensions import override

from .. import edgir
from ..core import *
from . import footprint as kicad
from .NetlistGenerator import NetlistTransform


class NetlistBackend(BaseBackend):
    @override
    def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
        if set(args.keys()) - {"RefdesMode"} != set():
            raise ValueError("Invalid argument found in args")
        refdes_mode_arg = args.get("RefdesMode", "refdesPathNameValue")
        if refdes_mode_arg == "refdes":
            refdes_mode = kicad.RefdesMode.Conventional
        elif refdes_mode_arg == "refdesPathNameValue":
            refdes_mode = kicad.RefdesMode.PathnameAsValue
        else:
            raise ValueError(f"Invalid RefdesMode value {refdes_mode_arg}")

        board_netlists = NetlistTransform(design).run()
        return [
            (netlist_path.to_local_path(), kicad.generate_netlist(netlist, refdes_mode))
            for (netlist_path, netlist) in board_netlists.items()
        ]
