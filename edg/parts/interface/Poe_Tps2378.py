from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


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
    def contents(self) -> None:
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
                "8": self.rtn,  # APD, connect to RTN if unused
                "9": self.vss,
                # ("4", "5", "6", "7", "8"): NC
            },
            mfr="Texas Instruments",
            part="TPS2378",
            datasheet="https://www.ti.com/lit/ds/symlink/tps2378.pdf",
            pnp_rot=-90,
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
                    voltage=(POE_VOUT_MIN, POE_VOUT_MAX) * Volt, current_limits=(0, output_power_max / POE_VOUT_MAX)
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
