from ..abstract_parts import *
from .JlcPart import JlcPart


class FlirLepton_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vddc = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(1.14, 1.26)*Volt,  # 50mVpp max ripple
            current_draw=(76, 110)*mAmp  # no sleep current specified
        ))
        self.vdd = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(2.72, 2.88)*Volt,  # 30mVpp max ripple, 4.8V abs max
            current_draw=(12, 16)*mAmp  # no sleep current specified
        ))
        self.vddio = self.Port(VoltageSink.from_gnd(  # IO ring and shutter assembly
            self.gnd,
            voltage_limits=(2.8, 3.1)*Volt,  # 50mVpp max ripple, 4.8V abs max
            current_draw=(1, 310)*mAmp  # min to max during FFC
        ))
        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vddio,
            voltage_limit_tolerance=(0, 0.6)*Volt)

        self.master_clk = self.Port(DigitalSink.from_bidir(dio_model))  # 25MHz clock
        self.spi = self.Port(SpiPeripheral(dio_model, (0, 20)*MHertz))
        self.cs = self.Port(DigitalSink.from_bidir(dio_model))
        self.cci = self.Port(I2cTarget(dio_model, [0x2a]))  # frequency up to 1MHz

        self.reset_l = self.Port(DigitalSink.from_bidir(dio_model))
        self.pwr_dwn_l = self.Port(DigitalSink.from_bidir(dio_model))
        self.vsync = self.Port(DigitalSource.from_bidir(dio_model), optional=True)

    def contents(self) -> None:
        super().contents()

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
                # '3': GPIO2, reserved, "should not be connected"
                # '4': GPIO1, reserved, "should not be connected"
                # '5': GPIO0, reserved, "should not be connected"
                '7': self.vddc,
                '11': self.spi.mosi,
                '12': self.spi.miso,
                '13': self.spi.sck,
                '14': self.cs,
                '16': self.vddio,
                # '17': self.vprog,  # unused
                '19': self.vdd,
                '21': self.cci.scl,
                '22': self.cci.sda,
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


class FlirLepton(Sensor, Resettable, Block):
    """Series of socketed thermal cameras, 8.7Hz at either 80x60 or 160x120 resolution (depending on sensor) and
    <50mK (35mK typical) NETD.
    Only the part number for the socket is generated, the sensor (a $100+ part) must be purchased separately.
    """
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(FlirLepton_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr_io = self.Export(self.ic.vddio, doc="3.0v IO voltage including shutter, IOs are 3.3v compatible from +0.6v tolerance rating")
        self.pwr = self.Export(self.ic.vdd, doc="2.8v")
        self.pwr_core = self.Export(self.ic.vddc, doc="1.2v core voltage")

        self.shutdown = self.Export(self.ic.pwr_dwn_l)  # TODO this can be hard tied high

        self.connect(self.reset, self.ic.reset_l)
        self.require(self.reset.is_connected())  # must be sequenced post-pwr_dwn

        self.spi = self.Export(self.ic.spi, doc="Video over SPI")
        self.cs = self.Export(self.ic.cs)
        self.cci = self.Export(self.ic.cci, doc="I2C-like Command and Control Interface")
        self.vsync = self.Export(self.ic.vsync, optional=True, doc="Optional frame-sync output")

    def contents(self) -> None:
        super().contents()

        self.vddc_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vddc)
        self.vddio_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vddio)
        self.vdd_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)

        with self.implicit_connect(
                ImplicitConnect(self.pwr_io, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.mclk, ), _ = self.chain(imp.Block(Oscillator((24.975, 25.025)*MHertz)), self.ic.master_clk)
