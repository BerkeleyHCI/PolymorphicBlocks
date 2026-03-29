from .DummyDevice import DummyDevice
from .GroundPort import Ground, Common
from ..core import InOut


class DummyGround(DummyDevice):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common, InOut])
