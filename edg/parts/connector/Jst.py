from typing import Tuple, Optional

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


@abstract_block_default(lambda: JstXhAVertical)
class JstXh(FootprintPassiveConnector):
    """Abstract base class for JST XH 2.50mm shrouded and polarized headers."""


class JstXhAVertical(JstXh):
    """JST B*B-XH-A series connector: 2.50mm shrouded and polarized, in vertical through-hole."""

    allowed_pins = list(range(2, 16 + 1)) + [20]

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (f"Connector_JST:JST_XH_B{length}B-XH-A_1x{length:02d}_P2.50mm_Vertical", "JST", f"B{length}B-XH-A")


class JstXhAHorizontal(JstXh):
    """JST S*B-XH-A series connector: 2.50mm shrouded and polarized, in horizontal through-hole."""

    allowed_pins = list(range(2, 16 + 1)) + [20]

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (f"Connector_JST:JST_XH_S{length}B-XH-A_1x{length:02d}_P2.50mm_Horizontal", "JST", f"S{length}B-XH-A")


@abstract_block_default(lambda: JstPhKVertical)
class JstPh(FootprintPassiveConnector):
    """Abstract base class for JST PH 2.00mm shrouded and polarized headers."""


class JstPhKVertical(JstPh):
    """JST B*B-PH-K series connector: 2.00mm shrouded and polarized, in vertical through-hole."""

    allowed_pins = range(2, 16 + 1)

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (f"Connector_JST:JST_PH_B{length}B-PH-K_1x{length:02d}_P2.00mm_Vertical", "JST", f"B{length}B-PH-K")


class JstPhKHorizontal(JstPh, JlcPart):
    """JST S*B-PH-K series connector: 2.00mm shrouded and polarized, in horizontal (right-angle) through-hole."""

    allowed_pins = range(2, 16 + 1)
    PART_NUMBERS = {  # white colored, -S part suffix
        2: "C173752",
        3: "C157929",
        4: "C157926",
        5: "C157923",
        6: "C157920",
        7: "C157917",
        8: "C157915",
        9: "C157912",
        10: "C157947",
        11: "C157945",
        12: "C157943",
        13: "C157940",
        14: "C157938",
        15: "C157936",
        16: "C157934",
    }

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        self.assign(self.lcsc_part, self.PART_NUMBERS[length])
        self.assign(self.actual_basic_part, False)
        return (f"Connector_JST:JST_PH_S{length}B-PH-K_1x{length:02d}_P2.00mm_Horizontal", "JST", f"S{length}B-PH-K")

    @override
    def part_footprint_pnp_rot(self, length: int) -> Optional[float]:
        return 180

    @override
    def part_footprint_pnp_offset(self, length: int) -> Optional[Tuple[float, float]]:
        return (length - 1.0, 0)


class JstPhSmVertical(JstPh):
    """JST B*B-PH-SM4 series connector: 2.00mm shrouded and polarized, in vertical surface-mount."""

    allowed_pins = range(2, 16 + 1)

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (
            f"Connector_JST:JST_PH_B{length}B-PH-SM4-TB_1x{length:02d}-1MP_P2.00mm_Vertical",
            "JST",
            f"B{length}B-PH-SM4-TB",
        )


class JstPhSmVerticalJlc(JlcPart, JstPhSmVertical):
    """JST PH connector in SMD, with JLC part numbers for what parts are stocked (JST or clones,
    since JLC's inventory of PH SMD connectors is pretty spotty)."""

    PART_NUMBERS = {  # in order of decreasing stock, on 2022-08-23
        3: "C146054",
        2: "C64658",
        6: "C265088",
        5: "C273126",
        4: "C519161",
        8: "C519165",
        14: "C278813",
    }

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        # TODO this isn't the intended hook and uses side effects, but it works for now
        self.assign(self.lcsc_part, self.PART_NUMBERS[length])
        self.assign(self.actual_basic_part, False)
        return super().part_footprint_mfr_name(length)


class JstShSmHorizontal(FootprintPassiveConnector, JlcPart):
    """JST SH connector in SMD, with JLC part numbers for what parts are stocked."""

    PART_NUMBERS = {  # in order of decreasing stock, on 2022-08-23
        2: "C160402",
        3: "C160403",
        4: "C160404",
        5: "C136657",
        6: "C160405",
        7: "C160406",
        8: "C160407",
        9: "C160408",
        10: "C160409",
        11: "C515956",
        12: "C160411",
        13: "C160412",
        14: "C160413",
        15: "C160414",
        20: "C160415",
    }
    allowed_pins = PART_NUMBERS.keys()

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        # TODO this isn't the intended hook and uses side effects, but it works for now
        self.assign(self.lcsc_part, self.PART_NUMBERS[length])
        self.assign(self.actual_basic_part, False)
        return (
            f"Connector_JST:JST_SH_SM{length:02d}B-SRSS-TB_1x{length:02d}-1MP_P1.00mm_Horizontal",
            "JST",
            f"SM{length:02d}B-SRSS-TB",
        )
