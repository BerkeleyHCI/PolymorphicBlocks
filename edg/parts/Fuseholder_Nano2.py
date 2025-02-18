from ..core import RangeExpr
from ..electronics_model import Volt, FootprintBlock
from ..abstract_parts import Fuse
from .JlcPart import JlcPart


class Nano2Fuseholder(Fuse, JlcPart, FootprintBlock):
    """Littelfuse Nano2 / 154 series fuseholder. Generic versions exist as 1808 fuses.
    TODO: generate fuse part numbers from a table, currently this only generates the holder"""
    def contents(self):
        super().contents()
        self.footprint(
            'U', 'Fuse:Fuseholder_Littelfuse_Nano2_154x',
            {
                '1': self.a,
                '2': self.b,
            },
            mfr='Littelfuse', part='01550900M',
            datasheet='https://www.littelfuse.com/assetdocs/littelfuse-fuse-154-series-data-sheet?assetguid=a8a8a462-7295-481b-a91b-d770dabf005b'
        )
        self.assign(self.lcsc_part, "C108518")
        self.assign(self.actual_basic_part, False)

        self.assign(self.actual_trip_current, RangeExpr.EMPTY)  # assumed you can find the right fuse
        self.assign(self.actual_hold_current, RangeExpr.EMPTY)
        self.assign(self.actual_voltage_rating, (-125, 125)*Volt)
