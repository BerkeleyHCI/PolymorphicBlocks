from ..abstract_parts import *
from .JlcPart import JlcPart


class Bwipx_1_001e(RfConnectorTestPoint, UflConnector, JlcPart, FootprintBlock):
    """BAT WIRELESS IPEX connector"""
    def contents(self):
        super().contents()
        self.footprint(
            'J', 'Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical',
            {
                '1': self.sig,
                '2': self.gnd,
            },
            value=self.tp_name,
            mfr='BWIPX-1-001E', part='BAT WIRELESS',
            datasheet='https://datasheet.lcsc.com/lcsc/2012231509_BAT-WIRELESS-BWIPX-1-001E_C496552.pdf'
        )
        self.assign(self.lcsc_part, 'C496552')
        self.assign(self.actual_basic_part, False)


class Amphenol901143(SmaFConnector, FootprintBlock):
    """PTH right-angle SMA-F connector"""
    def contents(self):
        super().contents()
        self.footprint(
            'J', 'Connector_Coaxial:SMA_Amphenol_901-143_Horizontal',
            {
                '1': self.sig,
                '2': self.gnd,
            },
            mfr='Amphenol RF', part='901-143',
            datasheet='https://s3-us-west-2.amazonaws.com/catsy.582/C901-143.pdf'
        )
