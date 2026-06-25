from deprecated import deprecated

from ..electronics_model import *
from .DummyDevices import BaseDummyBlock
from .GroundPort import Ground, Common, GroundLink


class DummyGround(BaseDummyBlock[GroundLink]):
    def __init__(self) -> None:
        super().__init__()
        self.io: Ground = self.Port(Ground(), [Common, InOut])

    @property
    @deprecated(f"DummyGround.gnd is deprecated, use .io instead.")
    def gnd(self) -> Ground:
        return self.io
