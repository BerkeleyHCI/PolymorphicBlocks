from EInkBoostPowerPath import EInkBoostPowerPath
from electronics_abstract_parts import *
from electronics_lib import Fpc050Bottom


class Er_Epd027_2_Outline(InternalSubcircuit, FootprintBlock):
    def contents(self) -> None:
        super().contents()
        self.footprint('U', 'edg:Lcd_Er_Epd027_2_Outline', {},
                       'EastRising', 'ER-EPD027-2',
                       datasheet='https://www.buydisplay.com/download/manual/ER-EPD027-2_datasheet.pdf')


class Er_Epd027_2_Device(InternalSubcircuit, Block):
    """24-pin FPC connector for the ER-EPD-27-2 device"""
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.Block(Fpc050Bottom(length=24))
        self.lcd = self.Block(Er_Epd027_2_Outline())  # for device outline

        self.vss = self.Export(self.conn.pins.request('17').adapt_to(Ground()), [Common])
        self.vdd = self.Export(self.conn.pins.request('16').adapt_to(VoltageSink(
            # voltage_limits=(2.4, 3.5)*Volt,
            # current_draw=(1, 300)*uAmp  # sleep typ to max operating
        )))
        self.vddio = self.Export(self.conn.pins.request('15').adapt_to(VoltageSink(
            # voltage_limits=(2.4, 3.5)*Volt,
            # current_draw=(1, 300)*uAmp  # sleep typ to max operating
        )))
        self.vdd1v8 = self.Export(self.conn.pins.request('18').adapt_to(VoltageSource(
            # voltage_limits=(2.4, 3.5)*Volt,
            # current_draw=(1, 300)*uAmp  # sleep typ to max operating
        )))

        din_model = DigitalSink.from_supply(
            self.vss, self.vddio,
            voltage_limit_tolerance=(-0.3, 0.3),  # assumed +0.3 tolerance
            input_threshold_factor=(0.2, 0.8)
        )

        self.gdr = self.Export(self.conn.pins.request('2'))
        self.rese = self.Export(self.conn.pins.request('3'))

        self.vshr = self.Export(self.conn.pins.request('3').adapt_to(VoltageSource(
            #
        )))
        self.vsh = self.Export(self.conn.pins.request('3').adapt_to(VoltageSource(
            #
        )))
        self.vsl = self.Export(self.conn.pins.request('3').adapt_to(VoltageSource(
            #
        )))

        self.vgh = self.Export(self.conn.pins.request('3').adapt_to(VoltageSink(
            #
        )))
        self.vgl = self.Export(self.conn.pins.request('3').adapt_to(VoltageSink(
            #
        )))

        self.bs = self.Export(self.conn.pins.request('8').adapt_to(din_model))
        self.busy = self.Export(self.conn.pins.request('9').adapt_to(din_model), optional=True)
        self.rst = self.Export(self.conn.pins.request('10').adapt_to(din_model))
        self.dc = self.Export(self.conn.pins.request('11').adapt_to(din_model))
        self.csb = self.Export(self.conn.pins.request('12').adapt_to(din_model))

        self.spi = self.Port(SpiSlave.empty())
        self.connect(self.spi.sck, self.conn.pins.request('13').adapt_to(din_model))  # SCL
        self.connect(self.spi.mosi, self.conn.pins.request('14').adapt_to(din_model))  # SDA
        self.miso_nc = self.Block(DigitalBidirNotConnected())
        self.connect(self.spi.miso, self.miso_nc.port)

        self.vcomh = self.Export(self.conn.pins.request('24').adapt_to(VoltageSource(
            voltage_out=self.vcc.link().voltage,
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))


class Er_Epd027_2(EInk, Block):
    """EK79651AB-based white/black/red 2.7" 176x264 e-paper display."""
    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Er_Epd027_2_Device())
        self.gnd = self.Export(self.device.vss, [Common])
        self.vcc = self.Export(self.device.vcc)  # device power
        self.pwr = self.Export(self.device.vdd)  # logic power
        self.reset = self.Export(self.device.res)
        self.spi = self.Export(self.device.spi)
        self.cs = self.Export(self.device.cs)
        self.dc = self.Export(self.device.dc)

    def contents(self):
        super().contents()

        self.vcomh_cap = self.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2))).connected(self.gnd, self.device.vcomh)

        self.vdd_cap1 = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vdd)
        self.vdd_cap2 = self.Block(DecouplingCapacitor(capacitance=4.7*uFarad(tol=0.2))) \
            .connected(self.gnd, self.device.vdd)

        self.vcc_cap1 = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vcc)
        self.vcc_cap2 = self.Block(DecouplingCapacitor(capacitance=10*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vcc)

        # current limit based on 200mA saturation current of reference inductor
        self.boost = self.Block(EInkBoostPowerPath((0, 20)*Volt, (0, 200)*mAmp, 47*uHenry(tol=0.2),
                                                   1*uFarad(tol=0.2), 4.7*uFarad(tol=0.2), 2.2*Ohm(tol=0.01)))
