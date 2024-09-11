import unittest

from edg import *


class JiecangRj12Connector(Block):
    """RJ-12 connector for (some?) Jiecang standing desk controllers
    https://github.com/phord/Jarvis?tab=readme-ov-file#physical-interface-rj-12"""
    def __init__(self):
        super().__init__()
        self.conn = self.Block(PassiveConnector(length=6))
        self.gnd = self.Export(self.conn.pins.request('2').adapt_to(Ground()), [Common])
        self.pwr = self.Export(self.conn.pins.request('4').adapt_to(VoltageSource(
            voltage_out=5*Volt(tol=0))))  # TODO no voltage tolerance or current limits specified
        self.uart = self.Port(UartPort.empty())
        self.connect(self.uart.tx, self.conn.pins.request('5').adapt_to(DigitalSource()))  # DTX, controller -> handset
        self.connect(self.uart.rx, self.conn.pins.request('3').adapt_to(DigitalSink()))  # HTX, handset -> controller


class DeskController(JlcBoardTop):
    """Standing desk controller for desks with a Jiecang controller
    https://community.home-assistant.io/t/desky-standing-desk-esphome-works-with-desky-uplift-jiecang-assmann-others/383790
    """
    def contents(self) -> None:
        super().contents()

        self.conn = self.Block(JiecangRj12Connector())
        self.pwr = self.connect(self.conn.pwr)
        self.gnd = self.connect(self.conn.gnd)

        self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.conn.pwr)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.conn.gnd)

        with self.implicit_connect(  # POWER
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.pwr,
                imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

        with self.implicit_connect(  # 3V3 DOMAIN
                ImplicitConnect(self.v3v3, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            self.connect(self.mcu.uart.request('ctl'), self.conn.uart)

            self.sw = self.Block(SwitchMatrix(nrows=3, ncols=2))
            self.connect(self.sw.cols, self.mcu.gpio.request_vector())
            self.connect(self.sw.rows, self.mcu.gpio.request_vector())

            (self.ledr, ), _ = self.chain(self.mcu.gpio.request('ledr'), imp.Block(IndicatorLed(Led.Red)))

            self.oled = imp.Block(Er_Oled_096_1_1())
            self.i2c_pull = imp.Block(I2cPullup())
            self.connect(self.mcu.i2c.request('i2c'), self.i2c_pull.i2c, self.oled.i2c)

            self.io8_pu = imp.Block(PullupResistor(4.7*kOhm(tol=0.05)))
            self.io2_pu = imp.Block(PullupResistor(4.7*kOhm(tol=0.05)))
            self.connect(self.mcu.gpio.request('oled_rst'), self.io2_pu.io, self.oled.reset)
            self.connect(self.mcu.gpio.request('spk'), self.io8_pu.io)  # TODO support in chain

        with self.implicit_connect(  # 5V DOMAIN
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
                self.io8_pu.io,
                imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
                self.Block(AnalogTestPoint()),
                imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
                self.Block(Speaker()))

            (self.npx_tp, self.npx, ), _ = self.chain(self.mcu.gpio.request('npx'),
                                                      self.Block(DigitalTestPoint()),
                                                      imp.Block(NeopixelArray(6)))

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Ldl1117),
                (['conn', 'conn'], JstPhKHorizontal),
                (['spk', 'conn'], JstPhKHorizontal),
            ],
            instance_values=[
                (['refdes_prefix'], 'D'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'ledr=_GPIO9_STRAP',  # use the strapping pin to save on IOs
                    'oled_rst=_GPIO2_STRAP_EXT_PU',  # use the strapping pin to save on IOs
                    'spk=_GPIO8_STRAP_EXT_PU',  # use the strapping pin to save on IOs
                ]),
                (['mcu', 'programming'], 'uart-auto'),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TestPoint, CompactKeystone5015),
                (Speaker, ConnectorSpeaker),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
                (Nonstrict3v3Compatible, ['nonstrict_3v3_compatible'], True),
            ]
        )


class DeskControllerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(DeskController)
