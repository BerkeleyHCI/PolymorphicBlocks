from typing import Any

from ..electronics_model import *


class Nonstrict3v3Compatible(BlockInterfaceMixin[Block]):
    """A mixin for a block where 3.3v is outside the recommended operating conditions but
    within the absolute maximum, setting the nonstrict_3v3_compatible parameter to True
    extends the modeled voltage range to 3.6v or the absolute maximum, whichever is lower.
    Occurs in displays."""

    def __init__(self, *args: Any, nonstrict_3v3_compatible: BoolLike = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.nonstrict_3v3_compatible = self.ArgParameter(nonstrict_3v3_compatible)
