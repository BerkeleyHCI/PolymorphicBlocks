from edg.parts.PassiveConnector_Fpc import Fpc050BottomFlip
from edg import *
from edg.abstract_parts import *


class Er_Tft_128_3_Outline(InternalSubcircuit, FootprintBlock):
    """Footprint for TFT panel outline"""

    def contents(self) -> None:
        super().contents()
        self.footprint('U', 'edg:Lcd_Er_Tft1_28_3_Outline', {},
                       'EastRising', 'ER-TFT1.28-3',
                       datasheet='https://www.buydisplay.com/download/manual/ER-TFT1.28-3_Datasheet.pdf')


class Er_Tft_128_3_Device(InternalSubcircuit, Nonstrict3v3Compatible, Block):
    """15-pin FPC connector for the ER-TFT1.28-3 device"""

    def __init__(self) -> None:
        super().__init__()

        self.conn = self.Block(Fpc050BottomFlip(length=15))

        # Power pins
        self.vdd = self.Export(self.conn.pins.request('4').adapt_to(VoltageSink(
            voltage_limits=self.nonstrict_3v3_compatible.then_else(
                (2.5, 3.6) * Volt,  # abs max is 4.6v
                (2.5, 3.3) * Volt),
        )))
        self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()))
        # Backlight control
        self.ledk = self.Export(self.conn.pins.request('2'))
        self.leda = self.Export(self.conn.pins.request('3'))

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3)*Volt,
            input_threshold_factor=(0.3, 0.7)
        )

        self.rs = self.Export(self.conn.pins.request('5').adapt_to(DigitalSink()))

        # Control pins
        self.spi = self.Port(SpiPeripheral.empty())
        self.cs = self.Export(self.conn.pins.request('6').adapt_to(dio_model))
        self.connect(self.spi.sck, self.conn.pins.request('7').adapt_to(dio_model))
        self.connect(self.spi.mosi, self.conn.pins.request('8').adapt_to(dio_model))

        self.miso_nc = self.Block(DigitalBidirNotConnected())
        self.connect(self.spi.miso, self.miso_nc.port)

        self.rst = self.Export(self.conn.pins.request('9').adapt_to(DigitalSink()))

        # Capacitive Touch Panel (CTP)
        self.ctp_i2c = self.Port(I2cTarget(DigitalBidir.empty(), addresses=[0x15]),)

        self.ctp_vdd = self.Export(self.conn.pins.request('10').adapt_to(VoltageSink(
            voltage_limits=(2.7, 3.6) * Volt,
            current_draw=(5 * uAmp, 2.5 * mAmp)
        )))

        self.connect(self.gnd, self.conn.pins.request('11').adapt_to(Ground()))

        self.ctp_rst = self.Export(self.conn.pins.request('12').adapt_to(dio_model))
        self.ctp_int = self.Export(self.conn.pins.request('13').adapt_to(dio_model))
        self.connect(self.ctp_i2c.sda, self.conn.pins.request('14').adapt_to(dio_model))
        self.connect(self.ctp_i2c.scl, self.conn.pins.request('15').adapt_to(dio_model))


class Er_Tft_128_3(Lcd, Resettable, Block):
    """GC9A01-based 1.28" 240x240 TFT, with optional CST816S-based capacitive touch panel."""

    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Er_Tft_128_3_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.spi = self.Export(self.ic.spi)
        self.cs = self.Export(self.ic.cs)
        self.dc = self.Export(self.ic.rs)
        # touch interface
        self.ctp_i2c = self.Export(self.ic.ctp_i2c, optional=True, doc='Touch panel interface i2c')
        self.ctp_rst = self.Export(self.ic.ctp_rst, optional=True, doc='Touch panel interface')
        self.ctp_int = self.Export(self.ic.ctp_int, optional=True, doc='Touch panel interface')

    def contents(self):
        super().contents()
        self.connect(self.reset, self.ic.rst)
        self.require(self.reset.is_connected())

        # self.lcd = self.Block(Er_Tft_128_3_Outline())  # for ic outline

        self.connect(self.ic.ledk.adapt_to(Ground()), self.gnd)
        forward_current = (24, 30)*mAmp
        self.led_res = self.Block(Resistor(
            resistance=(self.pwr.link().voltage.upper() / forward_current.upper(),
                        self.pwr.link().voltage.lower() / forward_current.lower())))
        self.connect(self.led_res.a.adapt_to(VoltageSink(current_draw=(1, 40) * mAmp)), self.pwr)
        self.connect(self.led_res.b, self.ic.leda)
        self.connect(self.pwr, self.ic.ctp_vdd)
        self.require(self.ctp_i2c.is_connected() == self.ctp_rst.is_connected())
        self.require(self.ctp_i2c.is_connected() == self.ctp_int.is_connected())

