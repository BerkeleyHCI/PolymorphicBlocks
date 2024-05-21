from typing import Tuple
from ..abstract_parts import *


@abstract_block_default(lambda: TagConnectLegged)
class TagConnect(FootprintPassiveConnector):
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
