from abc import abstractmethod
from typing import Optional, Any, List, Tuple

from .NetlistGenerator import Netlist
from ..core import *


@non_library
class SvgPcbTemplateBlock(Block):
    """EXPERIMENTAL! MAY CHANGE, NOT API-STABLE!

    A Block that can generate a SVG-PCB (https://github.com/leomcelroy/svg-pcb) layout template.
    This defines the per-class methods (including per-class code generation), the actual board-level code composition
    and generation of non-templated footprints exists in the backend.

    This defines the interface and supporting utilities only."""
    @staticmethod
    def _svgpcb_pathname_to_svgpcb(path: TransformUtil.Path) -> str:
        return '_'.join(path.to_tuple()).replace('[', '_').replace(']', '_')

    @staticmethod
    def _svgpcb_footprint_to_svgpcb(footprint: str) -> str:  # KiCad footprint name to SVGPCB reference
        return footprint.split(':')[-1].replace('-', '_').replace(' ', '_').replace('.', '_')

    def _svgpcb_init(self, pathname: TransformUtil.Path, design: CompiledDesign, netlist: Netlist) -> None:
        """Initializes this Block for SVGPCB template generation. Called from the backend."""
        self._svgpcb_pathname_data = pathname
        self._svgpcb_design = design
        self._svgpcb_netlist = netlist
        self._svgpcb_ref_map = self._create_ref_map(pathname.to_local_path())

    def _svgpcb_pathname(self) -> str:
        """Infrastructure method, returns the pathname for this Block as a JS-code-friendly string."""
        return self._svgpcb_pathname_to_svgpcb(self._svgpcb_pathname_data)

    def _svgpcb_get(self, param: ConstraintExpr[Any, Any]) -> Any:
        """Infrastructure method, returns the value of the ConstraintExpr. Asserts out if the value isn't available"""
        param_path = self._svgpcb_ref_map.get(param, None)
        assert param_path is not None
        param_val = self._svgpcb_design.get_value(param_path)
        assert param_val is not None
        return param_val

    def _svgpcb_refdes_of(self, block_ref: List[str]) -> Tuple[str, int]:
        """Returns the refdes of a block, as a tuple of prefix and number,
        or crashes if the block is not valid."""
        block_path = self._svgpcb_pathname_data.append_block(*block_ref)
        candidate_blocks = [block for block in self._svgpcb_netlist.blocks
                            if block.full_path.startswith(block_path)]
        assert len(candidate_blocks) > 0
        refdes = candidate_blocks[0].refdes
        assert isinstance(refdes, str)
        assert refdes is not None
        for i in reversed(range(len(refdes))):  # split between letter and numeric parts
            if refdes[i].isalpha():
                if i == len(refdes) - 1:
                    return refdes, -1  # fallback if no numeric portion
                return refdes[:i+1], int(refdes[i+1:])
        return "", int(refdes)

    def _svgpcb_footprint_block_path_of(self, block_ref: List[str]) -> TransformUtil.Path:
        """Infrastructure method, given the name of a container block, returns the block path of the footprint block.
        Picks the first one, which is assumed to be the main / anchor device."""
        block_path = self._svgpcb_pathname_data.append_block(*block_ref)
        candidate_blocks = [block for block in self._svgpcb_netlist.blocks
                            if block.full_path.startswith(block_path)]
        assert len(candidate_blocks) > 0
        return candidate_blocks[0].full_path

    def _svgpcb_footprint_of(self, path: TransformUtil.Path) -> str:
        """Infrastructure method, returns the footprint for the output of _svgpcb_footprint_block_path_of.
        If _svgpcb_footprint_block_path_of returned a value, this will return the footprint; otherwise crashes."""
        candidate_blocks = [block for block in self._svgpcb_netlist.blocks
                            if block.full_path == path]
        assert len(candidate_blocks) > 0
        return self._svgpcb_footprint_to_svgpcb(candidate_blocks[0].footprint)

    def _svgpcb_pin_of(self, block_ref: List[str], pin_ref: List[str]) -> str:
        """Infrastructure method, given a footprint path from _svgpcb_footprint_block_path_of and a port that should
        be connected to one of its pins, returns the footprint pin that the port is connected to."""
        footprint_path = self._svgpcb_footprint_block_path_of(block_ref)
        port_path = footprint_path.append_port(*pin_ref)
        candidate_nets = [net for net in self._svgpcb_netlist.nets
                          if port_path in net.ports]
        assert len(candidate_nets) == 1
        candidate_pins = [pin for pin in candidate_nets[0].pins
                          if pin.block_path == footprint_path]
        assert len(candidate_pins) == 1
        return candidate_pins[0].pin_name

    def _svgpcb_fn_name_adds(self) -> Optional[str]:
        """Optional additional data to be added to the function name for readability, like parameter values."""
        return None

    def _svgpcb_fn_name(self) -> str:
        """Infrastructure method (optionally user override-able), returns the SVGPCB function name
        for the template. This must be unique per-Block (so the pathname is encoded by default)."""
        optional_adds = self._svgpcb_fn_name_adds()
        if optional_adds is not None:
            return f"""{self.__class__.__name__}_{optional_adds}_{self._svgpcb_pathname()}"""
        else:
            return f"""{self.__class__.__name__}_{self._svgpcb_pathname()}"""

    def _svgpcb_bbox(self) -> Tuple[float, float, float, float]:
        """Returns the bounding box (xmin, ymin, xmax, ymax) in mm of the svgpcb layout with default parameters."""
        return 0.0, 0.0, 1.0, 1.0

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
