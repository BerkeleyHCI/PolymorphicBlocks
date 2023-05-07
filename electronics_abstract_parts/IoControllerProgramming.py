from electronics_model import *
from .AbstractDebugHeaders import SwdCortexTargetWithSwoTdiConnector
from .IoController import BaseIoControllerExportable, IoController


@abstract_block
class IoControllerWithSwdTargetConnector(IoController, BaseIoControllerExportable):
  """An IoController with a SWD programming header and optional SWO and TDI pins that
  can be assigned to any microcontroller pin.

  This defines the interface for the SWO and TDI pin spec (passed to the pin assignment),
  and instantiates a SWD target with connected power and ground. SWD must be connected by
  the subclass.

  TODO: has-swd should be a mixin"""
  @init_in_parent
  def __init__(self, swd_swo_pin: StringLike = "NC", swd_tdi_pin: StringLike = "NC"):
    super().__init__()
    self.swd_swo_pin = self.ArgParameter(swd_swo_pin)
    self.swd_tdi_pin = self.ArgParameter(swd_tdi_pin)
    self.generator_param(self.swd_swo_pin, self.swd_tdi_pin)
    self.swd_node = self.connect()  # connect this internal node to the microcontroller

  def contents(self):
    super().contents()
    self.swd = self.Block(SwdCortexTargetWithSwoTdiConnector())
    self.connect(self.swd_node, self.swd.swd)
    self.connect(self.swd.pwr, self.pwr)
    self.connect(self.swd.gnd, self.gnd)

  def _inner_pin_assigns(self) -> list[str]:
    pin_assigns = super()._inner_pin_assigns()
    if self.get(self.swd_swo_pin) != 'NC':
      pin_assigns.append(f'swd_swo={self.get(self.swd_swo_pin)}')
    if self.get(self.swd_tdi_pin) != 'NC':
      pin_assigns.append(f'swd_tdi={self.get(self.swd_tdi_pin)}')
    return pin_assigns

  def generate(self):
    super().generate()
    if self.get(self.swd_swo_pin) != 'NC':
      self.connect(self.ic.gpio.request('swd_swo'), self.swd.swo)
    if self.get(self.swd_tdi_pin) != 'NC':
      self.connect(self.ic.gpio.request('swd_tdi'), self.swd.tdi)
