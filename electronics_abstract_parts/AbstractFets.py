from electronics_model import *
from .Categories import *


@abstract_block
class Fet(DiscreteSemiconductor):
  """Base class for untyped MOSFETs

  MOSFET equations
  - https://inst.eecs.berkeley.edu/~ee105/fa05/handouts/discussions/Discussion5.pdf (cutoff/linear/saturation regions)

  Potentially useful references for selecting FETs:
  - Toshiba application_note_en_20180726, Power MOSFET Selecting MOSFFETs and Consideration for Circuit Design
  - https://www.vishay.com/docs/71933/71933.pdf, MOSFET figures of merit (which don't help in choosing devices), Rds,on * Qg
  - https://www.allaboutcircuits.com/technical-articles/choosing-the-right-transistor-understanding-low-frequency-mosfet-parameters/
  - https://www.allaboutcircuits.com/technical-articles/choosing-the-right-transistor-understanding-dynamic-mosfet-parameters/
  """
  @init_in_parent
  def __init__(self, drain_voltage: RangeLike = RangeExpr(), drain_current: RangeLike = RangeExpr(),
               gate_voltage: RangeLike = RangeExpr(), rds_on: RangeLike = RangeExpr(),
               gate_charge: RangeLike = RangeExpr(), power: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.source = self.Port(Passive())
    self.drain = self.Port(Passive())
    self.gate = self.Port(Passive())

    self.drain_voltage = self.Parameter(RangeExpr(drain_voltage))
    self.drain_current = self.Parameter(RangeExpr(drain_current))
    self.gate_voltage = self.Parameter(RangeExpr(gate_voltage))
    self.rds_on = self.Parameter(RangeExpr(rds_on))
    self.gate_charge = self.Parameter(RangeExpr(gate_charge))
    self.power = self.Parameter(RangeExpr(power))


@abstract_block
class PFet(Fet):
  """Base class for PFETs. Drain voltage, drain current, and gate voltages are positive (absolute).
  """
  pass


@abstract_block
class NFet(Fet):
  """Base class for NFETs. Drain voltage, drain current, and gate voltage are positive (absolute).
  """
  pass


@abstract_block
class SwitchFet(Fet):
  """FET that switches between an off state and on state, not operating in the linear region except for rise/fall time.
  Ports remain untyped. TODO: are these limitations enough to type the ports? maybe except for the output?
  Models static and switching power dissipation. Gate charge and power parameters are optional, they will be the
  stricter of the explicit input or model-derived parameters."""
  # TODO ideally this would just instantaite a Fet internally, but the parts selection becomes more complex b/c
  # paramters are cross-dependent
  @init_in_parent
  def __init__(self, frequency: RangeLike = RangeExpr(), drive_current: RangeLike = RangeExpr(), **kwargs) -> None:
    super().__init__(**kwargs)

    self.frequency = self.Parameter(RangeExpr(frequency))
    self.drive_current = self.Parameter(RangeExpr(drive_current))  # positive is turn-on drive, negative is turn-off drive


@abstract_block
class SwitchPFet(SwitchFet, PFet):
  """Base class for PFETs. Drain voltage, drain current, and gate voltages are positive (absolute).
  """
  pass


@abstract_block
class SwitchNFet(SwitchFet, NFet):
  """Base class for NFETs. Drain voltage, drain current, and gate voltage are positive (absolute).
  """
  pass
