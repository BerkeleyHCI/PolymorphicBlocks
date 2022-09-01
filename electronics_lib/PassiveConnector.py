from typing import List, Tuple, Iterable
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
  allowed_pins: Iterable[int]

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
    # TODO ideally this is require, but we don't support set ops in the IR
    assert length in self.allowed_pins, f"requested length {length} outside allowed length {self.allowed_pins}"

    (footprint, mfr, part) = self.part_footprint_mfr_name(length)
    self.footprint(
      'J', footprint,
      {pin: self.pins[pin] for pin in pins},
      mfr, part
    )


class PinHeader254(PassiveConnector, FootprintBlock):
  """Generic 2.54mm pin header in vertical through-hole."""
  allowed_pins = range(2, 16+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_PinHeader_2.54mm:PinHeader_1x{length:02d}_P2.54mm_Vertical',
            "Generic", f"PinHeader2.54 1x{length}")


class JstPhK(PassiveConnector, FootprintBlock):
  """JST PH-K series connector: 2.00mm shrouded and polarized, in vertical through-hole."""
  allowed_pins = range(2, 16+1)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_JST:JST_PH_B{length}B-PH-K_1x{length:02d}_P2.00mm_Vertical',
            "JST", f"B{length}B-PH-K")


class MolexSl(PassiveConnector, FootprintBlock):
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


class HiroseFh12sh(Fpc050Bottom, FootprintBlock):
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


class Te1734839(Fpc050Top, FootprintBlock):
  """TE x-1734839 FFC/FPC connector, 0.50mm pitch horizontal top contacts."""
  allowed_positions = range(5, 50)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_FFC-FPC:TE_{length // 10}-1734839-{length % 10}_1x{length:02d}-1MP_P0.5mm_Horizontal',
            "TE Connectivity", f"{length // 10}-1734839-{length % 10}")
