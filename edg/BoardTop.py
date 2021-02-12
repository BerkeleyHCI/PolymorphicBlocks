from edg_core import DesignTop
from electronics_lib import *


class BoardTop(DesignTop):
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
