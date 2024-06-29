import unittest

from edg import *
from .test_robotcrawler import ServoFeedbackConnector
from .test_robotdriver import PwmConnector


# TODO: need to indent self

@abstract_block
class RobotCrawlerSpec(BoardTop):
    def __init__(self) -> None:
        super().__init__()

        self.servo_fs90fb_COUNT = 8
        # TODO: REPLACE: ServoFeedbackConnector
        self.servo_fs90fbs = ElementDict[ServoFeedbackConnector]()
        for i in range(self.servo_fs90fb_COUNT):
            self.servo_fs90fbs[str(i)] = self.Block(ServoFeedbackConnector())

        # TODO: REPLACE: PwmConnector
        self.servo_fs90r_COUNT = 4
        self.servo_fs90rs = ElementDict[PwmConnector]()
        for i in range(self.servo_fs90r_COUNT):
            # TODO add default draw to PWM connector
            self.servo_fs90rs[str(i)] = self.Block(PwmConnector(current_draw=(5, 5)*mAmp))

        self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

        # TODO: caps
        self.imu = self.Block(Imu_Lsm6ds3trc())


class RobotCrawler(RobotCrawlerSpec, JlcBoardTop):
    def __init__(self):
        super().__init__()
        pass

    def contents(self):
        super().contents()

        with self.implicit_connect(
                ImplicitConnect(self.batt.pwr, [Power]),
                ImplicitConnect(self.batt.gnd, [Common]),
        ) as imp:
            self.reg = imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05)))

            for i in range(self.servo_fs90fb_COUNT):
                self.connect(self.servo_fs90fbs[str(i)].gnd, self.batt.gnd)
                self.connect(self.servo_fs90fbs[str(i)].pwr, self.batt.pwr)

            for i in range(self.servo_fs90r_COUNT):
                self.connect(self.servo_fs90rs[str(i)].gnd, self.batt.gnd)
                self.connect(self.servo_fs90rs[str(i)].pwr, self.batt.pwr)

        # 3v3 domain
        with self.implicit_connect(
                ImplicitConnect(self.reg.pwr_out, [Power]),
                ImplicitConnect(self.reg.gnd, [Common]),
        ) as imp:
            self.connect(self.imu.gnd, self.reg.gnd)
            self.connect(self.imu.pwr, self.reg.pwr_out)

            self.mcu = imp.Block(Esp32s3_Wroom_1())

            self.i2c_pull = imp.Block(I2cPullup())
            self.connect(self.mcu.i2c.request(), self.i2c_pull.i2c, self.imu.i2c)
            for i in range(self.servo_fs90fb_COUNT):
                self.connect(self.servo_fs90fbs[str(i)].pwm, self.mcu.gpio.request(f'fs90fb_{i}_pwm'))
                self.connect(self.servo_fs90fbs[str(i)].fb, self.mcu.adc.request(f'fs90fb_{i}_fb'))

            for i in range(self.servo_fs90r_COUNT):
                self.connect(self.servo_fs90rs[str(i)].pwm, self.mcu.gpio.request(f'fs90r_{i}_pwm'))

            (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))  # overlapped with BOOT
            (self.ledy, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledy'))
            (self.ledw, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledw'))

            (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32s3_Wroom_1),
                (['reg'], Ldl1117),
                (['batt', 'conn'], JstPhKHorizontal),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
            ],
            instance_values=[
                (['mcu', 'pin_assigns'], [
                    'ledr=_GPIO0_STRAP',

                    'fs90fb_0_pwm=8',
                    'fs90fb_0_fb=4',
                    'fs90fb_1_pwm=9',
                    'fs90fb_1_fb=5',
                    'fs90fb_2_pwm=10',
                    'fs90fb_2_fb=6',
                    'fs90fb_3_pwm=11',
                    'fs90fb_3_fb=7',

                    'fs90r_0_pwm=13',
                    'fs90r_1_pwm=14',

                    'fs90fb_4_pwm=25',
                    'fs90fb_4_fb=15',
                    'fs90fb_5_pwm=31',
                    'fs90fb_5_fb=17',
                    'fs90fb_6_pwm=32',
                    'fs90fb_6_fb=38',
                    'fs90fb_7_pwm=33',
                    'fs90fb_7_fb=39',

                    'fs90r_2_pwm=34',
                    'fs90r_3_pwm=35',
                 ]),
                (['mcu', 'programming'], 'uart-auto'),
            ],
            class_values=[
                (ServoFeedbackConnector, ['pwr', 'current_draw'], Range(0.005, 0.005))
            ],
        )
