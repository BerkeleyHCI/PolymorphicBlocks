from ..abstract_parts import *
from .JlcPart import JlcPart


class Mp2722_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    @init_in_parent
    def __init__(self):
        super().__init__()
        # self.sw = self.Port(VoltageSource(
        #     current_limits=(0, 2)*Amp  # most conservative figures, low-side limited. TODO: better ones?
        # ))  # internal switch specs not defined, only bulk current limit defined
        # self.pwr_in = self.Port(VoltageSink(
        #     voltage_limits=(4.5, 28)*Volt,
        #     current_draw=self.sw.link().current_drawn  # TODO quiescent current
        # ), [Power])
        # self.gnd = self.Port(Ground(), [Common])
        # self.fb = self.Port(AnalogSink())  # no impedance specs
        # self.boot = self.Port(VoltageSource())
        # self.en = self.Port(DigitalSink(  # must be connected, floating is disable
        #     voltage_limits=(-0.1, 7) * Volt,
        #     input_thresholds=(1.16, 1.35)*Volt
        # ))

    def contents(self) -> None:
        super().contents()
        self.footprint(
            'U', 'edg:MPS_QFN-22_2.5x3.5mm_P0.4mm',
            {
                '2': self.vin,
                '3': self.pmid,
                '4': self.sw,
                '6': self.bst,
                '13': self.sys,
                '14': self.batt,
                '5': self.pgnd,
                '18': self.agnd,
                '19': self.vcc,
                '12': self.battsns,
                '8': self.int,
                '16': self.i2c.scl,
                '15': self.i2c.sda,
                '1': self.cc.cc1,
                '22': self.cc.cc2,
                '21': self.usb.dp,
                '20': self.usb.dm,
                '17': self.reset,
                '7': self.vrntc,  # powered to Vcc when in operation
                '10': self.ntc1,
                '9': self.pg,  # pull up with 10k
                '11': self.stat,  # pull up with 10k
            },
            mfr='Texas Instruments', part='MP2722GRH-0000-P',
            datasheet='https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MP2722GRH/document_id/10035/'
        )
        self.assign(self.lcsc_part, 'C20099550')
        self.assign(self.actual_basic_part, False)


class Mp2722(Resettable, DiscreteBuckConverter, GeneratorBlock):
    """Single-cell narrow voltage DC (5v Vbus <-> ~3.7v LiIon) with forward buck
    and reverse boost and integrated USB-PD CC controller and BC1.2 over D+/D-."""
    def contents(self):
        super().contents()
    #     self.generator_param(self.reset.is_connected())
    #
    #     self.assign(self.actual_frequency, (390, 590)*kHertz)
    #
    #     with self.implicit_connect(
    #             ImplicitConnect(self.pwr_in, [Power]),
    #             ImplicitConnect(self.gnd, [Common]),
    #     ) as imp:
    #         self.ic = imp.Block(Tps54202h_Device())
    #
    #         self.fb = imp.Block(FeedbackVoltageDivider(
    #             output_voltage=(0.581, 0.611) * Volt,
    #             impedance=(1, 10) * kOhm,
    #             assumed_input_voltage=self.output_voltage
    #         ))
    #         self.connect(self.fb.input, self.pwr_out)
    #         self.connect(self.fb.output, self.ic.fb)
    #
    #         self.hf_in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # Datasheet 8.2.3.1, "optional"?
    #
    #         self.boot_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 6) * Volt))
    #         self.connect(self.boot_cap.neg.adapt_to(VoltageSink()), self.ic.sw)
    #         self.connect(self.boot_cap.pos.adapt_to(VoltageSink()), self.ic.boot)
    #
    #         self.power_path = imp.Block(BuckConverterPowerPath(
    #             self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.actual_frequency,
    #             self.pwr_out.link().current_drawn, (0, 2.5)*Amp,
    #             input_voltage_ripple=self.input_ripple_limit,
    #             output_voltage_ripple=self.output_ripple_limit,
    #                                                ))
    #         # ForcedVoltage needed to provide a voltage value so current downstream can be calculated
    #         # and then the power path can generate
    #         (self.forced_out, ), _ = self.chain(self.power_path.pwr_out,
    #                                             self.Block(ForcedVoltage(self.fb.actual_input_voltage)),
    #                                             self.pwr_out)
    #         self.connect(self.power_path.switch, self.ic.sw)
    #
    # def generate(self):
    #     super().generate()
    #     if self.get(self.reset.is_connected()):
    #         self.connect(self.reset, self.ic.en)
    #     else:  # by default tie high to enable regulator
    #         # an internal 6.9v Zener clamps the enable voltage, datasheet recommends at 510k resistor
    #         # a pull-up resistor isn't used because
    #         self.en_res = self.Block(Resistor(resistance=510*kOhm(tol=0.05), power=0*Amp(tol=0)))
    #         self.connect(self.pwr_in, self.en_res.a.adapt_to(VoltageSink()))
    #         self.connect(self.en_res.b.adapt_to(DigitalSource()), self.ic.en)
