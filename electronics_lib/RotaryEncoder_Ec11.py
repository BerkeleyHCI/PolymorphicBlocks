from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ec11eWithSwitch(RotaryEncoderWithSwitch, JlcPart, FootprintBlock):
  """Generic EC11E PTH rotary with pushbutton switch.
  Default part is EC11E18244A5, with 1.5mm pushbutton travel, 36 detents,
  but footprint should be compatible with other parts in the EC11E w/ switch series"""
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm',
      {
        'A': self.a,
        'B': self.b,
        'C': self.c,
        'S1': self.sw,
        'S2': self.c,
      },
      mfr='Alps Alpine', part='EC11E18244A5',
      datasheet='https://tech.alpsalpine.com/assets/products/catalog/ec11.en.pdf'
    )
    self.assign(self.lcsc_part, 'C255515')
    self.assign(self.actual_basic_part, False)
