from electronics_lib import *


class BaseBoardTop(DesignTop):
  """Design top with refinements for intermediate-level (0603+ SMD), hand-solderable components."""
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Resistor, GenericChipResistor),
        (Capacitor, GenericMlcc),
        (Inductor, DigikeyInductor),
        (Switch, SmtSwitch),
        (Diode, DigikeySmtDiode),
        (Led, SmtLed),
        (RgbLedCommonAnode, SmtRgbLed),
        (ZenerDiode, DigikeySmtZenerDiode),
        (Fet, DigikeyFet),
        (SwitchFet, DigikeySwitchFet),
        (Crystal, DigikeyCrystal),

        (UsbEsdDiode, Tpd2e009),
        (TestPoint, Keystone5015),

        (SwdCortexTargetWithTdiConnector, SwdCortexTargetHeader),
      ],
    )


class BoardTop(BaseBoardTop):
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_values=[
        (JlcPart, ['require_basic_part'], False),  # for non-JLC boards, we don't care about this
      ]
    )


class JlcBoardTop(BaseBoardTop):
  """Design top with refinements to use parts from JLC's assembly service and including the tooling holes"""
  def contents(self):
    super().contents()
    self.jlc_th1 = self.Block(JlcToolingHole())
    self.jlc_th2 = self.Block(JlcToolingHole())
    self.jlc_th3 = self.Block(JlcToolingHole())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Resistor, JlcResistor),
        (Capacitor, JlcCapacitor),
        (Inductor, JlcInductor),
        (ResistorArray, JlcResistorArray),

        (Led, JlcLed),
        (ZenerDiode, JlcZenerDiode),
        (Diode, JlcDiode),
        (Fet, JlcFet),

        (UsbEsdDiode, Esda5v3l),
      ],
    )
