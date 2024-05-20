from typing import Tuple, Callable, Mapping, List

from ...electronics_model import *
from .JlcPart import JlcPart


class KiCadJlcBlackbox(KiCadBlackboxBase, JlcPart, FootprintBlock, GeneratorBlock, InternalBlock):
  """Similar to KiCadBlackbox, but also supports the lcsc_part field using the symbol's 'JLCPCB Part #'.
  This can't extend KiCadBlackbox because KiCadBlackbox.block_from_symbol is non-compositional
  """
  @classmethod
  def block_from_symbol(cls, symbol: KiCadSymbol, lib: KiCadLibSymbol) -> \
      Tuple['KiCadJlcBlackbox', Callable[['KiCadJlcBlackbox'], Mapping[str, BasePort]]]:
    pin_numbers = [pin.number for pin in lib.pins]
    refdes_prefix = symbol.properties.get('Refdes Prefix', symbol.refdes.rstrip('0123456789?'))
    block_model = KiCadJlcBlackbox(
      pin_numbers, refdes_prefix, symbol.properties['Footprint'],
      kicad_part=symbol.lib, kicad_value=symbol.properties.get('Value', ''),
      kicad_datasheet=symbol.properties.get('Datasheet', ''),
      kicad_jlcpcb_part=symbol.properties['JLCPCB Part #'])  # required, no .get(...)
    def block_pinning(block: KiCadJlcBlackbox) -> Mapping[str, BasePort]:
      return {pin: block.ports.request(pin) for pin in pin_numbers}
    return block_model, block_pinning

  @init_in_parent
  def __init__(self, kicad_pins: ArrayStringLike, kicad_refdes_prefix: StringLike, kicad_footprint: StringLike,
               kicad_part: StringLike, kicad_value: StringLike, kicad_datasheet: StringLike,
               kicad_jlcpcb_part: StringLike):
    super().__init__()
    self.ports = self.Port(Vector(Passive()), optional=True)
    self.kicad_refdes_prefix = self.ArgParameter(kicad_refdes_prefix)
    self.kicad_footprint = self.ArgParameter(kicad_footprint)
    self.kicad_part = self.ArgParameter(kicad_part)
    self.kicad_value = self.ArgParameter(kicad_value)
    self.kicad_datasheet = self.ArgParameter(kicad_datasheet)
    self.assign(self.lcsc_part, kicad_jlcpcb_part)
    self.assign(self.actual_basic_part, False)  # assumed

    self.kicad_pins = self.ArgParameter(kicad_pins)
    self.generator_param(self.kicad_pins)

  def generate(self):
    super().generate()
    mapping = {pin_name: self.ports.append_elt(Passive(), pin_name)
               for pin_name in self.get(self.kicad_pins)}
    self.ports.defined()
    self.footprint(self.kicad_refdes_prefix, self.kicad_footprint, mapping,
                   part=self.kicad_part, value=self.kicad_value, datasheet=self.kicad_datasheet)
