from ..electronics_model import *
from .GroundPort import Ground, Common


class DummyGround(DummyDevice):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common, InOut])
