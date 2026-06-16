import unittest
from typing import Tuple

from typing_extensions import override

from edg import *
from .util import run_test_board


class Fpc050Tab(FootprintPassiveConnector):
    """0.5mm FPC tab pattern.
    This pattern has the contacts facing up, numbered top to bottom, tab edge towards right.

    This is reversed pin order if using a bottom entry connector."""

    allowed_pins = [8]  # only 8-pin footprint exists, for now

    @override
    def part_footprint_mfr_name(self, length: int) -> Tuple[str, str, str]:
        return (f"edg:FpcTab_1x{length:02d}_P0.50mm", "", "")


class Fpc050SocketTabPair(SubboardConnectorPair, GeneratorBlock):
    """A FPC socket on the external side and a matching tab pattern on the internal side.

    Parameters:
        socket = "top" | "bottom": the contact side for the socket.
    """

    def __init__(
        self,
        length: IntLike = 0,
        socket: StringLike = "bot",
    ) -> None:
        super().__init__()
        self.length = self.ArgParameter(length)
        self.socket = self.ArgParameter(socket)
        self.pins = self.Port(Vector(Passive.empty()))
        self.generator_param(self.length, self.pins.requested(), self.socket)

    @override
    def generate(self) -> None:
        super().generate()
        socket = self.get(self.socket)
        if socket == "top":
            self.ext: Fpc050 = self.Block(Fpc050Top(self.length), external=True)
            mirror = False
        elif socket == "bot":
            self.ext = self.Block(Fpc050Bottom(self.length), external=True)
            mirror = True
        else:
            raise ValueError(f"invalid ext_contact")

        self.int = self.Block(Fpc050Tab(self.length))

        length = self.get(self.length)
        assert length > 0, "explicit length required"

        self.pins.defined()
        for pin_num in self.get(self.pins.requested()):
            pin = self.pins.append_elt(Passive.empty(), pin_num)
            self.export_tap(pin, self.ext.pins.request(pin_num))
            if mirror:
                self.connect(pin, self.int.pins.request(str(length - (int(pin_num) - 1))))
            else:
                self.connect(pin, self.int.pins.request(pin_num))


class JoystickSubboard(SubboardBlock):
    """Joystick mounted on a FPC to allow for placement flexibility"""

    def __init__(self) -> None:
        super().__init__()

        self.stick = self.Block(XboxElite2Joystick())
        self.gnd = self.Export(self.stick.gnd, [Common])
        self.pwr = self.Export(self.stick.pwr, [Power])
        self.sw = self.Export(self.stick.sw)
        self.ax1 = self.Export(self.stick.ax1)
        self.ax2 = self.Export(self.stick.ax2)

        self.conn = self.Block(Fpc050SocketTabPair(8), external=True)
        self.export_tap(self.gnd.net, self.conn.pins.request("1"))
        self.export_tap(self.pwr.net, self.conn.pins.request("2"))
        self.export_tap(self.ax2.net, self.conn.pins.request("3"))
        self.export_tap(self.ax1.net, self.conn.pins.request("4"))
        self.export_tap(self.sw.net, self.conn.pins.request("6"))
        self.export_tap(self.gnd.net, self.conn.pins.request("8"))


class ButtonSubboard(SubboardBlock):
    """Button sub-board that sits on top of the main board, providing the D-pad and neopixel rings."""

    def __init__(self) -> None:
        super().__init__()

        self.gnd = self.Port(Ground.empty(), [Common])
        self.pwr = self.Port(VoltageSink.empty())

        self.vbat = self.Port(VoltageSink.empty())
        self.i2c = self.Port(I2cTarget.empty())
        self.io0 = self.Port(DigitalBidir.empty())

        self.tp_gnd = self.Block(GroundTestPoint("gnd")).connected(self.gnd)
        self.tp_pwr = self.Block(VoltageTestPoint("v3v3")).connected(self.pwr)
        self.tp_vbat = self.Block(VoltageTestPoint("vbat")).connected(self.vbat)
        self.tp_i2c = self.Block(I2cTestPoint("i2c")).connected(self.i2c)

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
            ImplicitConnect(self.pwr, [Power]),
        ) as imp:
            self.ioe = imp.Block(IoController())
            self.connect(self.ioe.with_mixin(IoControllerI2cTarget()).i2c_target.request("i2c"), self.i2c)
            self.connect(self.ioe.gpio.request("io0"), self.io0)

            # d-pad buttons
            self.sw = ElementDict[DigitalSwitch]()
            for i in range(8):
                sw = self.sw[i] = imp.Block(DigitalSwitch())
                self.connect(sw.out, self.ioe.gpio.request(f"dpad_{i}"))

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
            ImplicitConnect(self.vbat, [Power]),
        ) as imp:
            (self.npx_tp, self.npx_dpad, self.npx_js), _ = self.chain(
                self.ioe.gpio.request("npx"),
                imp.Block(DigitalTestPoint("npx")),
                imp.Block(NeopixelArray(8)),
                imp.Block(NeopixelArray(3)),  # only the bottom arc
            )

        self.conn = self.Block(Fpc050Pair(8, cable="same"), external=True)
        self.export_tap(self.gnd.net, self.conn.pins.request("1"))
        self.export_tap(self.pwr.net, self.conn.pins.request("2"))
        self.export_tap(self.i2c.scl.net, self.conn.pins.request("3"))
        self.export_tap(self.i2c.sda.net, self.conn.pins.request("4"))
        self.export_tap(self.io0.net, self.conn.pins.request("5"))
        self.export_tap(self.gnd.net, self.conn.pins.request("6"))
        self.export_tap(self.vbat.net, self.conn.pins.request("7"))
        self.export_tap(self.vbat.net, self.conn.pins.request("8"))


class BleJoystick(JlcBoardTop):
    """BLE combination air-mouse and joystick with d-pad, trigger, and RGBs."""

    @override
    def contents(self) -> None:
        super().contents()

        # really should operate down to ~3.3v,
        # this forces the model to allow the LDO to go into tracking
        # and allows the neopixels to go below their minimum rated voltage which works in practice
        self.bat = self.Block(LipoConnector(voltage=(3.8, 4.2) * Volt, actual_voltage=(3.8, 4.2) * Volt))
        self.usb = self.Block(UsbCReceptacle(current_limits=(0, 1) * Amp))

        self.vbat = self.connect(self.bat.pwr)
        self.vusb = self.connect(self.usb.pwr)
        self.gnd = self.connect(self.bat.gnd, self.usb.gnd)

        self.tp_usb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.bat.gnd)

        # POWER
        with self.implicit_connect(ImplicitConnect(self.gnd, [Common])) as imp:
            self.vbat_sense = imp.Block(Ina219(100 * mOhm(tol=0.01)))
            (self.gate,), _ = self.chain(self.vbat, imp.Block(SoftPowerGate()), self.vbat_sense.sense_pos)
            self.vbat_gated = self.connect(self.vbat_sense.sense_neg)

            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.vbat_gated,
                imp.Block(VoltageRegulator(output_voltage=3.3 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9) * Volt)),
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out, self.vbat_sense.pwr)

            self.chg = imp.Block(Mcp73831(charging_current=100 * mAmp(tol=0.2)))
            self.connect(self.usb.pwr, self.chg.pwr)
            self.connect(self.chg.pwr_bat, self.bat.pwr)

        # 3V3 DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(Holyiot_18010())  # nRF52 weirdly requires Vbus, so this can't be abstract
            self.connect(self.mcu.pwr_usb, self.vusb)
            (self.usb_esd,), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request("led"))

            self.connect(self.gate.btn_out, self.mcu.gpio.request("sw"))
            self.connect(self.mcu.gpio.request("gate_ctl"), self.gate.control)

            self.bumper_sw = imp.Block(DigitalSwitch())
            self.connect(self.bumper_sw.out, self.mcu.gpio.request(f"bumper"))

            mcu_i2c = self.mcu.i2c.request("i2c")
            (self.i2c_pull,), _ = self.chain(mcu_i2c, imp.Block(I2cPullup()))
            self.tp_i2c = self.Block(I2cTestPoint("i2c")).connected(mcu_i2c)

            self.connect(mcu_i2c, self.vbat_sense.i2c)
            self.imu = imp.Block(Lsm6ds3trc())
            self.connect(mcu_i2c, self.imu.i2c)
            self.mag = imp.Block(Qmc5883l())
            self.connect(mcu_i2c, self.mag.i2c)

        # POWER GATED DOMAIN
        with self.implicit_connect(ImplicitConnect(self.gnd, [Common])) as imp:
            self.stick = imp.Block(JoystickSubboard())
            (self.stick_gate,), _ = self.chain(
                self.mcu.gpio.request("stick_pwr_gate"), imp.Block(LoadSwitch()), self.stick.pwr
            )
            self.connect(self.stick.ax1, self.mcu.adc.request("ax1"))
            self.connect(self.stick.ax2, self.mcu.adc.request("ax2"))
            self.connect(self.stick.sw, self.gate.btn_in)

            # use a load switch since the GPIO pin voltage drop may interfere with readings
            (self.trig,), _ = self.chain(imp.Block(A1304()), self.mcu.adc.request("trig"))
            (self.trig_gate,), _ = self.chain(
                self.mcu.gpio.request("trig_pwr_gate"), imp.Block(LoadSwitch()), self.trig.pwr
            )

            self.connect(self.v3v3, self.stick_gate.pwr_in, self.trig_gate.pwr_in)

        # MIXED POWER DOMAINS
        with self.implicit_connect(ImplicitConnect(self.gnd, [Common])) as imp:
            # alternative implementation instead of the INA219
            # self.vbat_sense_gate = imp.Block(HighSideSwitch())
            # self.connect(self.vbat_sense_gate.pwr, self.vbat_gated)
            # self.connect(self.mcu.gpio.request("vbat_sense_gate"), self.vbat_sense_gate.control)
            # (self.vbat_sense,), _ = self.chain(
            #     self.vbat_sense_gate.output,
            #     imp.Block(VoltageSenseDivider(full_scale_voltage=2.2 * Volt(tol=0.1), impedance=(1, 10) * kOhm)),
            #     self.mcu.adc.request("vbat_sense"),
            # )

            self.connect(self.mcu.gpio.request("chg"), self.chg.prog_ctl)  # allow custom charge cutoff

            self.btns = imp.Block(ButtonSubboard())
            self.connect(self.btns.pwr, self.v3v3)
            self.connect(self.btns.vbat, self.vbat_gated)
            self.connect(self.btns.i2c, mcu_i2c)
            self.connect(self.btns.io0, self.mcu.gpio.request("btns_io0"))

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Holyiot_18010),
                (["btns", "ioe"], Ch32v003),
                (["reg_3v3"], Ap7215),
                (["bumper_sw", "package"], SmtSwitchRa),
                # TODO debug why class refinements not working
                (["btns", "sw[0]", "package"], SmtSwitch),
                (["btns", "sw[1]", "package"], SmtSwitch),
                (["btns", "sw[2]", "package"], SmtSwitch),
                (["btns", "sw[3]", "package"], SmtSwitch),
                (["btns", "sw[4]", "package"], SmtSwitch),
                (["btns", "sw[5]", "package"], SmtSwitch),
                (["btns", "sw[6]", "package"], SmtSwitch),
                (["btns", "sw[7]", "package"], SmtSwitch),
            ],
            instance_values=[
                (["refdes_prefix"], "J"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        "i2c.scl=26",
                        "i2c.sda=27",
                        "chg=2",
                        "trig=6",
                        "ax1=8",
                        "ax2=9",
                        "stick_pwr_gate=3",
                        "led=10",
                        "bumper=11",
                        "trig_pwr_gate=12",
                        "sw=13",
                        "gate_ctl=15",
                        "btns_io0=20",
                    ],
                ),
                (
                    ["btns", "ioe", "pin_assigns"],
                    [
                        "i2c.scl=12",
                        "i2c.sda=11",
                        "npx=16",  # pinned to MOSI
                        "dpad_0=1",
                        "dpad_1=2",
                        "dpad_2=3",
                        "dpad_3=8",
                        "dpad_4=10",
                        "dpad_5=13",
                        "dpad_6=14",
                        "dpad_7=15",
                        "io0=17",
                    ],
                ),
                (["mcu", "gpio", "trig_pwr_gate", "current_limits"], Range(-0.010, 0.009)),  # use typ ratings
            ],
            class_refinements=[
                (SwdCortexTargetConnector, SwdCortexTargetTagConnect),
                (Ch32vSdiHeader, Ch32vSdiTc2030),
                (TestPoint, CompactKeystone5015),
                (TagConnect, TagConnectNonLegged),
                (PassiveConnector, PinHeader2mm),
                (Neopixel, Ws2812c_2020),
                (TactileSwitch, SmtSwitch),
            ],
            class_values=[
                (ProtectionZenerDiode, ["diode", "footprint_spec"], "Diode_SMD:D_SOD-123"),
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),
            ],
        )


class BleJoystickTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(BleJoystick)
