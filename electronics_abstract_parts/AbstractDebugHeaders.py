from .Categories import ProgrammingConnector
from electronics_model import *


@abstract_block
class SwdCortexTargetConnector(ProgrammingConnector):
  """Programming header with power and SWD (SWCLK/SWDIO/RESET) pins."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])  # in practice these are commonly used as sources
    self.gnd = self.Port(Ground(), [Common])
    self.swd = self.Port(SwdHostPort(), [Output])


@abstract_block
class SwdCortexTargetWithSwoTdiConnector(SwdCortexTargetConnector):
  """SWD programming header (power + SWD) with additional optional and generic-digital
  SWO (optional SWD pin) and TDI (if a JTAG header is used) pins which can be used as GPIOs
  for side-channel data like a supplementary UART console."""
  def __init__(self) -> None:
    super().__init__()

    self.swo = self.Port(DigitalBidir(), optional=True)
    self.tdi = self.Port(DigitalBidir(), optional=True)
