from electronics_model import *
from .AbstractDebugHeaders import SwdCortexTargetWithSwoTdiConnector
from .IoController import IoController


@abstract_block
class IoControllerWithSwdTargetConnector(IoController):
  """An IoController with a SWD programming header and optional SWO and TDI pins that
  can be assigned to any microcontroller pin.

  This defines the interface for the SWO and TDI pin spec (passed to the pin assignment),
  and instantiates a SWD target with connected power and ground. SWD must be connected by
  the subclass."""
  @init_in_parent
  def __init__(self, swd_swo_pin: StringLike = "NC", swd_tdi_pin: StringLike = "NC"):
    super().__init__()
    self.swd = self.Block(SwdCortexTargetWithSwoTdiConnector())
    self.connect(self.swd.pwr, self.pwr)
    self.connect(self.swd.gnd, self.gnd)

    self.swd_swo_pin = self.ArgParameter(swd_swo_pin)
    self.swd_tdi_pin = self.ArgParameter(swd_tdi_pin)
