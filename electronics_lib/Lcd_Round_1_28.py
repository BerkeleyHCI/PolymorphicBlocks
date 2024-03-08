from electronics_abstract_parts import *
from electronics_lib import JstGhSmHorizontal


class Lcd_Round_1_28_Board_Device(InternalSubcircuit, Block):
    """30-pin FPC connector for the ER-OLED-0.96-1.1* device, configured to run off internal DC/DC"""
    def __init__(self) -> None:
        super().__init__()
        self.conn = self.Block(JstGhSmHorizontal(length=13))

        self.vdd = self.Export(self.conn.pins.request('1').adapt_to(VoltageSink(
            voltage_limits=(3.3, 5.0)*Volt,  # abs max is 4v
            current_draw=(1, 300)*uAmp  # sleep to operating
        )))
        self.gnd = self.Export(self.conn.pins.request('2').adapt_to(Ground()), [Common])

        din_model = DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3),  # SSD1306 datasheet, Table 11-1
            input_threshold_factor=(0.2, 0.8)
        )

        self.miso = self.Export(self.conn.pins.request('3').adapt_to(din_model))
        self.mosi = self.Export(self.conn.pins.request('4').adapt_to(din_model))
        self.sclk = self.Export(self.conn.pins.request('5').adapt_to(din_model))

        self.cs = self.Export(self.conn.pins.request('6').adapt_to(din_model))
        self.dc = self.Export(self.conn.pins.request('7').adapt_to(din_model))
        self.rst = self.Export(self.conn.pins.request('8').adapt_to(din_model))
        self.bl = self.Export(self.conn.pins.request('9').adapt_to(din_model))
        self.sda = self.Export(self.conn.pins.request('10').adapt_to(din_model))
        self.scl = self.Export(self.conn.pins.request('11').adapt_to(din_model))
        self.tp_int = self.Export(self.conn.pins.request('12').adapt_to(din_model))
        self.tp_rst = self.Export(self.conn.pins.request('13').adapt_to(din_model))

class Lcd_Round_1_28(Lcd, GeneratorBlock):
    """1.28 inch round lcd" 240 by 240 Color LCD with optional touch, ISP display interface and I2C touch sensing."""
    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Lcd_Round_1_28_Board_Device)
        self.reset = self.Export(self.device.rst)
        self.spi = self.Port(SpiPeripheral.empty())
        self.cs = self.Export(self.device.cs, optional=True)
        self.dc = self.Export(self.device.dc, optional=True)
        self.bled = self.Export(self.device.bl, optional=True)
        self.i2c = self.Port(I2cTarget.empty(), optional=True)
        self.tp_int = self.Export(self.device.tp_int, optional=True)
        self.tp_reset = self.Export(self.device.tp_rst, optional=True)

    def contents(self):
        super().contents()
        self.connect(self.spi.miso, self.device.miso)
        self.connect(self.spi.mosi, self.device.mosi)
        self.connect(self.spi.sck, self.device.sclk)

        self.connect(self.i2c.sda, self.device.sda)
        self.connect(self.i2c.scl, self.device.scl)

