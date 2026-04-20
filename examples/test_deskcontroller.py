import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class JiecangConnector(Block):
    """RJ-12 connector for (some?) Jiecang standing desk controllers
    https://github.com/phord/Jarvis?tab=readme-ov-file#physical-interface-rj-12"""

    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(
            VoltageSource(voltage_out=5 * Volt(tol=0), current_limits=(0, 300) * mAmp)
        )  # reportedly drives at least 300mA
        self.uart = self.Port(UartPort(DigitalBidir.from_supply(self.gnd, self.pwr)))

        self.conn = self.Block(PassiveConnector(length=6)).connected(
            {
                "2": self.gnd,
                "4": self.pwr,
                "3": self.uart.tx,  # DTX, controller -> handset
                "5": self.uart.rx,  # HTX, handset -> controller
            }
        )


class UartLevelShifter(Block):
    """Level shifter for UART port, using a pair of BidirectionalLevelShifter internally.
    Not necessarily the most efficient implementation, but is bidirectional on both channels
    and not dependent on correct channel directionality."""

    def __init__(
        self,
        lv_res: RangeLike = 4.7 * kOhm(tol=0.05),
        hv_res: RangeLike = 4.7 * kOhm(tol=0.05),
    ) -> None:
        super().__init__()
        self.lv_pwr = self.Port(VoltageSink.empty())
        self.lv_uart = self.Port(UartPort.empty())
        self.hv_pwr = self.Port(VoltageSink.empty())
        self.hv_uart = self.Port(UartPort.empty())

        self.hv_tx_shift = self.Block(BidirectionaLevelShifter(lv_res=lv_res, hv_res=hv_res, src_hint="hv"))
        self.lv_tx_shift = self.Block(BidirectionaLevelShifter(lv_res=lv_res, hv_res=hv_res, src_hint="lv"))
        self.connect(self.hv_pwr, self.hv_tx_shift.hv_pwr, self.lv_tx_shift.hv_pwr)
        self.connect(self.lv_pwr, self.hv_tx_shift.lv_pwr, self.lv_tx_shift.lv_pwr)
        self.connect(self.hv_tx_shift.hv_io, self.hv_uart.tx)
        self.connect(self.lv_tx_shift.hv_io, self.hv_uart.rx)
        self.connect(self.hv_tx_shift.lv_io, self.lv_uart.tx)
        self.connect(self.lv_tx_shift.lv_io, self.lv_uart.rx)


class DeskController(JlcBoardTop):
    """Standing desk controller for desks with a Jiecang controller
    https://community.home-assistant.io/t/desky-standing-desk-esphome-works-with-desky-uplift-jiecang-assmann-others/383790
    """

    @override
    def contents(self) -> None:
        super().contents()

        self.conn = self.Block(JiecangConnector())
        self.gnd = self.connect(self.conn.gnd)

        self.conn_shift = self.Block(UartLevelShifter(hv_res=RangeExpr.INF))
        self.connect(self.conn.pwr, self.conn_shift.hv_pwr)
        self.connect(self.conn.uart, self.conn_shift.hv_uart)

        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.conn.gnd)

        with self.implicit_connect(  # POWER
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.choke, self.tp_pwr), _ = self.chain(
                self.conn.pwr, self.Block(SeriesPowerFerriteBead()), self.Block(VoltageTestPoint())
            )
            self.pwr = self.connect(self.choke.pwr_out)

            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.pwr,
                imp.Block(LinearRegulator(output_voltage=3.3 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9) * Volt)),
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

        with self.implicit_connect(  # 3V3 DOMAIN
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            self.connect(self.v3v3, self.conn_shift.lv_pwr)
            self.connect(self.mcu.uart.request("ctl"), self.conn_shift.lv_uart)

            self.sw = self.Block(SwitchMatrix(nrows=3, ncols=2))
            self.connect(self.sw.cols, self.mcu.gpio.request_vector("swc"))
            self.connect(self.sw.rows, self.mcu.gpio.request_vector("swr"))

            (self.ledr,), _ = self.chain(self.mcu.gpio.request("ledr"), imp.Block(IndicatorLed(Led.Red)))

            self.oled = imp.Block(Er_Oled_096_1_1())
            self.i2c_pull = imp.Block(I2cPullup())
            self.i2c = self.mcu.i2c.request("i2c")
            self.connect(self.i2c, self.i2c_pull.i2c, self.oled.i2c)

            self.reset = self.mcu.gpio.request("oled_rst")
            self.connect(self.reset, self.oled.reset)
            self.io8_pu = imp.Block(PullupResistor(4.7 * kOhm(tol=0.05)))
            self.connect(self.mcu.gpio.request("spk"), self.io8_pu.io)  # TODO support in chain

        with self.implicit_connect(  # 5V DOMAIN
            ImplicitConnect(self.pwr, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
                self.io8_pu.io,
                imp.Block(LowPassRcDac(1 * kOhm(tol=0.05), 5 * kHertz(tol=0.5))),
                self.Block(AnalogTestPoint()),
                imp.Block(Tpa2005d1(gain=Range.from_tolerance(4, 0.2))),
                self.Block(Speaker()),
            )

            # 1k pullup on the HV side is necessary for ~5v input, 4.7k does not provide a sufficient signal
            self.npx_shift = imp.Block(
                BidirectionaLevelShifter(lv_res=RangeExpr.INF, hv_res=1 * kOhm(tol=0.05), src_hint="lv")
            )
            self.connect(self.npx_shift.lv_pwr, self.v3v3)
            self.connect(self.npx_shift.hv_pwr, self.pwr)
            self.connect(self.mcu.gpio.request("npx"), self.npx_shift.lv_io)
            (self.npx_tp, self.npx), _ = self.chain(
                self.npx_shift.hv_io, self.Block(DigitalTestPoint("npx")), imp.Block(NeopixelArray(6))
            )

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Esp32c3_Wroom02),
                (["reg_3v3"], Ldl1117),
                (["conn", "conn"], JstPhKVertical),
                (["spk", "conn"], JstPhKVertical),
            ],
            instance_values=[
                (["refdes_prefix"], "D"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        "ledr=_GPIO9_STRAP",  # use the strapping pin to save on IOs
                        "oled_rst=_GPIO2_STRAP_EXT_PU",  # not pulled up, affects startup glitching
                        "spk=_GPIO8_STRAP_EXT_PU",  # use the strapping pin to save on IOs
                        "i2c.sda=18",
                        "i2c.scl=17",
                        "swr_2=10",
                        "swr_1=13",
                        "swr_0=14",
                        "swc_1=15",
                        "swc_0=5",
                        "ctl.rx=3",
                        "ctl.tx=4",
                    ],
                ),
                (["mcu", "programming"], "uart-auto"),
                (["spk_drv", "pwr", "current_draw"], Range(0.0022, 0.08)),  # don't run at full power
                (["npx", "pwr", "current_draw"], Range(0.0036, 0.08)),
                (["mcu", "ic", "pwr", "current_draw"], Range(1.0e-6, 0.1)),  # assume it doesn't run full bore
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TagConnect, TagConnectNonLegged),
                (TestPoint, CompactKeystone5015),
                (Speaker, ConnectorSpeaker),
                (Switch, KailhSocket),
                (Neopixel, Sk6812Mini_E),
                (Fpc050Bottom, Fpc050BottomFlip),
            ],
            class_values=[
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),
                (Nonstrict3v3Compatible, ["nonstrict_3v3_compatible"], True),
                (Er_Oled_096_1_1, ["iref_res", "resistance"], Range.from_tolerance(470e3, 0.1)),
            ],
        )


class DeskControllerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(DeskController)
