import unittest

from edg import *


class IotRollerBlindsConnector(Block):
    def __init__(self):
        super().__init__()
        self.conn = self.Block(JstXh(length=6))
        self.gnd = self.Export(self.conn.pins.request('4').adapt_to(Ground()))
        self.pwr = self.Export(self.conn.pins.request('1').adapt_to(
            VoltageSink.from_gnd(self.gnd, voltage_limits=(4.5, 24)*Volt)))

        self.enca = self.Export(self.conn.pins.request('2').adapt_to(DigitalSource.low_from_supply(self.gnd)))
        self.encb = self.Export(self.conn.pins.request('3').adapt_to(DigitalSource.low_from_supply(self.gnd)))

        self.motor2 = self.Export(self.conn.pins.request('5').adapt_to(DigitalSink(current_draw=(0, 0.5)*Amp)))
        self.motor1 = self.Export(self.conn.pins.request('6').adapt_to(DigitalSink(current_draw=(0, 0.5)*Amp)))


class PowerInConnector(Connector):
    def __init__(self):
        super().__init__()
        self.conn = self.Block(JstPh())
        self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()))
        self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSource(
            voltage_out=12*Volt(tol=0.2),
            current_limits=(0, 1)*Amp,
        )))


class PowerOutConnector(Connector):
    def __init__(self):
        super().__init__()
        self.conn = self.Block(JstPh())
        self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()))
        self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink()))


class IotRollerBlinds(JlcBoardTop):
    """IoT roller blinds driver with up-to-20v input and ESP32-C3

    Device has a 6-pin JST XH 2.50 connector, pinned as:
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

        self.pwr = self.Block(PowerInConnector())
        self.pwr_out = self.Block(PowerOutConnector())

        self.conn = self.Block(IotRollerBlindsConnector())

        self.vin_raw = self.connect(self.pwr.pwr, self.pwr_out.pwr, self.conn.pwr)  # TODO conn should be cuttable
        self.gnd = self.connect(self.pwr.gnd, self.pwr_out.gnd, self.conn.gnd)

        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.fuse, self.tp_vin), _ = self.chain(
                self.vin_raw,
                self.Block(SeriesPowerFuse(trip_current=(500, 1000)*mAmp)),
                self.Block(VoltageTestPoint()),
            )
            self.vin = self.connect(self.fuse.pwr_out)
            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.vin,
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

            (self.vin_sense, ), _ = self.chain(
                self.vin,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('vin_sense')
            )
            self.connect(self.conn.enca, self.mcu.gpio.request('enca'))
            self.connect(self.conn.encb, self.mcu.gpio.request('encb'))

        # 12V DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.vin, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.drv = imp.Block(Drv8870(current_trip=500*mAmp(tol=0.1)))
            self.connect(self.drv.vref, self.v3v3)
            self.connect(self.mcu.gpio.request('motor1'), self.drv.in1)
            self.connect(self.mcu.gpio.request('motor2'), self.drv.in2)
            self.connect(self.drv.out1, self.conn.motor1)
            self.connect(self.drv.out2, self.conn.motor2)

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Tps54202h),
            ],
            instance_values=[
                (['refdes_prefix'], 'B'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
                ]),
                (['mcu', 'programming'], 'uart-auto'),
                (['reg_3v3', 'power_path', 'inductor', 'part'], "NR5040T220M"),
                (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TestPoint, CompactKeystone5015),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
            ]
        )


class MotorConnector(Block):
    def __init__(self):
        super().__init__()
        self.conn = self.Block(Picoblade(length=2))
        self.motor1 = self.Export(self.conn.pins.request('1').adapt_to(DigitalSink(current_draw=(0, 0.5)*Amp)))
        self.motor2 = self.Export(self.conn.pins.request('2').adapt_to(DigitalSink(current_draw=(0, 0.5)*Amp)))


class IotCurtainRoller(JlcBoardTop):
    """IoT curtain roller, drives a motor and has hall sensors integrated on the board, next to the motor.
    Motor: LS16PQQ-030  -183.5
    ~2.7v min starting voltage; 40mA open current, 200mA stall current @ 4.0v

    Motor is a 2-pin PicoBlade 1.25mm connector, Molex_PicoBlade_53398-0271_1x02-1MP_P1.25mm_Vertical
    """
    def contents(self) -> None:
        super().contents()

        self.pwr = self.Block(PowerInConnector())
        self.pwr_out = self.Block(PowerOutConnector())

        self.vin_raw = self.connect(self.pwr.pwr, self.pwr_out.pwr)
        self.gnd = self.connect(self.pwr.gnd, self.pwr_out.gnd)

        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.fuse, self.tp_vin), _ = self.chain(
                self.vin_raw,
                self.Block(SeriesPowerFuse(trip_current=(300, 600)*mAmp)),
                self.Block(VoltageTestPoint()),
            )
            self.vin = self.connect(self.fuse.pwr_out)
            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.vin,
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

            (self.vin_sense, ), _ = self.chain(
                self.vin,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('vin_sense')
            )
            (self.enca, ), _ = self.chain(imp.Block(Ah1806()), self.mcu.gpio.request('enca'))
            (self.encb, ), _ = self.chain(imp.Block(Ah1806()), self.mcu.gpio.request('encb'))

            self.i2c = self.mcu.i2c.request('i2c')
            (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
                self.i2c,
                imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))
            self.als = imp.Block(Bh1750())
            self.connect(self.i2c, self.als.i2c)

            (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

        # 12V DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.vin, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.motor = self.Block(MotorConnector())
            self.drv = imp.Block(Drv8870(current_trip=500*mAmp(tol=0.1)))
            self.connect(self.drv.vref, self.v3v3)
            self.connect(self.mcu.gpio.request('motor1'), self.drv.in1)
            self.connect(self.mcu.gpio.request('motor2'), self.drv.in2)
            self.connect(self.drv.out1, self.motor.motor1)
            self.connect(self.drv.out2, self.motor.motor2)

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Tps54202h),
            ],
            instance_values=[
                (['refdes_prefix'], 'R'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
                ]),
                (['mcu', 'programming'], 'uart-auto'),
                (['reg_3v3', 'power_path', 'inductor', 'part'], "NR5040T220M"),
                (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TestPoint, CompactKeystone5015),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
            ]
        )


class IotRollerBlindsTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(IotRollerBlinds)


class IotCurtainRollerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(IotCurtainRoller)
