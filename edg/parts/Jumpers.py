from ..abstract_parts import *


class SolderJumperTriangular(Jumper, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'JP', 'Jumper:SolderJumper-2_P1.3mm_Open_TrianglePad1.0x1.5mm',
      {
        '1': self.a,
        '2': self.b
      }
    )
