from ..parts import *

from .JlcPartsResistorSmd import JlcPartsResistorSmd
from .JlcPartsMlcc import JlcPartsMlcc
from .JlcPartsInductor import JlcPartsInductor
from .JlcPartsFerriteBead import JlcPartsFerriteBead
from .JlcPartsDiode import JlcPartsDiode, JlcPartsZenerDiode
from .JlcPartsLed import JlcPartsLed
from .JlcPartsBjt import JlcPartsBjt
from .JlcPartsFet import JlcPartsFet, JlcPartsSwitchFet
from .JlcPartsPptcFuse import JlcPartsPptcFuse


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
        (SwitchFet, JlcPartsSwitchFet),
        (PptcFuse, JlcPartsPptcFuse),
        (FerriteBead, JlcPartsFerriteBead)
      ],
      class_values=[  # realistically only RCs are going to likely be basic parts
        (JlcPartsResistorSmd, ['require_basic_part'], True),
        (JlcPartsMlcc, ['require_basic_part'], True),
      ],
    )
