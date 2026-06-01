import warnings
from typing import Any

from ..electronics_model import *
from .DummyDevices import BaseDummyBlock
from .GroundPort import Ground, Common, GroundLink


class DummyGround(BaseDummyBlock[GroundLink]):
    def __init__(self) -> None:
        super().__init__()
        self.io = self.Port(Ground(), [Common, InOut])

    def __getattr__(self, item: str) -> Any:
        if item == "gnd":
            warnings.warn(
                f"DummyGround.gnd is deprecated, use .io instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return self.io
        else:
            raise AttributeError(
                item
            )  # ideally we'd use super().__getattr__(...), but that's not defined in base classes
