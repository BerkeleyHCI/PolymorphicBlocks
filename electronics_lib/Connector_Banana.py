from electronics_abstract_parts import *


"""
TODO: possibly support other safety banana jack models:
- CT3149 (12mm short pin), CT3150 (21mm long pin) - possibly used as SMD
- CLIFF Electronics FCR7350* ($5), through-hole socket
- Pomona 73099 (~$9)
  (is this footprint compatible with the CLIFF device?) 
"""


class Ct3151(BananaSafetyJack, FootprintBlock):
  """CT3151-x PTH right-angle safety banana jack connector.
  x indicates the color code.

  TODO: automatically support color code generation?
  """
  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector:CalTest_CT3151',
      {
        '1': self.port
      },
      mfr='CalTest', part='CT3151-*'
    )
