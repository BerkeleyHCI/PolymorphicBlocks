import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class IotFan(JlcBoardTop):
    """IoT fan controller with a 12v barrel jack input and a CPU fan connector."""

    @override
    def contents(self) -> None:
        super().contents()

        self.pwr = self.Block(PowerBarrelJack(voltage_out=12 * Volt(tol=0.05), current_limits=(0, 5) * Amp))

        self.vin = self.connect(self.pwr.pwr)
        self.gnd = self.connect(self.pwr.gnd)

        self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.pwr.pwr)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

        # POWER
        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.vin_sense = imp.Block(Ina219(10 * mOhm(tol=0.01)))
            self.connect(self.vin_sense.sense_pos, self.vin)

            (self.reg_5v, self.tp_5v, self.prot_5v), _ = self.chain(
                self.vin_sense.sense_neg,
                imp.Block(VoltageRegulator(output_voltage=4.5 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(5.5, 6.8) * Volt)),
            )
            self.v5 = self.connect(self.reg_5v.pwr_out)

            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.v5,
                imp.Block(VoltageRegulator(output_voltage=3.3 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9) * Volt)),
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

        # 3V3 DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request("led"))

            self.enc = imp.Block(DigitalRotaryEncoder())
            self.connect(self.enc.a, self.mcu.gpio.request("enc_a"))
            self.connect(self.enc.b, self.mcu.gpio.request("enc_b"))
            self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request("enc_sw"))

            mcu_i2c = self.mcu.i2c.request("i2c")
            self.connect(self.vin_sense.pwr, self.v3v3)
            self.connect(self.vin_sense.i2c, mcu_i2c)

        # 5V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.rgb_ring,), _ = self.chain(self.mcu.gpio.request("rgb"), imp.Block(NeopixelArray(6)))

        # 12V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.fan = imp.Block(CpuFanConnector())
            self.fan_drv = imp.Block(HighSideSwitch(pull_resistance=4.7 * kOhm(tol=0.05), max_rds=0.3 * Ohm))
            self.connect(self.fan_drv.pwr, self.vin)
            self.connect(self.fan.pwr, self.fan_drv.output)
            self.connect(self.mcu.gpio.request(f"fan_drv"), self.fan_drv.control)

            self.connect(self.fan.sense, self.mcu.gpio.request(f"fan_tach"))
            (self.fan_ctl,), _ = self.chain(
                self.mcu.gpio.request(f"fan_pwm"),
                imp.Block(OpenDrainDriver()),
                self.fan.with_mixin(CpuFanPwmControl()).control,
            )

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Esp32s3_Wroom_1),
                (["reg_5v"], Tps54202h),
                (["reg_3v3"], Ap7215),
            ],
            instance_values=[
                (["refdes_prefix"], "F"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        # "v12_sense=4",
                        # "rgb=_GPIO2_STRAP_EXT_PU",  # force using the strapping pin, since we're out of IOs
                        # "led=_GPIO9_STRAP",  # force using the strapping / boot mode pin
                        # "fan_drv_0=5",
                        # "fan_ctl_0=8",
                        # "fan_sense_0=9",
                        # "fan_drv_1=10",
                        # "fan_ctl_1=13",
                        # "fan_sense_1=12",
                        # "enc_sw=25",
                        # "enc_b=16",
                        # "enc_a=26",
                    ],
                ),
                (["mcu", "programming"], "uart-auto"),
                (["reg_5v", "power_path", "inductor", "manual_frequency_rating"], Range(0, 9e6)),
                (["fan_drv", "drv", "footprint_spec"], "Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic"),
                # gate voltage limit parsing is very unreliable
                (["fan_drv", "drv", "gate_voltage"], Range(0, 0)),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (PowerBarrelJack, Pj_036ah),
                (Neopixel, Sk6805_Ec15),
                (TestPoint, CompactKeystone5015),
                (TagConnect, TagConnectNonLegged),
            ],
            class_values=[
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),  # RH-5015, which is actually in stock
            ],
        )


class IotFanTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(IotFan)
