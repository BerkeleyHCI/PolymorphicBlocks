from ..electronics_model import *
from .DummyDevices import BaseDummyBlock
from .GroundPort import Ground, Common, GroundLink


class DummyGround(BaseDummyBlock[GroundLink]):
    def __init__(self) -> None:
        super().__init__()
        self.io = self.Port(Ground(), [Common, InOut])
