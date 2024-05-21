from ..abstract_parts import *
from .JlcPart import JlcPart


class Al8861_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    @init_in_parent
    def __init__(self, peak_output_current: FloatLike):
        super().__init__()

        self.vin = self.Port(VoltageSink(
            voltage_limits=(4.5, 40)*Volt,
            current_draw=(0.055, 0.55)*mAmp,  # shutdown typ to quiescent typ
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
        self.require(self.peak_output_current < 2*Amp)
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
                # '9': EP, connectivity not specified
            },
            mfr='Diodes Incorporated', part='AL8861MP',
            datasheet='https://www.diodes.com/assets/Datasheets/AL8861.pdf'
        )
        self.assign(self.lcsc_part, 'C155534')
        self.assign(self.actual_basic_part, False)


class Al8861(LedDriverPwm, LedDriverSwitchingConverter, LedDriver, GeneratorBlock):
    """AL8861 buck LED driver."""
    @init_in_parent
    def __init__(self, diode_voltage_drop: RangeLike = Range.all()):
        super().__init__()

        self.ic = self.Block(Al8861_Device(FloatExpr()))
        self.connect(self.pwr, self.ic.vin)
        self.connect(self.gnd, self.ic.gnd)

        self.generator_param(self.max_current)
        self.diode_voltage_drop = self.ArgParameter(diode_voltage_drop)

        self.generator_param(self.pwm.is_connected())

        self.actual_ripple = self.Parameter(RangeExpr())

    def generate(self):
        super().contents()

        self.require(self.max_current.within((0, 1.5)*Amp))  # for MSOP and SOT89 packages

        max_current = self.get(self.max_current)
        isense_ref = Range(0.096, 0.104)
        self.rsense = self.Block(CurrentSenseResistor(resistance=Range.cancel_multiply(isense_ref,
                                                                                       1/max_current),
                                                      sense_in_reqd=False))
        self.connect(self.rsense.pwr_in, self.pwr)
        self.connect(self.rsense.sense_out, self.ic.isense)
        self.connect(self.rsense.pwr_out, self.leda.adapt_to(VoltageSink(current_draw=self.max_current)))

        self.pwr_cap = self.Block(DecouplingCapacitor((4.7*0.8, 10*1.2)*uFarad))\
            .connected(self.gnd, self.pwr)  # "commonly used values""

        peak_current = isense_ref / self.rsense.actual_resistance + (0, self.ripple_limit / 2)
        self.assign(self.ic.peak_output_current, peak_current.upper())

        # minimum switch on time = 500ns, recommended maximum switch off time = 250kHz @ 75% = 30us
        min_inductance = self.pwr.link().voltage.upper() * (1.5*uSecond) / self.ripple_limit

        self.ind = self.Block(Inductor(
            inductance=(min_inductance, float('inf')),
            current=peak_current,
            frequency=(0.25, 1)*MHertz
        ))
        # recommended inductance between 33 and 100uH, accounting for ~20% tolerance
        self.require(self.ind.actual_inductance.within((33*0.8, 100*1.2)*uHenry))
        self.assign(self.actual_ripple, self.pwr.link().voltage * (1.5*uSecond) / self.ind.actual_inductance)

        self.diode = self.Block(Diode(
            reverse_voltage=self.pwr.link().voltage,
            current=peak_current,
            voltage_drop=self.diode_voltage_drop,
            reverse_recovery_time=(0, 500)*nSecond,  # arbitrary for 'fast'
        ))
        self.connect(self.ind.a, self.ledk)
        self.connect(self.ind.b, self.ic.lx, self.diode.anode)
        self.connect(self.diode.cathode.adapt_to(VoltageSink()), self.pwr)

        if self.get(self.pwm.is_connected()):
            self.connect(self.pwm, self.ic.vset_pwm)
