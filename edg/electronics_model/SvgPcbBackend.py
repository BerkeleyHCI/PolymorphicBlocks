import importlib
import inspect
from typing import List, Tuple, NamedTuple, Dict, Union, Set

from .. import edgir
from .KicadFootprintData import FootprintDataTable
from ..core import *
from .NetlistGenerator import NetlistTransform, NetBlock, Netlist
from .SvgPcbTemplateBlock import SvgPcbTemplateBlock


class PlacedBlock(NamedTuple):
    """A placement of a hierarchical block, including the coordinates of its immediate elements.
    Elements are placed in local space, with (0, 0) as the origin and elements moved as a group.
    Elements are indexed by name."""
    elts: Dict[str, Tuple[Union['PlacedBlock', TransformUtil.Path], Tuple[float, float]]]  # name -> elt, (x, y)
    height: float
    width: float


def arrange_netlist(netlist: Netlist) -> PlacedBlock:
    # create list of blocks by path
    block_subblocks: Dict[Tuple[str, ...], Set[str]] = {}
    block_footprints: Dict[Tuple[str, ...], List[NetBlock]] = {}
    for block in netlist.blocks:
        containing_path = block.full_path.blocks[:-1]
        block_footprints.setdefault(containing_path, []).append(block)
        for i in range(len(containing_path) - 1):
            block_subblocks.setdefault(tuple(containing_path[:i]), set()).add(containing_path[i])

    def arrange_hierarchy(root: Tuple[str, ...]) -> PlacedBlock:
        sub_placed: List[Tuple[float, Union[PlacedBlock, str]]] = []  # (area, PlacedBlock or footprint name)
        for subblock in block_subblocks.get(root, set()):
            subplaced = arrange_hierarchy(root + (subblock,))
            sub_placed.append((subplaced.width * subplaced.height, subplaced))

        for footprint in block_footprints.get(root, []):
            # bbox = FootprintDataTable.bbox_of(footprint.footprint)
            area = FootprintDataTable.area_of(footprint.footprint)
            # bbox[2] - bbox[0], bbox[3] - bbox[1]
            sub_placed.append((area, footprint.full_path.blocks[-1]))
            
        print(sub_placed)

    return arrange_hierarchy(())
    print(block_footprints[()])



class SvgPcbGeneratedBlock(NamedTuple):
    path: TransformUtil.Path
    fn_name: str
    svgpcb_code: str


class SvgPcbTransform(TransformUtil.Transform):
    """Collects all SVGPCB blocks and initializes them."""
    def __init__(self, design: CompiledDesign, netlist: Netlist):
        self.design = design
        self.netlist = netlist
        self._svgpcb_blocks: List[SvgPcbGeneratedBlock] = []

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        # ignore root, bit of a heuristic hack since importing the toplevel script can be brittle
        if context.path == TransformUtil.Path.empty():
            return

        # TODO: dedup w/ class_from_library in edg_hdl_server
        elt_split = block.self_class.target.name.split('.')
        elt_module = importlib.import_module('.'.join(elt_split[:-1]))
        assert inspect.ismodule(elt_module)
        cls = getattr(elt_module, elt_split[-1])
        if issubclass(cls, SvgPcbTemplateBlock):
            generator_obj = cls()
            generator_obj._svgpcb_init(context.path, self.design, self.netlist)
            self._svgpcb_blocks.append(SvgPcbGeneratedBlock(
                context.path, generator_obj._svgpcb_fn_name(), generator_obj._svgpcb_template()
            ))
        else:
            pass

    def run(self) -> List[SvgPcbGeneratedBlock]:
        self.transform_design(self.design.design)
        return self._svgpcb_blocks


class SvgPcbCompilerResult(NamedTuple):
    functions: list[str]
    instantiations: list[str]


class SvgPcbBackend(BaseBackend):
    def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
        netlist = NetlistTransform(design).run()
        result = self._generate(design, netlist)
        if result.functions:  # pack layout templates into a file
            svgpcb_str = ""
            svgpcb_str += "\n".join(result.functions)
            svgpcb_str += "\n" + "\n".join(result.instantiations)
            return [
                (edgir.LocalPath(), svgpcb_str)
            ]
        else:
            return []  # no layout templates, ignore

    def _generate(self, design: CompiledDesign, netlist: Netlist) -> SvgPcbCompilerResult:
        """Generates SVBPCB fragments as a structured result"""
        def block_matches_prefixes(block: NetBlock, prefixes: List[Tuple[str, ...]]):
            for prefix in prefixes:
                if block.full_path.blocks[0:min(len(block.full_path.blocks), len(prefix))] == prefix:
                    return True
            return False

        def filter_blocks_by_pathname(blocks: List[NetBlock], exclude_prefixes: List[Tuple[str, ...]]) -> List[NetBlock]:
            return [block for block in blocks
                    if not block_matches_prefixes(block, exclude_prefixes)]

        svgpcb_blocks = SvgPcbTransform(design, netlist).run()
        svgpcb_block_prefixes = [block.path.to_tuple() for block in svgpcb_blocks]
        netlist = NetlistTransform(design).run()
        other_blocks = filter_blocks_by_pathname(netlist.blocks, svgpcb_block_prefixes)

        svgpcb_block_instantiations = [
            f"const {SvgPcbTemplateBlock._svgpcb_pathname_to_svgpcb(block.path)} = {block.fn_name}(pt(0, 0))"
            for block in svgpcb_blocks
        ]

        x_pos = 0
        y_pos = 0

        # note, dimensions in inches
        other_block_instantiations = []
        for block in other_blocks:
            block_bbox = FootprintDataTable.bbox_of(block.footprint)

            if block_bbox is not None:
                x_pos += -block_bbox[0] / 25.4

            block_code = f"""\
const {SvgPcbTemplateBlock._svgpcb_pathname_to_svgpcb(block.full_path)} = board.add({SvgPcbTemplateBlock._svgpcb_footprint_to_svgpcb(block.footprint)}, {{
  translate: pt({x_pos:.3f}, {y_pos:.3f}), rotate: 0,
  id: '{SvgPcbTemplateBlock._svgpcb_pathname_to_svgpcb(block.full_path)}'
}})"""
            other_block_instantiations.append(block_code)

            if block_bbox is not None:
                x_pos += block_bbox[2] / 25.4

            x_pos += 0.1  # boundary

        return SvgPcbCompilerResult(
            [block.svgpcb_code for block in svgpcb_blocks],
            svgpcb_block_instantiations + other_block_instantiations
        )
