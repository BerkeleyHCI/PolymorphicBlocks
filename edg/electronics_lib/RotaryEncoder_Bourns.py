from ..electronics_abstract_parts import *


class Pec11s(RotaryEncoderSwitch, RotaryEncoder, FootprintBlock):
  """Bourns PEC11S SMD rotary with pushbutton switch.
  Default part is PEC11S-929K-S0015, but entire series is footprint-compatible.
  While the copper pattern is compatible with the EC11J15, there is a different mounting boss."""
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'edg:RotaryEncoder_Bourns_PEC11S',
      {
        'A': self.a,
        'B': self.b,
        'C': self.com,
        'S1': self.sw,
        'S2': self.com,
      },
      mfr='Bourns', part='PEC11S-929K-S0015',
      datasheet='https://www.bourns.com/docs/Product-Datasheets/PEC11S.pdf'
    )
