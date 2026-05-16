from typing import List, Tuple, override, Any
from typing_extensions import TypeVar

from ..core import *
from ..core.HdlUserExceptions import UnconnectableError


class SubboardBlock(Block):
    """A block that is a sub-board, where all its blocks not marked external are part of a different board.
    Provides the export_tap construct to tack connectors onto ports without breaking modeling."""

    def __init__(self) -> None:
        super().__init__()
        self._external_blocks: List[Block] = []
        self._export_taps: List[Tuple[Port, Port]] = []

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


class WrapperSubboardBlock(SubboardBlock):
    """A wrapper block where the internal blocks are skipped for netlisting and used for modeling only.
    Useful for eg, dev boards that only generate a connector or socket but re-use modeling from the raw subcircuit."""

    def __init__(self) -> None:
        super().__init__()
        # TODO flag wrapper block
