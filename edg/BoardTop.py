from electronics_lib import *


class BaseBoardTop(DesignTop):
  """Design top with refinements for intermediate-level (0603+ SMD), hand-solderable components."""
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.refdes_prefix = self.Parameter(StringExpr())
    self.assign(self.refdes_prefix, "")  # override with refinements

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Resistor, GenericChipResistor),
        (ResistorArray, JlcResistorArray),  # TODO: replace with generic resistor array
        (Capacitor, GenericMlcc),
        (Inductor, JlcInductor),  # TODO: replace with generic inductor
        (Switch, SmtSwitch),
        (RotaryEncoder, Ec11j15WithSwitch),
        (Diode, JlcDiode),  # TODO: replace with non-distributor parts list
        (ZenerDiode, JlcZenerDiode),  # TODO: replace with non-distributor parts list
        (Bjt, JlcBjt),  # TODO: replace with non-distributor parts list
        (Fet, JlcFet),  # TODO: replace with non-distributor parts list
        (SwitchFet, JlcSwitchFet),  # TODO: replace with non-distributor parts list
        (Led, SmtLed),
        (RgbLedCommonAnode, SmtRgbLed),
        (Crystal, JlcCrystal),  # TODO: replace with non-distributor parts list
        (Oscillator, JlcOscillator),  # TODO: replace with non-distributor parts list

        (Jumper, SolderJumperTriangular),
        (IndicatorSinkLed, IndicatorSinkLedResistor),

        (Fpc050Bottom, HiroseFh12sh),
        (UsbEsdDiode, Tpd2e009),
        (CanEsdDiode, Pesd1can),
        (TestPoint, TeRc),

        (SwdCortexTargetConnector, SwdCortexTargetHeader),

        (SpiMemory, W25q),

        (Speaker, ConnectorSpeaker),
      ], class_values=[
        (SmdStandardPackage, ['smd_min_package'], '0603'),
      ]
    )


class BoardTop(BaseBoardTop):
  pass


class SimpleBoardTop(BaseBoardTop):
  """A BoardTop with refinements that make getting started easier but may not be desirable everywhere."""
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
      class_values=[
        (JlcInductor, ['manual_frequency_rating'], Range.all()),
      ],
    )
    
    
class JlcToolingHoles(Mechanical, Block):
  def contents(self):
    super().contents()
    self.th1 = self.Block(JlcToolingHole())
    self.th2 = self.Block(JlcToolingHole())
    self.th3 = self.Block(JlcToolingHole())


class JlcBoardTop(BaseBoardTop):
  """Design top with refinements to use parts from JLC's assembly service and including the tooling holes"""
  def contents(self):
    super().contents()
    self.jlc_th = self.Block(JlcToolingHoles())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Resistor, JlcResistor),
        (Capacitor, JlcCapacitor),
        (Inductor, JlcInductor),
        (FerriteBead, JlcFerriteBead),
        (PptcFuse, JlcPptcFuse),
        (ResistorArray, JlcResistorArray),
        (Crystal, JlcCrystal),
        (Oscillator, JlcOscillator),

        (Switch, JlcSwitch),
        (Led, JlcLed),
        (ZenerDiode, JlcZenerDiode),
        (Diode, JlcDiode),
        (Bjt, JlcBjt),
        (Fet, JlcFet),

        (Fpc050Bottom, Afc01),
        (Fpc050Top, Afc07Top),
        (Fpc030Bottom, HiroseFh35cshw),
        (UsbEsdDiode, Pesd5v0x1bt),
        (Opamp, Lmv321),
        (SpiMemory, W25q),  # 128M version is a basic part
        (TestPoint, Keystone5015),  # this is larger, but is part of JLC's parts inventory
      ],
      class_values=[  # realistically only RCs are going to likely be basic parts
        (JlcResistor, ['require_basic_part'], True),
        (JlcCapacitor, ['require_basic_part'], True),
      ],
    )
