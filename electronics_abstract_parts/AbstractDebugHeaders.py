from .Categories import ProgrammingConnector
from electronics_model import *


@abstract_block
class SwdCortexTargetConnector(ProgrammingConnector):
  """Programming header with power and SWD (SWCLK/SWDIO/RESET) pins."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])  # in practice these are commonly used as sources
    self.gnd = self.Port(Ground.empty(), [Common])
    self.swd = self.Port(SwdHostPort.empty(), [Output])


class SwdCortexTargetConnectorReset(BlockInterfaceMixin[SwdCortexTargetConnector]):
  """Mixin for SWD connectors with adding the optional reset pin"""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.reset = self.Port(DigitalSource.empty())


class SwdCortexTargetConnectorSwo(BlockInterfaceMixin[SwdCortexTargetConnector]):
  """Mixin for SWD connectors with adding the optional SWO pin"""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.swo = self.Port(DigitalBidir.empty(), optional=True)


class SwdCortexTargetConnectorTdi(BlockInterfaceMixin[SwdCortexTargetConnector]):
  """Mixin for SWD connectors with adding the NONSTANDARD TDI pin (where pins are shared with JTAG)"""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.tdi = self.Port(DigitalBidir.empty(), optional=True)
