import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board


class EthernetMdiPairLink(Link):
    """Single pair ethernet twisted-pair MDI connection, between the PHY and magnetics."""

    def __init__(self) -> None:
        super().__init__()
        self.phy = self.Port(EthernetMdiPhyPairPort.empty())
        self.mag = self.Port(EthernetMdiMagPairPort.empty())

    @override
    def contents(self) -> None:
        # KiCad diffpair-friendly naming
        self.dp_P = self.connect(self.phy.pos, self.mag.pos)
        self.dp_N = self.connect(self.phy.neg, self.mag.neg)
        self.center = self.connect(self.phy.center, self.mag.center)


class EthernetMdiPhyPairPort(Port[EthernetMdiPairLink]):
    """PHY-side port of an ethernet twisted-pair MDI connection"""

    link_type = EthernetMdiPairLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())
        self.center = self.Port(Passive())


class EthernetMdiMagPairPort(Port[EthernetMdiPairLink]):
    """Magnetics-side port of a twisted-pair MDI connection"""

    link_type = EthernetMdiPairLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())
        self.center = self.Port(Passive())


class EthernetMdiLink(Link):
    """Full (multi-pair) connection for ethernet twisted-pair MDI connection, between the PHY and magnetics.
    Currently supports only 10/100Mbps (100BASE-TX) connections with TX/RX pairs."""

    def __init__(self) -> None:
        super().__init__()
        self.phy = self.Port(EthernetMdi100BaseTxPhyPort.empty())
        self.mag = self.Port(EthernetMdi100BaseTxMagPort.empty())

    @override
    def contents(self) -> None:
        self.tx = self.connect(self.phy.tx, self.mag.tx)
        self.rx = self.connect(self.phy.rx, self.mag.rx)


class EthernetMdi100BaseTxPhyPort(Port[EthernetMdiLink]):
    """PHY-side MDI port for 100BASE-TX / Fast Ethernet"""

    link_type = EthernetMdiLink

    def __init__(self) -> None:
        super().__init__()
        self.tx = self.Port(EthernetMdiPhyPairPort())
        self.rx = self.Port(EthernetMdiPhyPairPort())


class EthernetMdi100BaseTxMagPort(Port[EthernetMdiLink]):
    """Magnetics-side MDI port for 100BASE-TX / Fast Ethernet"""

    link_type = EthernetMdiLink

    def __init__(self) -> None:
        super().__init__()
        self.tx = self.Port(EthernetMdiMagPairPort())
        self.rx = self.Port(EthernetMdiMagPairPort())


class PoeLink(Link):
    """Power over Ethernet connection between the powered device and the magnetics."""

    def __init__(self) -> None:
        super().__init__()
        self.poe = self.Port(PoeDevicePort.empty())
        self.magnetics = self.Port(PoePowerPort.empty())

    @override
    def contents(self) -> None:
        self.connect(self.poe.pos, self.magnetics.pos)
        self.connect(self.poe.neg, self.magnetics.neg)


class PoeDevicePort(Port[PoeLink]):
    """Powered device side port for Power over Ethernet. Generally exposed by a PoE controller subcircuit"""

    link_type = PoeLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())


class PoePowerPort(Port[PoeLink]):
    """Jack side port for Power over Ethernet, post-rectification."""

    link_type = PoeLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())


class Hy931147c_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()

        self.eth = self.Port(EthernetMdi100BaseTxMagPort.empty(), optional=True)
        self.poe = self.Port(PoePowerPort.empty(), optional=True)

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
                "1": self.eth.rx.pos,
                "2": self.eth.rx.neg,
                "3": self.eth.rx.center,
                "6": self.eth.tx.neg,
                "5": self.eth.tx.pos,
                "4": self.eth.tx.center,
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

        self.eth = self.Export(self.conn.eth, optional=True)
        self.poe = self.Export(self.conn.poe, optional=True)

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

        self.require(self.eth.is_connected() | self.poe.is_connected(), "must use ethernet or PoE")

        self.require(
            (self.led_yel_sink.is_connected() | self.led_grn_sink.is_connected()).implies(self.pwr_led.is_connected()),
            "power required when LEDs used",
        )
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
            self.connect(self.led_yel_res.b, self.led_yel_sink.net)
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
            self.connect(self.led_grn_res.b, self.led_grn_sink.net)
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
                current_draw=(13, 132) * mAmp,  # power down to 100M link, arbitrarily lumped into avdd
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
                "30": self.crystal.xtal_in,
                "31": self.crystal.xtal_out,
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
    """SPI Ethernet controller supporting 10/100Mbps ethernet and onboard TCP/IP stack."""

    def __init__(self, *, damping_resistance: RangeLike = 33 * Ohm(tol=0.05)) -> None:
        super().__init__()
        self.damping_resistance = self.ArgParameter(damping_resistance)

        self.ic = self.Block(W5500_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])

        self.eth = self.Port(EthernetMdi100BaseTxPhyPort.empty())
        self.spi = self.Export(self.ic.spi)
        self.cs = self.Export(self.ic.scsn)
        self.int = self.Export(self.ic.intn, optional=True)

    def contents(self) -> None:
        super().contents()

        self.connect(self.reset, self.ic.rstn)
        self.connect(self.gnd, self.ic.agnd)
        self.l = self.Block(SeriesPowerFerriteBead(hf_impedance=(100, 2000) * Ohm)).connected(self.pwr, self.ic.avdd)

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

        # TODO parameterize PMODE configuration
        self.connect(self.ic.pmode0, self.ic.pmode1, self.ic.pmode2, self.pwr.as_digital_source())

        # optional damping resistors for EMI reduction
        damp_resistor_model = Resistor(self.damping_resistance)
        self.txp_damp = self.Block(damp_resistor_model)
        self.txn_damp = self.Block(damp_resistor_model)
        self.connect(self.txp_damp.a, self.ic.txp)
        self.connect(self.txn_damp.a, self.ic.txn)
        self.rxp_damp = self.Block(damp_resistor_model)
        self.rxn_damp = self.Block(damp_resistor_model)
        self.connect(self.rxp_damp.a, self.ic.rxp)
        self.connect(self.rxn_damp.a, self.ic.rxn)

        # Ethernet termination circuit
        bias_resistor_model = Resistor(49.9 * Ohm(tol=0.01))
        self.txp_bias = self.Block(bias_resistor_model)
        self.txn_bias = self.Block(bias_resistor_model)
        self.txc_bias = self.Block(Resistor(10 * Ohm(tol=0.01)))
        self.connect(self.txp_bias.a, self.txn_bias.a, self.txc_bias.a)
        self.connect(self.txc_bias.a.adapt_to(VoltageSink()), self.ic.avdd)
        self.connect(self.txp_damp.b, self.txp_bias.b, self.eth.tx.pos)
        self.connect(self.txn_damp.b, self.txn_bias.b, self.eth.tx.neg)
        self.txc_cap = self.Block(Capacitor(22 * nFarad(tol=0.2), voltage=(0, 5) * Volt))
        self.connect(self.txc_bias.b, self.txc_cap.pos, self.eth.tx.center)
        self.connect(self.txc_cap.neg.adapt_to(Ground()), self.gnd)

        ac_cap_model = Capacitor(6.8 * nFarad(tol=0.2), voltage=(0, 5) * Volt)
        self.rxp_ac = self.Block(ac_cap_model)
        self.rxn_ac = self.Block(ac_cap_model)
        self.connect(self.rxp_ac.pos, self.eth.rx.pos)
        self.connect(self.rxn_ac.pos, self.eth.rx.neg)
        self.rxp_bias = self.Block(bias_resistor_model)
        self.rxn_bias = self.Block(bias_resistor_model)
        self.connect(self.rxp_damp.b, self.rxp_bias.a, self.rxp_ac.neg)
        self.connect(self.rxn_damp.b, self.rxn_bias.a, self.rxn_ac.neg)
        self.rxc_cap = self.Block(Capacitor(10 * nFarad(tol=0.2), voltage=(0, 5) * Volt))
        self.connect(self.rxc_cap.pos, self.eth.rx.center, self.rxp_bias.b, self.rxn_bias.b)
        self.connect(self.rxc_cap.neg.adapt_to(Ground()), self.gnd)


class IotThermalCamera(JlcBoardTop):
    """Dual-mode IR and RGB camera board with ESP32 and ethernet PoE"""

    @override
    def contents(self) -> None:
        super().contents()

        self.usb = self.Block(UsbCReceptacle())
        self.gnd = self.connect(self.usb.gnd)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)

        self.eth = self.Block(Hy931147c())

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

            # debugging LEDs
            (self.ledr,), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request("ledr"))

            reset_line = self.mcu.gpio.request("reset")

            self.connect(self.eth.gnd, self.gnd)
            self.connect(self.eth.pwr_led, self.v3v3)
            self.phy = imp.Block(W5500())
            self.connect(self.eth.eth, self.phy.eth)
            self.connect(self.mcu.spi.request("eth_spi"), self.phy.spi)
            self.connect(self.mcu.gpio.request("eth_cs"), self.phy.cs)
            self.connect(reset_line, self.phy.reset)
            self.connect(self.mcu.gpio.request("eth_int"), self.phy.int)

            (self.usb_esd,), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

            self.i2c = self.mcu.i2c.request("i2c")
            (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
                self.i2c, imp.Block(I2cPullup()), imp.Block(I2cTestPoint("i2c"))
            )

            # out of IOs on the main ESP32S3
            self.ioe = imp.Block(IoController())
            self.connect(self.ioe.with_mixin(IoControllerI2cTarget()).i2c_target.request("i2c"), self.i2c)
            self.connect(self.ioe.gpio.request("eth_grn"), self.eth.led_grn_sink)
            self.connect(self.ioe.gpio.request("eth_yel"), self.eth.led_yel_sink)

            (self.poe_sense,), _ = self.chain(
                self.pwr,
                imp.Block(VoltageSenseDivider(full_scale_voltage=3.0 * Volt(tol=0.1), impedance=(1, 10) * kOhm)),
                self.ioe.adc.request("vusb_sense"),
            )

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
            self.connect(self.cam.reset, reset_line)

            self.flir = imp.Block(FlirLepton())
            self.connect(self.flir.pwr_io, self.v3v0)
            self.connect(self.flir.pwr, self.v2v8)
            self.connect(self.flir.pwr_core, self.v1v2)
            self.connect(self.flir.spi, self.mcu.spi.request("flir"))
            self.connect(self.flir.cci, self.i2c)
            self.connect(self.flir.reset, reset_line)
            self.connect(self.flir.shutdown, self.mcu.gpio.request("flir_pwrdn"))
            self.connect(self.flir.cs, self.mcu.gpio.request("flir_cs"))
            self.connect(self.flir.vsync, self.mcu.gpio.request("flir_vsync"))

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Esp32s3_Wroom_1),
                (["ioe"], Ch32v003),
                (["reg_3v3"], Tps54202h),
                (["cam", "device", "conn"], Fpc050BottomFlip),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (Ch32vSdiHeader, Ch32vSdiTc2030),
                (TestPoint, CompactKeystone5015),
                (LinearRegulator, Tlv757p),  # default type for all LDOs
            ],
            instance_values=[
                (["refdes_prefix"], "T"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        "cam.vsync=25",
                        "cam.href=24",
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
                        "flir_cs=38",
                        "flir.sck=39",
                        "flir.mosi=5",
                        "flir.miso=4",
                        "flir_vsync=7",
                        "ledr=_GPIO0_STRAP",
                    ],
                ),
                (["mcu", "programming"], "uart-auto"),
                (["reg_2v8", "ic", "actual_dropout"], Range(0.0, 0.05)),  # 3.3V @ 100mA
                (["reg_3v0", "ic", "actual_dropout"], Range(0.0, 0.16)),  # 3.3V @ 400mA
                (["reg_3v3", "power_path", "inductor", "manual_frequency_rating"], Range(0, 21e6)),
                (["usb", "pwr", "current_limits"], Range(0.0, 0.8)),  # a bit over
            ],
            class_values=[
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),
            ],
        )


class IotThermalCameraTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(IotThermalCamera)
