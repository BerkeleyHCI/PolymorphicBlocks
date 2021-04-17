from electronics_lib import *
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE


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


class SimpleBoardTop(BoardTop):
  """Temporary / hackaround design top with explicit empty pin assignments
  (automatically allocate) for microcontrollers, for simplicity of tutorials."""
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_values=[
        (Lpc1549_48, ['pin_assigns'], ''),
        (Lpc1549_64, ['pin_assigns'], ''),
        (Stm32f103_48, ['pin_assigns'], ''),
        (Nucleo_F303k8, ['pin_assigns'], ''),
        (Adafruit_ItsyBitsy_BLE, ['pin_assigns'], ''),
      ]
    )
