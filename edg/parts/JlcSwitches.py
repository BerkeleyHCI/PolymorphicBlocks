from ..abstract_parts import *
from .JlcPart import JlcPart


class JlcSwitch(TactileSwitch, JlcPart, FootprintBlock):
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Button_Switch_SMD:SW_SPST_SKQG_WithoutStem',  # 3.9mm x 2.9mm
      {
        '1': self.sw,
        '2': self.com,
      },
      part='5.1mm switch'
    )
    self.assign(self.lcsc_part, 'C318884')
    self.assign(self.actual_basic_part, True)


class Skrtlae010(TactileSwitch, JlcPart, FootprintBlock):
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010',
      {
        '1': self.com,
        '2': self.sw,
      },
      mfr='Alps Alpine', part='SKRTLAE010',
      datasheet='https://www.mouser.com/datasheet/2/15/SKRT-1370725.pdf'
    )
    self.assign(self.lcsc_part, 'C110293')
    self.assign(self.actual_basic_part, False)
