from electronics_abstract_parts import *
from electronics_lib import Fpc050Bottom


class Er_Oled022_1_Outline(InternalSubcircuit, FootprintBlock):
    def contents(self) -> None:
        super().contents()
        self.footprint('U', 'edg:Lcd_Er_Oled022_1_Outline', {},
                       'EastRising', 'ER-OLED022-1',
                       datasheet='https://www.buydisplay.com/download/manual/ER-OLED022-1_Series_Datasheet.pdf')


class Er_Oled022_1_Device(InternalSubcircuit, Block):
    """24-pin FPC connector for the ER-OLED022-1* device, based on the interfacing example
    https://www.buydisplay.com/download/interfacing/ER-OLED022-1_Interfacing.pdf"""
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.Block(Fpc050Bottom(length=24))
        self.lcd = self.Block(Er_Oled022_1_Outline())  # for device outline

        self.vdd = self.Export(self.conn.pins.request('5').adapt_to(VoltageSink(
            voltage_limits=(2.4, 3.5)*Volt,
            current_draw=(1, 300)*uAmp  # sleep typ to max operating
        )))

        self.vss = self.Export(self.conn.pins.request('3').adapt_to(Ground()), [Common])

        self.vcc = self.Export(self.conn.pins.request('23').adapt_to(VoltageSink(
            voltage_limits=(12.0, 13.0)*Volt,
            current_draw=(0.001, 35)*mAmp  # typ sleep to operating at 100% on
        )))

        self.iref = self.Export(self.conn.pins.request('21'))
        self.vcomh = self.Export(self.conn.pins.request('22').adapt_to(VoltageSource(
            voltage_out=self.vcc.link().voltage,
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))

        self.connect(self.vss,
                     self.conn.pins.request('1').adapt_to(Ground()),  # NC/GND
                     self.conn.pins.request('24').adapt_to(Ground()),  # NC/GND
                     self.conn.pins.request('2').adapt_to(Ground()))  # VLSS, connect to VSS externally

        din_model = DigitalSink.from_supply(
            self.vss, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3),  # assumed +0.3 tolerance
            input_threshold_factor=(0.2, 0.8)
        )

        self.connect(self.conn.pins.request('6').adapt_to(Ground()), self.vss)  # BS1, 0 for serial
        self.connect(self.conn.pins.request('7').adapt_to(Ground()), self.vss)  # BS2, 0 for serial

        self.spi = self.Port(SpiSlave.empty())
        self.connect(self.spi.sck, self.conn.pins.request('13').adapt_to(din_model))  # DB0
        self.connect(self.spi.mosi, self.conn.pins.request('14').adapt_to(din_model))  # DB1

        self.miso_nc = self.Block(DigitalBidirNotConnected())
        self.connect(self.spi.miso, self.miso_nc.port)

        self.res = self.Export(self.conn.pins.request('9').adapt_to(din_model))
        self.cs = self.Export(self.conn.pins.request('8').adapt_to(din_model))
        self.dc = self.Export(self.conn.pins.request('10').adapt_to(din_model))

        self.connect(self.vss, self.conn.pins.request('12').adapt_to(Ground()))  # RW
        self.connect(self.vss, self.conn.pins.request('11').adapt_to(Ground()))  # ER
        self.connect(self.vss, self.conn.pins.request('16').adapt_to(Ground()))  # DB3
        self.connect(self.vss, self.conn.pins.request('17').adapt_to(Ground()))  # DB4
        self.connect(self.vss, self.conn.pins.request('18').adapt_to(Ground()))  # DB5
        self.connect(self.vss, self.conn.pins.request('19').adapt_to(Ground()))  # DB6
        self.connect(self.vss, self.conn.pins.request('20').adapt_to(Ground()))  # DB7

class Er_Oled022_1(Oled, Block):
    """SSD1305-based 2.2" 128x32 monochrome OLED."""
    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Er_Oled022_1_Device())
        self.gnd = self.Export(self.device.vss, [Common])
        self.vcc = self.Export(self.device.vcc)  # device power
        self.pwr = self.Export(self.device.vdd)  # logic power
        self.reset = self.Export(self.device.res)
        self.spi = self.Export(self.device.spi)
        self.cs = self.Export(self.device.cs)
        self.dc = self.Export(self.device.dc)

    def contents(self):
        super().contents()

        self.iref_res = self.Block(Resistor(resistance=910*kOhm(tol=0.05)))  # TODO dynamic sizing
        self.connect(self.iref_res.a, self.device.iref)
        self.connect(self.iref_res.b.adapt_to(Ground()), self.gnd)
        self.vcomh_cap = self.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2))).connected(self.gnd, self.device.vcomh)

        self.vdd_cap1 = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vdd)
        self.vdd_cap2 = self.Block(DecouplingCapacitor(capacitance=4.7*uFarad(tol=0.2))) \
            .connected(self.gnd, self.device.vdd)

        self.vcc_cap1 = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vcc)
        self.vcc_cap2 = self.Block(DecouplingCapacitor(capacitance=10*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vcc)
