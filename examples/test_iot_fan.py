import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class ControlSubboard(SubboardBlock):
    """Top sub-board with microcontroller and some UI components."""

    def __init__(self) -> None:
        super().__init__()

        self.gnd = self.Port(Ground.empty(), [Common])
        self.v3v3 = self.Port(VoltageSink.empty())
        self.v5 = self.Port(VoltageSink.empty())

        self.i2c = self.Port(I2cController.empty())
        self.spk = self.Port(DigitalSource.empty())
        self.drv = self.Port(DigitalSource.empty())
        self.pwm = self.Port(DigitalSource.empty())
        self.tach = self.Port(DigitalBidir.empty())
        self.enc_a = self.Port(DigitalBidir.empty())
        self.enc_b = self.Port(DigitalBidir.empty())
        self.enc_sw = self.Port(DigitalBidir.empty())

    def contents(self) -> None:
        super().contents()

        # 3V3 DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request("led"))

            self.connect(self.mcu.gpio.request("spk"), self.spk)
            self.connect(self.mcu.gpio.request("drv"), self.drv)
            self.connect(self.mcu.gpio.request("tach"), self.tach)
            self.connect(self.mcu.gpio.request("pwm"), self.pwm)
            self.connect(self.mcu.gpio.request("enc_a"), self.enc_a)
            self.connect(self.mcu.gpio.request("enc_b"), self.enc_b)
            self.connect(self.mcu.gpio.request("enc_sw"), self.enc_sw)
            self.connect(self.i2c, self.mcu.i2c.request("i2c"))
            # 2.2kOhm as mandated by the VL53L5CX datasheet
            (self.i2c_pull,), _ = self.chain(self.i2c, imp.Block(I2cPullup(2.2 * kOhm(tol=0.05))))
            self.tp_i2c = self.Block(I2cTestPoint()).connected(self.i2c)

            self.dist = imp.Block(Vl53l5cx())
            self.connect(self.i2c, self.dist.i2c)

            self.als = imp.Block(Bh1750())
            self.connect(self.i2c, self.als.i2c)

            self.qwiic = imp.Block(QwiicTarget())
            self.connect(self.i2c, self.qwiic.i2c)

        # 5V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.npx_shift, self.npx_tp, self.npx), _ = self.chain(
                self.mcu.gpio.request("npx"),
                imp.Block(L74Ahct1g125()),
                imp.Block(DigitalTestPoint()),
                imp.Block(NeopixelArray(6)),
            )

        self.conn = self.Block(PinSocket254Pair(12), external=True)
        self.export_tap(self.gnd.net, self.conn.pins.request("1"))
        self.export_tap(self.v3v3.net, self.conn.pins.request("2"))
        self.export_tap(self.v5.net, self.conn.pins.request("3"))
        self.export_tap(self.i2c.scl.net, self.conn.pins.request("4"))
        self.export_tap(self.i2c.sda.net, self.conn.pins.request("5"))
        self.export_tap(self.spk.net, self.conn.pins.request("6"))
        self.export_tap(self.drv.net, self.conn.pins.request("7"))
        self.export_tap(self.pwm.net, self.conn.pins.request("8"))
        self.export_tap(self.tach.net, self.conn.pins.request("9"))
        self.export_tap(self.enc_a.net, self.conn.pins.request("10"))
        self.export_tap(self.enc_b.net, self.conn.pins.request("11"))
        self.export_tap(self.enc_sw.net, self.conn.pins.request("12"))


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
                imp.Block(VoltageRegulator(output_voltage=5.0 * Volt(tol=0.05))),
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
            self.connect(self.vin_sense.pwr, self.v3v3)

        self.control = self.Block(ControlSubboard())
        self.connect(self.control.gnd, self.gnd)
        self.connect(self.control.v3v3, self.v3v3)
        self.connect(self.control.v5, self.v5)

        # 3V3 DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.enc = imp.Block(DigitalRotaryEncoder())
            self.connect(self.enc.a, self.control.enc_a)
            self.connect(self.enc.b, self.control.enc_b)
            self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.control.enc_sw)

            self.connect(self.vin_sense.i2c, self.control.i2c)

        # 5V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), _ = self.chain(
                self.control.spk,
                imp.Block(LowPassRcDac(1 * kOhm(tol=0.05), 20 * kHertz(tol=0.5))),
                self.Block(AnalogTestPoint()),
                imp.Block(Pam8302a()),
                self.Block(Speaker()),
            )

        # 12V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.fan = imp.Block(CpuFanConnector())
            self.fan_drv = imp.Block(HighSideSwitch(pull_resistance=4.7 * kOhm(tol=0.05), max_rds=0.3 * Ohm))
            self.connect(self.fan_drv.pwr, self.vin)
            self.connect(self.fan.pwr, self.fan_drv.output)
            self.connect(self.control.drv, self.fan_drv.control)

            self.connect(self.fan.sense, self.control.tach)
            (self.fan_ctl,), _ = self.chain(
                self.control.pwm,
                imp.Block(OpenDrainDriver()),
                self.fan.with_mixin(CpuFanPwmControl()).control,
            )

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[],
            instance_values=[
                (["refdes_prefix"], "F"),  # unique refdes for panelization
                (
                    ["control", "mcu", "pin_assigns"],
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
                (["reg_5v", "power_path", "inductor", "manual_frequency_rating"], Range(0, 9e6)),
                (["fan_drv", "drv", "footprint_spec"], "Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic"),
                # gate voltage limit parsing is very unreliable
                (["fan_drv", "drv", "gate_voltage"], Range(0, 0)),
                (["vin_sense", "Rs", "res", "res", "require_basic_part"], False),  # current sense resistor
                (["spk_drv", "pwr", "current_draw"], Range(6.0e-7, 0.10)),  # restrict current draw for sizing
            ],
            class_refinements=[
                (IoController, Esp32s3_Wroom_1),
                (VoltageRegulator, Tps54202h),
                (EspProgrammingHeader, EspProgrammingTc2030),
                (PowerBarrelJack, Pj_036ah),
                (Neopixel, Sk6805_Ec15),
                (TestPoint, CompactKeystone5015),
                (TagConnect, TagConnectNonLegged),
                (PassiveConnector, JstPhKVertical),
            ],
            class_values=[
                (Esp32s3_Wroom_1, ["programming"], "uart-auto"),
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),  # RH-5015, which is actually in stock
            ],
        )


class IotFanTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(IotFan)
