from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Keystone5015(TestPoint, FootprintBlock, JlcPart):
  """Keystone 5015 / 5017 (difference in p/n is only from packaging) SMD test point"""
  def create_test_point(self, name: str) -> None:
    self.assign(self.lcsc_part, 'C238130')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'TP', 'TestPoint:TestPoint_Keystone_5015_Micro-Minature',
      {
        '1': self.io,  # also I2C SCL
      },
      value=name,
      mfr='Keystone', part='5015',
      datasheet='https://www.keyelco.com/userAssets/file/M65p55.pdf'
    )
