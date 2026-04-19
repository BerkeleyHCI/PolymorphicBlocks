from typing_extensions import override

from .PassiveConnector_Fpc import Fpc050Bottom
from ..abstract_parts import *


class Er_Tft_128_3_Outline(InternalSubcircuit, FootprintBlock):
    """Footprint for TFT panel outline"""

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "U",
            "edg:Lcd_Er_Tft1_28_3_Outline",
            {},
            "EastRising",
            "ER-TFT1.28-3",
            datasheet="https://www.buydisplay.com/download/manual/ER-TFT1.28-3_Datasheet.pdf",
        )


class Er_Tft_128_3_Device(InternalSubcircuit, Nonstrict3v3Compatible, Block):
    """15-pin FPC connector for the ER-TFT1.28-3 device"""

    def __init__(self) -> None:
        super().__init__()

        # Power pins
        self.gnd = self.Port(Ground())
        self.vdd = self.Port(
            VoltageSink(
                voltage_limits=self.nonstrict_3v3_compatible.then_else(
                    (2.5, 3.6) * Volt, (2.5, 3.3) * Volt  # abs max is 4.6v
                ),
            )
        )
        # Backlight control
        self.ledk = self.Port(Ground())
        self.leda = self.Port(Passive())

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd, voltage_limit_tolerance=(-0.3, 0.3) * Volt, input_threshold_factor=(0.3, 0.7)
        )
        din_model = DigitalSink.from_bidir(dio_model)

        self.rs = self.Port(din_model)

        # Control pins
        self.spi = self.Port(SpiPeripheral(dio_model))
        self.cs = self.Port(din_model)
        self.rst = self.Port(din_model)

        # Capacitive Touch Panel (CTP)
        self.ctp_vdd = self.Port(VoltageSink(voltage_limits=(2.7, 3.6) * Volt, current_draw=(5 * uAmp, 2.5 * mAmp)))
        self.ctp_i2c = self.Port(I2cTarget(dio_model, addresses=[0x15]))

        self.ctp_rst = self.Port(din_model)
        self.ctp_int = self.Port(din_model)

        self.conn = self.Block(Fpc050Bottom(length=15)).connected(
            {
                # Pin numbering in the doc is flipped in the footprint
                "15": self.gnd,
                "12": self.vdd,
                "14": self.ledk,
                "13": self.leda,
                "11": self.rs,
                "10": self.cs,
                "9": self.spi.sck,
                "8": self.spi.mosi,
                "7": self.rst,
                "6": self.ctp_vdd,
                "5": self.gnd,
                "4": self.ctp_rst,
                "3": self.ctp_int,
                "2": self.ctp_i2c.sda,
                "1": self.ctp_i2c.scl,
            }
        )


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
        self.ctp_i2c = self.Export(self.ic.ctp_i2c, optional=True, doc="Touch panel interface i2c")
        self.ctp_rst = self.Export(self.ic.ctp_rst, optional=True, doc="Touch panel interface")
        self.ctp_int = self.Export(self.ic.ctp_int, optional=True, doc="Touch panel interface")

    @override
    def contents(self) -> None:
        super().contents()
        self.connect(self.reset, self.ic.rst)
        self.require(self.reset.is_connected())

        self.lcd = self.Block(Er_Tft_128_3_Outline())  # for ic outline

        self.connect(self.ic.ledk, self.gnd)
        forward_current = (24, 30) * mAmp
        forward_voltage = 2.9 * Volt
        self.led_res = self.Block(
            Resistor(
                resistance=(
                    (self.pwr.link().voltage.upper() - forward_voltage) / forward_current.upper(),
                    (self.pwr.link().voltage.lower() - forward_voltage) / forward_current.lower(),
                )
            )
        )
        self.connect(self.led_res.a.adapt_to(VoltageSink(current_draw=forward_current)), self.pwr)
        self.connect(self.led_res.b, self.ic.leda)
        self.connect(self.pwr, self.ic.ctp_vdd)
        self.require(self.ctp_i2c.is_connected() == self.ctp_rst.is_connected())
        self.require(self.ctp_i2c.is_connected() == self.ctp_int.is_connected())
