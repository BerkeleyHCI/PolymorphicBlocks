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
            (self.usb_esd,), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request("led"))

            self.sw = self.Block(SwitchMatrix(nrows=3, ncols=4))
            self.connect(self.sw.cols, self.mcu.gpio.request_vector())
            self.connect(self.sw.rows, self.mcu.gpio.request_vector())

            self.enc = imp.Block(DigitalRotaryEncoder())
            self.connect(self.enc.a, self.mcu.gpio.request("enc_a"))
            self.connect(self.enc.b, self.mcu.gpio.request("enc_b"))
            self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request("enc_sw"))

            self.oled = imp.Block(Er_Oled_096_1_1())
            self.connect(self.mcu.spi.request("spi"), self.oled.spi)
            self.connect(self.mcu.gpio.request("oled_cs"), self.oled.cs)
            self.connect(self.mcu.gpio.request("oled_dc"), self.oled.dc)
            self.connect(self.mcu.gpio.request("oled_reset"), self.oled.reset)

        # Vbus 5v DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.usb.pwr, [Power]),
            ImplicitConnect(self.usb.gnd, [Common]),
        ) as imp:
            sw_npx = self.sw.with_mixin(SwitchMatrixNeopixels())
            self.connect(self.usb.gnd, sw_npx.npx_gnd)
            self.connect(self.usb.pwr, sw_npx.npx_pwr)
            (self.npx_shift, self.npx_tp), _ = self.chain(
                self.mcu.gpio.request("npx"), imp.Block(L74Ahct1g125()), imp.Block(DigitalTestPoint()), sw_npx.npx_din
            )

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            class_refinements=[
                (IoController, Ch32v203),
                (LinearRegulator, Ldl1117),
                (Switch, KailhSocket),
                (Neopixel, Sk6812Mini_E),
                (RotaryEncoder, Pec11s),
            ],
            instance_values=[(["mcu", "pin_assigns"], [])],  # TODO pinning: NPX must be SPI MOSI
            class_values=[
                # assume LEDs not run at full power to satisfy current limit checks
                (Sk6812Mini_E, ["pwr", "current_draw"], Range(0.001, 0.030)),
            ],
        )


class KeyboardTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(Keyboard)
