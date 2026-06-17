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
        self.tp_gnd = self.Block(GroundTestPoint("gnd")).connected(self.gnd)

        self.i2c = self.Port(I2cController.empty())
        self.pd_int = self.Port(DigitalBidir.empty())
        self.spk = self.Port(DigitalSource.empty())
        self.drv = self.Port(DigitalSource.empty())
        self.tach = self.Port(DigitalBidir.empty())
        self.pwm = self.Port(DigitalSource.empty())
        self.npx_en = self.Port(DigitalSource.empty())
        self.enc_a = self.Port(DigitalBidir.empty())
        self.enc_b = self.Port(DigitalBidir.empty())
        self.enc_sw = self.Port(DigitalBidir.empty())

        self.extra1 = self.Port(DigitalBidir.empty())

    @override
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

            self.connect(self.mcu.gpio.request("pd_int"), self.pd_int)
            self.connect(self.mcu.gpio.request("spk"), self.spk)
            self.connect(self.mcu.gpio.request("drv"), self.drv)
            self.connect(self.mcu.gpio.request("tach"), self.tach)
            self.connect(self.mcu.gpio.request("pwm"), self.pwm)
            self.connect(self.mcu.gpio.request("npx_en"), self.npx_en)
            self.connect(self.mcu.gpio.request("enc_a"), self.enc_a)
            self.connect(self.mcu.gpio.request("enc_b"), self.enc_b)
            self.connect(self.mcu.gpio.request("enc_sw"), self.enc_sw)

            self.connect(self.mcu.gpio.request("extra1"), self.extra1)

            self.connect(self.i2c, self.mcu.i2c.request("i2c"))
            # 2.2kOhm as mandated by the VL53L5CX datasheet
            (self.i2c_pull,), _ = self.chain(self.i2c, imp.Block(I2cPullup(2.2 * kOhm(tol=0.05))))

            self.dist = imp.Block(Vl53l5cx())
            self.connect(self.i2c, self.dist.i2c)

            self.als = imp.Block(Bh1750())
            self.connect(self.i2c, self.als.i2c)

            self.qwiic = imp.Block(QwiicTarget())
            self.connect(self.i2c, self.qwiic.i2c)

            # second qwiic port is on a seprate I2C bus
            (self.i2c2_pull, self.qwiic2), _ = self.chain(
                self.mcu.i2c.request("i2c2"), imp.Block(I2cPullup(2.2 * kOhm(tol=0.05))), imp.Block(QwiicTarget())
            )

        # 5V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.npx_shift, self.npx), _ = self.chain(
                self.mcu.gpio.request("npx"),
                imp.Block(L74Ahct1g125()),
                imp.Block(NeopixelArray(6)),
            )

        # left connector
        self.conn1 = self.Block(PinSocket2mmPair(8), external=True)
        self.export_tap(self.v3v3.net, self.conn1.pins.request("1"))
        self.export_tap(self.npx_en.net, self.conn1.pins.request("2"))
        self.export_tap(self.pwm.net, self.conn1.pins.request("3"))
        self.export_tap(self.spk.net, self.conn1.pins.request("4"))
        self.export_tap(self.pd_int.net, self.conn1.pins.request("5"))
        self.export_tap(self.i2c.scl.net, self.conn1.pins.request("6"))
        self.export_tap(self.i2c.sda.net, self.conn1.pins.request("7"))
        self.export_tap(self.gnd.net, self.conn1.pins.request("8"))

        # right connector
        self.conn2 = self.Block(PinSocket2mmPair(8), external=True)
        self.export_tap(self.v5.net, self.conn2.pins.request("1"))
        self.export_tap(self.tach.net, self.conn2.pins.request("2"))
        self.export_tap(self.drv.net, self.conn2.pins.request("3"))
        self.export_tap(self.extra1.net, self.conn2.pins.request("4"))
        self.export_tap(self.enc_a.net, self.conn2.pins.request("5"))
        self.export_tap(self.enc_b.net, self.conn2.pins.request("6"))
        self.export_tap(self.enc_sw.net, self.conn2.pins.request("7"))
        self.export_tap(self.gnd.net, self.conn2.pins.request("8"))


class IotFan(JlcBoardTop):
    """IoT controller with a 4-pin output that can either control / read a CPU fan or control a neopixel string.
    5 / 12 / 24v capable."""

    @override
    def contents(self) -> None:
        super().contents()

        # only populate ONE of these
        self.pwr = self.Block(PowerBarrelJack(voltage_out=(10, 24) * Volt, current_limits=(0, 5) * Amp))
        self.usb = self.Block(UsbCReceptacle(voltage_out=(5, 20) * Volt, current_limits=(0, 5) * Amp))
        self.pwr_merge = self.Block(MergedVoltageSource()).connected_from(self.pwr.pwr, self.usb.pwr)
        self.gnd = self.connect(self.pwr.gnd, self.usb.gnd)

        self.tp_vin = self.Block(VoltageTestPoint()).connected(self.pwr_merge.pwr_out)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

        # POWER
        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.vin_sense = imp.Block(Ina219(10 * mOhm(tol=0.01)))
            self.connect(self.pwr_merge.pwr_out, self.vin_sense.sense_pos)
            self.vin = self.connect(self.vin_sense.sense_pwr_out)

            (self.reg_5v, self.tp_5v, self.prot_5v), _ = self.chain(
                self.vin,
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

        self.extra1_sink = self.Block(DummyDigitalSink()).connected(self.control.extra1)

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

            self.pd = imp.Block(Fusb302b())
            self.connect(self.usb.pwr, self.pd.vbus)
            self.connect(self.usb.cc, self.pd.cc)
            self.connect(self.control.pd_int, self.pd.int)
            self.connect(self.control.i2c, self.pd.i2c)

        # 5V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.spk_dac, self.spk_drv, self.spk), _ = self.chain(
                self.control.spk,
                imp.Block(LowPassRcDac(1 * kOhm(tol=0.05), 20 * kHertz(tol=0.5))),
                imp.Block(Tpa2005d1(gain=Range.from_tolerance(4, 0.2))),
                self.Block(Speaker()),
            )

            # series resistor limits drive conflicts with fan controller
            (self.npx_shift, self.npx_res), _ = self.chain(
                self.control.pwm,
                imp.Block(L74Ahct1g125()),
                imp.Block(DigitalSeriesResistor(100 * Ohm(tol=0.05))),
            )
            self.connect(self.control.npx_en, self.npx_shift.disable)

        # 12V DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.fan = imp.Block(CpuFanConnector())
            self.fan_drv = imp.Block(HighSideSwitch(pull_resistance=4.7 * kOhm(tol=0.05), max_rds=0.3 * Ohm))
            (self._fan_forced,), _ = self.chain(  # fan is only to be used with 12v input
                self.vin, self.Block(ForcedVoltage(12 * Volt(tol=0.05))), self.fan_drv.pwr
            )
            self.connect(self.fan.pwr, self.fan_drv.output)
            self.connect(self.control.drv, self.fan_drv.control)

            self.connect(self.fan.sense, self.control.tach)
            (self.fan_ctl,), _ = self.chain(self.control.pwm, imp.Block(OpenDrainDriver()))
            self.connect(self.npx_res.output, self.fan_ctl.output, self.fan.with_mixin(CpuFanPwmControl()).control)

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["reg_5v"], Tps54202h),
                (["reg_3v3"], Tps54202h),
            ],
            instance_values=[
                (["refdes_prefix"], "F"),  # unique refdes for panelization
                (
                    ["control", "mcu", "pin_assigns"],
                    [  # for compatibility with esp32-c6 wroom: pins 15-26, 34 unavailable
                        "npx_en=5",
                        "pwm=8",
                        "spk=9",
                        "pd_int=10",
                        "i2c.scl=11",
                        "i2c.sda=12",
                        "enc_sw=31",
                        "enc_b=32",
                        "enc_a=33",
                        "extra1=35",
                        "drv=38",
                        "tach=39",
                        "npx=4",
                        "led=_GPIO0_STRAP",
                        "i2c2.scl=7",  # LP_I2C_SCL on -C6
                        "i2c2.sda=6",  # LP_I2C_SDA on -C6
                    ],
                ),
                (["fan_drv", "drv", "footprint_spec"], "Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic"),
                # gate voltage limit parsing is very unreliable
                (["fan_drv", "drv", "gate_voltage"], Range(0, 0)),
                (["vin_sense", "Rs", "res", "res", "require_basic_part"], False),  # current sense resistor
                (["spk_drv", "pwr", "current_draw"], Range(6.0e-7, 0.25)),  # restrict current draw for sizing
                (["npx_res", "output", "high_driver"], False),  # waive the driver conflict ERC
                # allow the regulator to track if needed
                (["reg_5v", "power_path", "dutycycle_limit"], Range(float("-inf"), float("inf"))),
                # ignore capacitance derating and lower margin on 24v input line
                (["reg_5v", "power_path", "in_cap", "cap", "exact_capacitance"], False),
                (["reg_5v", "power_path", "in_cap", "cap", "voltage_margin"], 1.25),
                (["control", "qwiic2", "pwr", "current_draw"], Range(0, 0)),
            ],
            class_refinements=[
                (IoController, Esp32s3_Wroom_1),
                (EspProgrammingHeader, EspProgrammingTc2030),
                (PowerBarrelJack, Pj_036ah),
                (Neopixel, Ws2812c_2020),
                (TestPoint, CompactKeystone5015),
                (TagConnect, TagConnectNonLegged),
                (PassiveConnector, PinHeader2mm),
            ],
            class_values=[
                (Esp32s3_Wroom_1, ["programming"], "uart-auto"),
                (JlcInductor, ["manual_frequency_rating"], Range(0, 9e6)),
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),
                (ProtectionZenerDiode, ["diode", "footprint_spec"], "Diode_SMD:D_SOD-123"),
                (Fusb302b, ["ic", "vbus", "voltage_limits"], Range(4.0, 28.0)),  # abs max ratings
            ],
        )


class IotFanTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(IotFan)
