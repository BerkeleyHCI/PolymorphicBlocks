from ..abstract_parts import *
from .JlcPart import JlcPart


class Lm2664_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    FREQUENCY = Range(40000, 80000)  # Hz
    SWITCH_RESISTANCE = Range(4, 8)  # Ohm
    @init_in_parent
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.vp = self.Port(VoltageSink(
            voltage_limits=(1.8, 5.5)*Volt,
            current_draw=RangeExpr()
        ), [Power])

        self.capn = self.Port(Passive())
        self.capp = self.Port(Passive())
        self.out = self.Port(VoltageSource(
            voltage_out=-self.vp.link().voltage,
            current_limits=(0, 40)*mAmp
        ))
        self.assign(self.vp.current_draw, (1, 500)*uAmp + self.out.link().current_drawn)

        # self.sd = self.Port(DigitalSink.from_supply(
        #     self.gnd, self.vp,
        #     voltage_limit_tolerance=(-0.3, 0.3)*Volt,
        #     input_threshold_abs=(0.8, 2)*Volt
        # ), optional=True)

    def contents(self):
        super().contents()
        self.footprint(
            'U', 'Package_TO_SOT_SMD:SOT-23-6',
            {
                '1': self.gnd,
                '2': self.out,
                '3': self.capn,
                '4': self.vp,  # self.sd,
                '5': self.vp,
                '6': self.capp,
            },
            mfr='Texas Instruments', part='LM2664',
            datasheet='https://www.ti.com/lit/ds/symlink/lm2664.pdf'
        )
        self.assign(self.lcsc_part, 'C840095')
        self.assign(self.actual_basic_part, False)


class Lm2664(PowerConditioner, Block):
    """Switched capacitor inverter"""
    @init_in_parent
    def __init__(self, output_resistance_limit: FloatLike = 25 * Ohm,
                 output_ripple_limit: FloatLike = 25 * mVolt):
        super().__init__()
        self.ic = self.Block(Lm2664_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr_in = self.Export(self.ic.vp, [Power, Input])
        self.pwr_out = self.Export(self.ic.out, [Output])
        self.output_resistance_limit = self.ArgParameter(output_resistance_limit)
        self.output_ripple_limit = self.ArgParameter(output_ripple_limit)

    def contents(self):
        super().contents()
        self.require(self.output_resistance_limit >= 2 * self.ic.SWITCH_RESISTANCE.upper,
                     "min output resistance spec below switch resistance")
        self.cf = self.Block(Capacitor(
            capacitance=(2 / self.ic.FREQUENCY.lower /
                         (self.output_resistance_limit - 2 * self.ic.SWITCH_RESISTANCE.upper),
                         float('inf')),
            voltage=self.pwr_out.voltage_out
        ))
        self.connect(self.cf.neg, self.ic.capn)
        self.connect(self.cf.pos, self.ic.capp)

        self.cout = self.Block(DecouplingCapacitor(
            (self.pwr_out.link().current_drawn.upper() / self.ic.FREQUENCY.lower / self.output_ripple_limit,
             float('inf'))
        )).connected(self.gnd, self.pwr_out)
