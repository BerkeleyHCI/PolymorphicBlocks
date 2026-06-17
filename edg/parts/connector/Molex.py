from typing import Tuple, Optional

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


@abstract_block_default(lambda: Picoblade53398)
class Picoblade(FootprintPassiveConnector):
    """Abstract base class for Molex PicoBlade 1.25mm shrouded and polarized headers.
    Sometimes generically referred to as JST 1.25mm, even though JST does not make 1.25mm headers."""


class Picoblade53398(Picoblade):
    """Picoblade connector in surface-mount vertical."""

    allowed_pins = list(range(2, 16 + 1)) + [20]

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"Connector_Molex:Molex_PicoBlade_53398-{length:02d}71_1x{length:02d}-1MP_P1.25mm_Vertical",
            "Molex",
            f"53398{length:02d}71",
        )


class Picoblade53261(Picoblade):
    """Picoblade connector in surface-mount horizontal."""

    allowed_pins = list(range(2, 16 + 1)) + [20]

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"Connector_Molex:Molex_PicoBlade_53261-{length:02d}71_1x{length:02d}-1MP_P1.25mm_Horizontal",
            "Molex",
            f"53261{length:02d}71",
        )


class MolexSl(FootprintPassiveConnector):
    """Molex SL series connector: 2.54mm shrouded and polarized, in vertical through-hole.
    Breadboard wire compatible - especially for debugging in a pinch."""

    allowed_pins = range(2, 25 + 1)

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"Connector_Molex:Molex_SL_171971-00{length:02d}_1x{length:02d}_P2.54mm_Vertical",
            "Molex",
            f"171971-00{length:02d}_1x{length:02d}",
        )
