from ..abstract_parts import *
from .PassiveConnector_Fpc import Fpc050Bottom


class Ch280qv10_Ct_Outline(InternalSubcircuit, FootprintBlock):
    def contents(self) -> None:
        super().contents()
        self.footprint('U', 'edg:Lcd_Ch280qv10_Ct_Outline', {},
                       'Adafruit', '2770',
                       datasheet='https://cdn-shop.adafruit.com/product-files/2770/SPEC-CH280QV10-CT_Rev.D.pdf')


class Ch280qv10_Ct_Device(InternalSubcircuit, Nonstrict3v3Compatible, Block):
    """50-pin FPC connector for the CH280QV10-CT as sold by Adafruit
    Pin-compatible with some other 2.8" ILI9341 devices like ER-TFT028A2-4
    https://www.buydisplay.com/download/manual/ER-TFT028A2-4_Datasheet.pdf
    LCD only interface is compatible with the resistive touch version.
    Some other IL9341 devices are 50-pin and share the digital interface but have reversed LED backlight pinning.
    """
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.Block(Fpc050Bottom(length=50))

        gnd_pin = self.conn.pins.request('43')
        self.gnd = self.Export(gnd_pin.adapt_to(Ground()), [Common])
        self.connect(gnd_pin, self.conn.pins.request('48'), self.conn.pins.request('49'), self.conn.pins.request('50'))

        iovcc_pin = self.conn.pins.request('40')
        self.iovcc = self.Export(iovcc_pin.adapt_to(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=self.nonstrict_3v3_compatible.then_else(
                (1.65, 3.6)*Volt,  # extended range, abs max up to 4.6v
                (1.65, 3.3)*Volt),  # typ 1.8/2.8
        )))
        self.connect(iovcc_pin, self.conn.pins.request('41'))

        self.vci = self.Export(self.conn.pins.request('42').adapt_to(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=self.nonstrict_3v3_compatible.then_else(
                (2.5, 3.6)*Volt,  # extended range, abs max up to 4.6v
                (2.5, 3.3)*Volt),  # typ 2.8
        )))

        self.ledk = self.Export(self.conn.pins.request('1'))
        self.leda1 = self.Export(self.conn.pins.request('2'))
        self.leda2 = self.Export(self.conn.pins.request('3'))
        self.leda3 = self.Export(self.conn.pins.request('4'))
        self.leda4 = self.Export(self.conn.pins.request('5'))

        self.connect(gnd_pin,  # per ILI9341 datasheet, fix to VDDI or VSS for pins not in use
                     self.conn.pins.request('11'),  # VSYNC
                     self.conn.pins.request('12'),  # HSYNC
                     self.conn.pins.request('13'),  # DOTCLK
                     self.conn.pins.request('14'),  # DC
                     )
        for i in range(15, 33):  # DB0-17 pins unused, must be fixed to VSS lelvel
            self.connect(gnd_pin, self.conn.pins.request(str(i)))
        self.connect(iovcc_pin,  # per ILI9341 datasheet, must be fixed to VDDI level
                     self.conn.pins.request('35'),  # RDX
                     )

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.iovcc,
            input_threshold_factor=(0.3, 0.7)
        )
        din_model = DigitalSink.from_bidir(dio_model)
        dout_model = DigitalSource.from_bidir(dio_model)

        self.reset = self.Export(self.conn.pins.request('10').adapt_to(din_model))

        self.im0 = self.Export(self.conn.pins.request('6').adapt_to(din_model))
        self.im1 = self.Export(self.conn.pins.request('7').adapt_to(din_model))
        self.im2 = self.Export(self.conn.pins.request('8').adapt_to(din_model))
        self.im3 = self.Export(self.conn.pins.request('9').adapt_to(din_model))

        self.sdo = self.Export(self.conn.pins.request('33').adapt_to(dout_model))
        self.sdi = self.Export(self.conn.pins.request('34').adapt_to(din_model))
        self.wr_rs = self.Export(self.conn.pins.request('36').adapt_to(din_model))
        self.rs_scl = self.Export(self.conn.pins.request('37').adapt_to(din_model))
        self.cs = self.Export(self.conn.pins.request('38').adapt_to(din_model))
        # pin 39 TE out unused

        ctp_dio_model = DigitalBidir.from_supply(
            self.gnd, self.iovcc,
            input_threshold_abs=(1.0, 1.9)*Volt
        )
        self.ctp_i2c = self.Port(I2cTarget(DigitalBidir.empty(), [0x38]), optional=True)
        self.connect(self.conn.pins.request('44').adapt_to(din_model), self.ctp_i2c.scl)
        self.connect(self.conn.pins.request('45').adapt_to(dio_model), self.ctp_i2c.sda)
        # pin 46 is CTQ IRQ, unused (semantics not defined)
        self.ctp_res = self.Export(self.conn.pins.request('47').adapt_to(DigitalSink.from_bidir(ctp_dio_model)))
        self.require(self.ctp_i2c.is_connected().implies(self.ctp_res.is_connected()))


class Ch280qv10_Ct(Lcd, Resettable, Block):
    """ILI9341-based 2.8" 320x240 color TFT supporting SPI interface and with optional capacitive touch
    Based on this example design https://www.adafruit.com/product/1947 / https://learn.adafruit.com/adafruit-2-8-tft-touch-shield-v2/downloads"""
    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Ch280qv10_Ct_Device())
        self.gnd = self.Export(self.device.gnd, [Common])
        self.pwr = self.Export(self.device.iovcc, [Power])
        self.spi = self.Port(SpiPeripheral.empty())
        self.cs = self.Export(self.device.cs)
        self.dc = self.Export(self.device.wr_rs)

        self.ctp_i2c = self.Export(self.device.ctp_i2c, optional=True)

    def contents(self):
        super().contents()
        self.connect(self.pwr, self.device.vci)
        self.connect(self.reset, self.device.reset, self.device.ctp_res)  # combined LCD and CTP reset
        self.require(self.reset.is_connected())

        self.lcd = self.Block(Ch280qv10_Ct_Outline())  # for device outline

        gnd_digital = self.gnd.as_digital_source()
        pwr_digital = self.pwr.as_digital_source()
        self.connect(self.device.im0, gnd_digital)  # 4-wire 8-bit SPI with SDO
        self.connect(self.device.im1, pwr_digital)
        self.connect(self.device.im2, pwr_digital)
        self.connect(self.device.im3, pwr_digital)

        self.connect(self.spi.sck, self.device.rs_scl)
        self.connect(self.spi.mosi, self.device.sdi)
        self.connect(self.spi.miso, self.device.sdo)

        self.connect(self.device.ledk.adapt_to(Ground()), self.gnd)
        self.led_res = ElementDict[Resistor]()
        for i, leda in [('1', self.device.leda1), ('2', self.device.leda2),
                        ('3', self.device.leda3), ('4', self.device.leda4)]:
            led_res = self.led_res[i] = self.Block(  # TODO dynamic LED resistance, this is sized for 5v
                Resistor(47*Ohm(tol=0.05), power=self.pwr.link().voltage * self.pwr.link().voltage / 47))
            self.connect(led_res.a.adapt_to(VoltageSink(current_draw=(0, 80)*mAmp)), self.pwr)  # TODO better current
            self.connect(led_res.b, leda)
