from ..abstract_parts import *
from .PassiveConnector_Fpc import Fpc050Bottom
from .EInkBoostPowerPath import EInkBoostPowerPath


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

        self.vss = self.Export(self.conn.pins.request('17').adapt_to(Ground()), [Common])
        self.vdd = self.Export(self.conn.pins.request('16').adapt_to(VoltageSink(
            voltage_limits=(2.5, 3.7)*Volt,  # VCI specs, assumed for all logic
            current_draw=(0.001, 2.1)*mAmp  # sleep max to operating typ
        )))
        self.vddio = self.Export(self.conn.pins.request('15').adapt_to(VoltageSink(
            voltage_limits=(2.5, 3.7)*Volt,  # VCI specs, assumed for all logic
        )))
        self.vdd1v8 = self.Export(self.conn.pins.request('18').adapt_to(VoltageSource(
            voltage_out=1.8*Volt(tol=0),  # specs not given
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))

        din_model = DigitalSink.from_supply(
            self.vss, self.vddio,
            input_threshold_factor=(0.2, 0.8)
        )

        self.gdr = self.Export(self.conn.pins.request('2'))
        self.rese = self.Export(self.conn.pins.request('3'))
        # pin 4 is NC for this part
        self.vshr = self.Export(self.conn.pins.request('5').adapt_to(VoltageSource(
            voltage_out=(0, 11)*Volt,  # inferred from power selection register
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))
        self.vsh = self.Export(self.conn.pins.request('20').adapt_to(VoltageSource(
            voltage_out=(2.4, 15)*Volt,  # inferred from power selection register
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))
        self.vsl = self.Export(self.conn.pins.request('22').adapt_to(VoltageSource(
            voltage_out=(-15, -2.4)*Volt,  # inferred from power selection register
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))

        self.vgh = self.Export(self.conn.pins.request('21').adapt_to(VoltageSink(
            voltage_limits=(13, 20)*Volt
        )))
        self.vgl = self.Export(self.conn.pins.request('23').adapt_to(VoltageSink(
            voltage_limits=(-20, -13)*Volt
        )))

        self.bs = self.Export(self.conn.pins.request('8').adapt_to(din_model))
        self.busy = self.Export(self.conn.pins.request('9').adapt_to(din_model), optional=True)
        self.rst = self.Export(self.conn.pins.request('10').adapt_to(din_model))
        self.dc = self.Export(self.conn.pins.request('11').adapt_to(din_model), optional=True)
        self.csb = self.Export(self.conn.pins.request('12').adapt_to(din_model))

        self.spi = self.Port(SpiPeripheral.empty())
        self.connect(self.spi.sck, self.conn.pins.request('13').adapt_to(din_model))  # SCL
        self.connect(self.spi.mosi, self.conn.pins.request('14').adapt_to(din_model))  # SDA
        self.miso_nc = self.Block(DigitalBidirNotConnected())
        self.connect(self.spi.miso, self.miso_nc.port)

        self.vcom = self.Export(self.conn.pins.request('24').adapt_to(VoltageSource(
            voltage_out=(2.4, 20)*Volt,  # configurable up to VGH
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))


class Er_Epd027_2(EInk, GeneratorBlock):
    """EK79651AB-based white/black/red 2.7" 176x264 e-paper display.
    (Probably) compatible with https://www.waveshare.com/w/upload/b/ba/2.7inch_e-Paper_V2_Specification.pdf,
    and https://www.waveshare.com/w/upload/7/7b/2.7inch-e-paper-b-v2-specification.pdf
    """
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Er_Epd027_2_Device())
        self.gnd = self.Export(self.device.vss, [Common])
        self.pwr = self.Export(self.device.vdd)
        self.reset = self.Export(self.device.rst)
        self.spi = self.Export(self.device.spi)
        self.cs = self.Export(self.device.csb)
        self.dc = self.Export(self.device.dc, optional=True)
        self.busy = self.Export(self.device.busy, optional=True)

        self.generator_param(self.dc.is_connected())

    def contents(self):
        super().contents()

        self.lcd = self.Block(Er_Epd027_2_Outline())  # for device outline

        self.vdd_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vdd)
        self.connect(self.device.vdd, self.device.vddio)

        self.vdd1v8_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))) \
            .connected(self.gnd, self.device.vdd1v8)

        self.vsh_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))) \
            .connected(self.gnd, self.device.vsh)
        self.vshr_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))) \
            .connected(self.gnd, self.device.vshr)
        self.vsl_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))) \
            .connected(self.gnd, self.device.vsl)
        self.vcom_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))) \
            .connected(self.gnd, self.device.vcom)

        # current limit based on 200mA saturation current of reference inductor
        self.boost = self.Block(EInkBoostPowerPath(20*Volt(tol=0), (0, 200)*mAmp, 47*uHenry(tol=0.2),
                                                   1*uFarad(tol=0.2), 4.7*uFarad(tol=0.2), 2.2*Ohm(tol=0.01)))
        self.connect(self.gnd, self.boost.gnd)
        self.connect(self.pwr, self.boost.pwr_in)
        self.connect(self.device.gdr, self.boost.gate)
        self.connect(self.device.rese, self.boost.isense)
        self.connect(self.boost.pos_out, self.device.vgh)
        self.connect(self.boost.neg_out, self.device.vgl)

    def generate(self):
        super().generate()
        if self.get(self.dc.is_connected()):  # 4-line serial, BS low
            self.connect(self.gnd.as_digital_source(), self.device.bs)
        else:  # 3-line serial, BS high
            self.connect(self.pwr.as_digital_source(), self.device.bs)
