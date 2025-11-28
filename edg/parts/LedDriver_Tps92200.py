from typing_extensions import override

from ..abstract_parts import *
from .JlcPart import JlcPart


class Tps92200_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self, peak_output_current: FloatLike):
        super().__init__()

        self.gnd = self.Port(Ground(), [Common])
        self.vin = self.Port(VoltageSink(
            voltage_limits=(4, 30)*Volt,  # note, UVLO at 3.5-3.9v
            current_draw=(0.001, 1)*mAmp,  # shutdown typ (Vdim=0) to operating max
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

        self.sw = self.Port(VoltageSource())
        self.boot = self.Port(Passive())

    @override
    def contents(self) -> None:
        super().contents()
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


class Tps92200(LedDriverPwm, LedDriver, GeneratorBlock):
    """TPS92200 buck 4-30V 1.5A 1 MHz LED driver and 150nS min on-time.
    This is the -D2 variant, with PWM input for 1-100% range as a 20-200kHz digital signal"""
    def __init__(self, led_voltage: RangeLike = (1, 4)*Volt, *,
                 input_ripple_limit: FloatLike = 0.2*Volt,  # from 8.2 example application
                 output_ripple_limit: FloatLike = 0.01*Volt) -> None:
        super().__init__()

        self.ic = self.Block(Tps92200_Device(FloatExpr()))
        self.connect(self.gnd, self.ic.gnd)
        self.connect(self.pwr, self.ic.vin)
        self.connect(self.pwm, self.ic.dim)
        self.require(self.pwm.is_connected())  # DIM does not appear to have a internal pull

        self.led_voltage = self.ArgParameter(led_voltage)
        self.input_ripple_limit = self.ArgParameter(input_ripple_limit)
        self.output_ripple_limit = self.ArgParameter(output_ripple_limit)

    @override
    def generate(self) -> None:
        super().generate()

        with self.implicit_connect(
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))

            self.boot_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 7) * Volt))
            self.connect(self.boot_cap.neg.adapt_to(VoltageSink()), self.ic.sw)
            self.connect(self.boot_cap.pos, self.ic.boot)

            isense_ref = Range(0.096, 0.102)
            self.rsense = self.Block(CurrentSenseResistor(resistance=(1/self.max_current).shrink_multiply(isense_ref),
                                                          sense_in_reqd=False))
            self.connect(self.rsense.sense_out, self.ic.fb)
            self.connect(self.rsense.pwr_out, self.ledk.adapt_to(VoltageSink(current_draw=self.max_current)))
            self.connect(self.rsense.pwr_in, self.gnd.as_voltage_source())

            self.require(self.pwr.current_draw.within((0, 1.5)*Amp))  # continuous current rating
            frequency = (0.8, 1.2)*MHertz
            self.power_path = imp.Block(BuckConverterPowerPath(
                self.pwr.link().voltage, self.led_voltage, frequency,
                self.max_current, (0, 2.4)*Amp,  # lower of switch source limits
                input_voltage_ripple=self.input_ripple_limit,
                output_voltage_ripple=self.output_ripple_limit,
                dutycycle_limit=(0, 0.99)
            ))
            self.connect(self.power_path.pwr_out, self.leda.adapt_to(VoltageSink(current_draw=self.max_current)))
            self.connect(self.power_path.switch, self.ic.sw)
            self.require(self.power_path.actual_inductor_current_ripple.lower() > 0.3*Amp)  # minimum for stability
