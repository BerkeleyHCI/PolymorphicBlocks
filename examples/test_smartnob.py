import unittest

from edg import *

from .test_robotdriver import PwmConnector
from .test_multimeter import FetPowerGate
from test_bldc_controller import *

class PcbBot(JlcBoardTop):
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

        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.fuse, self.gate, self.prot_batt, self.tp_batt), _ = self.chain(
                self.batt.pwr,
                imp.Block(SeriesPowerPptcFuse((2, 4)*Amp)),
                imp.Block(FetPowerGate()),
                imp.Block(ProtectionZenerDiode(voltage=(4.5, 6.0)*Volt)),
                self.Block(VoltageTestPoint()))
            self.vbatt = self.connect(self.gate.pwr_out)  # downstream of fuse

            self.pwr_or = self.Block(PriorityPowerOr(  # also does reverse protection
                (0, 1)*Volt, (0, 0.1)*Ohm
            )).connected_from(self.gnd_merge.pwr_out, self.usb.pwr, self.gate.pwr_out)
            self.pwr = self.connect(self.pwr_or.pwr_out)

            (self.reg_3v3, self.prot_3v3, self.tp_3v3), _ = self.chain(
                self.pwr,
                imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt)),
                self.Block(VoltageTestPoint()),
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

            (self.charger, ), _ = self.chain(
                self.vusb, imp.Block(Mcp73831(200*mAmp(tol=0.2))), self.batt.chg
            )
            (self.charge_led, ), _ = self.chain(
                self.Block(IndicatorSinkLed(Led.Yellow)), self.charger.stat
            )
            self.connect(self.vusb, self.charge_led.pwr)

        # 3V3 DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.v3v3, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())

            (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                          self.mcu.usb.request())

            # single onboard debugging LED
            (self.led, ), _ = self.chain(self.mcu.gpio.request('led'), imp.Block(IndicatorLed(Led.Red)))

            self.i2c = self.mcu.i2c.request('i2c')

            # IO EXPANDER
            self.expander = imp.Block(Pca9554())
            self.connect(self.i2c, self.expander.i2c)

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
                self.vbatt,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('vbatt_sense')
            )

        # VBATT DOMAIN
        with self.implicit_connect(
                ImplicitConnect(self.vbatt, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.npx, self.npx_key), _ = self.chain(self.mcu.gpio.request('npx'),  imp.Block(NeopixelArray(4*4)), imp.Block(Neopixel()))


        with self.implicit_connect(
                    ImplicitConnect(self.gnd, [Common]),
            ) as imp:
            # Power gait
            self.chain(self.gate.btn_out, self.mcu.gpio.request('sw0'))
            self.chain(self.mcu.gpio.request('gate_control'), self.gate.control)

            (self.switch, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('pwr'))



        with self.implicit_connect(
                    ImplicitConnect(self.gnd, [Common]),
            ) as imp:
            BldcConnector()
            BldcController()
            MagneticEncoder()



    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (['mcu'], Esp32s3_Wroom_1),
                (['reg_3v3'], Ldl1117),
                (['tof', 'elt[0]', 'conn'], PinSocket254),
                (['tof', 'elt[1]', 'conn'], PinSocket254),
                (['tof', 'elt[2]', 'conn'], PinSocket254),
                (['tof', 'elt[3]', 'conn'], PinSocket254),
                (['switch', 'package'], KailhSocket),

                (['reg_2v5'], Xc6206p),
                (['reg_1v2'], Xc6206p),
                (['rgb', 'package'], ThtRgbLed),
                (['npx_key'], Sk6812Mini_E),

            ],
            instance_values=[
                (['mcu', 'pin_assigns'], [
                    "i2c=I2CEXT0",
                    "i2c.scl=38",
                    "i2c.sda=4",
                    "0.dp=14",
                    "0.dm=13",
                    "npx=9",
                    'led=_GPIO0_STRAP',
                ]),
                (['expander', 'pin_assigns'], [
                ]),

                (['prot_batt', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),  # big diodes to dissipate more power
            ],
            class_refinements=[
                (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
                (TestPoint, CompactKeystone5015),
                (Vl53l0x, Vl53l0xConnector),
                (Speaker, ConnectorSpeaker),
                (Neopixel, Ws2812b),
                (MountingHole, MountingHole_M3),
            ],
            class_values=[
                (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock

                (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),

                # the camera recommended specs are excessively tight, so loosen them a bit
                (Ov2640_Fpc24, ['device', 'dovdd', 'voltage_limits'], Range(1.71, 4.5)),
                (Ov2640_Fpc24, ['device', 'dvdd', 'voltage_limits'], Range(1.1, 1.36)),  # allow 1v2
                (Ov2640_Fpc24, ['device', 'avdd', 'voltage_limits'], Range(2.3, 3.0)),  # allow 2v5

                (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
                (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
            ],
        )


class PcbBotTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(PcbBot)
