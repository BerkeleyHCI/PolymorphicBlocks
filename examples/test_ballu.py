
import unittest
from typing import Optional, cast

from edg import *

from .components_lib import OrPowerGate, ProtectedVoltageRegulator, LipoCharger, OrPowerGateDirSw
from .test_robotdriver import PwmConnector



class Ballu(JlcBoardTop):
    """
    Ballu robot new generation pcb board that is designed to fit on each foot of the ballu.

    Key features:
    - ESP32-S3,
    - usb-c programing, power supply, and charging
    - 9 axis IMU
    - Side firing Neopixel
    - Speaker
    - Oled screen
    - Software power switch with directional switch (center)
    - Directional switch


    """
    def contents(self) -> None:
        super().contents()

        self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))
        self.vusb = self.connect(self.usb.pwr)
        self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))
        self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
            self.usb.gnd, self.batt.gnd
        )
        self.gnd = self.connect(self.gnd_merge.pwr_out)
        self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.gnd_merge.pwr_out)


        self.gate = self.Block(OrPowerGateDirSw((0, 1)*Volt, (0, 0.1)*Ohm)).connected_from(self.gnd, self.vusb, self.batt.pwr)
        self.pwr = self.connect(self.gate.pwr_out)


        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.preg_3v3 = imp.Block(ProtectedVoltageRegulator(
                output_voltage=3.3*Volt(tol=0.05), zener_diode_voltage=(3.45, 3.9)*Volt
            ))
            self.v3v3 = self.connect(self.preg_3v3.pwr_out)


        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.charger, ), _ = self.chain(self.vusb, imp.Block(LipoCharger(charging_current=200*mAmp(tol=0.2),)), self.batt.chg)


        # 3V3 DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.v3v3, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.i2s = self.mcu.with_mixin(IoControllerI2s())

            (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                          self.mcu.usb.request())

            # single onboard debugging LED
            (self.led, ), _ = self.chain(self.mcu.gpio.request('led'), imp.Block(IndicatorLed(Led.Red)))

            self.i2c = self.mcu.i2c.request('i2c')

            (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
                self.i2c,
                imp.Block(I2cPullup()), imp.Block(I2cTestPoint('i2c')),)


            (self.batt_sense, ), _ = self.chain(
                self.pwr,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('pwr_sense')
            )

        # pwr DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            # (self.npx, self.npx_side), _ = self.chain(self.mcu.gpio.request('npx'),  imp.Block(NeopixelArray(4)), imp.Block(NeopixelArray(6)),)
            (self.npx_side, ), _ = self.chain(self.mcu.gpio.request('npx'), imp.Block(NeopixelArray(8)))


        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
        # IMU
            self.imu = imp.Block(Imu_Lsm6ds3trc())
            self.mag = imp.Block(Mag_Qmc5883l())
            self.connect(self.i2c, self.imu.i2c, self.mag.i2c)

            # Oled
            self.oled = imp.Block(Er_Oled_096_1_1())
            self.connect(self.i2c, self.oled.i2c)
            self.connect(self.oled.reset, self.mcu.gpio.request("oled_reset"))


        # pwr DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.servo = ElementDict[PwmConnector]()
            for i in range(2):
                servo = self.servo[i] = imp.Block(PwmConnector((0, 200)*mAmp))
                self.connect(self.mcu.gpio.request(f'servo{i}'), servo.pwm)


        # Speaker
        with self.implicit_connect(
                ImplicitConnect(self.v3v3, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.spk_drv, self.spk), _ = self.chain(
                self.i2s.i2s.request('speaker'),
                imp.Block(Max98357a()),
                self.Block(Speaker())
            )


        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            # Power gait io
            self.chain(self.gate.btn_out, self.mcu.gpio.request('dir_cnt'))
            self.chain(self.gate.dir_a, self.mcu.gpio.request('dir_a'))
            self.chain(self.gate.dir_b, self.mcu.gpio.request('dir_b'))
            self.chain(self.gate.dir_c, self.mcu.gpio.request('dir_c'))
            self.chain(self.gate.dir_d, self.mcu.gpio.request('dir_d'))

            self.chain(self.mcu.gpio.request('gate_control'), self.gate.control)

            # Mounting holes
        self.m = ElementDict[MountingHole]()
        for i in range(4):
            self.m[i] = self.Block(MountingHole())




    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32s3_Wroom_1),
                (['preg_3v3', 'reg'], Ldl1117),



                # (['reg_2v5'], Xc6206p),
                # (['reg_1v2'], Xc6206p),
                # (['rgb', 'package'], ThtRgbLed),
                # (['npx_key'], Sk6812Mini_E),

                (['spk', 'conn'], JstPhKVertical),
                # (['npx', 'led[0]'], Ws2812b),
                # (['npx', 'led[1]'], Ws2812b),
                # (['npx', 'led[2]'], Ws2812b),
                # (['npx', 'led[3]'], Ws2812b),
                (['npx_side', 'led[0]'], Sk6812_Side_A),
                (['npx_side', 'led[1]'], Sk6812_Side_A),
                (['npx_side', 'led[2]'], Sk6812_Side_A),
                (['npx_side', 'led[3]'], Sk6812_Side_A),
                (['npx_side', 'led[4]'], Sk6812_Side_A),
                (['npx_side', 'led[5]'], Sk6812_Side_A),
                (['npx_side', 'led[6]'], Sk6812_Side_A),
                (['npx_side', 'led[7]'], Sk6812_Side_A),



            ],
            instance_values=[
                (['mcu', 'pin_assigns'], [
                    # "i2c=I2CEXT0",
                    "led=5",
                    "speaker.ws=12",
                    "speaker.sd=10",
                    "speaker.sck=11",
                    "i2c.scl=18",
                    "i2c.sda=19",
                    "0.dp=14",
                    "0.dm=13",
                    "oled_reset=17",
                    "gate_control=20",
                    "npx=39",
                    "servo0=8",
                    "dir_cnt=22",
                    "dir_b=34",
                    "dir_d=33",
                    "dir_c=32",
                    "dir_a=31",
                    "servo1=35",
                    "pwr_sense=38"
                    # 'led=_GPIO0_STRAP',
                ]),
                # (['expander', 'pin_assigns'], [
                # ]),

                (['gate', 'prot', 'diode', 'part'], 'TCLLZ5V6TR'),
            ],
            class_refinements=[
                (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
                (TestPoint, CompactKeystone5015),
                (DirectionSwitch, Skrh),
                # (Vl53l0x, Vl53l0xConnector),
                #(Neopixel, Ws2812b),
                (MountingHole, MountingHole_M2_5),
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TagConnect, TagConnectNonLegged)

            ],
            class_values=[
                # (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
                (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),

                (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
                (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
            ],
        )


class SmartNobTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(Ballu)