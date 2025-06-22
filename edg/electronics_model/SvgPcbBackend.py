import importlib
import inspect
import math
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
    FOOTPRINT_BORDER = 1  # mm
    BLOCK_BORDER = 2  # mm

    # create list of blocks by path
    block_subblocks: Dict[Tuple[str, ...], Set[str]] = {}
    block_footprints: Dict[Tuple[str, ...], List[NetBlock]] = {}
    for block in netlist.blocks:
        containing_path = block.full_path.blocks[:-1]
        block_footprints.setdefault(containing_path, []).append(block)
        for i in range(len(containing_path) - 1):
            block_subblocks.setdefault(tuple(containing_path[:i]), set()).add(containing_path[i])

    def arrange_hierarchy(root: Tuple[str, ...]) -> PlacedBlock:
        """Recursively arranges the immediate components of a hierarchy, treating each element
        as a bounding box rectangle, and trying to maintain some aspect ratio."""
        # TODO don't count borders as part of a block's width / height
        ASPECT_RATIO = 16 / 9

        sub_placed: List[Tuple[str, float, float, Union[PlacedBlock, NetBlock]]] = []  # (name, width, height, PlacedBlock or footprint)
        for subblock in block_subblocks.get(root, set()):
            subplaced = arrange_hierarchy(root + (subblock,))
            sub_placed.append((subblock, subplaced.width + BLOCK_BORDER, subplaced.height + BLOCK_BORDER, subplaced))

        for footprint in block_footprints.get(root, []):
            bbox = FootprintDataTable.bbox_of(footprint.footprint)
            width = bbox[2] - bbox[0] + FOOTPRINT_BORDER
            height = bbox[3] - bbox[1] + FOOTPRINT_BORDER
            sub_placed.append((footprint.full_path.blocks[-1], width, height, footprint))

        total_area = sum(width * height for _, width, height, _ in sub_placed)
        max_width = math.sqrt(total_area * ASPECT_RATIO)

        y_pos = 0
        x_max = 0
        y_max = 0
        # track the y limits and y position of the prior elements
        x_stack: List[Tuple[float, float, float]] = []  # [(x pos of next, y pos, y limit)]
        elts: Dict[str, Tuple[Union[PlacedBlock, TransformUtil.Path], Tuple[float, float]]] = {}
        for name, width, height, entry in sorted(sub_placed, key=lambda x: -x[2]):  # by height
            if not x_stack:
                next_y = y_pos
            else:
                next_y = x_stack[-1][1]  # y position of the next element

            while True:  # advance rows as needed
                if not x_stack:
                    break
                if x_stack[-1][0] + width > max_width:  # out of X space, advance a row
                    _, _, next_y = x_stack.pop()
                if next_y + height > x_stack[-1][2]:  # out of Y space, advance a row
                    _, _, next_y = x_stack.pop()
                break

            if not x_stack:
                next_x = 0
            else:
                next_x = x_stack[-1][0]

            if isinstance(entry, PlacedBlock):  # assumed (0, 0) at top left
                elts[name] = (entry, (next_x, next_y))
            elif isinstance(entry, NetBlock):  # account for footprint origin
                bbox = FootprintDataTable.bbox_of(entry.footprint)
                elts[name] = (entry.full_path, (next_x - bbox[0], next_y - bbox[1]))
            x_stack.append((next_x + width, next_y, next_y + height))
            x_max = max(x_max, next_x + width)
            y_max = max(y_max, next_y + height)
        return PlacedBlock(
            elts=elts, height=x_max, width=y_max
        )

    return arrange_hierarchy(())


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
