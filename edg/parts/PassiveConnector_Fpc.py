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
  _afc01_pins = set(range(4, 60 + 1))  # as listed by the part table
  allowed_pins = _afc01_pins.intersection(HiroseFh12sh._kicad_pins)
  PART_NUMBERS = {  # partial list of the ones currently used
    # including -FCC (tube) and -FCA (T&R) suffix
    4: 'C262260',  # FCC
    5: 'C262654',  # FCA
    6: 'C262262',  # FCC
    7: 'C262263',  # FCC
    8: 'C262657',  # also C262264 for -FCC
    9: 'C262265',  # FCC
    10: 'C262266',  # FCC
    12: 'C262268',  # FCC
    13: 'C262269',  # FCC
    14: 'C577443',  # FCC
    15: 'C262664',  # also C262271 for -FCC
    16: 'C262272',  # FCC
    18: 'C262273',  # FCC
    20: 'C262274',  # FCC
    22: 'C262275',  # FCC
    24: 'C262669',  # also C262276 for -FCC
    26: 'C262277',  # FCC
    28: 'C262278',  # FCC
    30: 'C262671',  # also C262279 for -FCC
    32: 'C262280',  # FCC
    36: 'C262673',  # FCA
    40: 'C262674',  # also C262282 for FCC
    45: 'C13507',  # FCC
    50: 'C262676',  # also C262284 for FCC
    54: 'C262677',  # FCA
    60: 'C2918970'  # FCC
  }

  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    # TODO this isn't the intended hook and uses side effects, but it works for now
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return (f'Connector_FFC-FPC:Hirose_FH12-{length}S-0.5SH_1x{length:02d}-1MP_P0.50mm_Horizontal',
            "Jushuo", f"AFC01-S{length:02d}FC*-00")  # CA is T&R packaging


class Afc07Top(Fpc050Top, FootprintPassiveConnector, JlcPart):
  """Jushuo AFC07 series slide-lock top-contact 0.5mm-pitch FPC connectors, with partial JLC numbers for some parts
  and re-using the probably-compatible but not-purpose-designed FH12 footprint."""
  _afc07_pins = set(range(4, 60 + 1))  # as listed by the part table
  allowed_pins = _afc07_pins.intersection(HiroseFh12sh._kicad_pins)
  PART_NUMBERS = {  # partial list of the ones currently used
    # including -ECC (tube) and -ECA (T&R) suffix
    4: 'C2764271',  # ECA
    5: 'C262230',  # also C262578 for -ECA
    6: 'C413943',  # ECC
    7: 'C262232',  # ECC
    8: 'C262581',  # also C11084 for -ECC
    10: 'C262583',  # ECA
    12: 'C11086',  # ECC
    13: 'C262238',  # ECC
    14: 'C11087',  # also C262587 for -ECA
    15: 'C262240',  # also C262588 for -ECA
    16: 'C11088',  # ECC
    18: 'C11089',  # also C2840708 for -ECC
    20: 'C262641',  # ECA
    22: 'C262642',  # also C11091 for -ECC
    24: 'C262643',  # also C11092 for -ECC
    26: 'C262644',  # also C11094 for -ECC
    28: 'C2886796',  # ECA
    30: 'C262645',  # also C262645 for -ECA
    32: 'C11096',  # ECC
    34: 'C262252',  # ECC
    36: 'C262254',  # ECC
    40: 'C262648',  # also C11097 for -ECC
    45: 'C262256',  # ECC
    50: 'C262650',  # also C11098 for -ECC
    54: 'C262258',  # also C2691600 for -ECC
    60: 'C262652'  # ECA
  }
  def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
    # TODO this isn't the intended hook and uses side effects, but it works for now
    self.assign(self.lcsc_part, self.PART_NUMBERS[length])
    self.assign(self.actual_basic_part, False)
    return (f'Connector_FFC-FPC:Hirose_FH12-{length}S-0.5SH_1x{length:02d}-1MP_P0.50mm_Horizontal',
            "Jushuo", f"AFC07-S{length:02d}EC*-00")  # CA is packaging


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
