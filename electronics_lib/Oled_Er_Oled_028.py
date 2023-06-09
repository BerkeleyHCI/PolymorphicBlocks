from electronics_abstract_parts import *
from electronics_lib import Fpc050Bottom


class Er_Oled028_1_Outline(InternalSubcircuit, FootprintBlock):
    def contents(self) -> None:
        super().contents()
        self.footprint('U', 'edg:Lcd_Er_Oled028_1_Outline', {},
                       'EastRising', 'ER-OLED028-1',
                       datasheet='https://www.buydisplay.com/download/manual/ER-OLED028-1_Series_Datasheet.pdf')


class Er_Oled028_1_Device(InternalSubcircuit, Block):
    """30-pin FPC connector for the ER-OLED028-1* device, based on the interfacing example
    https://www.buydisplay.com/download/interfacing/ER-OLED028-1_Interfacing.pdf"""
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.Block(Fpc050Bottom(length=30))
        self.lcd = self.Block(Er_Oled028_1_Outline())  # for device outline

        vcc3_pin = self.conn.pins.request('3')
        self.connect(vcc3_pin, self.conn.pins.request('29'))
        self.vcc = self.Export(vcc3_pin.adapt_to(VoltageSink(
            voltage_limits=(11.5, 12.5)*Volt,
            current_draw=(15.6, 60)*mAmp  # typ 30% display to abs max
        )))

        self.vcomh = self.Export(self.conn.pins.request('4').adapt_to(VoltageSource(
            voltage_out=self.vcc.link().voltage,
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))
        self.vdd = self.Export(self.conn.pins.request('25').adapt_to(VoltageSource(
            voltage_out=(2.4, 2.6)*Volt,
            current_limits=0*mAmp(tol=0)  # only for external capacitor
        )))
        self.vci = self.Export(self.conn.pins.request('26').adapt_to(VoltageSink(
            voltage_limits=(2.4, 3.5)*Volt,
            current_draw=(20, 300)*uAmp  # typ sleep to max operating
        )))
        self.vddio = self.Export(self.conn.pins.request('24').adapt_to(VoltageSink(
            voltage_limits=(1.65*Volt, self.vci.link().voltage.upper()),
            current_draw=(2, 10)*uAmp  # typ sleep to max sleep, no operating draw given
        )))

        vlss5_pin = self.conn.pins.request('5')
        self.connect(vlss5_pin, self.conn.pins.request('28'))
        self.vss = self.Export(self.conn.pins.request('2').adapt_to(Ground()), [Common])
        self.connect(self.vss,
                     self.conn.pins.request('1').adapt_to(Ground()),  # NC/GND
                     self.conn.pins.request('30').adapt_to(Ground()),  # NC/GND
                     vlss5_pin.adapt_to(Ground()))  # VLSS, connect to VSS externally

        din_model = DigitalSink.from_supply(
            self.vss, self.vddio,
            voltage_limit_tolerance=(-0.5, 0.3),  # assumed +0.3 tolerance
            input_threshold_factor=(0.2, 0.8)
        )

        self.bs0 = self.Export(self.conn.pins.request('16').adapt_to(din_model))  # 3-wire (1) / 4-wire (0) serial
        self.connect(self.conn.pins.request('17').adapt_to(Ground()), self.vss)  # BS1, 0 for any serial

        self.spi = self.Port(SpiSlave.empty())
        self.connect(self.spi.sck, self.conn.pins.request('13').adapt_to(din_model))  # DB0
        self.connect(self.spi.mosi, self.conn.pins.request('12').adapt_to(din_model))  # DB1

        self.miso_nc = self.Block(DigitalBidirNotConnected())
        self.connect(self.spi.miso, self.miso_nc.port)

        self.connect(self.vss,
                     self.conn.pins.request('10').adapt_to(Ground()),  # DB3
                     self.conn.pins.request('9').adapt_to(Ground()),  # DB4
                     self.conn.pins.request('8').adapt_to(Ground()),  # DB5
                     self.conn.pins.request('7').adapt_to(Ground()),  # DB6
                     self.conn.pins.request('6').adapt_to(Ground()),  # DB7
                     self.conn.pins.request('15').adapt_to(Ground()),  # RW
                     self.conn.pins.request('14').adapt_to(Ground()))  # ER

        self.dc = self.Export(self.conn.pins.request('18').adapt_to(din_model))  # ground if unused
        self.cs = self.Export(self.conn.pins.request('19').adapt_to(din_model))
        self.res = self.Export(self.conn.pins.request('20').adapt_to(din_model))
        # pin 21 FR disconnected
        self.iref = self.Export(self.conn.pins.request('22'))
        self.vsl = self.Export(self.conn.pins.request('27'))


class Er_Oled028_1(Oled, GeneratorBlock):
    """SSD1322-based 2.8" 256x64 monochrome OLED."""
    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Er_Oled028_1_Device())
        self.gnd = self.Export(self.device.vss, [Common])
        self.vcc = self.Export(self.device.vcc)  # device power
        self.pwr = self.Export(self.device.vddio)  # logic power
        self.reset = self.Export(self.device.res)
        self.spi = self.Export(self.device.spi)
        self.cs = self.Export(self.device.cs)
        self.dc = self.Export(self.device.dc, optional=True)

        self.generator_param(self.dc.is_connected())

    def contents(self):
        super().contents()
        self.connect(self.pwr, self.device.vci)

        self.iref_res = self.Block(Resistor(resistance=680*kOhm(tol=0.05)))  # TODO dynamic sizing
        self.connect(self.iref_res.a, self.device.iref)
        self.connect(self.iref_res.b.adapt_to(Ground()), self.gnd)
        self.vcomh_cap = self.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2))).connected(self.gnd, self.device.vcomh)

        self.vdd_cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vdd)
        self.vci_cap1 = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vci)
        self.vci_cap2 = self.Block(DecouplingCapacitor(capacitance=4.7*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vci)

        self.vcc_cap1 = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vcc)
        self.vcc_cap2 = self.Block(DecouplingCapacitor(capacitance=10*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vcc)

        self.vsl_res = self.Block(Resistor(resistance=50*kOhm(tol=0.05)))
        diode_model = Diode(reverse_voltage=(0, 0)*Volt, current=(0, 0)*Amp,
                            voltage_drop=(0, 1.2)*Volt)
        self.vsl_d1 = self.Block(diode_model)
        self.vsl_d2 = self.Block(diode_model)
        self.connect(self.device.vsl, self.vsl_res.a)
        self.connect(self.vsl_res.b, self.vsl_d1.anode)
        self.connect(self.vsl_d1.cathode, self.vsl_d2.anode)
        self.connect(self.vsl_d2.cathode.adapt_to(Ground()), self.gnd)

    def generate(self):
        super().generate()
        if self.get(self.dc.is_connected()):  # 4-line serial
            self.connect(self.gnd.as_digital_source(), self.device.bs0)
        else:  # 3-line serial
            self.connect(self.pwr.as_digital_source(), self.device.bs0)
