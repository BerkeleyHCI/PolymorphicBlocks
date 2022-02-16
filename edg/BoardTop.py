from electronics_lib import *


class BoardTop(DesignTop):
  """Design top with refinements for intermediate-level (0603+ SMD), hand-solderable components."""
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Resistor, ChipResistor),
        (Capacitor, SmtCeramicCapacitor),
        (Inductor, SmtInductor),
        (Switch, SmtSwitch),
        (Diode, SmtDiode),
        (Led, SmtLed),
        (RgbLedCommonAnode, SmtRgbLed),
        (ZenerDiode, SmtZenerDiode),
        (NFet, SmtNFet),
        (PFet, SmtPFet),
        (SwitchNFet, SmtSwitchNFet),
        (SwitchPFet, SmtSwitchPFet)
      ]
    )
