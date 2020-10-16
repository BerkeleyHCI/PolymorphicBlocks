from electronics_abstract_parts import *


class SmtSwitch(Switch, CircuitBlock):
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Button_Switch_SMD:SW_Push_SPST_NO_Alps_SKRK',  # 3.9mm x 2.9mm
      # 'Button_Switch_SMD:SW_SPST_CK_KXT3',  # 3.0mm x 2.0mm
      {
        '1': self.b,
        '2': self.a,
      },
      part='3.9x2.9mm Switch'
    )

# TODO right-angle-ness should be a layout-level decision?
class SmtSwitchRa(Switch, CircuitBlock):
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Button_Switch_SMD:SW_SPST_EVQP7C',  # 3.5mm x 2.9/3.55mm w/ boss
      {
        '1': self.b,
        '2': self.a,
      },
      part='EVQ-P7C01P'
    )
