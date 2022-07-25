from electronics_abstract_parts import *
from .JlcPart import JlcPart


class SmtLed(Led, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_SMD:LED_0603_1608Metric',
      {
        '2': self.a,
        '1': self.k,
      },
      part='LED',
    )


class ThtLed(Led, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_THT:LED_D5.0mm',
      {
        '2': self.a,
        '1': self.k,
      },
      part='LED',
    )


class SmtRgbLed(RgbLedCommonAnode, JlcPart, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_SMD:LED_LiteOn_LTST-C19HE1WT',
      {  # ABGR configuration - also pins 1/2 and 3/4 are swapped on this pattern
        '2': self.a,
        '1': self.k_blue,
        '4': self.k_green,
        '3': self.k_red,
      },
      mfr='Everlight Electronics Co Ltd', part='EAST1616RGBB2'
    )
    self.assign(self.lcsc_part, 'C264517')
    self.assign(self.actual_basic_part, False)


class ThtRgbLed(RgbLedCommonAnode, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_THT:LED_D5.0mm-4_RGB_Staggered_Pins',
      {  # RAGB configuration
        '1': self.k_red,
        '2': self.a,
        '3': self.k_green,
        '4': self.k_blue,
      },
      mfr='Sparkfun', part='COM-09264'
    )
