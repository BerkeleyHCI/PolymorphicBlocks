import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class IotThermalCamera(JlcBoardTop):
    """Dual-mode IR and RGB camera board with ESP32 and ethernet PoE"""

    @override
    def contents(self) -> None:
        super().contents()

        # IMPORTANT! use only USB OR PoE, both cannot be used simultaneously since this is a non-isolated converter
        self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3) * Amp))

        self.eth = self.Block(Hy931147c())
        self.poe = self.Block(Tps2378(poe_class=0))
        # allow using a jumper to disable and isolate PoE while still using ethernet
        (self.poe_jmp,), _ = self.chain(self.eth.poe, self.Block(PoeJumper()), self.poe.poe)

        self.gnd = self.connect(self.usb.gnd, self.poe.gnd)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)
        self.tp_poe = self.Block(VoltageTestPoint()).connected(self.poe.pwr_out)

        with self.implicit_connect(  # POWER
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.reg_poe, self.prot_v5), _ = self.chain(
                self.poe.pwr_out,
                imp.Block(BuckConverter(output_voltage=5.0 * Volt(tol=0.05))),
                imp.Block(ProtectionZenerDiode(voltage=(5.5, 7) * Volt)),
            )

            self.v5_merge = self.Block(MergedVoltageSource()).connected_from(self.reg_poe.pwr_out, self.usb.pwr)

            (self.choke, self.tp_pwr), _ = self.chain(
                self.v5_merge.pwr_out, self.Block(SeriesPowerFerriteBead()), self.Block(VoltageTestPoint())
            )
            self.pwr = self.connect(self.choke.pwr_out)

            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.pwr,
                imp.Block(BuckConverter(output_voltage=3.3 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9) * Volt)),
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

            (self.reg_3v0,), _ = self.chain(self.v3v3, imp.Block(LinearRegulator(output_voltage=3.0 * Volt(tol=0.03))))
            self.v3v0 = self.connect(self.reg_3v0.pwr_out)

            (self.reg_2v8,), _ = self.chain(self.v3v3, imp.Block(LinearRegulator(output_voltage=2.8 * Volt(tol=0.03))))
            self.v2v8 = self.connect(self.reg_2v8.pwr_out)

            (self.reg_1v2,), _ = self.chain(self.v3v3, imp.Block(LinearRegulator(output_voltage=1.2 * Volt(tol=0.03))))
            self.v1v2 = self.connect(self.reg_1v2.pwr_out)

        # 3V3 DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request("ledr"))

            reset_line = self.mcu.gpio.request("reset")
            int_line = self.mcu.gpio.request("int")

            self.connect(self.eth.gnd, self.gnd)
            self.connect(self.eth.pwr_led, self.v3v3)
            self.phy = imp.Block(W5500())
            self.connect(self.eth.eth, self.phy.eth)
            self.connect(self.mcu.spi.request("eth_spi"), self.phy.spi)
            self.connect(self.mcu.gpio.request("eth_cs"), self.phy.cs)
            self.connect(int_line, self.phy.int)

            self.connect(self.usb.usb, self.mcu.usb.request())

            self.i2c = self.mcu.i2c.request("i2c")
            (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
                self.i2c, imp.Block(I2cPullup()), imp.Block(I2cTestPoint("i2c"))
            )

            self.dist = imp.Block(Vl53l5cx())
            self.connect(self.i2c, self.dist.i2c)

            self.pd = imp.Block(Fusb302b())
            self.connect(self.usb.pwr, self.pd.vbus)
            self.connect(self.usb.cc, self.pd.cc)
            self.connect(self.i2c, self.pd.i2c)
            self.connect(int_line, self.pd.int)

            # out of IOs on the main ESP32S3
            self.ioe = imp.Block(IoController())
            self.connect(self.ioe.with_mixin(IoControllerI2cTarget()).i2c_target.request("i2c"), self.i2c)
            self.connect(self.ioe.gpio.request("eth_grn"), self.eth.led_grn_sink)
            self.connect(self.ioe.gpio.request("eth_yel"), self.eth.led_yel_sink)

            (self.poe_sense,), _ = self.chain(
                self.pwr,
                imp.Block(VoltageSenseDivider(full_scale_voltage=3.0 * Volt(tol=0.1), impedance=(1, 10) * kOhm)),
                self.ioe.adc.request("pwr_sense"),
            )

        # CAMERA MULTI DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.cam = imp.Block(Ov2640_Fpc24())
            self.connect(self.cam.pwr, self.v3v0)
            self.connect(self.cam.pwr_analog, self.v2v8)
            self.connect(self.cam.pwr_digital, self.v1v2)
            self.connect(self.cam.dvp8, self.mcu.with_mixin(IoControllerDvp8()).dvp8.request("cam"))
            self.connect(self.cam.sio, self.i2c)
            self.connect(self.cam.reset, reset_line)

            self.flir = imp.Block(FlirLepton())
            self.connect(self.flir.pwr_io, self.v3v0)
            self.connect(self.flir.pwr, self.v2v8)
            self.connect(self.flir.pwr_core, self.v1v2)
            self.connect(self.flir.spi, self.mcu.spi.request("flir"))
            self.connect(self.flir.cci, self.i2c)
            self.connect(self.flir.reset, reset_line)
            self.connect(self.flir.shutdown, self.mcu.gpio.request("flir_pwrdn"))
            self.connect(self.flir.cs, self.mcu.gpio.request("flir_cs"))
            self.connect(self.flir.vsync, self.mcu.gpio.request("flir_vsync"))

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Esp32s3_Wroom_1),
                (["ioe"], Ch32v003),
                (["reg_poe"], Lmr38020),
                (["reg_3v3"], Tps54202h),
                (["cam", "device", "conn"], Fpc050BottomFlip),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (Ch32vSdiHeader, Ch32vSdiTc2030),
                (TagConnect, TagConnectNonLegged),
                (TestPoint, CompactKeystone5015),
                (LinearRegulator, Tlv757p),  # default type for all LDOs
            ],
            instance_values=[
                (["refdes_prefix"], "T"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        "reset=25",
                        "cam.vsync=24",
                        "cam.href=23",
                        "cam.y7=22",
                        "cam.xclk=21",
                        "cam.y6=20",
                        "cam.y5=15",
                        "cam.pclk=19",
                        "cam.y0=18",
                        "cam.y1=17",
                        "cam.y4=10",
                        "cam.y3=11",
                        "cam.y2=12",
                        "i2c.sda=32",
                        "i2c.scl=33",
                        "flir_pwrdn=34",
                        "flir_cs=38",
                        "flir.sck=39",
                        "flir.mosi=5",
                        "flir.miso=4",
                        "flir_vsync=6",
                        "ledr=_GPIO0_STRAP",
                        "int=31",
                        "eth_cs=35",
                        "eth_spi.sck=9",
                        "eth_spi.mosi=8",
                        "eth_spi.miso=7",
                    ],
                ),
                (
                    ["ioe", "pin_assigns"],
                    [
                        "i2c.scl=12",
                        "i2c.sda=11",
                        "pwr_sense=14",
                        "eth_grn=8",
                        "eth_yel=10",
                    ],
                ),
                (["mcu", "programming"], "uart-auto"),
                (["reg_2v8", "ic", "actual_dropout"], Range(0.0, 0.05)),  # 3.3V @ 100mA
                (["reg_3v0", "ic", "actual_dropout"], Range(0.0, 0.16)),  # 3.3V @ 400mA
                (["poe", "vdd_cap", "cap", "voltage_margin"], 1.5),  # reduce excessive overhead to allow basic part
                (["reg_poe", "frequency"], Range.from_tolerance(800e3, 0.1)),
                (["reg_poe", "hf_cap", "cap", "voltage_margin"], 1.5),
                (["eth", "cap", "voltage_margin"], 1.0),  # 1kV rated only
                (["reg_poe", "power_path", "in_cap", "cap", "voltage_margin"], 1.5),
                (["poe", "prot", "diode", "filter_footprints"], ["Diode_SMD:D_SMA"]),
                (["poe", "den", "resistance"], Range.from_tolerance(25000, 0.05)),  # find a basic part
                (["phy", "exres1", "res", "require_basic_part"], False),
            ],
            class_values=[
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),
                (ProtectionZenerDiode, ["diode", "filter_footprints"], ["Diode_SMD:D_SOD-123"]),
                (JlcInductor, ["manual_frequency_rating"], Range(0, 9e6)),
            ],
        )


class IotThermalCameraTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(IotThermalCamera)
