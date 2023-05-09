from typing import Tuple
from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block_default(lambda: TagConnectLegged)
class TagConnect(PassiveConnector):
  """Abstract block for tag-connect pogo pin pads."""


class TagConnectLegged(TagConnect):
  """Tag-connect pogo pin pad for the legged version. Compatible with non-legged versions."""
  allowed_pins = {6, 10, 14}  # KiCad only has footprints for 2x03, 2x05, 2x07
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector:Tag-Connect_TC20{length // 2}0-IDC-FP_2x{length // 2:02d}_P1.27mm_Vertical', '', '')  # no physical part


class TagConnectNonLegged(TagConnect):
  """Tag-connect pogo pin pad for the non-legged version. NOT compatible with legged versions."""
  allowed_pins = {6, 10}  # KiCad only has footprints for 2x03 and 2x05
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector:Tag-Connect_TC20{length // 2}0-IDC-NL_2x{length // 2:02d}_P1.27mm_Vertical', '', '')  # no physical part


class PinHeader254(PassiveConnector):
  """Generic 2.54mm pin header in vertical through-hole."""
  allowed_pins = range(1, 40+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Vertical',
            "Generic", f"PinHeader2.54 1x{length}")


class PinSocket254(PassiveConnector):
  """Generic 2.54mm pin socket in vertical through-hole."""
  allowed_pins = range(1, 40+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_PinSocket_2.54mm:PinSocket_1x{length:02d}_P2.54mm_Vertical',
            "Generic", f"PinSocket2.54 1x{length}")


class PinHeader127DualShrouded(PassiveConnector, JlcPart):
  """Generic dual-row 1.27mm pin header in vertical through-hole pinned in zigzag."""
  allowed_pins = [10]  # TODO support more
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    assert length == 10, "TODO support more lengths"
    self.assign(self.lcsc_part, 'C2962219')
    self.assign(self.actual_basic_part, False)
    # TODO shrouded footprint
    return (f'Connector_PinHeader_1.27mm:PinHeader_2x{length//2:02d}_P1.27mm_Vertical_SMD',
            "Generic", f"PinHeader1.27 Shrouded 2x{length//2}")


class JstPhKVertical(PassiveConnector):
  """JST B*B-PH-K series connector: 2.00mm shrouded and polarized, in vertical through-hole."""
  allowed_pins = range(2, 16+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_JST:JST_PH_B{length}B-PH-K_1x{length:02d}_P2.00mm_Vertical',
            "JST", f"B{length}B-PH-K")


class JstPhSmVertical(PassiveConnector):
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


class MolexSl(PassiveConnector):
  """Molex SL series connector: 2.54mm shrouded and polarized, in vertical through-hole.
  Breadboard wire compatible - especially for debugging in a pinch."""
  allowed_pins = range(2, 25+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_Molex:Molex_SL_171971-00{length:02d}_1x{length:02d}_P2.54mm_Vertical',
            "Molex", f"171971-00{length:02d}_1x{length:02d}")


@abstract_block
class Fpc050(PassiveConnector):
  """Abstract base class for 0.50mm pitch FPC connectors."""


@abstract_block
class Fpc050Top(Fpc050):
  """Abstract base class for top-contact FPC connectors.
  IMPORTANT: the pin numbering scheme differs for top- and bottom-contact connectors."""


@abstract_block
class Fpc050Bottom(Fpc050):
  """Abstract base class for bottom-contact FPC connectors.
  IMPORTANT: the pin numbering scheme differs for top- and bottom-contact connectors."""


class HiroseFh12sh(Fpc050Bottom):
  """Hirose FH12 SH FFC/FPC connector, 0.50mm pitch horizontal bottom contacts.
  Mostly footprint-compatible with TE 1775333-8, which is cheaper."""
  # positions the FH12 exists in, per https://www.hirose.com/product/series/FH12
  _fh12_pins = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 25, 26, 28, 29,
                     30, 32, 33, 34, 35, 36, 40, 42, 45, 49, 50, 53, 60}
  # positions for which there are KiCad footprints
  _kicad_pins = {6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 25, 26, 28,
                      30, 32, 33, 34, 35, 36, 40, 45, 50, 53}
  allowed_pins = _fh12_pins.intersection(_kicad_pins)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_FFC-FPC:Hirose_FH12-{length}S-0.5SH_1x{length:02d}-1MP_P0.50mm_Horizontal',
            "Hirose", f"FH12-{length}S-0.5SH")


class Afc01(Fpc050Bottom, JlcPart):
  """Jushuo AFC01 series bottom-entry 0.5mm-pitch FPC connectors, with partial JLC numbers for some parts
  and re-using the probably-compatible but not-purpose-designed FH12 footprint."""
  _afc01_pins = set(range(4, 60+1))  # as listed by the part table
  allowed_pins = _afc01_pins.intersection(HiroseFh12sh._kicad_pins)
  PART_NUMBERS = {  # partial list of the ones currently used
    8: 'C262657',
    15: 'C262664',
    24: 'C262669',
    30: 'C262671',
  }
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    # TODO this isn't the intended hook and uses side effects, but it works for now
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return (f'Connector_FFC-FPC:Hirose_FH12-{length}S-0.5SH_1x{length:02d}-1MP_P0.50mm_Horizontal',
            "Jushuo", f"AFC01-S{length:02d}FCA-00")  # CA is T&R packaging


class Te1734839(Fpc050Top):
  """TE x-1734839 FFC/FPC connector, 0.50mm pitch horizontal top contacts."""
  allowed_positions = range(5, 50)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_FFC-FPC:TE_{length // 10}-1734839-{length % 10}_1x{length:02d}-1MP_P0.5mm_Horizontal',
            "TE Connectivity", f"{length // 10}-1734839-{length % 10}")
