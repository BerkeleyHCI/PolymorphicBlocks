"""
Mechanical keyboard example design.

Relies on footprints from external libraries.
In the KiCad Plugin and Content Manager, install the Keyswitch Kicad Library,
also on GitHub here https://github.com/perigoso/keyswitch-kicad-library
The project is set up to reference the third party library as installed by the KiCad
Plugin Manager, it does not need to be in your global library table.
"""

import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class Keyboard(SimpleBoardTop):
    @override
    def contents(self) -> None:
        super().contents()

        self.usb = self.Block(UsbCReceptacle())
        self.reg = self.Block(LinearRegulator(3.3 * Volt(tol=0.05)))
        self.connect(self.usb.gnd, self.reg.gnd)
        self.connect(self.usb.pwr, self.reg.pwr_in)

        with self.implicit_connect(
            ImplicitConnect(self.reg.pwr_out, [Power]),
            ImplicitConnect(self.reg.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            (self.usb_esd,), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request("led"))

            self.sw = self.Block(SwitchMatrix(ncols=3, nrows=4))
            self.connect(self.sw.cols, self.mcu.gpio.request_vector("sw_col"))
            self.connect(self.sw.rows, self.mcu.gpio.request_vector("sw_row"))

            self.enc = imp.Block(DigitalRotaryEncoder())
            self.connect(self.enc.a, self.mcu.gpio.request("enc_a"))
            self.connect(self.enc.b, self.mcu.gpio.request("enc_b"))
            self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request("enc_sw"))

            self.oled = imp.Block(Er_Oled_096_1_1())
            # use I2C because this chip only has one SPI which is used for NPX
            (self.i2c_pull,), _ = self.chain(self.mcu.i2c.request("i2c"), imp.Block(I2cPullup()), self.oled.i2c)
            self.connect(self.mcu.gpio.request("oled_rst"), self.oled.reset)

        # Vbus 5v DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.usb.pwr, [Power]),
            ImplicitConnect(self.usb.gnd, [Common]),
        ) as imp:
            sw_npx = self.sw.with_mixin(SwitchMatrixNeopixels())
            self.connect(self.usb.gnd, sw_npx.npx_gnd)
            self.connect(self.usb.pwr, sw_npx.npx_pwr)
            (self.npx_shift,), _ = self.chain(self.mcu.gpio.request("npx"), imp.Block(L74Ahct1g125()), sw_npx.npx_din)

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            class_refinements=[
                (IoController, Ch32v203),
                (LinearRegulator, Ap7215),
                (Switch, KailhSocket),
                (Neopixel, Sk6812Mini_E),
                (RotaryEncoder, Pec11s),
            ],
            instance_values=[
                (
                    ["mcu", "pin_assigns"],
                    [
                        "led=27",
                        "enc_a=9",
                        "enc_b=8",
                        "enc_sw=7",
                        "npx=28",  # MOSI pin, don't use other SPI pins 26 and 27
                        "i2c.scl=29",
                        "i2c.sda=30",
                        "oled_rst=15",
                        "sw_row_0=20",
                        "sw_row_1=19",
                        "sw_col_0=18",
                        "sw_row_2=13",
                        "sw_col_1=12",
                        "sw_row_3=11",
                        "sw_col_2=10",
                    ],
                )
            ],
            class_values=[
                # assume LEDs not run at full power to satisfy current limit checks
                (Sk6812Mini_E, ["pwr", "current_draw"], Range(0.001, 0.030)),
            ],
        )


class KeyboardTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(Keyboard)
