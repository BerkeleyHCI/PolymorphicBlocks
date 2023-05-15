from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ec11eWithSwitch(RotaryEncoderWithSwitch, JlcPart, FootprintBlock):
  """Generic EC11E PTH rotary with pushbutton switch.
  Default part is EC11E18244A5, with 1.5mm pushbutton travel, 36 detents (finest),
  but footprint should be compatible with other parts in the EC11E w/ switch series"""
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm',
      {
        'A': self.a,
        'B': self.b,
        'C': self.com,
        'S1': self.sw,
        'S2': self.com,
      },
      mfr='Alps Alpine', part='EC11E18244A5',
      datasheet='https://tech.alpsalpine.com/assets/products/catalog/ec11.en.pdf'
    )
    self.assign(self.lcsc_part, 'C255515')
    self.assign(self.actual_basic_part, False)


class Ec11j15WithSwitch(RotaryEncoderWithSwitch, JlcPart, FootprintBlock):
  """Generic EC11J15 PTH rotary with pushbutton switch.
  Default part is EC11J1525402, with 1.5mm pushbutton travel, 30 detents (finest),
  but footprint should be compatible with other parts in the EC11J15 w/ switch series"""
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'edg:RotaryEncoder_Alps_EC11J15-Switch',
      {
        'A': self.a,
        'B': self.b,
        'C': self.com,
        'S1': self.sw,
        'S2': self.com,
      },
      mfr='Alps Alpine', part='EC11J1525402',
      # datasheet / catalog doesn't appear to be available from the manufacturer like the PTH ersion
      datasheet='https://cdn-shop.adafruit.com/product-files/5454/5454_1837001.pdf'
    )
    self.assign(self.lcsc_part, 'C209762')
    self.assign(self.actual_basic_part, False)
