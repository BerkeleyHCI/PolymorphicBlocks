from electronics_abstract_parts import *
from .JlcFootprint import JlcFootprint


class Keystone5015(TestPoint, FootprintBlock, JlcFootprint):
  """Keystone 5015 / 5017 (difference in p/n is only from packaging) SMD test point"""
  def create_test_point(self, name: str) -> None:
    self.assign(self.lcsc_part, 'C238130')
    self.footprint(
      'TP', 'TestPoint:TestPoint_Keystone_5015_Micro-Minature',
      {
        '1': self.io,  # also I2C SCL
      },
      mfr='Keystone', part='5015',
      datasheet='https://www.keyelco.com/userAssets/file/M65p55.pdf'
    )
