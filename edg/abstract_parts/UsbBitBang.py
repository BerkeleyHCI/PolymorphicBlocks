from typing import cast

from deprecated import deprecated
from typing_extensions import override

from ..electronics_model import *
from .Categories import *
from .AbstractResistor import DigitalSeriesResistor, DigitalBidirSeriesResistor


class UsbBitBang(BitBangAdapter, Block):
    """Bit-bang circuit for USB, from the UPduino3.0 circuit and for 3.3v.
    Presumably generalizes to any digital pin that can be driven fast enough.

    TODO: a more formal analysis of tolerances"""

    @staticmethod
    @deprecated("Use DigitalBidirSeriesResistor instead")
    def digital_external_from_link(link_port: DigitalBidir) -> DigitalBidir:
        """Creates a DigitalBidir model that is the external-facing port that exports from
        an internal-facing (link-side) port. The internal-facing port should be ideal.
        These are basically the semantics of a DigitalBidir bridge.
        TODO: unify code w/ DigitalBidir bridge?"""
        return DigitalBidir(
            voltage_out=link_port.link().voltage,
            current_draw=link_port.link().current_drawn,
            voltage_limits=link_port.link().voltage_limits,
            current_limits=link_port.link().current_limits,
            output_thresholds=link_port.link().output_thresholds,
            input_thresholds=link_port.link().input_thresholds,
            pulldown_capable=link_port.link().pulldown_capable,
            pullup_capable=link_port.link().pullup_capable,
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

    @override
    def contents(self) -> None:
        super().contents()

        self.dp_pull_res = self.Block(DigitalSeriesResistor(1.5 * kOhm(tol=0.05))).connected(self.dp_pull, self.usb.dp)
        self.dp_res = self.Block(DigitalBidirSeriesResistor(68 * Ohm(tol=0.05))).connected(self.dp, self.usb.dp)
        self.dm_res = self.Block(DigitalBidirSeriesResistor(68 * Ohm(tol=0.05))).connected(self.dm, self.usb.dm)

    def connected_from(self, dp_pull: Port[DigitalLink], dp: Port[DigitalLink], dm: Port[DigitalLink]) -> "UsbBitBang":
        cast(Block, builder.get_enclosing_block()).connect(dp_pull, self.dp_pull)
        cast(Block, builder.get_enclosing_block()).connect(dp, self.dp)
        cast(Block, builder.get_enclosing_block()).connect(dm, self.dm)
        return self
