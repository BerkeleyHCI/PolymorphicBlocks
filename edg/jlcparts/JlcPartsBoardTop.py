from ..parts import *
from ..jlcparts import *


class JlcPartsRefinements(DesignTop):
  """List of refinements that use JlcParts - mix this into a BoardTop"""
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Resistor, JlcPartsResistorSmd),
        (Capacitor, JlcPartsMlcc),
        (Inductor, JlcPartsInductor),
        (Diode, JlcPartsDiode),
        (ZenerDiode, JlcPartsZenerDiode),
        (Led, JlcPartsLed),
        (Bjt, JlcPartsBjt),
        (Fet, JlcPartsFet),
        (SwitchFet, JlcSwitchFet),
        (PptcFuse, JlcPartsPptcFuse),
        (FerriteBead, JlcPartsFerriteBead)
      ]
    )