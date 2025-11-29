import unittest

from typing_extensions import override

from edg import *


class EspLora(JlcBoardTop):
    """ESP32 + discrete 915MHz LoRa via SX1262. USB-C powered.
    TODO: add RF TVS diode to avoid device damage
    TODO: for future versions: use TCXO for SX1262, connect BUSY pin

    Compatible with Meshtastic, with these notes for build configuration:
    - SX126X_DIO3_TCXO_VOLTAGE must not be defined (this design uses a crystal)
    - SX126X_BUSY should be defined to -1 (BUSY not connected)
    - SX126X_DIO2, SX126X_DIO3 can be left undefined (not connected to microcontroller)

    variant.h defines:
    #define BUTTON_PIN 0 // This is the BOOT button
    #define BUTTON_NEED_PULLUP

    #define USE_SX1262

    #define LORA_SCK 5
    #define LORA_MISO 3
    #define LORA_MOSI 6
    #define LORA_CS 7
    #define LORA_RESET 8
    #define LORA_DIO1 38

    #ifdef USE_SX1262
    #define SX126X_CS LORA_CS
    #define SX126X_DIO1 LORA_DIO1
    #define SX126X_RESET LORA_RESET
    #define SX126X_DIO2_AS_RF_SWITCH
    #define SX126X_BUSY -1
    #endif

    pins_arduino.h defines:
    static const uint8_t SDA = 18;
    static const uint8_t SCL = 17;

    static const uint8_t SS = 7;
    static const uint8_t MOSI = 6;
    static const uint8_t MISO = 3;
    static const uint8_t SCK = 5;

    #define SPI_MOSI (11)
    #define SPI_SCK (14)
    #define SPI_MISO (2)
    #define SPI_CS (13)

    #define SDCARD_CS SPI_CS
    """

    @override
    def contents(self) -> None:
        super().contents()

        self.usb = self.Block(UsbCReceptacle())
        self.gnd = self.connect(self.usb.gnd)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)

        with self.implicit_connect(  # POWER
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.choke, self.tp_pwr), _ = self.chain(
                self.usb.pwr, self.Block(SeriesPowerFerriteBead()), self.Block(VoltageTestPoint())
            )
            self.pwr = self.connect(self.choke.pwr_out)

            (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
                self.pwr,
                imp.Block(LinearRegulator(output_voltage=3.3 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9) * Volt)),
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

        with self.implicit_connect(  # 3V3 DOMAIN
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerBle())

            (self.usb_esd,), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

            (self.ledr,), _ = self.chain(self.mcu.gpio.request("ledr"), imp.Block(IndicatorLed(Led.Red)))
            (self.ledg,), _ = self.chain(self.mcu.gpio.request("ledg"), imp.Block(IndicatorLed(Led.Yellow)))
            (self.ledb,), _ = self.chain(self.mcu.gpio.request("ledb"), imp.Block(IndicatorLed(Led.White)))

            self.lora = imp.Block(Sx1262())
            (self.tp_lora_spi,), _ = self.chain(
                self.mcu.spi.request("lora"), imp.Block(SpiTestPoint("lr")), self.lora.spi
            )
            (self.tp_lora_cs,), _ = self.chain(
                self.mcu.gpio.request("lora_cs"), imp.Block(DigitalTestPoint("lr_cs")), self.lora.cs
            )
            (self.tp_lora_rst,), _ = self.chain(
                self.mcu.gpio.request("lora_rst"), imp.Block(DigitalTestPoint("lr_rs")), self.lora.reset
            )
            (self.tp_lora_dio,), _ = self.chain(
                self.mcu.gpio.request("lora_irq"), imp.Block(DigitalTestPoint("lr_di")), self.lora.irq
            )
            (self.tp_lora_busy,), _ = self.chain(
                self.mcu.gpio.request("lora_busy"), imp.Block(DigitalTestPoint("lr_bs")), self.lora.busy
            )

            self.i2c = self.mcu.i2c.request("i2c")
            (self.i2c_pull, self.i2c_tp), _ = self.chain(
                self.i2c, imp.Block(I2cPullup()), self.Block(I2cTestPoint("i2c"))
            )

            self.oled = imp.Block(Er_Oled_096_1_1())
            self.connect(self.i2c, self.oled.i2c)
            (self.oled_rst, self.oled_pull), _ = self.chain(
                imp.Block(Apx803s()),  # -29 variant used on Adafruit boards
                imp.Block(PullupResistor(10 * kOhm(tol=0.05))),
                self.oled.reset,
            )

            self.sd = imp.Block(SdCard())
            self.connect(self.mcu.spi.request("sd"), self.sd.spi)
            self.connect(self.mcu.gpio.request("sd_cs"), self.sd.cs)

            self.nfc = imp.Block(Pn7160())
            self.connect(self.nfc.pwr, self.pwr)
            self.connect(self.nfc.pwr_io, self.v3v3)
            self.connect(self.nfc.i2c, self.i2c)
            self.connect(self.nfc.reset, self.mcu.gpio.request("nfc_rst"))
            self.connect(self.nfc.irq, self.mcu.gpio.request("nfc_irq"))

    @override
    def multipack(self) -> None:
        self.tx_cpack = self.PackedBlock(CombinedCapacitor())
        self.pack(self.tx_cpack.elements.request("0"), ["lora", "tx_l", "c"])
        self.pack(self.tx_cpack.elements.request("1"), ["lora", "tx_pi", "c1"])

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Esp32s3_Wroom_1),
                (["reg_3v3"], Ldl1117),
                (["lora", "ant"], RfConnectorAntenna),
                (["lora", "ant", "conn"], Amphenol901143),
            ],
            instance_values=[
                (["refdes_prefix"], "L"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        # LoRa and OLED pinnings consistent with Lilygo T3S3
                        "lora.mosi=GPIO6",
                        "lora.sck=GPIO5",
                        "lora_cs=GPIO7",
                        "lora_rst=GPIO8",
                        "lora.miso=GPIO3",
                        "lora_irq=GPIO38",  # IO33 on original, but is a PSRAM pin
                        "lora_busy=GPIO40",  # IO34 on original, but is a PSRAM pin
                        "i2c.sda=GPIO18",
                        "i2c.scl=GPIO17",
                        "sd_cs=GPIO13",
                        "sd.mosi=GPIO11",
                        "sd.sck=GPIO14",
                        "sd.miso=GPIO2",
                        "nfc_rst=32",
                        "nfc_irq=GPIO47",
                        "ledr=34",
                        "ledg=35",
                        "ledb=39",
                    ],
                ),
                (["mcu", "programming"], "uart-auto-button"),
                (["usb", "conn", "current_limits"], Range(0.0, 1.1)),  # fudge it a lot
                (
                    ["pwr", "current_drawn"],
                    Range(0.031392638, 0.8),
                ),  # allow use of basic part ferrite, assume not everything run simultaneously
                (
                    ["lora", "balun", "c", "capacitance"],
                    Range(2.8e-12 * 0.8, 2.8e-12 * 1.2),
                ),  # extend tolerance to find a part
                (["lora", "dcc_l", "manual_frequency_rating"], Range(0, 20e6)),
                (["nfc", "emc", "l1", "manual_frequency_rating"], Range(0, 100e6)),
                (["nfc", "emc", "l2", "manual_frequency_rating"], Range(0, 100e6)),
                # these RF passives aren't common / basic parts and will be DNP'd anyways
                (["lora", "tx_l", "c_lc", "require_basic_part"], False),
                (["lora", "tx_pi", "c2", "require_basic_part"], False),
                (["lora", "balun", "c_p", "require_basic_part"], False),
                (["lora", "ant_pi", "c1", "require_basic_part"], False),
                (["lora", "ant_pi", "c2", "require_basic_part"], False),
                (["nfc", "emc", "c1", "require_basic_part"], False),
                (["nfc", "emc", "c2", "require_basic_part"], False),
                (["nfc", "damp", "r1", "require_basic_part"], False),
                (["nfc", "damp", "r2", "require_basic_part"], False),
                (["nfc", "match", "cp1", "require_basic_part"], False),
                (["nfc", "match", "cp2", "require_basic_part"], False),
                (["nfc", "cvdd1", "cap", "footprint_spec"], "Capacitor_SMD:C_0805_2012Metric"),
                (["nfc", "cvdd2", "cap", "footprint_spec"], "Capacitor_SMD:C_0805_2012Metric"),
                (["nfc", "ctvdd1", "cap", "footprint_spec"], "Capacitor_SMD:C_0805_2012Metric"),
                (["nfc", "ctvdd2", "cap", "footprint_spec"], "Capacitor_SMD:C_0805_2012Metric"),
                (["nfc", "cvdd1", "cap", "require_basic_part"], False),
                (["nfc", "cvdd2", "cap", "require_basic_part"], False),
                (["nfc", "ctvdd1", "cap", "require_basic_part"], False),
                (["nfc", "ctvdd2", "cap", "require_basic_part"], False),
                # got bamboozled, this will be replaced in the future with a part from a non-awful vendor
                (["lora", "rf_sw", "ic", "restricted_availiability"], False),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (SdCard, Molex1040310811),
                (TestPoint, CompactKeystone5015),
            ],
            class_values=[
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),
                (Nonstrict3v3Compatible, ["nonstrict_3v3_compatible"], True),
                (DiscreteRfWarning, ["discrete_rf_warning"], False),
                (Er_Oled_096_1_1, ["iref_res", "resistance"], Range.from_tolerance(470e3, 0.1)),
            ],
        )


class EspLoraTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(EspLora)
