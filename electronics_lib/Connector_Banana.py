from electronics_abstract_parts import *


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


class Fcr7350(BananaSafetyJack, FootprintBlock):
  """FCR7350x PTH right-angle safety banana jack connector.
  x indicates the color code.

  Potentially footprint compatible with Pomona 73099 (~$9)?

  TODO: automatically support color code generation?
  """
  def contents(self):
    super().contents()
    self.footprint(
      'J', 'edg:CLIFF_FCR7350',
      {
        '1': self.port
      },
      mfr='CLIFF', part='FCR7350*'
    )
