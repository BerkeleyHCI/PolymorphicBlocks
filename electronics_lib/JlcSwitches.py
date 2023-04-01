from electronics_abstract_parts import *
from .JlcPart import JlcPart


class JlcSwitch(TactileSwitch, JlcPart, FootprintBlock):
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Button_Switch_SMD:SW_SPST_SKQG_WithoutStem',  # 3.9mm x 2.9mm
      {
        '1': self.b,
        '2': self.a,
      },
      part='5.1mm switch'
    )
    self.assign(self.lcsc_part, 'C318884')
    self.assign(self.actual_basic_part, True)
