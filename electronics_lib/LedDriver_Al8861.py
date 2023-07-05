from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Al8861_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    @init_in_parent
    def __init__(self, peak_output_current: FloatLike):
        super().__init__()

        self.vin = self.Port(VoltageSink(
            voltage_limits=(4.5, 40)*Volt,
            current_draw=(0.055*mAmp, 0.55*mAmp + peak_output_current),  # shutdown typ to quiescent typ
        ), [Power])
        self.gnd = self.Port(Ground(), [Common])

        self.lx = self.Port(Passive())
        self.isense = self.Port(AnalogSink())
        self.vset_pwm = self.Port(DigitalSink(
            voltage_limits=(0, 5)*Volt,
            input_thresholds=(0.2, 0.25)*Volt
        ), optional=True)

        self.peak_output_current = self.ArgParameter(peak_output_current)

    def contents(self):
        self.require(self.peak_output_current < 1.5*Amp)  # for MSOP and SOT89 packages
        self.footprint(
            'U', 'Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.68x1.88mm_ThermalVias',
            {
                '1': self.isense,
                '2': self.gnd,
                '3': self.gnd,
                '4': self.vset_pwm,
                '5': self.lx,
                '6': self.lx,
                # '7': NC
                '8': self.vin,
                '9': self.isense,  # EP
            },
            mfr='Diodes Incorporated', part='AL8861MP',
            datasheet='https://www.diodes.com/assets/Datasheets/AL8861.pdf'
        )
        self.assign(self.lcsc_part, 'C155534')
        self.assign(self.actual_basic_part, False)


class Al8861(PowerConditioner, Interface, GeneratorBlock):
    """AL8861 buck LED driver."""
    @init_in_parent
    def __init__(self, max_current: RangeLike, ripple_limit: RangeLike):
        super().__init__()

        self.ic = self.Block(Al8861_Device(FloatExpr()))
        self.pwr = self.Export(self.ic.vin, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

        self.pwm = self.Export(self.ic.vset_pwm, optional=True)
        self.leda = self.Port(Passive())
        self.ledk = self.Port(Passive())

        self.max_current = self.ArgParameter(max_current)
        self.generator_param(self.max_current)
        self.ripple_limit = self.ArgParameter(ripple_limit)

    def generate(self):
        super().contents()

        max_current = self.get(self.max_current)
        isense_ref = Range(0.96, 0.104)
        self.rsense = self.Block(CurrentSenseResistor(resistance=Range.cancel_multiply(isense_ref,
                                                                                       1/max_current)))
        self.connect(self.rsense.pwr_in, self.pwr)
        self.connect(self.rsense.sense_out, self.ic.isense)
        self.connect(self.rsense.pwr_out, self.leda.adapt_to(VoltageSink(current_draw=self.max_current)))

        self.pwr_cap = self.Block(DecouplingCapacitor(...,
                                                      exact_capacitance=True))\
            .connected(self.gnd, self.pwr)

        peak_current = Range(0.96, 0.104) / self.rsense.actual_resistance + self.ripple_limit
        self.assign(self.ic.peak_output_current, peak_current.upper())
        self.ind = self.Block(Inductor(
            inductance=...,
            current=peak_current,
            frequency=(0.25, 1)*MHertz
        ))
        self.diode = self.Block(Diode(
            reverse_voltage=self.pwr.link().voltage,
            current=peak_current,
            reverse_recovery_time=(0, 500)*nSecond,  # arbitrary for 'fast'
        ))
        self.connect(self.ind.a, self.ledk)
        self.connect(self.ind.b, self.ic.lx, self.diode.anode)
        self.connect(self.diode.cathode.adapt_to(VoltageSink()), self.pwr)
