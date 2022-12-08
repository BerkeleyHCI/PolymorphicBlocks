from electronics_model import *
from .Categories import *
from .AbstractResistor import Resistor


class UsbBitBang(DiscreteApplication):
  """Bit-bang circuit for USB, from the UPduino3.0 circuit and for 3.3v.
  Presumably generalizes to any digital pin that can be driven fast enough.

  TODO: a more formal analysis of tolerances"""
  def __init__(self) -> None:
    super().__init__()
    self.usb = self.Port(UsbDevicePort(DigitalBidir.empty()), [Output])
    self.dp = self.Port(DigitalBidir.empty())
    self.dm = self.Port(DigitalBidir.empty())
    self.dp_pull = self.Port(DigitalSink.empty())

  def contents(self) -> None:
    super().contents()

    self.dp_pull_res = self.Block(Resistor(1.5*kOhm(tol=0.05)))

    self.dp_res = self.Block(Resistor(68*Ohm(tol=0.05)))
    self.dm_res = self.Block(Resistor(68*Ohm(tol=0.05)))

    # this only propagates discrete digital IO -> USB, since bidirectional
    # propagation causes a cycle that the system is unable to handle:
    # digital voltage depends on USB voltage which depends on digital voltage
    # in practice this means the voltages on both links must be merged,
    # but there is no mechanism for that
    self.connect(self.dm, self.dm_res.a.adapt_to(DigitalBidir()))
    self.connect(self.usb.dm, self.dm_res.b.adapt_to(DigitalBidir(
      voltage_out=self.dm.link().voltage
    )))

    self.connect(self.dp, self.dp_res.a.adapt_to(DigitalBidir()))
    self.connect(self.usb.dp, self.dp_res.b.adapt_to(DigitalBidir(
      voltage_out=self.dp.link().voltage.hull(self.dp_pull.link().voltage)
    )))

    self.connect(self.dp_pull, self.dp_pull_res.a.adapt_to(DigitalSink()))
    self.connect(self.dp_pull_res.b, self.dp_res.b)  # upstream of adapter
