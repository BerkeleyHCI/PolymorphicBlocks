from electronics_abstract_parts import *


class TeRc(TestPoint, FootprintBlock, GeneratorBlock):
  """TE Type RC 0603/0805/1206 SMD test point"""
  _PART_TABLE = {  # size designator -> part number, footprint
    '0603': ('RCU-0C', 'edg:TestPoint_TE_RCU_0603'),
    '0805': ('RCT-0C', 'edg:TestPoint_TE_RCT_0805'),
    '1206': ('RCS-0C', 'edg:TestPoint_TE_RCS_RCW_1206'),
  }

  @init_in_parent
  def __init__(self, size: StringLike = '0603'):
    super().__init__()
    self.generator(self.generate, size)

  def generate(self, size: str) -> None:
    super().contents()
    if size in self._PART_TABLE:
      part, footprint = self._PART_TABLE[size]
      self.footprint(
        'TP', footprint,
        {
          '1': self.io,
        },
        value=self.tp_name,
        mfr='TE Connectivity', part=part,
        datasheet='https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=1773266&DocType=DS&DocLang=English'
      )
    else:
      allowed_sizes = ', '.join(self._PART_TABLE.keys())
      self.require(False, f"invalid size designator '{size}', must be in ({allowed_sizes})")
