from ..abstract_parts import *
from .JlcPart import JlcPart


class Tps92200_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    @init_in_parent
    def __init__(self, peak_output_current: FloatLike):
        super().__init__()

        self.gnd = self.Port(Ground(), [Common])
        self.vin = self.Port(VoltageSink(
            voltage_limits=(4, 30)*Volt,  # note, UVLO at 3.5-3.9v
            current_draw=(0.055, 0.55)*mAmp,  # shutdown typ to quiescent typ
        ), [Power])

        self.dim = self.Port(DigitalSink.from_supply(
            self.gnd, self.vin,
            voltage_limit_abs=(-0.1, 6)*Volt,
            input_threshold_abs=(0.3, 0.65)*Volt
        ))
        self.fb = self.Port(AnalogSink.from_supply(
            self.gnd, self.vin,
            voltage_limit_abs=(-0.1, 6)*Volt
        ))

        self.sw = self.Port(Passive())
        self.boot = self.Port(Passive())

        # self.vset_pwm = self.Port(DigitalSink(
        #     voltage_limits=(0, 5)*Volt,
        #     input_thresholds=(0.2, 0.25)*Volt
        # ), optional=True)
        #
        # self.peak_output_current = self.ArgParameter(peak_output_current)

    def contents(self):
        # self.require(self.peak_output_current < 2*Amp)
        self.footprint(
            'U', 'Package_TO_SOT_SMD:SOT-23-6',
            {
                '6': self.boot,
                '1': self.fb,
                '3': self.gnd,
                '2': self.dim,
                '5': self.sw,
                '4': self.vin,
            },
            mfr='Texas Instruments', part='TPS92200D2DDCR',
            datasheet='https://www.ti.com/lit/ds/symlink/tps92200.pdf'
        )
        self.assign(self.lcsc_part, 'C2865497')
        self.assign(self.actual_basic_part, False)


class Tps92200(LedDriverPwm, LedDriverSwitchingConverter, LedDriver, GeneratorBlock):
    """TPS92200 buck 4-30V 1.5A 1 MHz LED driver and 150nS min on-time.
    This is the -D2 variant, with PWM input for 1-100% range as a 20-200kHz digital signal"""
    @init_in_parent
    def __init__(self, diode_voltage_drop: RangeLike = Range.all()):
        super().__init__()

        self.ic = self.Block(Tps92200_Device(FloatExpr()))
        # self.connect(self.pwr, self.ic.vin)
        # self.connect(self.gnd, self.ic.gnd)
        #
        # self.generator_param(self.max_current)
        # self.diode_voltage_drop = self.ArgParameter(diode_voltage_drop)
        #
        # self.generator_param(self.pwm.is_connected())
        #
        # self.actual_ripple = self.Parameter(RangeExpr())

    def generate(self):
        super().contents()

        # self.require(self.max_current.within((0, 1.5)*Amp))  # for MSOP and SOT89 packages
        #
        # isense_ref = Range(0.096, 0.104)
        # self.rsense = self.Block(CurrentSenseResistor(resistance=(1/self.max_current).shrink_multiply(isense_ref),
        #                                               sense_in_reqd=False))
        # self.connect(self.rsense.pwr_in, self.pwr)
        # self.connect(self.rsense.sense_out, self.ic.isense)
        # self.connect(self.rsense.pwr_out, self.leda.adapt_to(VoltageSink(current_draw=self.max_current)))
        #
        # self.pwr_cap = self.Block(DecouplingCapacitor((4.7*0.8, 10*1.2)*uFarad))\
        #     .connected(self.gnd, self.pwr)  # "commonly used values""
        #
        # peak_current = isense_ref / self.rsense.actual_resistance + (0, self.ripple_limit / 2)
        # self.assign(self.ic.peak_output_current, peak_current.upper())
        #
        # # minimum switch on time = 500ns, recommended maximum switch off time = 250kHz @ 75% = 30us
        # min_inductance = self.pwr.link().voltage.upper() * (1.5*uSecond) / self.ripple_limit
        #
        # self.ind = self.Block(Inductor(
        #     inductance=(min_inductance, float('inf')),
        #     current=peak_current,
        #     frequency=(0.25, 1)*MHertz
        # ))
        # # recommended inductance between 33 and 100uH, accounting for ~20% tolerance
        # self.require(self.ind.actual_inductance.within((33*0.8, 100*1.2)*uHenry))
        # self.assign(self.actual_ripple, self.pwr.link().voltage * (1.5*uSecond) / self.ind.actual_inductance)
        #
        # self.diode = self.Block(Diode(
        #     reverse_voltage=self.pwr.link().voltage,
        #     current=peak_current,
        #     voltage_drop=self.diode_voltage_drop,
        #     reverse_recovery_time=(0, 500)*nSecond,  # arbitrary for 'fast'
        # ))
        # self.connect(self.ind.a, self.ledk)
        # self.connect(self.ind.b, self.ic.lx, self.diode.anode)
        # self.connect(self.diode.cathode.adapt_to(VoltageSink()), self.pwr)
        #
        # if self.get(self.pwm.is_connected()):
        #     self.connect(self.pwm, self.ic.vset_pwm)
