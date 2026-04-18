from typing_extensions import override

from ..abstract_parts import *
from .PassiveConnector_Header import PinHeader127DualShrouded
from .PassiveConnector_TagConnect import TagConnect


class SwdCortexTargetHeader(
    SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo, SwdCortexTargetConnectorTdi
):
    @override
    def contents(self) -> None:
        super().contents()

        self.pwr.init_from(VoltageSink())
        self.gnd.init_from(Ground())
        self.swd.init_from(SwdHostPort())
        self.swo.init_from(DigitalBidir())
        self.tdi.init_from(DigitalBidir())
        self.reset.init_from(
            DigitalSource.pulldown_from_supply(self.gnd)
        )  # pulldown to not conflict with other drivers

        self.conn = self.Block(PinHeader127DualShrouded(10)).connected(
            {
                "1": self.pwr,
                ("3", "5", "9"): self.gnd,
                "2": self.swd.swdio,
                "4": self.swd.swclk,
                "6": self.swo,
                "8": self.tdi,
                "10": self.reset,
            }
        )


class SwdCortexTargetTagConnect(SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo):
    """OFFICIAL tag connect SWD header using the TC2030 series cables.
    https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2030-CTX_1.pdf"""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())
        self.swd.init_from(SwdHostPort())
        self.swo.init_from(DigitalBidir())
        self.reset.init_from(
            DigitalSource.pulldown_from_supply(self.gnd)
        )  # pulldown to not conflict with other drivers

        self.conn = self.Block(TagConnect(6)).connected(
            {"1": self.pwr, "2": self.swd.swdio, "3": self.reset, "4": self.swd.swclk, "5": self.gnd, "6": self.swo}
        )


class SwdCortexTargetTc2050(
    SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo, SwdCortexTargetConnectorTdi
):
    """UNOFFICIAL tag connect SWD header, maintaining physical pin compatibility with the 2x05 1.27mm header.
    NOT RECOMMENDED for use, this is a legacy artifact and will be removed.
    Use one of the official pinnings instead."""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())
        self.swd.init_from(SwdHostPort())
        self.swo.init_from(DigitalBidir())
        self.tdi.init_from(DigitalBidir())
        self.reset.init_from(
            DigitalSource.pulldown_from_supply(self.gnd)
        )  # pulldown to not conflict with other drivers

        self.conn = self.Block(TagConnect(10)).connected(
            {
                "1": self.pwr,
                ("2", "3", "5"): self.gnd,
                "10": self.swd.swdio,
                "9": self.swd.swclk,
                "8": self.swo,
                "7": self.tdi,
                "6": self.reset,
            }
        )
