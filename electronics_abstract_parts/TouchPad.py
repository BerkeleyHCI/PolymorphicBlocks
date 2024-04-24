from electronics_model import *
from .Categories import HumanInterface


class FootprintToucbPad(FootprintBlock, HumanInterface):
    @init_in_parent
    def __init__(self, touch_footprint: StringLike):
        super().__init__()
        self.pad = self.Port(TouchPadPort(), [Input])
        self.touch_footprint = self.ArgParameter(touch_footprint)

    def contents(self):
        super().contents()
        self.footprint('U', self.touch_footprint, {'1': self.pad})
