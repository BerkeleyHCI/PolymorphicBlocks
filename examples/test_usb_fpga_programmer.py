import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class FpgaProgrammingHeader(Connector, Block):
    """Custom programming header for iCE40 loosely based on the SWD pinning"""

    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(VoltageSink(), optional=True)
        self.gnd = self.Port(Ground(), [Common])
        self.spi = self.Port(SpiPeripheral())
        self.cs = self.Port(DigitalSink())
        self.reset = self.Port(DigitalSink())

    @override
    def contents(self) -> None:
        super().contents()
        self.conn = self.Block(PinHeader127DualShrouded(10)).connected(
            {
                "1": self.pwr,
                ("3", "5", "9"): self.gnd,
                "2": self.cs,  # swd: swdio
                "4": self.spi.sck,  # swd: swclk
                "6": self.spi.mosi,  # swd: swo
                "8": self.spi.miso,  # swd: NC or jtag: tdi
                "10": self.reset,
            }
        )


class UsbFpgaProgrammer(JlcBoardTop):
    """USB UART converter board"""

    @override
    def contents(self) -> None:
        super().contents()
        self.usb = self.Block(UsbCReceptacle())

        self.vusb = self.connect(self.usb.pwr)
        self.gnd = self.connect(self.usb.gnd)

        # POWER
        with self.implicit_connect(
            ImplicitConnect(self.vusb, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            # since USB is 5.25 max, we can't use the 5.2v Zener that is a basic part =(
            self.vusb_protect = imp.Block(ProtectionZenerDiode(voltage=(5.25, 6) * Volt))

            self.ft232 = imp.Block(Ft232hl())
            (self.usb_esd,), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.ft232.usb)
            (self.led0,), _ = self.chain(self.ft232.acbus.request("0"), imp.Block(IndicatorLed(Led.White)))  # TXDEN
            (self.led1,), _ = self.chain(self.ft232.acbus.request("3"), imp.Block(IndicatorLed(Led.Green)))  # RXLED
            (self.led2,), _ = self.chain(self.ft232.acbus.request("4"), imp.Block(IndicatorLed(Led.Yellow)))  # TXLED

            self.out = imp.Block(FpgaProgrammingHeader())
            self.connect(self.ft232.mpsse, self.out.spi)
            self.connect(self.ft232.adbus.request("4"), self.out.cs)
            self.connect(self.ft232.adbus.request("7"), self.out.reset)

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[],
            instance_values=[
                (["refdes_prefix"], "F"),  # unique refdes for panelization
            ],
            class_refinements=[
                (
                    UsbEsdDiode,
                    Pgb102st23,
                ),  # as recommended by the FT232H datasheet, also for the weird "sot-23" package
            ],
            class_values=[],
        )


class UsbFpgaProgrammerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(UsbFpgaProgrammer)
