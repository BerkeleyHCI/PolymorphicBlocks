import unittest

from edg import *


class IotRollerBlindsConnector(Block):
    def __init__(self):
        super().__init__()
        self.conn = self.Block(JstXh(length=6))
        self.gnd = self.Export(self.conn.pins.request('4').adapt_to(Ground()))
        self.pwr = self.Export(self.conn.pins.request('1').adapt_to(
            VoltageSink.from_gnd(self.gnd, voltage_limits=(4.5, 25)*Volt)))

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
            voltage_out=(10, 25)*Volt,
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

        self.vin_raw = self.connect(self.pwr.pwr, self.pwr_out.pwr)
        self.gnd = self.connect(self.pwr.gnd, self.pwr_out.gnd, self.conn.gnd)

        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.fuse, self.ferrite, self.tp_vin), _ = self.chain(
                self.vin_raw,
                self.Block(SeriesPowerFuse(trip_current=(500, 1000)*mAmp)),
                self.Block(SeriesPowerFerriteBead()),
                self.Block(VoltageTestPoint()),
            )
            self.vin = self.connect(self.ferrite.pwr_out, self.conn.pwr)

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

            # generic expansion
            (self.qwiic_pull, self.qwiic, ), _ = self.chain(self.mcu.i2c.request('qwiic'),
                                                            imp.Block(I2cPullup()),
                                                            imp.Block(QwiicTarget()))

        # 12V DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.vin, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.drv = imp.Block(Drv8870(current_trip=500*mAmp(tol=0.1)))
            self.connect(self.drv.vref, self.v3v3)
            self.connect(self.mcu.gpio.request('motor1'), self.drv.in1)
            self.connect(self.mcu.gpio.request('motor2'), self.drv.in2)
            self.connect(self.drv.out1, self.conn.motor2)
            self.connect(self.drv.out2, self.conn.motor1)

        self._block_diagram_grouping = self.Metadata({
            'pwr': 'pwr, pwr_out, tp_gnd, fuse, tp_vin, reg_3v3, prot_3v3, tp_3v3, vin_sense',
            'mcu': 'mcu, ledr, als, qwiic, qwiic_pull',
            'app': 'conn, drv',
        })

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Tps54202h),
                (['drv', 'vm_cap1', 'cap'], AluminumCapacitor),
            ],
            instance_values=[
                (['refdes_prefix'], 'B'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
                    'vin_sense=3',  # 4 as sent to fabrication before ADC2 removed from model, blue-wire to 3
                    'motor1=15',
                    'motor2=14',
                    'enca=13',
                    'encb=10',
                    'qwiic.sda=6',
                    'qwiic.scl=5',
                ]),
                (['mcu', 'programming'], 'uart-auto'),
                (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
                (['drv', 'isen_res', 'res', 'footprint_spec'], 'Resistor_SMD:R_1206_3216Metric'),
                (['drv', 'isen_res', 'res', 'require_basic_part'], False),
                (['reg_3v3', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 1.0),
                # 15uH inductors are more common
                (['reg_3v3', 'power_path', 'inductor', 'inductance'], Range.from_tolerance(15e-6, 0.2))
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


class IotCurtainCrawler(JlcBoardTop):
    """IoT curtain crawler, drives a motor and has hall sensors integrated on the board, next to the motor.
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
            (self.fuse, self.ferrite, self.tp_vin), _ = self.chain(
                self.vin_raw,
                self.Block(SeriesPowerFuse(trip_current=(300, 600)*mAmp)),
                self.Block(SeriesPowerFerriteBead()),
                self.Block(VoltageTestPoint()),
            )
            self.vin = self.connect(self.ferrite.pwr_out)

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
                imp.Block(I2cPullup()), imp.Block(I2cTestPoint('i2c')))
            self.als = imp.Block(Bh1750())
            self.connect(self.i2c, self.als.i2c)

            (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

            # generic expansion
            (self.qwiic, ), _ = self.chain(self.i2c, imp.Block(QwiicTarget()))

        # 12V DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.vin, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.motor = self.Block(MotorConnector())
            self.drv = imp.Block(Drv8870(current_trip=150*mAmp(tol=0.1)))
            self.connect(self.drv.vref, self.v3v3)
            self.connect(self.mcu.gpio.request('motor1'), self.drv.in1)
            self.connect(self.mcu.gpio.request('motor2'), self.drv.in2)
            self.connect(self.drv.out1, self.motor.motor1)
            self.connect(self.drv.out2, self.motor.motor2)

        self._block_diagram_grouping = self.Metadata({
            'pwr': 'pwr, pwr_out, fuse, tp_vin, reg_3v3, prot_3v3, vin_sense',
            'mcu': 'mcu, ledr, i2c_pull, als, qwiic',
            'app': 'motor, drv, enca, encb',
        })

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32c3_Wroom02),
                (['reg_3v3'], Tps54202h),
                (['drv', 'vm_cap1', 'cap'], AluminumCapacitor),
            ],
            instance_values=[
                (['refdes_prefix'], 'R'),  # unique refdes for panelization
                (['mcu', 'pin_assigns'], [
                    'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
                    'vin_sense=17',  # 4 as sent to fabrication before ADC2 removed from model, blue-wire to 17
                    'motor1=14',
                    'motor2=15',
                    'enca=13',
                    'encb=10',
                    'i2c.sda=5',
                    'i2c.scl=6',
                    'sw=3',
                ]),
                (['mcu', 'programming'], 'uart-auto'),
                (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
                (['drv', 'isen_res', 'res', 'footprint_spec'], 'Resistor_SMD:R_1206_3216Metric'),
                (['drv', 'isen_res', 'res', 'require_basic_part'], False),
                (['reg_3v3', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 1.0),
                # 15uH inductors are more common
                (['reg_3v3', 'power_path', 'inductor', 'inductance'], Range.from_tolerance(15e-6, 0.2))
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


class IotCurtainCrawlerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(IotCurtainCrawler)
