import importlib
import inspect
import math
from typing import List, Tuple, NamedTuple, Dict, Union, Set

from typing_extensions import override

from .. import edgir
from .KicadFootprintData import FootprintDataTable
from ..core import *
from .NetlistGenerator import NetlistTransform, NetBlock, Netlist
from .SvgPcbTemplateBlock import SvgPcbTemplateBlock


class PlacedBlock(NamedTuple):
    """A placement of a hierarchical block, including the coordinates of its immediate elements.
    Elements are placed in local space, with (0, 0) as the origin and elements moved as a group.
    Elements are indexed by name."""
    elts: List[Tuple[Union['PlacedBlock', TransformUtil.Path], Tuple[float, float]]]  # name -> elt, (x, y)
    height: float
    width: float


class BlackBoxBlock(NamedTuple):
    path: TransformUtil.Path
    bbox: Tuple[float, float, float, float]


def arrange_blocks(blocks: List[NetBlock],
                   additional_blocks: List[BlackBoxBlock] = []) -> PlacedBlock:
    FOOTPRINT_BORDER = 1  # mm
    BLOCK_BORDER = 2  # mm

    # create list of blocks by path
    block_subblocks: Dict[Tuple[str, ...], List[str]] = {}  # list to maintain sortedness
    block_footprints: Dict[Tuple[str, ...], List[Union[NetBlock, BlackBoxBlock]]] = {}

    # for here, we only group one level deep
    for block in blocks:
        containing_path = block.full_path.blocks[0:min(len(block.full_path.blocks) - 1, 1)]
        block_footprints.setdefault(containing_path, []).append(block)
        for i in range(len(containing_path)):
            subblocks_list = block_subblocks.setdefault(tuple(containing_path[:i]), list())
            if containing_path[i] not in subblocks_list:
                subblocks_list.append(containing_path[i])

    for blackbox in additional_blocks:
        containing_path = blackbox.path.blocks[0:min(len(blackbox.path.blocks) - 1, 1)]
        block_footprints.setdefault(containing_path, []).append(blackbox)
        for i in range(len(containing_path)):
            subblocks_list = block_subblocks.setdefault(tuple(containing_path[:i]), list())
            if containing_path[i] not in subblocks_list:
                subblocks_list.append(containing_path[i])

    def arrange_hierarchy(root: Tuple[str, ...]) -> PlacedBlock:
        """Recursively arranges the immediate components of a hierarchy, treating each element
        as a bounding box rectangle, and trying to maintain some aspect ratio."""
        # TODO don't count borders as part of a block's width / height
        ASPECT_RATIO = 16 / 9

        sub_placed: List[Tuple[float, float, Union[PlacedBlock, NetBlock, BlackBoxBlock]]] = []  # (width, height, entry)
        for subblock in block_subblocks.get(root, list()):
            subplaced = arrange_hierarchy(root + (subblock,))
            sub_placed.append((subplaced.width + BLOCK_BORDER, subplaced.height + BLOCK_BORDER, subplaced))

        for footprint in block_footprints.get(root, []):
            if isinstance(footprint, NetBlock):
                bbox = FootprintDataTable.bbox_of(footprint.footprint) or (1, 1, 1, 1)
                entry: Union[PlacedBlock, NetBlock, BlackBoxBlock] = footprint
            elif isinstance(footprint, BlackBoxBlock):
                bbox = footprint.bbox
                entry = footprint
            else:
                raise TypeError()
            width = bbox[2] - bbox[0] + FOOTPRINT_BORDER
            height = bbox[3] - bbox[1] + FOOTPRINT_BORDER
            # use refdes as key so it's globally unique, for when this is run with blocks grouped together
            sub_placed.append((width, height, entry))

        total_area = sum(width * height for width, height, _ in sub_placed)
        max_width = math.sqrt(total_area * ASPECT_RATIO)

        x_max = 0.0
        y_max = 0.0
        # track the y limits and y position of the prior elements
        x_stack: List[Tuple[float, float, float]] = []  # [(x pos of next, y pos, y limit)]
        elts: List[Tuple[Union[PlacedBlock, TransformUtil.Path], Tuple[float, float]]] = []
        for width, height, entry in sorted(sub_placed, key=lambda x: -x[1]):  # by height
            if not x_stack:  # only on first component
                next_y = 0.0
            else:
                next_y = x_stack[-1][1]  # y position of the next element

            while True:  # advance rows as needed
                if not x_stack:
                    break
                if x_stack[-1][0] + width > max_width:  # out of X space, advance a row
                    _, _, next_y = x_stack.pop()
                    continue
                if next_y + height > x_stack[-1][2]:  # out of Y space, advance a row
                    _, _, next_y = x_stack.pop()
                    continue
                break

            if not x_stack:
                next_x = 0.0
            else:
                next_x = x_stack[-1][0]

            if isinstance(entry, PlacedBlock):  # assumed (0, 0) at top left
                elts.append((entry, (next_x, next_y)))
            elif isinstance(entry, NetBlock):  # account for footprint origin, flipping y-axis
                bbox = FootprintDataTable.bbox_of(entry.footprint) or (0, 0, 0, 0)
                elts.append((entry.full_path, (next_x - bbox[0], next_y + bbox[3])))
            elif isinstance(entry, BlackBoxBlock):  # account for footprint origin, flipping y-axis
                bbox = entry.bbox
                elts.append((entry.path, (next_x - bbox[0], next_y - bbox[0])))
            x_stack.append((next_x + width, next_y, next_y + height))
            x_max = max(x_max, next_x + width)
            y_max = max(y_max, next_y + height)
        return PlacedBlock(
            elts=elts, width=x_max, height=y_max
        )
    return arrange_hierarchy(())


def flatten_packed_block(block: PlacedBlock) -> Dict[TransformUtil.Path, Tuple[float, float]]:
    """Flatten a packed_block to a dict of individual components."""
    flattened: Dict[TransformUtil.Path, Tuple[float, float]] = {}
    def walk_group(block: PlacedBlock, x_pos: float, y_pos: float) -> None:
        for elt, (elt_x, elt_y) in block.elts:
            if isinstance(elt, PlacedBlock):
                walk_group(elt, x_pos + elt_x, y_pos + elt_y)
            elif isinstance(elt, TransformUtil.Path):
                flattened[elt] = (x_pos + elt_x, y_pos + elt_y)
            else:
                raise TypeError
    walk_group(block, 0, 0)
    return flattened


class SvgPcbGeneratedBlock(NamedTuple):
    path: TransformUtil.Path
    fn_name: str
    svgpcb_code: str
    bbox: Tuple[float, float, float, float]


class SvgPcbTransform(TransformUtil.Transform):
    """Collects all SVGPCB blocks and initializes them."""
    def __init__(self, design: CompiledDesign, netlist: Netlist):
        self.design = design
        self.netlist = netlist
        self._svgpcb_blocks: List[SvgPcbGeneratedBlock] = []

    @override
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
                context.path, generator_obj._svgpcb_fn_name(), generator_obj._svgpcb_template(), generator_obj._svgpcb_bbox()
            ))
        else:
            pass

    def run(self) -> List[SvgPcbGeneratedBlock]:
        self.transform_design(self.design.design)
        return self._svgpcb_blocks


class SvgPcbBackend(BaseBackend):
    @override
    def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
        netlist = NetlistTransform(design).run()
        result = self._generate(design, netlist)
        return [
            (edgir.LocalPath(), result)
        ]

    def _generate(self, design: CompiledDesign, netlist: Netlist) -> str:
        """Generates SVBPCB fragments as a structured result"""
        def block_matches_prefixes(block: NetBlock, prefixes: List[Tuple[str, ...]]) -> bool:
            for prefix in prefixes:
                if block.full_path.blocks[0:min(len(block.full_path.blocks), len(prefix))] == prefix:
                    return True
            return False

        def filter_blocks_by_pathname(blocks: List[NetBlock], exclude_prefixes: List[Tuple[str, ...]]) -> List[NetBlock]:
            return [block for block in blocks
                    if not block_matches_prefixes(block, exclude_prefixes)]

        # handle blocks with svgpcb templates
        svgpcb_blocks = SvgPcbTransform(design, netlist).run()
        svgpcb_block_bboxes = [BlackBoxBlock(block.path, block.bbox) for block in svgpcb_blocks]

        # handle footprints
        netlist = NetlistTransform(design).run()
        svgpcb_block_prefixes = [block.path.to_tuple() for block in svgpcb_blocks]
        other_blocks = filter_blocks_by_pathname(netlist.blocks, svgpcb_block_prefixes)
        arranged_blocks = arrange_blocks(other_blocks, svgpcb_block_bboxes)
        pos_dict = flatten_packed_block(arranged_blocks)

        # note, dimensions in inches, divide by 25.4 to convert from mm
        svgpcb_block_instantiations = []
        for svgpcb_block in svgpcb_blocks:
            x_pos, y_pos = pos_dict.get(svgpcb_block.path, (0, 0))  # in mm, need to convert to in below
            block_code = f"const {SvgPcbTemplateBlock._svgpcb_pathname_to_svgpcb(svgpcb_block.path)} = {svgpcb_block.fn_name}(pt({x_pos/25.4:.3f}, {y_pos/25.4:.3f}))"
            svgpcb_block_instantiations.append(block_code)

        other_block_instantiations = []
        for net_block in other_blocks:
            x_pos, y_pos = pos_dict.get(net_block.full_path, (0, 0))  # in mm, need to convert to in below
            block_code = f"""\
// {net_block.full_path}
const {net_block.refdes} = board.add({SvgPcbTemplateBlock._svgpcb_footprint_to_svgpcb(net_block.footprint)}, {{
  translate: pt({x_pos/25.4:.3f}, {y_pos/25.4:.3f}), rotate: 0,
  id: '{net_block.refdes}'
}})"""
            other_block_instantiations.append(block_code)

        net_blocks_by_path = {net_block.full_path: net_block for net_block in netlist.blocks}
        netlist_code_entries = []
        for net in netlist.nets:
            pads_code = [f"""["{net_blocks_by_path[pin.block_path].refdes}", "{pin.pin_name}"]""" for pin in net.pins]
            netlist_code_entries.append(f"""{{name: "{net.name}", pads: [{', '.join(pads_code)}]}}""")

        NEWLINE = '\n'
        full_code = f"""\
const board = new PCB();

{NEWLINE.join(svgpcb_block_instantiations + other_block_instantiations)}

board.setNetlist([
  {("," + NEWLINE + "  ").join(netlist_code_entries)}
])

const limit0 = pt(-{2/25.4}, -{2/25.4});
const limit1 = pt({arranged_blocks.width/25.4}, {arranged_blocks.height/25.4});
const xMin = Math.min(limit0[0], limit1[0]);
const xMax = Math.max(limit0[0], limit1[0]);
const yMin = Math.min(limit0[1], limit1[1]);
const yMax = Math.max(limit0[1], limit1[1]);

const filletRadius = 0.1;
const outline = path(
  [(xMin+xMax/2), yMax],
  ["fillet", filletRadius, [xMax, yMax]],
  ["fillet", filletRadius, [xMax, yMin]],
  ["fillet", filletRadius, [xMin, yMin]],
  ["fillet", filletRadius, [xMin, yMax]],
  [(xMin+xMax/2), yMax],
);
board.addShape("outline", outline);

renderPCB({{
  pcb: board,
  layerColors: {{
    "F.Paste": "#000000ff",
    "F.Mask": "#000000ff",
    "B.Mask": "#000000ff",
    "componentLabels": "#00e5e5e5",
    "outline": "#002d00ff",
    "padLabels": "#ffff99e5",
    "B.Cu": "#ef4e4eff",
    "F.Cu": "#ff8c00cc",
  }},
  limits: {{
    x: [xMin, xMax],
    y: [yMin, yMax]
  }},
  background: "#00000000",
  mmPerUnit: 25.4
}})

{NEWLINE.join([block.svgpcb_code for block in svgpcb_blocks])}
"""

        return full_code
