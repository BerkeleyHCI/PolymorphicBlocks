from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Keystone5015(TestPoint, FootprintBlock, JlcPart):
  """Keystone 5015 / 5017 (difference in p/n is only from packaging) SMD test point"""
  def contents(self) -> None:
    super().contents()
    self.assign(self.lcsc_part, 'C238130')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'TP', 'TestPoint:TestPoint_Keystone_5015_Micro-Minature',
      {
        '1': self.io,
      },
      value=self.tp_name,
      mfr='Keystone', part='5015',
      datasheet='https://www.keyelco.com/userAssets/file/M65p55.pdf'
    )


class CompactKeystone5015(TestPoint, FootprintBlock, JlcPart):
  """Keystone 5015 / 5017 but with an experimental compact footprint"""
  def contents(self) -> None:
    super().contents()
    self.assign(self.lcsc_part, 'C238130')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'TP', 'edg:TestPoint_TE_RCT_0805',
      {
        '1': self.io,
      },
      value=self.tp_name,
      mfr='Keystone', part='5015',
      datasheet='https://www.keyelco.com/userAssets/file/M65p55.pdf'
    )


class Keystone5000(TestPoint, FootprintBlock, JlcPart):
  """Keystone 5000-5004 series PTH test mini points"""
  def contents(self) -> None:
    super().contents()
    self.assign(self.lcsc_part, 'C238122')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'TP', 'TestPoint:TestPoint_Keystone_5000-5004_Miniature',
      {
        '1': self.io,
      },
      value=self.tp_name,
      mfr='Keystone', part='5001',
      datasheet='https://www.keyelco.com/userAssets/file/M65p56.pdf'
    )
