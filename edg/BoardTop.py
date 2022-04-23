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
        (SwitchPFet, SmtSwitchPFet),
        (TestPoint, Keystone5015),

        (SwdCortexTargetWithTdiConnector, SwdCortexTargetHeader),
      ]
    )


class JlcBoardTop(BoardTop):
  """Design top with refinements to use parts from JLC's assembly service and including the tooling holes"""
  def contents(self):
    super().contents()
    self.jlc_th1 = self.Block(JlcToolingHole())
    self.jlc_th2 = self.Block(JlcToolingHole())
    self.jlc_th3 = self.Block(JlcToolingHole())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Capacitor, JlcCapacitor),
        (Resistor, JlcResistor),
        (ZenerDiode, JlcZenerDiode),
      ]
    )
