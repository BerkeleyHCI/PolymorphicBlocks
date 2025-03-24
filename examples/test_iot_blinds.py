import unittest

from edg import *


class IotRollerBlinds(JlcBoardTop):
    """IoT roller blinds driver with up-to-20v input and ESP32-C3

    Device has a 6-pin JST XH 2.54 connector, pinned as:
    1 (dot) Vdd - UHS41 hall effect ICs, 4.5-24v
    2 enc a
    3 enc b
    4 GND
    5 motor 2 - TP25-12v/6000, xiaomiteng
    6 motor 1
    Motor takes ~12v (stall ~500mA, no-load ~300mA, min start 4v @ 150mA)
    """
    def contents(self) -> None:
        super().contents()

        self.pwr = self.Block(PowerBarrelJack(voltage_out=12*Volt(tol=0.05), current_limits=(0, 5)*Amp))

        self.vin = self.connect(self.pwr.pwr)
        self.gnd = self.connect(self.pwr.gnd)

        self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.pwr.pwr)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.reg_5v, self.tp_5v, self.prot_5v), _ = self.chain(
                self.v12,
                imp.Block(VoltageRegulator(output_voltage=4*Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(5.5, 6.8)*Volt))
            )
            self.v5 = self.connect(self.reg_5v.pwr_out)

            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.v5,
                imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
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
            (self.ledr, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('led'))

            self.enc = imp.Block(DigitalRotaryEncoder())
            self.connect(self.enc.a, self.mcu.gpio.request('enc_a'))
            self.connect(self.enc.b, self.mcu.gpio.request('enc_b'))
            self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request('enc_sw'))

            (self.v12_sense, ), _ = self.chain(
                self.v12,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('v12_sense')
            )

        # 5V DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.v5, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.rgb_ring, ), _ = self.chain(
                self.mcu.gpio.request('rgb'),
                imp.Block(NeopixelArray(RING_LEDS)))

        # 12V DOMAIN
        self.fan = ElementDict[CpuFanConnector]()
        self.fan_drv = ElementDict[HighSideSwitch]()
        self.fan_sense = ElementDict[OpenDrainDriver]()
        self.fan_ctl = ElementDict[OpenDrainDriver]()

        with self.implicit_connect(
                ImplicitConnect(self.v12, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            for i in range(2):
                fan = self.fan[i] = self.Block(CpuFanConnector())
                fan_drv = self.fan_drv[i] = imp.Block(HighSideSwitch(pull_resistance=4.7*kOhm(tol=0.05), max_rds=0.3*Ohm))
                self.connect(fan.pwr, fan_drv.output)
                self.connect(fan.gnd, self.gnd)
                self.connect(self.mcu.gpio.request(f'fan_drv_{i}'), fan_drv.control)

                self.connect(fan.sense, self.mcu.gpio.request(f'fan_sense_{i}'))
                (self.fan_ctl[i], ), _ = self.chain(
                    self.mcu.gpio.request(f'fan_ctl_{i}'),
                    imp.Block(OpenDrainDriver()),
                    fan.with_mixin(CpuFanPwmControl()).control
                )

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_5v'], Tps54202h),
                (['reg_3v3'], Ap7215),
            ],
            instance_values=[
                (['refdes_prefix'], 'F'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'rgb=_GPIO2_STRAP_EXT_PU',  # force using the strapping pin, since we're out of IOs
                    'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
                ]),
                (['mcu', 'programming'], 'uart-auto'),
                (['reg_5v', 'power_path', 'inductor', 'part'], "NR5040T220M"),
                (['reg_5v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TestPoint, CompactKeystone5015),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
            ]
        )


class IotCurtainRoller(JlcBoardTop):
    """IoT curtain roller, drives a motor and has hall sensors integrated on the board, next to the motor.
    Motor: LS16PQQ-030  -183.5
    ~2.7v min starting voltage; 40mA open current, 200mA stall current @ 4.0v
    """
    def contents(self) -> None:
        super().contents()


class IotRollerBlindsTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(IotRollerBlinds)


class IotCurtainRollerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(IotCurtainRoller)