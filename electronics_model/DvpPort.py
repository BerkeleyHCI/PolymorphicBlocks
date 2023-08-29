from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir


class Dvp8Link(Link):
    """DVP (Digital Video Port) camera link with 8-wide data connection.
    TODO: ideally this would be width-parameterized, but that core logic doesn't exist yet."""
    def __init__(self) -> None:
        super().__init__()
        self.host = self.Port(Dvp8Host(DigitalBidir.empty()))
        self.cam = self.Port(Dvp8Camera(DigitalBidir.empty()))

    def contents(self) -> None:
        super().contents()

        self.xclk = self.connect(self.host.xclk, self.cam.xclk)
        self.pclk = self.connect(self.host.pclk, self.cam.pclk)
        self.href = self.connect(self.host.href, self.cam.href)
        self.vsync = self.connect(self.host.vsync, self.cam.vsync)

        self.y0 = self.connect(self.host.y0, self.cam.y0)
        self.y1 = self.connect(self.host.y1, self.cam.y1)
        self.y2 = self.connect(self.host.y2, self.cam.y2)
        self.y3 = self.connect(self.host.y3, self.cam.y3)
        self.y4 = self.connect(self.host.y4, self.cam.y4)
        self.y5 = self.connect(self.host.y5, self.cam.y5)
        self.y6 = self.connect(self.host.y6, self.cam.y6)
        self.y7 = self.connect(self.host.y7, self.cam.y7)


class Dvp8Host(Bundle[Dvp8Link]):
    link_type = Dvp8Link

    def __init__(self, model: Optional[DigitalBidir] = None) -> None:
        super().__init__()
        if model is None:
            model = DigitalBidir()  # ideal by default
        source_model = DigitalSource.from_bidir(model)
        sink_model = DigitalSink.from_bidir(model)

        self.xclk = self.Port(source_model)  # clock in
        self.pclk = self.Port(sink_model)  # pixel valid
        self.href = self.Port(sink_model)  # new line
        self.vsync = self.Port(sink_model)  # new frame

        self.y0 = self.Port(sink_model)
        self.y1 = self.Port(sink_model)
        self.y2 = self.Port(sink_model)
        self.y3 = self.Port(sink_model)
        self.y4 = self.Port(sink_model)
        self.y5 = self.Port(sink_model)
        self.y6 = self.Port(sink_model)
        self.y7 = self.Port(sink_model)


class Dvp8Camera(Bundle[Dvp8Link]):
    link_type = Dvp8Link

    def __init__(self, model: Optional[DigitalBidir] = None) -> None:
        super().__init__()
        if model is None:
            model = DigitalBidir()  # ideal by default
        source_model = DigitalSource.from_bidir(model)
        sink_model = DigitalSink.from_bidir(model)

        self.xclk = self.Port(sink_model)  # clock in
        self.pclk = self.Port(source_model)  # pixel valid
        self.href = self.Port(source_model)  # new line
        self.vsync = self.Port(source_model)  # new frame

        self.y0 = self.Port(source_model)
        self.y1 = self.Port(source_model)
        self.y2 = self.Port(source_model)
        self.y3 = self.Port(source_model)
        self.y4 = self.Port(source_model)
        self.y5 = self.Port(source_model)
        self.y6 = self.Port(source_model)
        self.y7 = self.Port(source_model)
