from ..abstract_parts import *
from .JlcPart import JlcPart


class FlirLepton_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vdd = self.Port(VoltageSink(
            # voltage_limits=(1.62, 3.6)*Volt,
            # current_draw=(0.5, 85)*uAmp
        ))

    def generate(self) -> None:
        super().generate()

        self.footprint(
            'U', 'edg:Molex_1050281001',
            {
                '1': self.gnd,
                '6': self.gnd,
                '8': self.gnd,
                '9': self.gnd,
                '10': self.gnd,
                '15': self.gnd,
                '18': self.gnd,
                '20': self.gnd,
                '25': self.gnd,
                '27': self.gnd,
                '30': self.gnd,
                '33': self.gnd,  # socket shield

                '2': self.vsync,  # aka GPIO3
                # '3': GPIO2, reserved
                # '4': GPIO2, reserved
                # '5': GPIO2, reserved
                '7': self.vddc,
                '11': self.spi.mosi,
                '12': self.spi.miso,
                '13': self.spi.sck,
                '14': self.cs,
                '16': self.vddio,
                '17': self.vprog,
                '19': self.vdd,
                '21': self.i2c.scl,
                '22': self.i2c.sda,
                '23': self.pwr_dwn_l,
                '24': self.reset_l,
                '26': self.master_clk,
                # '28': reserved
                # '29': reserved
                # '31': reserved
                # '32': reserved
            },
            mfr='Molex', part='1050281001',
            datasheet='https://www.molex.com/pdm_docs/ps/PS-105028-101.pdf'
        )
        self.assign(self.lcsc_part, 'C585422')
        self.assign(self.actual_basic_part, False)


class FlirLepton(Sensor, Block):
    """Series of socketed thermal cameras, 9Hz at either 80x60 or 160x120 resolution depending on sensor.
    Only the part number for the socket is generated, the sensor (a $100+ part) must be purchased separately."""
    @init_in_parent
    def __init__(self):
        super().__init__()
        self.ic = self.Block(FlirLepton_Device())

    def contents(self):
        super().contents()
        # self.vdd_cap = self.Block(DecouplingCapacitor(0.01*uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
