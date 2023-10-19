from typing import List

from electronics_model import *
from .AbstractDebugHeaders import SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo, \
  SwdCortexTargetConnectorTdi
from .IoController import IoController
from .IoControllerExportable import BaseIoControllerExportable


@non_library
class IoControllerWithSwdTargetConnector(IoController, BaseIoControllerExportable):
  """An IoController with a SWD programming header and optional SWO and TDI pins that
  can be assigned to any microcontroller pin.

  This defines the interface for the SWO and TDI pin spec (passed to the pin assignment),
  and instantiates a SWD target with connected power and ground. SWD must be connected by
  the subclass."""
  @init_in_parent
  def __init__(self, swd_swo_pin: StringLike = "NC", swd_tdi_pin: StringLike = "NC", swd_connect_reset: BoolLike = True):
    super().__init__()
    self.swd_swo_pin = self.ArgParameter(swd_swo_pin)
    self.swd_tdi_pin = self.ArgParameter(swd_tdi_pin)
    self.swd_connect_reset = self.ArgParameter(swd_connect_reset)
    self.generator_param(self.swd_swo_pin, self.swd_tdi_pin, self.swd_connect_reset)
    self.swd_node = self.connect()  # connect this internal node to the microcontroller
    self.reset_node = self.connect()  # connect this internal node to the microcontroller

  def contents(self):
    super().contents()
    self.swd = self.Block(SwdCortexTargetConnector())
    self.connect(self.swd.gnd, self.gnd)
    self.connect(self.swd.pwr, self.pwr)
    self.connect(self.swd_node, self.swd.swd)

  def _inner_pin_assigns(self, assigns: List[str]) -> List[str]:
    assigns = super()._inner_pin_assigns(assigns)
    if self.get(self.swd_swo_pin) != 'NC':
      assigns.append(f'swd_swo={self.get(self.swd_swo_pin)}')
    if self.get(self.swd_tdi_pin) != 'NC':
      assigns.append(f'swd_tdi={self.get(self.swd_tdi_pin)}')
    return assigns

  def generate(self):
    super().generate()
    if self.get(self.swd_swo_pin) != 'NC':
      self.connect(self.ic.gpio.request('swd_swo'), self.swd.with_mixin(SwdCortexTargetConnectorSwo()).swo)
    if self.get(self.swd_tdi_pin) != 'NC':
      self.connect(self.ic.gpio.request('swd_tdi'), self.swd.with_mixin(SwdCortexTargetConnectorTdi()).tdi)
    if self.get(self.swd_connect_reset):  # reset commonly connected but not required by SWD
      self.connect(self.reset_node, self.swd.with_mixin(SwdCortexTargetConnectorReset()).reset)
