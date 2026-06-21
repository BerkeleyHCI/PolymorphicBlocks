import unittest

from typing_extensions import override

from edg import *
from .util import run_test_board

# these libraries live in this example until it gets fabbed out and tested


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
    """Power over Ethernet connection between the powered device and the post-rectification jack-facing circuit."""

    def __init__(self) -> None:
        super().__init__()
        self.jack = self.Port(PoePowerPort.empty())
        self.poe = self.Port(PoeDevicePort.empty())

    @override
    def contents(self) -> None:
        self.connect(self.jack.pos, self.poe.pos)
        self.connect(self.jack.neg, self.poe.neg)


class PoePowerPort(Port[PoeLink]):
    """Jack side port for Power over Ethernet, post-rectification."""

    link_type = PoeLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())


class PoeDevicePort(Port[PoeLink]):
    """Powered device side port for Power over Ethernet. Generally exposed by a PoE controller subcircuit"""

    link_type = PoeLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())


class PoeJumper(TypedJumper, Block):
    def __init__(self) -> None:
        super().__init__()
        self.jack = self.Port(PoeDevicePort(), [Input])  # jack-facing, device-presenting port
        self.device = self.Port(PoePowerPort(), [Output])  # device-facing, power-presenting port

    @override
    def contents(self) -> None:
        super().contents()
        self.pos = self.Block(Jumper())
        self.connect(self.jack.pos, self.pos.a)
        self.connect(self.device.pos, self.pos.b)
        self.neg = self.Block(Jumper())
        self.connect(self.jack.neg, self.neg.a)
        self.connect(self.device.neg, self.neg.b)


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


class Tps2378_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()

        self.vss = self.Port(Ground())
        self.vdd = self.Port(
            VoltageSink.from_gnd(self.vss, voltage_limits=(0, 57) * Volt, current_draw=(285, 500) * uAmp)
        )
        self.den = self.Port(Passive())  # AnalogSink
        self.cls = self.Port(AnalogSource())

        self.rtn = self.Port(Ground())
        self.cdb = self.Port(DigitalSource.low_from_supply(self.rtn), optional=True)  # -0.3 - 100v standoff limit
        self.t2p = self.Port(DigitalSource.low_from_supply(self.rtn), optional=True)

    @override
    def contents(self):
        super().contents()

        self.footprint(
            "U",
            "Package_SO:HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm_ThermalVias",
            {
                "1": self.vdd,
                "2": self.den,
                "3": self.cls,
                "4": self.vss,
                "5": self.rtn,
                "6": self.cdb,
                "7": self.t2p,
                # "8": self.apd,
                "9": self.vss,
                # ("4", "5", "6", "7", "8"): NC
            },
            mfr="Texas Instruments",
            part="TPS2378",
            datasheet="https://www.ti.com/lit/ds/symlink/tps2378.pdf",
        )
        self.assign(self.lcsc_part, "C337500")
        self.assign(self.actual_basic_part, False)


class Tps2378(Interface, GeneratorBlock):
    def __init__(self, poe_class: IntLike = 0) -> None:
        super().__init__()
        self.poe_class = self.ArgParameter(poe_class)
        self.generator_param(self.poe_class)

        self.ic = self.Block(Tps2378_Device())
        self.gnd = self.Export(self.ic.rtn, [Common])
        self.pwr_out = self.Port(VoltageSource.empty(), [Output])

        self.poe = self.Port(PoeDevicePort(), [Input], doc="PoE input")

        self.cdb = self.Export(
            self.ic.cdb,
            doc="active-low output when the in inrush limiting, intended to disable a downstream converter",
            optional=True,
        )
        self.t2p = self.Export(self.ic.t2p, doc="active-low output indicating type-2 PSE", optional=True)

    @override
    def generate(self) -> None:
        super().generate()

        POE_VOUT_MIN = 37
        POE_VOUT_MAX = 57

        poe_class = self.get(self.poe_class)
        if poe_class == 0:
            cls_res = 270 * Ohm(tol=0.05)
            output_power_max = 12.95
        elif poe_class == 1:
            cls_res = 243 * Ohm(tol=0.05)
            output_power_max = 3.84
        elif poe_class == 2:
            cls_res = 137 * Ohm(tol=0.05)
            output_power_max = 6.49
        elif poe_class == 3:
            cls_res = 90.9 * Ohm(tol=0.05)
            output_power_max = 12.95
        elif poe_class == 4:
            cls_res = 63.4 * Ohm(tol=0.05)
            output_power_max = 25.5
            self.require(self.t2p.is_connected(), "class 4 devices must use T2P to draw >13W")
        else:
            raise ValueError(f"unsupported PoE class {poe_class}")

        self.cls = self.Block(AnalogSetpointResistor(cls_res)).connected(self.ic.vss, self.ic.cls)

        self.den = self.Block(Resistor(24.9 * kOhm(tol=0.01)))
        self.connect(self.den.a, self.poe.pos)
        self.connect(self.den.b, self.ic.den)

        self.connect(
            self.poe.pos.adapt_to(
                VoltageSource(
                    voltage_out=(POE_VOUT_MIN, POE_VOUT_MAX) * Volt, current_limits=(0, output_power_max / POE_VOUT_MAX)
                )
            ),
            self.ic.vdd,
            self.pwr_out,
        )
        self.connect(self.poe.neg.adapt_to(Ground()), self.ic.vss)

        with self.implicit_connect(
            ImplicitConnect(self.ic.vss, [Common]),
            ImplicitConnect(self.ic.vdd, [Power]),
        ) as imp:
            self.vdd_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.1)))
            self.prot = imp.Block(ProtectionZenerDiode((57, 66) * Volt))  # based on SMAJ58A as recommended in datasheet


class IotThermalCamera(JlcBoardTop):
    """Dual-mode IR and RGB camera board with ESP32 and ethernet PoE"""

    @override
    def contents(self) -> None:
        super().contents()

        # IMPORTANT! use only USB OR PoE, both cannot be used simultaneously since this is a non-isolated converter
        self.usb = self.Block(UsbCReceptacle())

        self.eth = self.Block(Hy931147c())
        self.poe = self.Block(Tps2378(poe_class=0))
        # allow using a jumper to disable and isolate PoE while still using ethernet
        (self.poe_jmp,), _ = self.chain(self.eth.poe, self.Block(PoeJumper()), self.poe.poe)

        self.gnd = self.connect(self.usb.gnd, self.poe.gnd)
        self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)
        self.tp_poe = self.Block(VoltageTestPoint()).connected(self.poe.pwr_out)

        with self.implicit_connect(  # POWER
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.reg_poe, self.tp_v5, self.prot_v5), _ = self.chain(
                self.poe.pwr_out,
                imp.Block(BuckConverter(output_voltage=5.0 * Volt(tol=0.05))),
                self.Block(VoltageTestPoint()),
                imp.Block(ProtectionZenerDiode(voltage=(5.5, 7) * Volt)),
            )

            self.v5_merge = self.Block(MergedVoltageSource()).connected_from(self.reg_poe.pwr_out, self.usb.pwr)

            (self.choke, self.tp_pwr), _ = self.chain(
                self.v5_merge.pwr_out, self.Block(SeriesPowerFerriteBead()), self.Block(VoltageTestPoint())
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
            self.connect(self.ioe.gpio.request("t2p"), self.poe.t2p)

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
                (["reg_poe"], Lmr39020),
                (["reg_3v3"], Tps54202h),
                (["cam", "device", "conn"], Fpc050BottomFlip),
            ],
            class_refinements=[
                (EspProgrammingHeader, EspProgrammingTc2030),
                (Ch32vSdiHeader, Ch32vSdiTc2030),
                (TagConnect, TagConnectNonLegged),
                (TestPoint, CompactKeystone5015),
                (LinearRegulator, Tlv757p),  # default type for all LDOs
            ],
            instance_values=[
                (["refdes_prefix"], "T"),  # unique refdes for panelization
                (
                    ["mcu", "pin_assigns"],
                    [
                        "reset=25",
                        "cam.vsync=24",
                        "cam.href=23",
                        "cam.y7=22",
                        "cam.xclk=21",
                        "cam.y6=20",
                        "cam.y5=15",
                        "cam.pclk=19",
                        "cam.y0=18",
                        "cam.y1=17",
                        "cam.y4=10",
                        "cam.y3=11",
                        "cam.y2=12",
                        "i2c.sda=32",
                        "i2c.scl=33",
                        "flir_pwrdn=34",
                        "flir_cs=38",
                        "flir.sck=39",
                        "flir.mosi=5",
                        "flir.miso=4",
                        "flir_vsync=6",
                        "ledr=_GPIO0_STRAP",
                    ],
                ),
                (["mcu", "programming"], "uart-auto"),
                (["reg_2v8", "ic", "actual_dropout"], Range(0.0, 0.05)),  # 3.3V @ 100mA
                (["reg_3v0", "ic", "actual_dropout"], Range(0.0, 0.16)),  # 3.3V @ 400mA
                # over USB2 power limits, don't run wifi and ethernet together
                (["usb", "pwr", "current_limits"], Range(0.0, 0.9)),
                (["poe", "vdd_cap", "cap", "voltage_margin"], 1.5),  # reduce excessive overhead to allow basic part
                (["reg_poe", "frequency"], Range.from_tolerance(800e3, 0.1)),
                (["reg_poe", "hf_cap", "cap", "voltage_margin"], 1.5),
                (["eth", "cap", "voltage_margin"], 1.0),  # 1kV rated only
                (["reg_poe", "power_path", "in_cap", "cap", "voltage_margin"], 1.5),
                (["poe", "prot", "diode", "footprint_spec"], "Diode_SMD:D_SMA"),
                (["poe", "den", "resistance"], Range.from_tolerance(25000, 0.05)),  # find a basic part
                (["phy", "exres1", "res", "require_basic_part"], False),
            ],
            class_values=[
                (CompactKeystone5015, ["lcsc_part"], "C5199798"),
                (JlcInductor, ["manual_frequency_rating"], Range(0, 9e6)),
            ],
        )


class IotThermalCameraTestCase(unittest.TestCase):
    def test_design(self) -> None:
        run_test_board(IotThermalCamera)
