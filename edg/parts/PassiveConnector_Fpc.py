from typing import Tuple
from ..abstract_parts import *
from .JlcPart import JlcPart


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


class Fpc050BottomFlip(Fpc050Bottom, GeneratorBlock):
  """Flipped FPC connector - bottom entry connector is top entry on the opposite board side.
  Reverses the pin ordering to reflect the mirroring."""
  def contents(self):
    super().contents()
    self.generator_param(self.length, self.pins.requested())

  def generate(self):
    super().generate()
    self.conn = self.Block(Fpc050Top(self.length))
    length = self.get(self.length)
    for pin in self.get(self.pins.requested()):
      self.connect(self.pins.append_elt(Passive.empty(), pin),
                   self.conn.pins.request(str(length - (int(pin) - 1))))


class HiroseFh12sh(Fpc050Bottom, FootprintPassiveConnector):
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


class Afc01(Fpc050Bottom, FootprintPassiveConnector, JlcPart):
  """Jushuo AFC01 series bottom-contact 0.5mm-pitch FPC connectors, with partial JLC numbers for some parts
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


class Afc07Top(Fpc050Top, FootprintPassiveConnector, JlcPart):
  """Jushuo AFC07 series slide-lock top-contact 0.5mm-pitch FPC connectors, with partial JLC numbers for some parts
  and re-using the probably-compatible but not-purpose-designed FH12 footprint."""
  _afc07_pins = set(range(4, 60+1))  # as listed by the part table
  allowed_pins = _afc07_pins.intersection(HiroseFh12sh._kicad_pins)
  PART_NUMBERS = {  # partial list of the ones currently used
    8: 'C262581',
    24: 'C262643',
    30: 'C262645',
  }
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    # TODO this isn't the intended hook and uses side effects, but it works for now
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return (f'Connector_FFC-FPC:Hirose_FH12-{length}S-0.5SH_1x{length:02d}-1MP_P0.50mm_Horizontal',
            "Jushuo", f"AFC07-S{length:02d}ECA-00")  # CA is packaging


class Te1734839(Fpc050Top, FootprintPassiveConnector):
  """TE x-1734839 FFC/FPC connector, 0.50mm pitch horizontal top contacts."""
  allowed_positions = range(5, 50)
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    return (f'Connector_FFC-FPC:TE_{length // 10}-1734839-{length % 10}_1x{length:02d}-1MP_P0.5mm_Horizontal',
            "TE Connectivity", f"{length // 10}-1734839-{length % 10}")


@abstract_block
class Fpc030(PassiveConnector):
  """Abstract base class for 0.30mm pitch (dual row, staggered)) FPC connectors."""


@abstract_block
class Fpc030Top(Fpc030):
  """Abstract base class for top-contact FPC connectors.
  IMPORTANT: the pin numbering scheme differs for top- and bottom-contact connectors."""


@abstract_block
class Fpc030Bottom(Fpc030):
  """Abstract base class for bottom-contact FPC connectors.
  IMPORTANT: the pin numbering scheme differs for top- and bottom-contact connectors."""


@abstract_block
class Fpc030TopBottom(Fpc030Bottom):
  """Abstract base class for top and bottom-contact FPC connectors. Bottom entry pin numbering is treated as canonical.
  To use in place of a top-contact connector, a flip is needed.
  IMPORTANT: the pin numbering scheme differs for top- and bottom-contact connectors."""


class HiroseFh35cshw(Fpc030TopBottom, FootprintPassiveConnector, JlcPart):
  """Hirose FH35C SHW FFC/FPC connector, 0.30mm pitch horizontal top/bottom contacts."""
  # positions the FH35C exists in, per datasheet
  _fh35c_pins = {9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 31, 33, 35, 37, 39, 41, 45, 49, 51, 55, 61}
  # positions for which there are KiCad footprints
  _kicad_pins = {31}
  allowed_pins = _fh35c_pins.intersection(_kicad_pins)
  PART_NUMBERS = {  # partial list of the ones currently used
    31: 'C424662',
  }
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    # TODO this isn't the intended hook and uses side effects, but it works for now
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return (f'edg:Hirose_FH35C-{length}S-0.3SHW_1x{length:02d}-1MP_P0.30mm_Horizontal',
            "Hirose", f"FH35C-{length}S-0.3SHW")
