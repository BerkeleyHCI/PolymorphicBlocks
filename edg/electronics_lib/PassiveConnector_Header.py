from typing import Tuple
from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block_default(lambda: PinHeader254Vertical)
class PinHeader254(PassiveConnector):
  """Abstract base class for all 2.54mm pin headers."""


class PinHeader254Vertical(PinHeader254, FootprintPassiveConnector):
  """Generic 2.54mm pin header in vertical through-hole."""
  allowed_pins = range(1, 40+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Vertical',
            "Generic", f"PinHeader2.54 1x{length}")


class PinHeader254Horizontal(PinHeader254, FootprintPassiveConnector):
  """Generic 2.54mm pin header in horizontal (right-angle) through-hole."""
  allowed_pins = range(1, 40+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Horizontal',
            "Generic", f"PinHeader2.54 1x{length} Horizontal")


class PinSocket254(FootprintPassiveConnector):
  """Generic 2.54mm pin socket in vertical through-hole."""
  allowed_pins = range(1, 40+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_PinSocket_2.54mm:PinSocket_1x{length:02d}_P2.54mm_Vertical',
            "Generic", f"PinSocket2.54 1x{length}")


class PinHeader254DualShroudedInline(FootprintPassiveConnector):
  """Generic 2.54mm dual-row pin header in edge-inline."""
  allowed_pins = {6}
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'edg:PinHeader_2x{length//2:02d}_P2.54mm_EdgeInline',
            "Generic", f"PinHeader2.54 Shrouded 2x{length//2}")


class PinHeader127DualShrouded(FootprintPassiveConnector, JlcPart):
  """Generic dual-row 1.27mm pin header in vertical through-hole pinned in zigzag."""
  allowed_pins = [10]  # TODO support more
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    assert length == 10, "TODO support more lengths"
    self.assign(self.lcsc_part, 'C2962219')
    self.assign(self.actual_basic_part, False)
    # TODO shrouded footprint
    return (f'Connector_PinHeader_1.27mm:PinHeader_2x{length//2:02d}_P1.27mm_Vertical_SMD',
            "Generic", f"PinHeader1.27 Shrouded 2x{length//2}")


class JstPhKVertical(FootprintPassiveConnector):
  """JST B*B-PH-K series connector: 2.00mm shrouded and polarized, in vertical through-hole."""
  allowed_pins = range(2, 16+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_JST:JST_PH_B{length}B-PH-K_1x{length:02d}_P2.00mm_Vertical',
            "JST", f"B{length}B-PH-K")


"""JST S*B-PH-K series connector: 2.00mm shrouded and polarized, in horizontal (right-angle) through-hole."""
class JstPhKHorizontal(FootprintPassiveConnector, JlcPart):
  allowed_pins = range(2, 16+1)
  PART_NUMBERS = {  # white colored, -S part suffix
    2: 'C173752',
    3: 'C157929',
    4: 'C157926',
    5: 'C157923',
    6: 'C157920',
    7: 'C157917',
    8: 'C157915',
    9: 'C157912',
    10: 'C157947',
    11: 'C157945',
    12: 'C157943',
    13: 'C157940',
    14: 'C157938',
    15: 'C157936',
    16: 'C157934',
  }
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return (f'Connector_JST:JST_PH_S{length}B-PH-K_1x{length:02d}_P2.00mm_Horizontal',
            "JST", f"S{length}B-PH-K")


class JstPhSmVertical(FootprintPassiveConnector):
  """JST B*B-PH-SM4 series connector: 2.00mm shrouded and polarized, in vertical surface-mount."""
  allowed_pins = range(2, 16+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_JST:JST_PH_B{length}B-PH-SM4-TB_1x{length:02d}-1MP_P2.00mm_Vertical',
            "JST", f"B{length}B-PH-SM4-TB")


class JstPhSmVerticalJlc(JstPhSmVertical, JlcPart):
  """JST PH connector in SMD, with JLC part numbers for what parts are stocked (JST or clones,
  since JLC's inventory of PH SMD connectors is pretty spotty)."""
  PART_NUMBERS = {  # in order of decreasing stock, on 2022-08-23
    3: 'C146054',
    2: 'C64658',
    6: 'C265088',
    5: 'C273126',
    4: 'C519161',
    8: 'C519165',
    14: 'C278813',
  }
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    # TODO this isn't the intended hook and uses side effects, but it works for now
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return super().part_footprint_mfr_name(length)


class JstShSmHorizontal(FootprintPassiveConnector, JlcPart):
  """JST SH connector in SMD, with JLC part numbers for what parts are stocked."""
  PART_NUMBERS = {  # in order of decreasing stock, on 2022-08-23
    2: 'C160402',
    3: 'C160403',
    4: 'C160404',
    5: 'C136657',
    6: 'C160405',
    7: 'C160406',
    8: 'C160407',
    9: 'C160408',
    10: 'C160409',
    11: 'C515956',
    12: 'C160411',
    13: 'C160412',
    14: 'C160413',
    15: 'C160414',
    20: 'C160415',
  }
  allowed_pins = PART_NUMBERS.keys()
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    # TODO this isn't the intended hook and uses side effects, but it works for now
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return (f'Connector_JST:JST_SH_SM{length:02d}B-SRSS-TB_1x{length:02d}-1MP_P1.00mm_Horizontal',
            "JST", f"SM{length:02d}B-SRSS-TB")


class MolexSl(FootprintPassiveConnector):
  """Molex SL series connector: 2.54mm shrouded and polarized, in vertical through-hole.
  Breadboard wire compatible - especially for debugging in a pinch."""
  allowed_pins = range(2, 25+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_Molex:Molex_SL_171971-00{length:02d}_1x{length:02d}_P2.54mm_Vertical',
            "Molex", f"171971-00{length:02d}_1x{length:02d}")
