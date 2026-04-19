from ..core import *
from .PassivePort import HasPassivePort


class TouchLink(Link):
    """Touch sensor link, consisting of one sensor (typically a PCB copper pattern) and one driver.
    These contain no modeling."""

    def __init__(self) -> None:
        super().__init__()
        self.driver = self.Port(TouchDriver())
        self.pad = self.Port(TouchPadPort())

        self.net = self.connect(self.driver.net, self.pad.net)


class TouchDriver(HasPassivePort, Port[TouchLink]):
    """Touch sensor driver-side port, typically attached to a microcontroller pin.
    Internal to this port should be any circuitry needed to make the sensor work.
    Separately from the port, the microcontroller should generate additionally needed circuits,
    like the sensing caps for STM32 devices."""

    link_type = TouchLink

    def __init__(self) -> None:
        super().__init__()
        self.net = self.link().net


class TouchPadPort(HasPassivePort, Port[TouchLink]):
    """Touch sensor-side port, typically attached to a copper pad."""

    link_type = TouchLink

    def __init__(self) -> None:
        super().__init__()
        self.net = self.link().net
