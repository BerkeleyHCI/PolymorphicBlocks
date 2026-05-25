from typing import List, Any
from typing_extensions import override

from ..electronics_model import *
from .SwdCortexConnectors import (
    SwdCortexTargetConnector,
    SwdCortexTargetConnectorReset,
    SwdCortexTargetConnectorSwo,
    SwdCortexTargetConnectorTdi,
)
from .IoController import IoController


@non_library
class IoControllerWithSwdTargetConnector(IoController, GeneratorBlock):
    """An IoController with a SWD programming header, with connected power and ground,
    and optional SWO and TDI pins that are connected to the microcontroller's GPIO Vector.
    These are defined with names swd_swo and swd_tdi and can be pinned with the normal pin_assigns.

    By default, SWD and SWO pins are not connected, but the reset pin is connected.

    Subclasses must connect the swd_mode and reset_node to the microcontroller.
    Subclasses must also ensure the internal GPIO vector is left open (not direct vector-connected).
    """

    def __init__(
        self,
        swd_connect_swo: BoolLike = False,
        swd_connect_tdi: BoolLike = False,
        swd_connect_reset: BoolLike = True,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.swd_connect_swo = self.ArgParameter(swd_connect_swo)
        self.swd_connect_tdi = self.ArgParameter(swd_connect_tdi)
        self.swd_connect_reset = self.ArgParameter(swd_connect_reset)
        self.generator_param(self.swd_connect_swo, self.swd_connect_tdi, self.swd_connect_reset)
        self.swd_node = self.connect()  # connect this internal node to the microcontroller
        self.reset_node = self.connect()  # connect this internal node to the microcontroller

    @override
    def generate(self) -> None:
        super().generate()
        self.swd = self.Block(SwdCortexTargetConnector())
        self.connect(self.swd.gnd, self.gnd)
        self.connect(self.swd.pwr, self.pwr)
        self.connect(self.swd_node, self.swd.swd)

        if self.get(self.swd_connect_swo):
            self.connect(self.ic.gpio.request("swd_swo"), self.swd.with_mixin(SwdCortexTargetConnectorSwo()).swo)
        if self.get(self.swd_connect_tdi):
            self.connect(self.ic.gpio.request("swd_tdi"), self.swd.with_mixin(SwdCortexTargetConnectorTdi()).tdi)
        if self.get(self.swd_connect_reset):  # reset commonly connected but not required by SWD
            self.connect(self.reset_node, self.swd.with_mixin(SwdCortexTargetConnectorReset()).reset)
