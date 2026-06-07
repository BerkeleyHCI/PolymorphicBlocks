from typing import Tuple, Optional

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


@abstract_block_default(lambda: PinHeader254Vertical)
class PinHeader254(PassiveConnector):
    """Abstract base class for all 2.54mm pin headers."""


class PinHeader254Vertical(PinHeader254, FootprintPassiveConnector):
    """Generic 2.54mm pin header in vertical through-hole."""

    allowed_pins = range(1, 40 + 1)

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Vertical",
            "Generic",
            f"PinHeader2.54 1x{length}",
        )


class PinHeader254Horizontal(PinHeader254, FootprintPassiveConnector):
    """Generic 2.54mm pin header in horizontal (right-angle) through-hole."""

    allowed_pins = range(1, 40 + 1)

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Horizontal",
            "Generic",
            f"PinHeader2.54 1x{length} Horizontal",
        )


class PinSocket254(FootprintPassiveConnector):
    """Generic 2.54mm pin socket in vertical through-hole."""

    allowed_pins = range(1, 40 + 1)

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"Connector_PinSocket_2.54mm:PinSocket_1x{length:02d}_P2.54mm_Vertical",
            "Generic",
            f"PinSocket2.54 1x{length}",
        )


class PinSocket254Pair(SubboardConnectorPair, GeneratorBlock):
    """2.54mm pin socket (external) - header (internal) pair for sub-board connectors,
    matching same pin-number to pin-number.

    Optionally can be reversed, with the header being on the external side and the socket being on the internal side."""

    def __init__(self, length: IntLike = 0, *, reverse: BoolLike = False) -> None:
        super().__init__()
        self.length = self.ArgParameter(length)
        self.reverse = self.ArgParameter(reverse)
        self.generator_param(self.reverse)

        self.pins = self.Port(Vector(Passive.empty()))

    @override
    def generate(self) -> None:
        super().generate()
        if not self.get(self.reverse):
            self.ext: PassiveConnector = self.Block(PinSocket254(self.length), external=True)
            self.int: PassiveConnector = self.Block(PinHeader254(self.length))
        else:
            self.ext = self.Block(PinHeader254(self.length), external=True)
            self.int = self.Block(PinSocket254(self.length))
        self.connect(self.pins, self.int.pins)
        self.export_tap(self.pins, self.ext.pins)


class PinHeader254DualShroudedInline(FootprintPassiveConnector):
    """Generic 2.54mm dual-row pin header in edge-inline."""

    allowed_pins = {6}

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"edg:PinHeader_2x{length//2:02d}_P2.54mm_EdgeInline",
            "Generic",
            f"PinHeader2.54 Shrouded 2x{length//2}",
        )


class PinHeader127DualShrouded(FootprintPassiveConnector, JlcPart):
    """Generic dual-row 1.27mm pin header in vertical through-hole pinned in zigzag."""

    allowed_pins = [10]  # TODO support more

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        assert length == 10, "TODO support more lengths"
        self.assign(self.lcsc_part, "C2962219")
        self.assign(self.actual_basic_part, False)
        # TODO shrouded footprint
        return (
            f"Connector_PinHeader_1.27mm:PinHeader_2x{length//2:02d}_P1.27mm_Vertical_SMD",
            "Generic",
            f"PinHeader1.27 Shrouded 2x{length//2}",
        )

    @override
    def part_footprint_pnp_rot(self, length: int) -> Optional[float]:
        return -90
