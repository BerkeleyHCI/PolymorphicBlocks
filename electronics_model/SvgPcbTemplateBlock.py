from typing import Optional, Any, List, Tuple

import edgir
from edg_core import *
from edg_core.ConstraintExpr import ConstraintExpr
from abc import abstractmethod
from .NetlistGenerator import Netlist


class SvgPcbTemplateBlock(Block):
    """EXPERIMENTAL! MAY CHANGE, NOT API-STABLE!

    A Block that can generate a SVG-PCB (https://github.com/leomcelroy/svg-pcb) layout template.
    This defines the per-class methods (including per-class code generation), the actual board-level code composition
    and generation of non-templated footprints exists in the backend.

    This defines the interface and supporting utilities only."""
    @staticmethod
    def _svgpcb_pathname_to_svgpcb(path: TransformUtil.Path):
        return '_'.join(path.to_tuple())

    @staticmethod
    def _svgpcb_footprint_to_svgpcb(footprint: str) -> str:  # KiCad footprint name to SVGPCB reference
        return footprint.split(':')[-1].replace('-', '_').replace(' ', '_').replace('.', '_')

    def _svgpcb_init(self, pathname: TransformUtil.Path, design: CompiledDesign, netlist: Netlist) -> None:
        """Initializes this Block for SVGPCB template generation. Called from the backend."""
        self._svgpcb_pathname_data = pathname
        self._svgpcb_design = design
        self._svgpcb_netlist = netlist
        self._svgpcb_ref_map = self._get_ref_map(pathname.to_local_path())

    def _svgpcb_pathname(self) -> str:
        """Infrastructure method, returns the pathname for this Block as a JS-code-friendly string."""
        return self._svgpcb_pathname_to_svgpcb(self._svgpcb_pathname_data)

    def _svgpcb_get(self, param: ConstraintExpr[Any, Any]) -> Optional[str]:
        """Infrastructure method, returns the value of the ConstraintExpr as a JS literal.
        Ranges are mapped to a two-element list."""
        param_path = self._svgpcb_ref_map.get(param, None)
        if param_path is None:
            return None
        param_val = self._svgpcb_design.get_value(param_path)
        if param_val is None:
            return None
        # TODO structure the output to be JS-friendly
        return str(param_val)

    def _svgpcb_footprint_block_path_of(self, block_path: List[str]) -> Optional[TransformUtil.Path]:
        """Infrastructure method, given the name of a container block, returns the block path of the footprint block
        if there is exactly one. Otherwise, returns None."""
        block_path = self._svgpcb_pathname_data.append_block(*block_path)
        candidate_blocks = [block for block in self._svgpcb_netlist.blocks
                            if block.full_path.startswith(block_path)]
        if len(candidate_blocks) != 1:
            return None
        return self._svgpcb_footprint_to_svgpcb(candidate_blocks[0].full_path)

    def _svgpcb_footprint_of(self, path: TransformUtil.Path) -> str:
        """Infrastructure method, returns the footprint for the output of _svgpcb_footprint_block_path_of.
        If _svgpcb_footprint_block_path_of returned a value, this will return the footprint; otherwise crashes."""
        candidate_blocks = [block for block in self._svgpcb_netlist.blocks
                            if block.full_path == path]
        assert len(candidate_blocks) == 1
        return candidate_blocks[0].footprint

    def _svgpcb_pin_of(self, block_path: List[str], pin_path: List[str], footprint_path: TransformUtil.Path) -> Optional[str]:
        """Infrastructure method, given a footprint path from _svgpcb_footprint_block_path_of and a port that should
        be connected to one of its pins, returns the footprint pin that the port is connected to, if any."""
        port_path = self._svgpcb_pathname_data.append_block(*block_path).append_port(*pin_path)
        candidate_nets = [net for net in self._svgpcb_netlist.nets
                          if port_path in net.ports]
        if len(candidate_nets) != 1:
            return None
        candidate_pins = [pin for pin in candidate_nets[0].pins
                          if pin.block_path == footprint_path]
        if len(candidate_pins) != 1:
            return None
        return candidate_pins[0].pin_name

    def _svgpcb_fn_name(self) -> str:
        """Infrastructure method (optionally user override-able), returns the SVGPCB function name
        for the template. This must be unique per-Block (so the pathname is encoded by default)."""
        return f"""{self.__class__.__name__}_{self._svgpcb_pathname()}"""

    @abstractmethod
    def _svgpcb_template(self) -> str:
        """IMPLEMENT ME. Returns the SVGPCB layout template code as JS function named _svgpcb_fn_name.
        First argument must be xy (the XY origin of the block, defined from top-level code), but
        can have additional arguments (which must have defaults).

        Footprint IDs should be prefixed with _svgpcb_pathname, using underscores as additional separators.
        Use _svgpcb_get to get parameter values.

        Should include a trailing newline.
        """
        raise NotImplementedError("implement me!")
