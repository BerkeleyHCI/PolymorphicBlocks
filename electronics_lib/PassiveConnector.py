from typing import List, Tuple
from electronics_abstract_parts import *


@abstract_block
class PassiveConnector(Connector, GeneratorBlock, FootprintBlock):
  """A base Block that is an elastic n-ported connector with passive type.
  Intended as an infrastructural block where a particular connector series is not fixed,
  but can be selected through the refinements system.
  An optional length argument can be specified, which forces total number of pins. This must be larger
  than the maximum pin index (but can be smaller, unassigned pins are NC).
  The allocated pin names correlate with the footprint pin, 1-indexed (per electronics convention).
  It is up to the instantiating layer to set the pinmap (or allow the user to set it by refinements)."""
  allowed_pins: Tuple[int, int] = (0, 0)  # inclusive on both ends, default disallowed anywhere

  @init_in_parent
  def __init__(self, length: IntLike = 0):
    super().__init__()
    self.pins = self.Port(Vector(Passive().empty()))
    self.actual_length = self.Parameter(IntExpr())

    self.generator(self.generate, length, self.pins.allocated())

  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    """Returns the part footprint, manufacturer, and name given the number of pins (length).
    Implementing classes must implement this method."""
    raise NotImplementedError

  def generate(self, length: int, pins: List[str]):
    max_pin_index = 0
    for pin in pins:
      self.pins.append_elt(Passive(), pin)
      assert pin != '0', "cannot have zero pin, explicit pin numbers through suggested_name are required"
      max_pin_index = max(max_pin_index, int(pin))
    if length == 0:
      length = max_pin_index

    self.assign(self.actual_length, length)
    self.require(max_pin_index <= self.actual_length,
                 f"maximum pin index {max_pin_index} over requested length {length}")
    self.require(self.actual_length >= self.allowed_pins[0],
                 f"requested length {length} below allowed range {self.allowed_pins[0]} - {self.allowed_pins[1]}")
    self.require(self.actual_length <= self.allowed_pins[1],
                 f"requested length {length} above allowed range {self.allowed_pins[0]} - {self.allowed_pins[1]}")

    (footprint, mfr, part) = self.part_footprint_mfr_name(length)
    self.footprint(
      'J', footprint,
      {pin: self.pins[pin] for pin in pins},
      mfr, part
    )


class PinHeader254(PassiveConnector, FootprintBlock):
  """Generic 2.54mm pin header in vertical through-hole."""
  allowed_pins = (2, 16)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Vertical',
            "Generic", f"PinHeader2.54 1x{length}")


class JstPhK(PassiveConnector, FootprintBlock):
  """JST PH-K series connector: 2.00mm shrouded and polarized, in vertical through-hole."""
  allowed_pins = (2, 16)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_JST:JST_PH_B{length}B-PH-K_1x{length:02d}_P2.00mm_Vertical',
            "JST", f"B{length}B-PH-K")


class MolexSl(PassiveConnector, FootprintBlock):
  """Molex SL series connector: 2.54mm shrouded and polarized, in vertical through-hole.
  Breadboard wire compatible - especially for debugging in a pinch."""
  allowed_pins = (2, 25)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_Molex:Molex_SL_171971-00{length:02d}_1x{length:02d}_P2.54mm_Vertical',
            "Molex", f"171971-00{length:02d}_1x{length:02d}")
