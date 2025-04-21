import unittest

from edg import *


class BleJoystick(JlcBoardTop):
    """BLE joystick with XYAB buttons
    """
    def contents(self) -> None:
        super().contents()

        self.pwr = self.Block(LipoConnector())

        self.vbat = self.connect(self.pwr.pwr)
        self.gnd = self.connect(self.pwr.gnd)

        self.tp_bat = self.Block(VoltageTestPoint()).connected(self.pwr.pwr)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.gate, self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.vbat,
                imp.Block(SoftPowerGate()),
                imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

            self.vbat_sense_gate = imp.Block(HighSideSwitch())
            self.connect(self.vbat_sense_gate.pwr, self.vbat)


        # 3V3 DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.v3v3, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            self.stick = imp.Block(XboxElite2Joystick())
            self.connect(self.stick.ax1, self.mcu.adc.request('ax1'))
            self.connect(self.stick.ax2, self.mcu.adc.request('ax2'))

            self.connect(self.stick.sw, self.gate.btn_in)
            self.connect(self.gate.btn_out, self.mcu.gpio.request('sw'))
            self.connect(self.mcu.gpio.request('gate_ctl'), self.gate.control)

            self.trig = imp.Block(A1304())
            self.connect(self.trig.out, self.mcu.adc.request('trig'))

            # debugging LEDs
            (self.ledr, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('led'))

            self.connect(self.vbat_sense_gate.control, self.mcu.gpio.request('vbat_sense_gate'))
            (self.vbat_sense, ), _ = self.chain(
                self.vbat_sense_gate.output,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('vbat_sense')
            )

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Ldl1117),
            ],
            instance_values=[
                (['refdes_prefix'], 'J'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
                    # 'vin_sense=4',
                    # 'motor1=15',
                    # 'motor2=14',
                    # 'enca=13',
                    # 'encb=10',
                    # 'qwiic.sda=6',
                    # 'qwiic.scl=5',
                ]),
                (['mcu', 'programming'], 'uart-auto'),

            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TagConnect, TagConnectNonLegged),
                (TestPoint, CompactKeystone5015),
                (PassiveConnector, JstPhKHorizontal),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
            ]
        )


class BleJoystickTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(BleJoystick)
