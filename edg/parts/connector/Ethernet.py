from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


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
    def contents(self) -> None:
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
            pnp_rot=90,
            pnp_offset=(5.6, 6.4),
        )
        self.assign(self.lcsc_part, "C91754")
        self.assign(self.actual_basic_part, False)


class Hy931147c(Connector, GeneratorBlock):
    """Commonly available RJ45 magjack with PoE support.
    Footprint and pin-compatible with Wuerth 7499211121A.

    This uses the footprint for the Wuerth 7499111446, which shares the same pattern
    but is not functionally compatible.

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
