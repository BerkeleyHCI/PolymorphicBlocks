import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class EthernetPhyPairLink(Link):
    """Ethernet connection between the PHY and magnetics."""

    def __init__(self) -> None:
        super().__init__()
        self.phy = self.Port(EthernetPhyPairPort.empty())
        self.magnetics = self.Port(EthernetPhyPairPort.empty())

    @override
    def contents(self) -> None:
        self.connect(self.phy.pos, self.magnetics.pos)
        self.connect(self.phy.neg, self.magnetics.neg)
        self.connect(self.phy.center, self.magnetics.center)


class EthernetPhyPairPort(Port[EthernetPhyPairLink]):
    """PHY-side port for an ethernet pair"""

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())
        self.center = self.Port(Passive())


class EthernetMagneticsPairPort(Port[EthernetPhyPairLink]):
    """Magnetics-side port for an ethernet pair"""

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())
        self.center = self.Port(Passive())


class EthernetPoeLink(Link):
    """Power over Ethernet connection between the powered device and the magnetics."""

    def __init__(self) -> None:
        super().__init__()
        self.poe = self.Port(EthernetPoeDevicePort.empty())
        self.magnetics = self.Port(EthernetPoeJackPort.empty())

    @override
    def contents(self) -> None:
        self.connect(self.poe.pos, self.magnetics.pos)
        self.connect(self.poe.neg, self.magnetics.neg)


class EthernetPoeDevicePort(Port[EthernetPoeLink]):
    """Powered device side port for Power over Ethernet. Generally exposed by a PoE controller subcircuit"""

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())


class EthernetPoeJackPort(Port[EthernetPoeLink]):
    """Jack side port for Power over Ethernet, post-rectification."""

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())


class Hy931147c_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()

        self.rx = self.Port(EthernetMagneticsPairPort.empty())
        self.tx = self.Port(EthernetMagneticsPairPort.empty())
        self.poe = self.Port(EthernetPoeJackPort.empty())

        self.led_grn_anode = self.Port(Passive(), optional=True)
        self.led_grn_cathode = self.Port(Passive(), optional=True)

        self.led_yel_anode = self.Port(Passive(), optional=True)
        self.led_yel_cathode = self.Port(Passive(), optional=True)

        self.shield = self.Port(Passive())

    @override
    def contents(self):
        super().contents()

        self.require(self.led_grn_anode.is_connected() == self.led_grn_cathode.is_connected())
        self.require(self.led_yel_anode.is_connected() == self.led_yel_cathode.is_connected())

        self.footprint(
            "J",
            "Connector_RJ:RJ45_Wuerth_7499111446_Horizontal",
            {
                "1": self.rx.pos,
                "2": self.rx.neg,
                "3": self.rx.center,
                "6": self.tx.neg,
                "5": self.tx.pos,
                "4": self.tx.center,
                "9": self.poe.pos,
                "10": self.poe.neg,
                "11": self.led_yel_anode,
                "12": self.led_yel_cathode,
                "13": self.led_grn_anode,
                "14": self.led_grn_cathode,
                "SH": self.shield,
            },
            "Hanrun",
            "HY931147C",
        )
        self.assign(self.lcsc_part, "C91754")
        self.assign(self.actual_basic_part, False)


class Hy931147c(Connector, GeneratorBlock):
    """Commonly available RJ45 magjack with PoE support.
    Footprint and pin-compatible with Wuerth 7499211121A.

    TODO should define and implement an abstract base class, EthernetConnector, which defines the
    magnetics-side ports and can also be implemented by DiscreteMagneticsEthernetConnector,
    which has a passive-typed RJ45, discrete magnetics, and optional PoE diode bridge generator.

    TODO: allow LEDs to be driven in source mode

    TODO: support LED connection by multipacking"""

    _LED_CURRENT_LIMITS = (0, 20) * mAmp

    def __init__(self, *, led_target_current: RangeLike = (1, 10) * mAmp) -> None:
        super().__init__()
        self.led_target_current = self.ArgParameter(led_target_current)

        self.conn = self.Block(Hy931147c_Device())

        self.rx = self.Export(self.conn.rx)
        self.tx = self.Export(self.conn.tx)
        self.poe = self.Export(self.conn.poe)

        self.gnd = self.Port(Ground())  # for termination
        self.pwr_led = self.Port(VoltageSink(), optional=True)  # for LED power
        self.led_yel_sink = self.Port(
            DigitalSink(current_draw=RangeExpr()), optional=True, doc="Yellow LED cathode connection"
        )
        self.led_grn_sink = self.Port(
            DigitalSink(current_draw=RangeExpr()), optional=True, doc="Green LED cathode connection"
        )
        self.generator_param(self.led_yel_sink.is_connected(), self.led_grn_sink.is_connected())

    @override
    def generate(self) -> None:
        super().generate()

        self.require(self.pwr_led.is_connected() == self.led_yel_sink.is_connected() | self.led_grn_sink.is_connected())
        if self.get(self.led_yel_sink.is_connected()):
            self.led_yel_res = self.Block(
                Resistor(
                    (1 / self.led_target_current).shrink_multiply(
                        self.pwr_led.link().voltage - self.led_yel_sink.link().output_thresholds.lower()
                    )
                )
            )
            self.connect(self.pwr_led.net, self.conn.led_yel_anode)
            self.connect(self.conn.led_yel_cathode, self.led_yel_res.a)
            self.connect(self.led_yel_res.a, self.led_yel_sink.net)
            self.assign(
                self.led_yel_sink.current_draw, -self.pwr_led.link().voltage / self.led_yel_res.actual_resistance
            )

        if self.get(self.led_grn_sink.is_connected()):
            self.led_grn_res = self.Block(
                Resistor(
                    (1 / self.led_target_current).shrink_multiply(
                        self.pwr_led.link().voltage - self.led_grn_sink.link().output_thresholds.lower()
                    )
                )
            )
            self.connect(self.pwr_led.net, self.conn.led_grn_anode)
            self.connect(self.conn.led_grn_cathode, self.led_grn_res.a)
            self.connect(self.led_grn_res.a, self.led_grn_sink.net)
            self.assign(
                self.led_grn_sink.current_draw, -self.pwr_led.link().voltage / self.led_grn_res.actual_resistance
            )

        self.cap = self.Block(Capacitor(1 * nFarad(tol=0.2), voltage=(0, 1000) * Volt))  # termination
        self.connect(self.cap.neg, self.gnd.net)
        self.connect(self.cap.pos, self.conn.shield)


class W5500_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()

        self.agnd = self.Port(Ground())
        self.gnd = self.Port(Ground())

        self.avdd = self.Port(
            VoltageSink(
                voltage_limits=(2.97, 3.63) * Volt,
                current_draw=(13, 132) * mAmp,  # power down to 100M link
            )
        )
        self.vdd = self.Port(VoltageSink(voltage_limits=(2.97, 3.63) * Volt))

        self.v1v20 = self.Port(VoltageSource(voltage_out=1.2 * Volt(tol=0), current_limits=0 * Amp(tol=0)))
        self.tocap = self.Port(VoltageSource(voltage_out=self.avdd.link().voltage))  # assumed, not documented
        self.exres1 = self.Port(AnalogSource.from_supply(self.gnd, self.avdd))  # assumed, not documented

        self.crystal = self.Port(CrystalDriver(frequency_limits=25 * MHertz(tol=30e-6)))  # TODO also support CLKIN

        self.txp = self.Port(Passive())
        self.txn = self.Port(Passive())
        self.rxp = self.Port(Passive())
        self.rxn = self.Port(Passive())

        dio_model = DigitalBidir.from_supply(
            self.gnd,
            self.vdd,
            voltage_limit_abs=(-0.3, 5.5) * Volt,
            input_threshold_abs=(0.8, 2.0) * Volt,
            current_limits=(-5, 5) * mAmp,  # absolute max rating for DC input current
        )
        dio_pu_model = DigitalSink.from_supply(
            self.gnd,
            self.vdd,
            voltage_limit_abs=(-0.3, 5.5) * Volt,
            input_threshold_abs=(0.8, 2.0) * Volt,
            pullup_capable=True,
        )

        self.spi = self.Port(SpiPeripheral(dio_model))
        self.scsn = self.Port(dio_pu_model)
        # according to some internet forum posts, a reset pulse is not needed
        self.rstn = self.Port(dio_pu_model, optional=True)
        self.intn = self.Port(DigitalSource.low_from_supply(self.gnd), optional=True)

        # PMODE[0..2] internally pulled up, defaulting to auto-negotiation
        self.pmode0 = self.Port(dio_pu_model, optional=True)
        self.pmode1 = self.Port(dio_pu_model, optional=True)
        self.pmode2 = self.Port(dio_pu_model, optional=True)

        # TODO add LEDs

    @override
    def contents(self):
        super().contents()

        self.footprint(
            "U",
            "Package_QFP:LQFP-48_7x7mm_P0.5mm",
            {
                "1": self.txn,
                "2": self.txp,
                ("3", "9", "14", "16", "19", "48"): self.agnd,
                ("4", "8", "11", "15", "17", "21"): self.avdd,
                "5": self.rxn,
                "6": self.rxp,
                # "7": DNC
                "10": self.exres1,
                # ("12", "13"): NC
                # "18": VBG, "must be left floating"
                "20": self.tocap,
                "22": self.v1v20,
                "23": self.gnd,  # RSVD, "must be tied to GND"
                # "24": self.spdled,
                # "25": self.linkled,
                # "26": self.dupled,
                # "27": self.actled,
                "28": self.vdd,
                "29": self.gnd,
                "30": self.crystal.xi,
                "31": self.crystal.xo,
                "32": self.scsn,
                "33": self.spi.sck,
                "34": self.spi.miso,
                "35": self.spi.mosi,
                "36": self.intn,
                "37": self.rstn,
                # ("38", "39", "40", "41", "42"): NC
                "43": self.pmode2,
                "44": self.pmode1,
                "45": self.pmode0,
                # ("46", "47"): NC
            },
            "Wiznet",
            "W5500",
        )
        self.assign(self.lcsc_part, "C32843")
        self.assign(self.actual_basic_part, False)


class W5500(Resettable, Interface, Block):
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(W5500_Device())
        self.pwr = self.Export(self.ic.vdd)
        self.gnd = self.Export(self.ic.gnd)

        self.tx = self.Port(EthernetPhyPairPort.empty())
        self.rx = self.Port(EthernetPhyPairPort.empty())
        self.spi = self.Export(self.ic.spi)
        self.cs = self.Export(self.ic.scsn)
        self.int = self.Export(self.ic.intn, optional=True)

    def contents(self) -> None:
        super().contents()

        self.connect(self.reset, self.ic.rstn)
        self.connect(self.gnd, self.ic.agnd)
        self.l = self.Block(SeriesPowerFerriteBead()).connected(self.pwr, self.ic.avdd)

        self.crystal = self.Block(OscillatorReference(frequency=25 * MHertz(tol=30e-6)))
        self.connect(self.crystal.gnd, self.gnd)
        self.connect(self.crystal.crystal, self.ic.crystal)

        with self.implicit_connect(ImplicitConnect(self.gnd, [Common])) as imp:
            self.exres1 = imp.Block(AnalogSetpointResistor(12.4 * kOhm(tol=0.01))).connected(io=self.ic.exres1)
            self.c1v20 = imp.Block(DecouplingCapacitor(10 * nFarad(tol=0.2))).connected(pwr=self.ic.v1v20)
            self.tocap = imp.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(pwr=self.ic.tocap)

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
            ImplicitConnect(self.ic.vdd, [Power]),
        ) as imp:
            self.vdd_cap0 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
            self.vdd_cap1 = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
            ImplicitConnect(self.ic.avdd, [Power]),
        ) as imp:
            self.avdd_caps = ElementDict[DecouplingCapacitor]()
            for i in range(6):
                self.avdd_caps[str(i)] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
            self.avdd_caps[6] = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

        # TODO ethernet circuits


class IotThermalCamera(JlcBoardTop):
    """Dual-mode IR and RGB camera board with ESP32"""

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
                imp.Block(BuckConverter(output_voltage=3.3 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9) * Volt)),
            )
            self.v3v3 = self.connect(self.reg_3v3.pwr_out)

            (self.reg_3v0,), _ = self.chain(self.v3v3, imp.Block(LinearRegulator(output_voltage=3.0 * Volt(tol=0.03))))
            self.v3v0 = self.connect(self.reg_3v0.pwr_out)

            (self.reg_2v8,), _ = self.chain(self.v3v3, imp.Block(LinearRegulator(output_voltage=2.8 * Volt(tol=0.03))))
            self.v2v8 = self.connect(self.reg_2v8.pwr_out)

            (self.reg_1v2,), _ = self.chain(self.v3v3, imp.Block(LinearRegulator(output_voltage=1.2 * Volt(tol=0.03))))
            self.v1v2 = self.connect(self.reg_1v2.pwr_out)

        # 3V3 DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())
            self.mcu.with_mixin(IoControllerWifi())

            (self.usb_esd,), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

            self.i2c = self.mcu.i2c.request("i2c")
            (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
                self.i2c, imp.Block(I2cPullup()), imp.Block(I2cTestPoint("i2c"))
            )

            mcu_touch = self.mcu.with_mixin(IoControllerTouchDriver())
            (self.touch_duck,), _ = self.chain(
                mcu_touch.touch.request("touch_duck"), imp.Block(FootprintTouchPad("edg:Symbol_DucklingSolid"))
            )

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request("ledr"))

        # CAMERA MULTI DOMAIN
        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.cam = imp.Block(Ov2640_Fpc24())
            self.connect(self.cam.pwr, self.v3v0)
            self.connect(self.cam.pwr_analog, self.v2v8)
            self.connect(self.cam.pwr_digital, self.v1v2)
            self.connect(self.cam.dvp8, self.mcu.with_mixin(IoControllerDvp8()).dvp8.request("cam"))
            self.connect(self.cam.sio, self.i2c)
            self.connect(self.cam.reset, self.mcu.gpio.request("cam_rst"))

            self.flir = imp.Block(FlirLepton())
            self.connect(self.flir.pwr_io, self.v3v0)
            self.connect(self.flir.pwr, self.v2v8)
            self.connect(self.flir.pwr_core, self.v1v2)
            self.connect(self.flir.spi, self.mcu.spi.request("flir"))
            self.connect(self.flir.cci, self.i2c)
            self.connect(self.flir.reset, self.mcu.gpio.request("flir_rst"))
            self.connect(self.flir.shutdown, self.mcu.gpio.request("flir_pwrdn"))
            self.connect(self.flir.cs, self.mcu.gpio.request("flir_cs"))
            self.connect(self.flir.vsync, self.mcu.gpio.request("flir_vsync"))

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Esp32s3_Wroom_1),
                (["reg_3v3"], Tps54202h),
                (["cam", "device", "conn"], Fpc050BottomFlip),
            ],
            instance_values=[
                (["refdes_prefix"], "T"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        "cam.vsync=25",
                        "cam.href=24",
                        "cam_rst=23",
                        "cam.y7=22",
                        "cam.xclk=21",
                        "cam.y6=20",
                        "cam.y5=15",
                        "cam.pclk=19",
                        "cam.y4=12",
                        "cam.y0=18",
                        "cam.y3=10",
                        "cam.y1=17",
                        "cam.y2=11",
                        "i2c.sda=31",
                        "i2c.scl=32",
                        "flir_pwrdn=33",
                        "flir_rst=34",
                        "flir_cs=38",
                        "flir.sck=39",
                        "flir.mosi=5",
                        "flir.miso=4",
                        "flir_vsync=7",
                        "ledr=_GPIO0_STRAP",
                        "touch_duck=6",
                    ],
                ),
                (["mcu", "programming"], "uart-auto"),
                (["reg_2v8", "ic", "actual_dropout"], Range(0.0, 0.05)),  # 3.3V @ 100mA
                (["reg_3v0", "ic", "actual_dropout"], Range(0.0, 0.16)),  # 3.3V @ 400mA
                (["reg_3v3", "power_path", "inductor", "manual_frequency_rating"], Range(0, 21e6)),
                (["usb", "pwr", "current_limits"], Range(0.0, 0.8)),  # a bit over
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (TestPoint, CompactKeystone5015),
                (LinearRegulator, Tlv757p),  # default type for all LDOs
            ],
            class_values=[
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),  # RH-5015, which is actually in stock
            ],
        )


class IotThermalCameraTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(IotThermalCamera)
