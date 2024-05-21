from ..abstract_parts import *
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


class Smt0606RgbLed(RgbLedCommonAnode, JlcPart, FootprintBlock):
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


class Smt0404RgbLed(RgbLedCommonAnode, JlcPart, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_SMD:LED_Lumex_SML-LX0404SIUPGUSB',
      {
        '1': self.a,
        '2': self.k_red,
        '3': self.k_green,
        '4': self.k_blue,
      },
      mfr='Foshan NationStar Optoelectronics', part='FC-B1010RGBT-HG'
    )
    self.assign(self.lcsc_part, 'C158099')
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
