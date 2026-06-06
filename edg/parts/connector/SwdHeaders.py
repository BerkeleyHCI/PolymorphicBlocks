from typing_extensions import override

from ...circuits import *
from ..connector.Headers import PinHeader127DualShrouded
from ..connector.TagConnect import TagConnect


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
        # reset modeled as pulldown to not conflict with other drivers, technically an open-drain
        self.reset.init_from(DigitalSource.pulldown_from_supply(self.gnd))

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
        # reset modeled as pulldown to not conflict with other drivers, technically an open-drain
        self.reset.init_from(DigitalSource.pulldown_from_supply(self.gnd))

        self.conn = self.Block(TagConnect(6)).connected(
            {"1": self.pwr, "2": self.swd.swdio, "3": self.reset, "4": self.swd.swclk, "5": self.gnd, "6": self.swo}
        )
