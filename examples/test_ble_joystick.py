import unittest

from edg import *


class BleJoystick(JlcBoardTop):
    """BLE joystick with XYAB buttons
    """
    @override
    def contents(self) -> None:
        super().contents()

        # really should operate down to ~3.3v,
        # this forces the model to allow the LDO to go into tracking
        self.bat = self.Block(LipoConnector(voltage=(4.0, 4.2)*Volt,
                                            actual_voltage=(4.0, 4.2)*Volt))
        self.usb = self.Block(UsbCReceptacle(current_limits=(0, 1)*Amp))

        self.vbat = self.connect(self.bat.pwr)
        self.vusb = self.connect(self.usb.pwr)
        self.gnd = self.connect(self.bat.gnd, self.usb.gnd)

        self.tp_bat = self.Block(VoltageTestPoint()).connected(self.bat.pwr)
        self.tp_usb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.bat.gnd)

        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            # (self.gate, self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
            #     self.vbat,
            #     imp.Block(SoftPowerGate()),
            #     imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
            #     self.Block(VoltageTestPoint()),
            #     imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
            # )

            # self.chg = imp.Block(Mcp73831(charging_current=200*mAmp(tol=0.2)))
            # self.connect(self.usb.pwr, self.chg.pwr)
            # self.connect(self.chg.pwr_bat, self.bat.chg)

            self.mp2722 = imp.Block(Mp2722(output_voltage=(3.7, 4.35)*Volt,
                                           charging_current=200*mAmp(tol=0.2)))
            self.connect(self.mp2722.pwr_in, self.usb.pwr)
            self.connect(self.mp2722.batt, self.vbat)
            self.connect(self.mp2722.cc, self.usb.cc)
            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.mp2722.pwr_out,
                imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

            self.fake_ntc = imp.Block(VoltageDivider(output_voltage=(1.5, 2)*Volt, impedance=(10, 100)*kOhm))
            self.connect(self.mp2722.vrntc, self.fake_ntc.input)
            self.connect(self.fake_ntc.output, self.mp2722.ntc1)  # TODO actual NTC

            # self.vbat_sense_gate = imp.Block(HighSideSwitch())
            # self.connect(self.vbat_sense_gate.pwr, self.vbat)

        # 3V3 DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.v3v3, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            self.stick = imp.Block(XboxElite2Joystick())
            (self.ax1_div, ), _ = self.chain(self.stick.ax1,
                                             imp.Block(SignalDivider(ratio=(0.45, 0.55), impedance=(1, 10)*kOhm)),
                                             self.mcu.adc.request('ax1'))
            (self.ax2_div, ), _ = self.chain(self.stick.ax2,
                                             imp.Block(SignalDivider(ratio=(0.45, 0.55), impedance=(1, 10)*kOhm)),
                                             self.mcu.adc.request('ax2'))

            # self.connect(self.stick.sw, self.gate.btn_in)
            # self.connect(self.gate.btn_out, self.mcu.gpio.request('sw'))
            # self.connect(self.mcu.gpio.request('gate_ctl'), self.gate.control)
            self.connect(self.stick.sw, self.mcu.gpio.request('sw'), self.mp2722.rst)

            self.trig = imp.Block(A1304())
            (self.trig_div, ), _ = self.chain(self.trig.out,
                                              imp.Block(SignalDivider(ratio=(0.45, 0.55), impedance=(1, 10)*kOhm)),
                                              self.mcu.adc.request('trig'))

            self.sw = ElementDict[DigitalSwitch]()
            for i in range(3):
                sw = self.sw[i] = imp.Block(DigitalSwitch())
                self.connect(sw.out, self.mcu.gpio.request(f'sw{i}'))

            # debugging LEDs
            (self.ledr, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('led'))

            # self.connect(self.vbat_sense_gate.control, self.mcu.gpio.request('vbat_sense_gate'))
            (self.vbat_sense, ), _ = self.chain(
                # self.vbat_sense_gate.output,
                self.vbat,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('vbat_sense')
            )

            (self.i2c_pull, ), _ = self.chain(
                self.mcu.i2c.request('i2c'),
                imp.Block(I2cPullup()),
                self.mp2722.i2c
            )

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Ap7215),
                (['sw[0]', 'package'], SmtSwitch),
                (['sw[1]', 'package'], SmtSwitch),
                (['sw[2]', 'package'], SmtSwitch),
                (['mcu', 'boot', 'package'], SmtSwitch),
            ],
            instance_values=[
                (['refdes_prefix'], 'J'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
                    # note, only ADC pins are IO0/1/3/4/5 (pins 18/17/15/3/4)
                    'ax1=3',
                    'ax2=15',
                    'trig=17',
                    'vbat_sense=18',
                    # 'vbat_sense_gate=14',
                    # 'gate_ctl=5',
                    'i2c.scl=4',
                    'i2c.sda=14',
                    'sw=5',  # joystick
                    'sw0=10',  # membranes
                    'sw1=13',
                    'sw2=6',
                ]),
                (['mcu', 'programming'], 'uart-auto-button'),
                (['mp2722', 'power_path', 'dutycycle_limit'], Range(0.1, 1)),  # allow tracking
                (['mp2722', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0.0, 10e6)),
                (['mp2722', 'power_path', 'inductor', 'footprint_spec'], "Inductor_SMD:L_1210_3225Metric")
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TestPoint, CompactKeystone5015),
                (PassiveConnector, JstPhKVertical),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
                (SmtSwitch, ['fp_footprint'], "project:MembraneSwitch_4mm")
            ]
        )


class BleJoystickTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(BleJoystick)
