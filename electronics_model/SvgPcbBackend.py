import importlib
import inspect
from typing import List, Tuple, NamedTuple, Dict

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil
from .NetlistGenerator import NetlistTransform, NetBlock, Netlist
from .SvgPcbTemplateBlock import SvgPcbTemplateBlock


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
        other_block_instantiations = [
            f"""\
    const {SvgPcbTemplateBlock._svgpcb_pathname_to_svgpcb(block.full_path)} = board.add({SvgPcbTemplateBlock._svgpcb_footprint_to_svgpcb(block.footprint)}, {{
    translate: pt(0, 0), rotate: 0,
    id: '{SvgPcbTemplateBlock._svgpcb_pathname_to_svgpcb(block.full_path)}'
    }})"""
            for block in other_blocks
        ]

        return SvgPcbCompilerResult(
            [block.svgpcb_code for block in svgpcb_blocks],
            svgpcb_block_instantiations + other_block_instantiations
        )
