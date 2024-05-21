from ..electronics_abstract_parts import *
from .JlcPart import JlcPart


class Skrh(DirectionSwitchCenter, DirectionSwitch, JlcPart, FootprintBlock):
    """Generic SKRH directional switch with pushbutton.
    Default part is SKRHABE010, but footprint should be compatible with the entire SKRH series."""
    def contents(self) -> None:
        super().contents()

        self.footprint(
            'SW', 'edg:DirectionSwitch_Alps_SKRH',
            {
                '1': self.a,
                '2': self.center,
                '3': self.c,
                '4': self.b,
                '5': self.com,
                '6': self.d,
            },
            mfr='Alps Alpine', part='SKRHABE010',
            datasheet='https://www.mouser.com/datasheet/2/15/SKRH-1370966.pdf'
        )
        self.assign(self.lcsc_part, 'C139794')
        self.assign(self.actual_basic_part, False)
