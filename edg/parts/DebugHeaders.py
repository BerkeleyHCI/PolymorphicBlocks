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

        self.conn = self.Block(PinHeader127DualShrouded(10)).connected({"1": self.pwr, ("3", "5", "9"): self.gnd})

        self.connect(self.swd.swdio, self.conn.pins.request("2").adapt_to(DigitalBidir()))
        self.connect(self.swd.swclk, self.conn.pins.request("4").adapt_to(DigitalSource()))
        self.connect(self.swo, self.conn.pins.request("6").adapt_to(DigitalBidir()))
        self.connect(self.tdi, self.conn.pins.request("8").adapt_to(DigitalBidir()))
        # TODO: pulldown is a hack to prevent driver conflict warnings, this should be a active low (open drain) driver
        self.connect(self.reset, self.conn.pins.request("10").adapt_to(DigitalSource.pulldown_from_supply(self.gnd)))


class SwdCortexTargetTagConnect(SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo):
    """OFFICIAL tag connect SWD header using the TC2030 series cables.
    https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2030-CTX_1.pdf"""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())

        self.conn = self.Block(TagConnect(6)).connected({"1": self.pwr, "5": self.gnd})

        self.connect(self.swd.swdio, self.conn.pins.request("2").adapt_to(DigitalBidir()))  # also TMS
        # TODO: pulldown is a hack to prevent driver conflict warnings, this should be a active low (open drain) driver
        self.connect(self.reset, self.conn.pins.request("3").adapt_to(DigitalSource.pulldown_from_supply(self.gnd)))
        self.connect(self.swd.swclk, self.conn.pins.request("4").adapt_to(DigitalSource()))
        self.connect(self.swo, self.conn.pins.request("6").adapt_to(DigitalBidir()))


class SwdCortexTargetTc2050(
    SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo, SwdCortexTargetConnectorTdi
):
    """UNOFFICIAL tag connect SWD header, maintaining physical pin compatibility with the 2x05 1.27mm header."""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())

        self.conn = self.Block(TagConnect(10)).connected({"1": self.pwr, ("2", "3", "5"): self.gnd})

        self.connect(self.swd.swdio, self.conn.pins.request("10").adapt_to(DigitalBidir()))
        self.connect(self.swd.swclk, self.conn.pins.request("9").adapt_to(DigitalSource()))
        self.connect(self.swo, self.conn.pins.request("8").adapt_to(DigitalBidir()))
        self.connect(self.tdi, self.conn.pins.request("7").adapt_to(DigitalBidir()))
        # TODO: pulldown is a hack to prevent driver conflict warnings, this should be a active low (open drain) driver
        self.connect(self.reset, self.conn.pins.request("6").adapt_to(DigitalSource.pulldown_from_supply(self.gnd)))
