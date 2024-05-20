from deprecated import deprecated
from electronics_abstract_parts import *

@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class Outline_Pn1332(Mechanical, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      '', 'calisco:Outline_150mm_70mm_PNX-91432',
      {},
      mfr='Bud Industries', part='PN-1332-CMB',
      datasheet='http://www.budind.com/pdf/hbpn1332.pdf'
    )


@abstract_block
@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class MountingHole(Mechanical, FootprintBlock):
  FOOTPRINT: str = ''
  VALUE: str = ''
  def __init__(self):
    super().__init__()
    self.pad = self.Port(Passive(), optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'H', self.FOOTPRINT,
      {},
      value=self.VALUE
    )


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class MountingHole_NoPad_M2_5(MountingHole):
  FOOTPRINT = 'MountingHole:MountingHole_2.5mm'
  VALUE = 'M2.5'


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class MountingHole_M2_5(MountingHole):
  FOOTPRINT = 'MountingHole:MountingHole_2.7mm_M2.5_Pad_Via'
  VALUE = 'M2.5'


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class MountingHole_M3(MountingHole):
  FOOTPRINT = 'MountingHole:MountingHole_3.2mm_M3_Pad_Via'
  VALUE = 'M3'


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class MountingHole_M4(MountingHole):
  FOOTPRINT = 'MountingHole:MountingHole_4.3mm_M4_Pad_Via'
  VALUE = 'M4'
