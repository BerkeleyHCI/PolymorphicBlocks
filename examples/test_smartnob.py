import unittest
from typing import Optional, cast

from edg import *

from .test_multimeter import FetPowerGate
# from .test_bldc_controller import *



class OrPowerGate(PowerConditioner, Block):
    @init_in_parent
    def __init__(self, diode_voltage_drop: RangeLike, fet_rds_on: RangeLike) -> None:
        super().__init__()
        self.pwr_out = self.Port(VoltageSource.empty())
        self.gnd = self.Port(Ground.empty(), [Common])
        self.pwr_hi = self.Port(VoltageSink().empty(),)
        self.pwr_lo = self.Port(VoltageSink().empty(),)

        self.btn_out = self.Port(DigitalSingleSource.empty())
        self.control = self.Port(DigitalSink.empty())  # digital level control - gnd-referenced NFET gate


        self.diode_voltage_drop = self.ArgParameter(diode_voltage_drop)
        self.fet_rds_on = self.ArgParameter(fet_rds_on)

    def contents(self):
        super().contents()
        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.fuse, self.gate, self.prot_batt, self.tp_batt), _ = self.chain(
                self.pwr_lo,
                imp.Block(SeriesPowerPptcFuse((2, 4)*Amp)),
                imp.Block(FetPowerGate()),
                imp.Block(ProtectionZenerDiode(voltage=(4.5, 6.0)*Volt)),
                self.Block(VoltageTestPoint()))
            self.vbatt = self.connect(self.gate.pwr_out)  # downstream of fuse

            self.pwr_or = self.Block(PriorityPowerOr(  # also does reverse protection
                self.diode_voltage_drop, self.fet_rds_on
            )).connected_from(self.gnd, self.pwr_hi, self.gate.pwr_out)

            self.connect(self.pwr_or.pwr_out, self.pwr_out)

            # Power gait
            self.connect(self.gate.control, self.control)
            self.connect(self.gate.btn_out, self.btn_out)

    def connected_from(self, gnd: Optional[Port[VoltageLink]] = None, pwr_hi: Optional[Port[VoltageLink]] = None,
                       pwr_lo: Optional[Port[VoltageLink]] = None) -> 'OrPowerGate':
        """Convenience function to connect ports, returning this object so it can still be given a name."""
        if gnd is not None:
            cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
        if pwr_hi is not None:
            cast(Block, builder.get_enclosing_block()).connect(pwr_hi, self.pwr_hi)
        if pwr_lo is not None:
            cast(Block, builder.get_enclosing_block()).connect(pwr_lo, self.pwr_lo)
        return self


class ProtectedVoltageRegulator(VoltageRegulator, Block):
    @init_in_parent
    def __init__(self, output_voltage: RangeLike, zener_diode_voltage: RangeLike) -> None:
        super().__init__(output_voltage)
        self.zener_diode_voltage = self.ArgParameter(zener_diode_voltage)
        #
        # self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])
        # self.pwr_out = self.Port(VoltageSource.empty(), [Output])
        # self.gnd = self.Port(Ground.empty(), [Common])

    def contents(self):
        super().contents()
        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.reg, self.prot, self.tp), _ = self.chain(
                self.pwr_in,
                imp.Block(VoltageRegulator(self.output_voltage)),
                imp.Block(ProtectionZenerDiode(self.zener_diode_voltage)),
                self.Block(VoltageTestPoint()),
            )

        self.connect(self.reg.pwr_out, self.pwr_out)

class LipoCharger(Block):
    @init_in_parent
    def __init__(self, charging_current:RangeLike) -> None:
        super().__init__()
        self.charging_current = self.ArgParameter(charging_current)

        self.chg = self.Port(VoltageSource.empty(), [Output])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.vusb = self.Port(VoltageSink().empty(), [Power, Input])

    def contents(self):
        super().contents()
        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.charger, ), _ = self.chain(
                self.vusb, imp.Block(Mcp73831(self.charging_current)), self.chg
            )
            (self.charge_led, ), _ = self.chain(
                self.Block(IndicatorSinkLed(Led.Yellow)), self.charger.stat
            )
            self.connect(self.vusb, self.charge_led.pwr)



class SmartNob(JlcBoardTop):
    """Robot driver that uses a ESP32 w/ camera and has student-proofing

    Key features:
    - USB-C receptacle for power input and battery charging.
    - LiPo battery connector with voltage regulation and protection circuits.
    - Power management with priority power selection, fuse protection, and gate control.
    - 3.3V voltage regulation for the main logic level power supply.
    - Integrated battery charging circuit with status indication.
    - I2C communication interface with pull-up resistors and test points.
    - Time-of-flight (ToF) sensor array for distance measurement.
    - Inertial Measurement Unit (IMU) and magnetometer for orientation sensing.
    - IO expander for additional GPIOs and a thru-hole RGB LED indicator.
    - Circular LCD display
    - Neopixel LED array for RGB lighting
    - Digital switch for power control.

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

        self.gate = self.Block(OrPowerGate((0, 1)*Volt, (0, 0.1)*Ohm)).connected_from(self.gnd, self.vusb, self.batt.pwr)
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

            # IO EXPANDER

            self.expander = imp.Block(Pca9554())
            self.connect(self.i2c, self.expander.i2c)
            self.r_led = imp.Block(IndicatorLed(Led.Red))
            self.connect(self.expander.io.request('led'), self.r_led.signal)



            self.lcd = imp.Block(Lcd_Round_1_28())
            self.connect(self.mcu.spi.request('spi'), self.lcd.spi)
            self.connect(self.lcd.cs, self.mcu.gpio.request('lcd_cs'))
            self.connect(self.lcd.reset, self.mcu.gpio.request('lcd_reset'))
            self.connect(self.lcd.dc, self.mcu.gpio.request('lcd_dc'))
            self.connect(self.lcd.bled, self.mcu.gpio.request('lcd_bled'))
            self.connect(self.i2c, self.lcd.i2c)
            self.connect(self.lcd.tp_reset, self.mcu.gpio.request("lcd_tp_reset"))
            self.connect(self.lcd.tp_int, self.mcu.gpio.request("lcd_tp_int"))

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
            (self.npx, self.npx_key), _ = self.chain(self.mcu.gpio.request('npx'),  imp.Block(NeopixelArray(4*4)), imp.Block(Neopixel()))


        with self.implicit_connect(
                    ImplicitConnect(self.gnd, [Common]),
            ) as imp:
            # Power gait io
            self.chain(self.gate.btn_out, self.mcu.gpio.request('sw0'))
            self.chain(self.mcu.gpio.request('gate_control'), self.gate.control)
            (self.switch, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('pwr'))


        #
        # with self.implicit_connect(
        #             ImplicitConnect(self.gnd, [Common]),
        #     ) as imp:
        #     BldcConnector()
        #     BldcController()
        #     MagneticEncoder()



    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32s3_Wroom_1),
                (['reg_3v3'], Ldl1117),


                # (['reg_2v5'], Xc6206p),
                # (['reg_1v2'], Xc6206p),
                # (['rgb', 'package'], ThtRgbLed),
                # (['npx_key'], Sk6812Mini_E),

            ],
            instance_values=[
                (['mcu', 'pin_assigns'], [
                    # "i2c=I2CEXT0",
                    # "i2c.scl=38",
                    # "i2c.sda=4",
                    "0.dp=14",
                    "0.dm=13",
                    "npx=9",
                    # 'led=_GPIO0_STRAP',
                ]),
                # (['expander', 'pin_assigns'], [
                # ]),

                # (['prot_batt', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),  # big diodes to dissipate more power
            ],
            class_refinements=[
                (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
                (TestPoint, CompactKeystone5015),
                # (Vl53l0x, Vl53l0xConnector),
                # (Speaker, ConnectorSpeaker),
                (Neopixel, Ws2812b),
                # (MountingHole, MountingHole_M3),
            ],
            class_values=[
                # (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
                #
                # (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),

                # the camera recommended specs are excessively tight, so loosen them a bit
                # (Ov2640_Fpc24, ['device', 'dovdd', 'voltage_limits'], Range(1.71, 4.5)),
                # (Ov2640_Fpc24, ['device', 'dvdd', 'voltage_limits'], Range(1.1, 1.36)),  # allow 1v2
                # (Ov2640_Fpc24, ['device', 'avdd', 'voltage_limits'], Range(2.3, 3.0)),  # allow 2v5
                #
                # (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
                # (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
            ],
        )


class SmartNobTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(SmartNob)
