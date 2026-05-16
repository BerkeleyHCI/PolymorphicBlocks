from typing import List, Tuple, override, Any
from typing_extensions import TypeVar

from ..core import *
from ..core.Core import Refable
from ..core.HdlUserExceptions import UnconnectableError
from .. import edgir


class SubboardBlock(Block):
    """A block that is a sub-board, where all its blocks not marked external are part of a different board.
    Provides the export_tap construct to tack connectors onto ports without breaking modeling.

    IMPORTANT: pseudo-blocks like bridges and adapters are considered internal blocks and do not affect
    netlisting in the exterior board. In general, external blocks should only be connected via export-tap
    and not direct connections where they may generate pseudo-blocks that end up in the wrong board."""

    def __init__(self) -> None:
        super().__init__()
        self._external_blocks: List[Block] = []
        self._export_taps: List[Tuple[Port, Port]] = []

        self.fp_subboard = self.Metadata("A")  # dummy distinct value
        self.fp_external_blocks = self.Parameter(ArrayStringExpr())  # names of all external blocks

    BlockType = TypeVar("BlockType", bound=Block)

    @override
    def Block(self, tpe: BlockType, *args: Any, external: bool = False, **kwargs: Any) -> BlockType:
        """Creates an internal Block.
        By default, these are internal (part of the sub-board), unless marked external (in which case
        it is placed in the containing board, eg for connectors).
        Connector-pairs should be marked external, but will resolve to an external-internal pair."""
        ret = super().Block(tpe, *args, **kwargs)
        if external:
            self._external_blocks.append(ret)
        return ret

    def export_tap(self, exterior_port: Port, internal_port: Port) -> None:
        """Connects an exterior port (on self) to an interior port (on an internal block)
        as a non-propagating connection which may coexist with other connections on the exterior port
        (but not the interior port).
        The interior port may not have parameters defined.
        This is used to tack a connector onto a port that already has electrical modeling from the internal blocks."""
        if exterior_port._block_parent() is not self:
            raise UnconnectableError("Exterior port must be on the block")
        internal_port_parent = internal_port._block_parent()
        if internal_port_parent is None or internal_port_parent._parent is not self:
            raise UnconnectableError("Internal port must be a block within this block")
        if type(exterior_port) != type(internal_port):
            raise UnconnectableError("Exported ports must be the same type")
        self._export_taps.append((exterior_port, internal_port))

    @override
    def _populate_def_proto_hierarchy(self, pb: edgir.HierarchyBlock, ref_map: Refable.RefMapType) -> None:
        self.assign(self.fp_external_blocks, [self._blocks.name_of(block) for block in self._external_blocks])

        super()._populate_def_proto_hierarchy(pb, ref_map)

        for exterior_port, internal_port in self._export_taps:
            internal_port_name = internal_port._name_from(self).replace(".", "_")
            constraint_pb = edgir.add_pair(pb.constraints, f"(export_tap){internal_port_name}")
            if isinstance(exterior_port, Vector):
                constraint_pb.exportedArray.exterior_port.ref.CopyFrom(ref_map[exterior_port])
                constraint_pb.exportedArray.internal_block_port.ref.CopyFrom(ref_map[internal_port])
                constraint_pb.exportedArray.tap = True
            else:
                constraint_pb.exported.exterior_port.ref.CopyFrom(ref_map[exterior_port])
                constraint_pb.exported.internal_block_port.ref.CopyFrom(ref_map[internal_port])
                constraint_pb.exported.tap = True


class WrapperSubboardBlock(SubboardBlock):
    """A wrapper block where the internal blocks are skipped for netlisting and used for modeling only.
    Useful for eg, dev boards that only generate a connector or socket but re-use modeling from the raw subcircuit."""

    def __init__(self) -> None:
        super().__init__()
        self.fp_subblocks_ignored = self.Metadata("B")  # dummy distinct value
