import unittest  # Importing the unittest module for creating test cases

from edg import *  # Importing all from the 'edg' library for electronics design

from .test_robotdriver import PwmConnector  # Importing PwmConnector from test_robotdriver module
from .test_multimeter import FetPowerGate  # Importing FetPowerGate from test_multimeter module

# Defining a class PcbBot which inherits from JlcBoardTop, for designing a PCB with specific features
class Estop(JlcBoardTop):
    """Robot driver that uses an ESP32 with a camera and has student-proofing."""

    # Method to define the contents of the PCB
    def contents(self) -> None:
        super().contents()  # Calling the contents method from the superclass

        # Adding a USB C receptacle with a current limit of 0-3 Amps
        self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))
        # Connecting the power line of the USB
        self.vusb = self.connect(self.usb.pwr)

        # Adding a LiPo battery connector with a specified voltage range
        #self.batt = self.Block(LipoConnector(actual_voltage=(7.2, 28)*Volt))
        self.batt = self.Block(LipoConnector(voltage=(7.2, 28)*Volt, actual_voltage=(7.2, 28)*Volt))
        self.vbatt = self.connect(self.batt.pwr)
        #self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

        # Creating a merged voltage source from the USB and battery ground
        self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
            self.usb.gnd, self.batt.gnd
        )
        # Connecting the merged ground source
        self.gnd = self.connect(self.gnd_merge.pwr_out)
        # Creating a test point for the ground connection
        self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.gnd_merge.pwr_out)


        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),  # Implicitly connecting ground to common ground
        ) as imp:
            pass

            # Chain for 3.3V power regulation
            (self.reg_3v3, self.prot_3v3, self.tp_3v3), _ = self.chain(
                self.vbatt,
                imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),  # 3.3V Voltage Regulator
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt)),  # Zener Diode for protection
                self.Block(VoltageTestPoint()),  # Voltage test point
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)  # Connecting the output of 3.3V regulator

            # TODO: Chain for 12V power regulation
            (self.reg_12v, self.prot_12v, self.tp_12v), _ = self.chain(
                self.vbatt,
                imp.Block(BuckConverter(output_voltage=12*Volt(tol=0.05))),  # 12V Voltage Regulator
                imp.Block(ProtectionZenerDiode(voltage=(12.5, 14.0)*Volt)),  # Zener Diode for protection
                self.Block(VoltageTestPoint()),  # Voltage test point
            )
            self.v12 = self.connect(self.reg_12v.pwr_out)  # Connecting the output of 12V regulator

            # TODO: Chain for 5V power regulation
            (self.reg_5v, self.prot_5v, self.tp_5v), _ = self.chain(
                self.vbatt,
                imp.Block(BuckConverter(output_voltage=5*Volt(tol=0.05))),  # 12V Voltage Regulator
                imp.Block(ProtectionZenerDiode(voltage=(5.5, 6.0)*Volt)),  # Zener Diode for protection
                self.Block(VoltageTestPoint()),  # Voltage test point
            )
            self.v5 = self.connect(self.reg_5v.pwr_out)  # Connecting the output of 12V regulator


        # 3V3 DOMAIN section begins
        with self.implicit_connect(
                ImplicitConnect(self.v3v3, [Power]),  # Implicitly connecting to the 3.3V power line
                ImplicitConnect(self.gnd, [Common]),  # Implicitly connecting to common ground
        ) as imp:
            self.mcu = imp.Block(IoController())  # Adding an IO Controller (Microcontroller Unit)
            self.i2s = self.mcu.with_mixin(IoControllerI2s())

            # Chain for USB ESD protection
            (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                          self.mcu.usb.request())  # ESD protection diode
            # I2C bus setup
            self.i2c = self.mcu.i2c.request('i2c')

            (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
                self.i2c,
                imp.Block(I2cPullup()), imp.Block(I2cTestPoint('i2c')),)

            # # IO Expander setup
            # self.expander = imp.Block(Pca9554())
            # self.connect(self.i2c, self.expander.i2c)

            # TODO: Check: Directional switch: 5 buttons
            self.dir = imp.Block(DigitalDirectionSwitch())
            self.connect(self.dir.a, self.mcu.gpio.request('dir_a'))
            self.connect(self.dir.b, self.mcu.gpio.request('dir_b'))
            self.connect(self.dir.c, self.mcu.gpio.request('dir_c'))
            self.connect(self.dir.d, self.mcu.gpio.request('dir_d'))
            self.connect(self.dir.with_mixin(DigitalDirectionSwitchCenter()).center, self.mcu.gpio.request('dir_cen'))

            # Chain for RGB LED
            (self.led, ), _ = self.chain(self.mcu.gpio.request('led'), imp.Block(IndicatorLed(Led.Red)))


            # OLED display setup
            self.oled = imp.Block(Er_Oled_096_1_1())
            self.connect(self.i2c, self.oled.i2c)
            self.connect(self.oled.reset, self.mcu.gpio.request("oled_reset"))

            # Chain for battery voltage sensing
            (self.vbatt_sense, ), _ = self.chain(
                self.vbatt,
                imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                self.mcu.adc.request('vbatt_sense')
            )

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

        # Power switch setup
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),  # Implicitly connecting to common ground
        ) as imp:
            self.switch = imp.Block(DigitalSwitch())
            self.connect(self.switch.out, self.mcu.gpio.request('pwr'))


        #TODO: Check: 3v3 output pins
        self.jst_3v3 = self.Block(PassiveConnector(length=2))   # lenth number of pins (auto allocate?
        self.connect(self.jst_3v3.pins.request('2').adapt_to(VoltageSink()), self.reg_3v3.pwr_out)
        self.connect(self.jst_3v3.pins.request('1').adapt_to(Ground()), self.gnd)

        #TODO: 5v devices
        with self.implicit_connect(
                ImplicitConnect(self.v5, [Power]),  # Implicitly connecting to the 3.3V power line
                ImplicitConnect(self.gnd, [Common]),  # Implicitly connecting to common ground
        ) as imp:
            (self.npx, ), _ = self.chain(self.mcu.gpio.request('npx'), imp.Block(Neopixel()))

            self.jst_5v = self.Block(PassiveConnector(length=2))   # lenth number of pins (auto allocate?
            self.connect(self.jst_5v.pins.request('2').adapt_to(VoltageSink()), self.v5)
            self.connect(self.jst_5v.pins.request('1').adapt_to(Ground()), self.gnd)



    #TODO: mosfet
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common])
        ) as imp:
            self.mosfet = imp.Block(HighSideSwitch(clamp_voltage=(14, 17)*Volt))
            self.connect(self.mosfet.pwr, self.batt.pwr)
            self.connect(self.mosfet.control, self.mcu.gpio.request('mosfet'))

        # 3V3 DOMAIN section begins
        with self.implicit_connect(
                ImplicitConnect(self.mosfet.output, [Power]),  # Implicitly connecting to the 3.3V power line
                ImplicitConnect(self.gnd, [Common]),  # Implicitly connecting to common ground
        ) as imp:
            #TODO: Check: Current Sensor
            self.cbatt_sense = imp.Block(OpampCurrentSensor(
                resistance=0.01*Ohm(tol=0.01),
                ratio=Range.from_tolerance(15, 0.05),
                input_impedance=20*kOhm(tol=0.05)
                ))
            (self.cbatt_sense_tp, self.cbatt_sense_clamp), _ = self.chain(
                self.cbatt_sense.out,
                self.Block(AnalogTestPoint()),
                imp.Block(AnalogClampZenerDiode((2.7, 3.3)*Volt)),
                self.mcu.adc.request('cbatt_sense')
            )

            self.connect(self.cbatt_sense.pwr_in, self.mosfet.output)
            self.connect(self.cbatt_sense.ref, self.batt.gnd.as_analog_source())

        #TODO: Check: Power output pins
        self.jst_out = self.Block(PassiveConnector(length=2))   # lenth number of pins auto allocate?
        self.connect(self.jst_out.pins.request('2').adapt_to(VoltageSink()), self.cbatt_sense.pwr_out)
        #self.connect(self.jst_out.pins.request('2').adapt_to(VoltageSink()), self.mosfet.output)
        self.connect(self.jst_out.pins.request('1').adapt_to(Ground()), self.gnd)

        #TODO:
        n_lipo_pins = 6
        self.lipo_pins = self.Block(PassiveConnector(length=n_lipo_pins+1))   # lenght number of pins auto allocate?
        self.connect(self.lipo_pins.pins.request('1').adapt_to(Ground()), self.gnd)
        self.v_sense = ElementDict[Connector]()

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common])
        ) as imp:
            for i in range(n_lipo_pins):
                (self.v_sense[i], ), _ = self.chain(
                    self.lipo_pins.pins.request(str(i+2)).adapt_to(VoltageSource(voltage_out=(0.0, 5.0))),
                    imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
                    self.mcu.adc.request(f'v_sense_{i+2}')
                )


# Method to define refinements for the PCB design
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            # Below are various refinements and specifications for the components
            instance_refinements=[
                # Refinements for specific components like MCU, voltage regulators, connectors, etc.
                # These define particular models or types for the components used in the design
                (['mcu'], Esp32s3_Wroom_1),
                (['reg_12v'], Tps54202h),
                (['reg_5v'], Tps54202h),
                (['reg_3v3'], Tps54202h),
                (['reg_2v5'], Xc6206p),
                (['reg_1v2'], Xc6206p),
            ],
            instance_values=[
                # Specific value assignments for various component parameters
                # These customize component features like pin assignments, diode footprints, etc.
                (['mcu', 'pin_assigns'], [
                    "i2c=I2CEXT0",
                    "i2c.scl=38",
                    "i2c.sda=4",
                ]),
                (['cbatt_sense', 'sense', 'res', 'res', 'require_basic_part'], False),
                (['reg_3v3', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 0.85),
                # (['reg_3v3', 'power_path', 'in_cap', 'cap', 'exact_capacitance'], False),
            ],
            class_refinements=[
                # Class-level refinements for certain types of components
                # These set default series or types for categories of components like connectors, test points, etc.
                (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
                (DirectionSwitch, Skrh),            # TODO: Check which one to use?
                (Speaker, ConnectorSpeaker),
                (Opamp, Opa197),
            ],
            class_values=[
                # Class-level value settings for components
                # These adjust specifications like voltage limits, part numbers, etc., for component types
                (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
                (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
                (JlcInductor, ['manual_frequency_rating'], Range.all()),
            ],
        )

# Test case class for PcbBot, inherits from unittest.TestCase
class EstopTestCase(unittest.TestCase):
    # Test method to compile and check the PCB design
    def test_design(self) -> None:
        compile_board_inplace(Estop)  # Compiles the PcbBot design to validate it
