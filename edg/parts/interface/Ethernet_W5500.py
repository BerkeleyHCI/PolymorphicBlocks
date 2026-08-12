from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


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

        self.v1v20 = self.Port(VoltageSource(voltage=1.2 * Volt(tol=0), current_limits=0 * Amp(tol=0)))
        self.tocap = self.Port(VoltageSource(voltage=self.avdd.link().voltage))  # assumed, not documented
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
    def contents(self) -> None:
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

    @override
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
