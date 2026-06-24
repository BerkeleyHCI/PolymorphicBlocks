from typing import Any

from typing_extensions import override

from ....circuits import *
from ....vendor_parts.jlc.JlcPart import JlcPart


class Tps561201_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.pwr_in = self.Port(VoltageSink(voltage_limits=(4.5, 17) * Volt, current_draw=RangeExpr()), [Power])
        self.sw = self.Port(VoltageSource(voltage_out=self.pwr_in.link().voltage.hull(self.gnd.link().voltage)))
        self.fb = self.Port(AnalogSink(impedance=(8000, float("inf")) * kOhm))  # based on input current spec
        self.vbst = self.Port(
            VoltageSink(
                voltage_limits=(0, 23) * Volt,
                reverse_voltage_out=(3.6, 6) * Volt,  # assumed from UVLO to BST-SW abs max
                reverse_current_limits=0 * Amp(tol=0),
            )
        )
        self.en = self.Port(DigitalSink(voltage_limits=(-0.1, 17) * Volt, input_thresholds=(0.8, 1.6) * Volt))

    @override
    def contents(self) -> None:
        super().contents()
        self.assign(self.pwr_in.current_draw, self.sw.link().current_drawn)  # TODO quiescent current
        self.footprint(
            "U",
            "Package_TO_SOT_SMD:SOT-23-6",
            {
                "1": self.gnd,
                "2": self.sw,
                "3": self.pwr_in,
                "4": self.fb,
                "5": self.en,
                "6": self.vbst,
            },
            mfr="Texas Instruments",
            part="TPS561201",
            datasheet="https://www.ti.com/lit/ds/symlink/tps561201.pdf",
            pnp_rot=180,
        )
        self.assign(self.lcsc_part, "C220433")
        self.assign(self.actual_basic_part, False)


class Tps561201(VoltageRegulatorEnableWrapper, DiscreteBuckConverter):
    """Adjustable synchronous buck converter in SOT-23-6 with integrated switch"""

    @override
    def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
        return self.ic.en

    @override
    def contents(self) -> None:
        super().contents()

        self.assign(self.actual_frequency, 580 * kHertz(tol=0))

        with self.implicit_connect(
            ImplicitConnect(self.pwr_in, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.ic = imp.Block(Tps561201_Device())

            self.fb = imp.Block(
                FeedbackVoltageDivider(
                    output_voltage=(0.749, 0.787) * Volt,
                    impedance=(1, 10) * kOhm,
                    assumed_input_voltage=self.output_voltage,
                )
            )
            self.connect(self.fb.input, self.pwr_out)
            self.connect(self.fb.output, self.ic.fb)

            self.hf_in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))  # Datasheet 8.2.2.4

            self.vbst_cap = self.Block(BootstrapCapacitor(capacitance=0.1 * uFarad(tol=0.2))).connected(
                self.ic.sw, self.ic.vbst
            )

            # TODO: the control mechanism requires a specific capacitor / inductor selection, datasheet 8.2.2.3
            self.power_path = imp.Block(
                BuckConverterPowerPath(
                    self.pwr_in.link().voltage,
                    self.fb.actual_input_voltage,
                    self.actual_frequency,
                    self.pwr_out.link().current_drawn,
                    (0, 1.2) * Amp,  # output current limit, switch limit not given
                    input_voltage_ripple=self.input_ripple_limit,
                    output_voltage_ripple=self.output_ripple_limit,
                )
            )
            # ForcedVoltage needed to provide a voltage value so current downstream can be calculated
            # and then the power path can generate
            (self.forced_out,), _ = self.chain(
                self.power_path.pwr_out, self.Block(ForcedVoltage(self.fb.actual_input_voltage)), self.pwr_out
            )
            self.connect(self.power_path.switch, self.ic.sw)


class Tps54202h_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

        self.gnd = self.Port(Ground(), [Common])
        self.pwr_in = self.Port(
            VoltageSink(voltage_limits=(4.5, 28) * Volt, current_draw=RangeExpr()),
            [Power],
        )
        self.sw = self.Port(
            VoltageSource(
                voltage_out=self.pwr_in.link().voltage.hull(self.gnd.link().voltage),
                current_limits=(0, 2) * Amp,  # most conservative figures, low-side limited. TODO: better ones?
            )
        )  # internal switch specs not defined, only bulk current limit defined
        self.assign(self.pwr_in.current_draw, self.sw.link().current_drawn)  # TODO quiescent current)

        self.fb = self.Port(AnalogSink())  # no impedance specs
        self.boot = self.Port(
            VoltageSink(
                voltage_limits=self.sw.link().voltage + (-0.3, 7) * Volt,
                reverse_voltage_out=(4.5, 7) * Volt,  # assumed from Vin,min to BST-SW abs max
                reverse_current_limits=0 * Amp(tol=0),
            )
        )
        self.en = self.Port(
            DigitalSink(  # must be connected, floating is disable
                voltage_limits=(-0.1, 7) * Volt, input_thresholds=(1.16, 1.35) * Volt
            )
        )

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "U",
            "Package_TO_SOT_SMD:SOT-23-6",
            {
                "1": self.gnd,
                "2": self.sw,
                "3": self.pwr_in,
                "4": self.fb,
                "5": self.en,
                "6": self.boot,
            },
            mfr="Texas Instruments",
            part="TPS54202H",
            datasheet="https://www.ti.com/lit/ds/symlink/tps54202h.pdf",
            pnp_rot=-90,
        )
        self.assign(self.lcsc_part, "C527684")
        self.assign(self.actual_basic_part, False)


class Tps54202h(Resettable, DiscreteBuckConverter, GeneratorBlock):
    """Adjustable synchronous buck converter in SOT-23-6 with integrated switch, 4.5-24v capable
    Note: TPS54202 has frequency spread-spectrum operation and internal pull-up on EN
    TPS54202H has no internal EN pull-up but a Zener diode clamp to limit voltage.
    """

    @override
    def contents(self) -> None:
        super().contents()
        self.generator_param(self.reset.is_connected())

        self.assign(self.actual_frequency, (390, 590) * kHertz)

        with self.implicit_connect(
            ImplicitConnect(self.pwr_in, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.ic = imp.Block(Tps54202h_Device())

            self.fb = imp.Block(
                FeedbackVoltageDivider(
                    output_voltage=(0.581, 0.611) * Volt,
                    impedance=(1, 10) * kOhm,
                    assumed_input_voltage=self.output_voltage,
                )
            )
            self.connect(self.fb.input, self.pwr_out)
            self.connect(self.fb.output, self.ic.fb)

            self.hf_in_cap = imp.Block(
                DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2))
            )  # Datasheet 8.2.3.1, "optional"?

            self.boot_cap = self.Block(BootstrapCapacitor(capacitance=0.1 * uFarad(tol=0.2))).connected(
                self.ic.sw, self.ic.boot
            )

            self.power_path = imp.Block(
                BuckConverterPowerPath(
                    self.pwr_in.link().voltage,
                    self.fb.actual_input_voltage,
                    self.actual_frequency,
                    self.pwr_out.link().current_drawn,
                    (0, 2.5) * Amp,
                    input_voltage_ripple=self.input_ripple_limit,
                    output_voltage_ripple=self.output_ripple_limit,
                )
            )
            # ForcedVoltage needed to provide a voltage value so current downstream can be calculated
            # and then the power path can generate
            (self.forced_out,), _ = self.chain(
                self.power_path.pwr_out, self.Block(ForcedVoltage(self.fb.actual_input_voltage)), self.pwr_out
            )
            self.connect(self.power_path.switch, self.ic.sw)

    @override
    def generate(self) -> None:
        super().generate()
        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.en)
        else:  # by default tie high to enable regulator
            # an internal 6.9v Zener clamps the enable voltage, datasheet recommends at 510k resistor
            # TODO this should model clamping the input voltage, but doesn't matter since the VDD UVLO handles this case
            self.pwr_in_zener_clamp = self.Block(ForcedVoltage(6.9 * Volt(tol=0)))
            self.connect(self.pwr_in, self.pwr_in_zener_clamp.pwr_in)
            self.en_res = self.Block(PullupResistor(resistance=510 * kOhm(tol=0.05))).connected(
                self.pwr_in_zener_clamp.pwr_out, self.ic.en
            )


class Lmr38020_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.vin = self.Port(VoltageSink(voltage_limits=(4.2, 80) * Volt, current_draw=RangeExpr()), [Power])
        self.sw = self.Port(VoltageSource(voltage_out=self.vin.link().voltage.hull(self.gnd.link().voltage)))
        self.fb = self.Port(AnalogSink(impedance=(10, float("inf")) * MOhm))  # assumed given RFbb maximum spec
        self.boot = self.Port(
            VoltageSink(
                voltage_limits=self.sw.link().voltage + (-0.3, 5.5) * Volt,
                reverse_voltage_out=(3.8, 5.5) * Volt,  # assumed from UVLO to BOOT-SW abs max
                reverse_current_limits=0 * Amp(tol=0),
            )
        )
        self.en = self.Port(
            DigitalSink.from_supply(
                self.gnd, self.vin, voltage_limit_tolerance=(-0.3, 0.3) * Volt, input_threshold_abs=(0.95, 1.4) * Volt
            )
        )
        self.rt = self.Port(AnalogSource())  # for timing
        self.pg = self.Port(DigitalSource.low_from_supply(self.gnd), optional=True)  # may be left open

    @override
    def contents(self) -> None:
        super().contents()
        self.assign(
            self.vin.current_draw, self.sw.link().current_drawn + (3, 40) * uAmp
        )  # shutdown to non-switching Iq
        self.footprint(
            "U",
            "Package_SO:HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm_ThermalVias",
            {
                "1": self.gnd,
                "2": self.en,
                "3": self.vin,
                "4": self.rt,
                "5": self.fb,
                "6": self.pg,
                "7": self.boot,
                "8": self.sw,
                "9": self.gnd,  # EP
            },
            mfr="Texas Instruments",
            part="LMR38020SDDAR",
            datasheet="https://www.ti.com/lit/ds/symlink/lmr38020.pdf",
            pnp_rot=-90,
        )
        self.assign(self.lcsc_part, "C3192337")
        self.assign(self.actual_basic_part, False)


class Lmr38020(VoltageRegulatorEnableWrapper, DiscreteBuckConverter, GeneratorBlock):
    """4.2-80 V, 2 A synchronous buck converter in SO-8 with thermal pad.
    Adjustable frequency, defaulting to 400kHz per the datasheet example."""

    def __init__(self, *, frequency: RangeLike = 400 * kHertz(tol=0.1), **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.frequency = self.ArgParameter(frequency)
        self.generator_param(self.frequency)

        self.ic = self.Block(Lmr38020_Device())
        self.connect(self.pwr_in, self.ic.vin)
        self.connect(self.gnd, self.ic.gnd)

        self.pg = self.Export(self.ic.pg, optional=True, doc="Open-drain active-high power-good flag")

    @override
    def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
        return self.ic.en

    @override
    def generate(self) -> None:
        super().generate()

        with self.implicit_connect(
            ImplicitConnect(self.pwr_in, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.fb = imp.Block(
                FeedbackVoltageDivider(
                    output_voltage=(0.985, 1.015) * Volt,  # across temperature range
                    impedance=(10, 100) * kOhm,
                    assumed_input_voltage=self.output_voltage,
                )
            )
            self.connect(self.fb.input, self.pwr_out)
            self.connect(self.fb.output, self.ic.fb)

            self.hf_cap = imp.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))
            self.boot_cap = self.Block(BootstrapCapacitor(capacitance=0.1 * uFarad(tol=0.2))).connected(
                self.ic.sw, self.ic.boot
            )

            target_frequency = self.get(self.frequency)
            rt_resistance = (
                30970 * ((target_frequency.upper / 1000) ** -1.027) * 1000,
                30970 * ((target_frequency.lower / 1000) ** -1.027) * 1000,
            )
            self.rt = imp.Block(AnalogSetpointResistor(rt_resistance)).connected(io=self.ic.rt)
            self.assign(
                self.actual_frequency, 30970 / (self.rt.actual_resistance / 1000) * 1000
            )  # TODO add exponent term when the infrastructure supports it

            self.power_path = imp.Block(
                BuckConverterPowerPath(
                    self.pwr_in.link().voltage,
                    self.fb.actual_input_voltage,
                    self.actual_frequency,
                    self.pwr_out.link().current_drawn,
                    (0, 1.8) * Amp,  # low-side min switch current limit
                    input_voltage_ripple=self.input_ripple_limit,
                    output_voltage_ripple=self.output_ripple_limit,
                    dutycycle_limit=(0, 0.97),  # goes into PFM at low duty cycles
                )
            )
            # ForcedVoltage needed to provide a voltage value so current downstream can be calculated
            # and then the power path can generate
            (self.forced_out,), _ = self.chain(
                self.power_path.pwr_out, self.Block(ForcedVoltage(self.fb.actual_input_voltage)), self.pwr_out
            )
            self.connect(self.power_path.switch, self.ic.sw)
