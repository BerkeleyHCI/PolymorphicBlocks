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
            voltage_out=5*Volt(tol=0),
            current_limits=(0, 300)*mAmp)))  # reportedly drives at least 300mA
        self.uart = self.Port(UartPort.empty())
        # UART pins internally pulled up to 5v, use a resistor + zener as a cheap level shifter
        res_model = Resistor(1*kOhm(tol=0.05))
        self.r_dtx = self.Block(res_model)
        self.r_htx = self.Block(res_model)
        zener_model = ZenerDiode((3.0, 3.6)*Volt)
        self.z_dtx = self.Block(zener_model)
        self.z_htx = self.Block(zener_model)
        self.connect(self.z_dtx.anode.adapt_to(Ground()), self.z_htx.anode.adapt_to(Ground()), self.gnd)

        self.connect(self.conn.pins.request('5'), self.r_dtx.a)  # DTX, controller -> handset
        self.connect(self.r_dtx.b, self.z_dtx.cathode)
        self.connect(self.uart.tx, self.z_dtx.cathode.adapt_to(DigitalSource()))
        self.connect(self.conn.pins.request('3'), self.r_htx.a)  # HTX, handset -> controller
        self.connect(self.r_htx.b, self.z_htx.cathode)
        self.connect(self.uart.rx, self.z_htx.cathode.adapt_to(DigitalSink()))


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
            self.connect(self.sw.cols, self.mcu.gpio.request_vector('swc'))
            self.connect(self.sw.rows, self.mcu.gpio.request_vector('swr'))

            (self.ledr, ), _ = self.chain(self.mcu.gpio.request('ledr'), imp.Block(IndicatorLed(Led.Red)))

            self.oled = imp.Block(Er_Oled_096_1_1())
            self.i2c_pull = imp.Block(I2cPullup())
            self.connect(self.mcu.i2c.request('i2c'), self.i2c_pull.i2c, self.oled.i2c)

            self.io2_pu = imp.Block(PullupResistor(4.7*kOhm(tol=0.05)))
            self.connect(self.mcu.gpio.request('oled_rst'), self.oled.reset, self.io2_pu.io)
            self.io8_pu = imp.Block(PullupResistor(4.7*kOhm(tol=0.05)))
            self.connect(self.mcu.gpio.request('spk'), self.io8_pu.io)  # TODO support in chain

        with self.implicit_connect(  # 5V DOMAIN
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
                self.io8_pu.io,
                imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
                self.Block(AnalogTestPoint()),
                imp.Block(Tpa2005d1(gain=Range.from_tolerance(4, 0.2))),
                self.Block(Speaker()))

            (self.npx_tp, self.npx, ), _ = self.chain(self.mcu.gpio.request('npx'),
                                                      self.Block(DigitalTestPoint()),
                                                      imp.Block(NeopixelArray(6)))

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Ap7215),
                (['conn', 'conn'], JstPhKVertical),
                (['spk', 'conn'], JstPhKVertical),
            ],
            instance_values=[
                (['refdes_prefix'], 'D'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'ledr=_GPIO9_STRAP',  # use the strapping pin to save on IOs
                    'oled_rst=_GPIO2_STRAP_EXT_PU',  # use the strapping pin to save on IOs
                    'spk=_GPIO8_STRAP_EXT_PU',  # use the strapping pin to save on IOs

                    'i2c.sda=10',  # PU part of I2C pullup
                    'i2c.scl=13',

                    'swr_2=14',
                    'swr_1=15',
                    'swr_0=17',
                    'swc_1=18',
                    'swc_0=3',
                ]),
                (['mcu', 'programming'], 'uart-auto'),
                (['spk_drv', 'pwr', 'current_draw'], Range(0.0022, 0.08)),  # don't run at full power
                (['npx', 'vdd', 'current_draw'], Range(0.0036, 0.08)),
                (['mcu', 'ic', 'pwr', 'current_draw'], Range(1.0E-6, 0.1))  # assume it doesn't run full bore
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TagConnect, TagConnectNonLegged),
                (TestPoint, CompactKeystone5015),
                (Speaker, ConnectorSpeaker),
                (Switch, KailhSocket),
                (Neopixel, Sk6812Mini_E),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
                (Nonstrict3v3Compatible, ['nonstrict_3v3_compatible'], True),
            ]
        )


class DeskControllerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(DeskController)
