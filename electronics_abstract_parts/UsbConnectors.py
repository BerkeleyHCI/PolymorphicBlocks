from electronics_model import *
from .Categories import Connector, TvsDiode


@abstract_block
@non_library
class UsbConnector(Connector):
  """USB connector of any generation / type."""
  USB2_VOLTAGE_RANGE = (4.75, 5.25)*Volt
  USB2_CURRENT_LIMITS = (0, 0.5)*Amp


@abstract_block
class UsbHostConnector(UsbConnector):
  """Abstract base class for a USB 2.0 device-side port connector"""
  def __init__(self) -> None:
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), optional=True)
    self.gnd = self.Port(Ground.empty())

    self.usb = self.Port(UsbDevicePort.empty(), optional=True)


@abstract_block
class UsbDeviceConnector(UsbConnector):
  """Abstract base class for a USB 2.0 device-side port connector"""
  def __init__(self) -> None:
    super().__init__()
    self.pwr = self.Port(VoltageSource.empty(), optional=True)
    self.gnd = self.Port(GroundSource.empty())

    self.usb = self.Port(UsbHostPort.empty(), optional=True)


@abstract_block
class UsbEsdDiode(TvsDiode):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground.empty(), [Common])
    self.usb = self.Port(UsbPassivePort.empty(), [InOut])
