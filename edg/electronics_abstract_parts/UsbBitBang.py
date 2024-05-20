from typing import cast

from ...electronics_model import *
from .Categories import *
from .AbstractResistor import Resistor


class UsbBitBang(Interface, Block):
  """Bit-bang circuit for USB, from the UPduino3.0 circuit and for 3.3v.
  Presumably generalizes to any digital pin that can be driven fast enough.

  TODO: a more formal analysis of tolerances"""
  @staticmethod
  def digital_external_from_link(link_port: DigitalBidir) -> DigitalBidir:
    """Creates a DigitalBidir model that is the external-facing port that exports from
    an internal-facing (link-side) port. The internal-facing port should be ideal.
    These are basically the semantics of a DigitalBidir bridge.
    TODO: unify code w/ DigitalBidir bridge?"""
    return DigitalBidir(
      voltage_out=link_port.link().voltage, current_draw=link_port.link().current_drawn,
      voltage_limits=link_port.link().voltage_limits, current_limits=link_port.link().current_limits,
      output_thresholds=link_port.link().output_thresholds, input_thresholds=link_port.link().input_thresholds,
      pulldown_capable=link_port.link().pulldown_capable, pullup_capable=link_port.link().pullup_capable
    )

  def __init__(self) -> None:
    super().__init__()
    self.usb = self.Port(UsbDevicePort.empty(), [Output])

    # Internally, this behaves like a bridge, with defined 'external' (USB) and 'internal' (FPGA)
    # sides and propagating port data from internal to external as with bridge semantics.
    # Undirected / bidirectional propagation doesn't work with the current solver, since
    # we need the FPGA-side link voltage to propagate to the USB port, and the USB-side link voltage
    # to propagate to the FPGA port, and this causes both to deadlock (both link voltages depend on
    # the port voltages, and neither is available until the other link voltage is available).
    # Other ideas include moving to a fixed point solver, but that has other trade-offs.
    self.dp = self.Port(DigitalBidir.empty())
    self.dm = self.Port(DigitalBidir.empty())
    self.dp_pull = self.Port(DigitalSink.empty())

  def contents(self) -> None:
    super().contents()

    self.dp_pull_res = self.Block(Resistor(1.5*kOhm(tol=0.05)))

    self.dp_res = self.Block(Resistor(68*Ohm(tol=0.05)))
    self.dm_res = self.Block(Resistor(68*Ohm(tol=0.05)))

    self.connect(self.dm, self.dm_res.a.adapt_to(DigitalBidir()))  # internal ports are ideal
    self.connect(self.usb.dm, self.dm_res.b.adapt_to(
      self.digital_external_from_link(self.dm)))

    self.connect(self.dp, self.dp_res.a.adapt_to(DigitalBidir()))
    self.connect(self.usb.dp, self.dp_res.b.adapt_to(DigitalBidir(
      voltage_out=self.dp.link().voltage.hull(self.dp_pull.link().voltage),
      current_draw=self.dp.link().current_drawn + self.dp_pull.link().current_drawn,
      voltage_limits=self.dp.link().voltage_limits.intersect(self.dp_pull.link().voltage_limits),
      current_limits=self.dp.link().current_limits.intersect(self.dp_pull.link().current_limits),
      output_thresholds=self.dp.link().output_thresholds.intersect(self.dp_pull.link().output_thresholds),
      input_thresholds=self.dp.link().input_thresholds.hull(self.dp_pull.link().input_thresholds),
      pulldown_capable=self.dp.link().pulldown_capable | self.dp_pull.link().pulldown_capable,
      pullup_capable=self.dp.link().pullup_capable | self.dp_pull.link().pullup_capable
    )))

    self.connect(self.dp_pull, self.dp_pull_res.a.adapt_to(DigitalSink()))
    self.connect(self.dp_pull_res.b, self.dp_res.b)  # upstream of adapter

  def connected_from(self, dp_pull: Port[DigitalLink], dp: Port[DigitalLink], dm: Port[DigitalLink]) -> 'UsbBitBang':
    cast(Block, builder.get_enclosing_block()).connect(dp_pull, self.dp_pull)
    cast(Block, builder.get_enclosing_block()).connect(dp, self.dp)
    cast(Block, builder.get_enclosing_block()).connect(dm, self.dm)
    return self
