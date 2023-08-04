from electronics_abstract_parts import *
from electronics_lib import Fpc030Bottom


class Er_Oled_096_1c_Outline(InternalSubcircuit, FootprintBlock):
    """Footprint for OLED panel outline"""
    def contents(self) -> None:
        super().contents()
        self.footprint('U', 'edg:Lcd_Er_Oled0.96_1C_Outline', {},
                       'EastRising', 'ER-OLED0.96-1C',
                       datasheet='https://www.buydisplay.com/download/manual/ER-OLED0.96-1C_Datasheet.pdf')


class Er_Oled_096_1c_Device(InternalSubcircuit, Block):
    """31-pin FPC connector for the ER-OLED0.96-1C device, configured to run off internal DC/DC"""
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.Block(Fpc030Bottom(length=31))
        self.lcd = self.Block(Er_Oled_096_1c_Outline())  # for device outline

        self.vdd = self.Export(self.conn.pins.request('8').adapt_to(VoltageSink(
            voltage_limits=(1.65, 3.5)*Volt,  # abs max is 4v
            current_draw=(10, 800)*uAmp  # sleep mode current to supply current from SSD1357 datasheet
        )))
        self.connect(self.vdd, self.conn.pins.request('17').adapt_to(VoltageSink()))

        self.vss = self.Export(self.conn.pins.request('7').adapt_to(Ground()), [Common])
        self.connect(self.vss,
                     self.conn.pins.request('1').adapt_to(Ground()),  # VLSS
                     self.conn.pins.request('26').adapt_to(Ground()),  # VLL
                     self.conn.pins.request('31').adapt_to(Ground()))  # VLSS

        self.vcc = self.Export(self.conn.pins.request('5').adapt_to(VoltageSink(
          voltage_limits=(14.5, 15.5)*Volt,  # abs max is 8-19v
          current_draw=(0.010, 46)*mAmp  # sleep mode current to normal mode with all pixels on
        )))
        self.connect(self.vcc, self.conn.pins.request('27').adapt_to(VoltageSink()))

        self.iref = self.Export(self.conn.pins.request('6'))
        self.vcomh = self.Export(self.conn.pins.request('3').adapt_to(VoltageSource(
            voltage_out=self.vcc.voltage_out,  # assumed
            current_limits=0*mAmp(tol=0)  # external draw not allowed
        )))
        self.connect(self.vcomh, self.conn.pins.request('29').adapt_to(VoltageSink()))

        self.vsl = self.Export(self.conn.pins.request('2'))
        self.connect(self.vsl, self.conn.pins.request('30'))

        self.vp = self.Export(self.conn.pins.request('4'))
        self.connect(self.vp, self.conn.pins.request('28'))

        din_model = DigitalSink.from_supply(
            self.vss, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3),  # SSD1357 datasheet, Table 7-1 and 8-1
            input_threshold_factor=(0.2, 0.8)
        )

        self.bs0 = self.Export(self.conn.pins.request('14').adapt_to(din_model))
        self.bs1 = self.Export(self.conn.pins.request('13').adapt_to(din_model))
        self.connect(self.conn.pins.request('12').adapt_to(Ground()), self.vss)  # BS2, 0 for any serial

        self.res = self.Export(self.conn.pins.request('9').adapt_to(din_model))
        self.cs = self.Export(self.conn.pins.request('11').adapt_to(din_model))
        self.dc = self.Export(self.conn.pins.request('10').adapt_to(din_model))

        self.d0 = self.Export(self.conn.pins.request('18').adapt_to(din_model))
        self.d1 = self.Export(self.conn.pins.request('19').adapt_to(din_model))
        self.d2 = self.Export(self.conn.pins.request('20').adapt_to(din_model), optional=True)

        self.connect(self.vss,
                     self.conn.pins.request('16').adapt_to(Ground()),  # RD#, only for parallel
                     self.conn.pins.request('15').adapt_to(Ground()),  # R/W#, only for parallel
                     self.conn.pins.request('21').adapt_to(Ground()),  # D3
                     self.conn.pins.request('22').adapt_to(Ground()),  # D4
                     self.conn.pins.request('23').adapt_to(Ground()),  # D5
                     self.conn.pins.request('24').adapt_to(Ground()),  # D6
                     self.conn.pins.request('25').adapt_to(Ground()))  # D7


class Er_Oled_096_1c(Oled, GeneratorBlock):
    """SSD1357-based 0.96" 128x64 RGB OLED, in either I2C or SPI mode."""
    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Er_Oled_096_1c_Device())
        self.gnd = self.Export(self.device.vss, [Common])
        self.vcc = self.Export(self.device.vcc)  # device power
        self.pwr = self.Export(self.device.vdd)  # logic power
        self.reset = self.Export(self.device.res)
        self.spi = self.Port(SpiSlave.empty(), optional=True)
        self.cs = self.Port(DigitalSink.empty(), optional=True)
        self.dc = self.Port(DigitalSink.empty(), optional=True)
        self.i2c = self.Port(I2cSlave.empty(), optional=True)
        self.generator_param(self.spi.is_connected(), self.dc.is_connected(), self.i2c.is_connected())

    def contents(self):
        super().contents()

        self.iref_res = self.Block(Resistor(resistance=390*kOhm(tol=0.05)))  # TODO dynamic sizing
        self.connect(self.iref_res.a, self.device.iref)
        self.connect(self.iref_res.b.adapt_to(Ground()), self.gnd)
        self.vcomh_cap = self.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2))).connected(self.gnd, self.device.vcomh)

        self.vdd_cap1 = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vdd)
        self.vbat_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))\
            .connected(self.gnd, self.device.vbat)
        self.vcc_cap = self.Block(DecouplingCapacitor(capacitance=(2.2*0.8, 20)*uFarad))\
            .connected(self.gnd, self.device.vcc)

    def generate(self):
        super().generate()

        gnd_digital = self.gnd.as_digital_source()

        if self.get(self.i2c.is_connected()):
            pwr_digital = self.pwr.as_digital_source()  # workaround for issue #259: if this is never used it creates a broken empty adapter
            self.connect(self.device.bs0, gnd_digital)
            self.connect(self.device.bs1, pwr_digital)

            self.connect(self.i2c.scl, self.device.d0)
            self.connect(self.i2c.sda, self.device.d1, self.device.d2)
            self.connect(self.device.dc, gnd_digital)  # addr, TODO support I2C addr
            self.connect(self.device.cs, gnd_digital)
            self.require(~self.spi.is_connected() & ~self.cs.is_connected() & ~self.dc.is_connected())
            self.assign(self.i2c.addresses, [0x3c])
        elif self.get(self.spi.is_connected()):
            self.connect(self.device.bs1, gnd_digital)
            self.connect(self.spi.sck, self.device.d0)
            self.connect(self.spi.mosi, self.device.d1)
            self.connect(self.cs, self.device.cs)
            # D2 not-connected
            if self.get(self.dc.is_connected()):  # 4-line SPI
                self.connect(self.device.bs0, gnd_digital)
                self.connect(self.dc, self.device.dc)
            else:  # 3-line SPI
                pwr_digital = self.pwr.as_digital_source()
                self.connect(self.device.bs0, pwr_digital)
                self.connect(self.device.dc, gnd_digital)
            self.require(~self.i2c.is_connected())

        self.require(self.spi.is_connected() | self.i2c.is_connected())
