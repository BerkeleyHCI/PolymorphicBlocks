from typing import Dict

from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ad8418a_Device(JlcPart, FootprintBlock, InternalSubcircuit):
    GAIN = Range.from_tolerance(20, 0.0015)
    @init_in_parent
    def __init__(self, in_diff_range: RangeLike):
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.vs = self.Port(VoltageSink(
            voltage_limits=(2.7, 5.5)*Volt,
            current_draw=(4.1, 4.2)*mAmp  # maximum only
        ))
        input_model = AnalogSink(
            voltage_limits=(2, 70)*Volt,
            signal_limits=(2, 70)*Volt,
            impedance=(46.1, 92.3)*kOhm  # at IN=12v, 130-260uA bias current
        )
        self.inn = self.Port(input_model)
        self.inp = self.Port(input_model)

        ref_model = AnalogSink.from_supply(self.gnd, self.vs)  # not specified, surprisingly
        self.vref1 = self.Port(ref_model)
        self.vref2 = self.Port(ref_model)

        self.in_diff_range = self.ArgParameter(in_diff_range)
        self.out = self.Port(AnalogSource(
            voltage_out=(0.032, self.vs.link().voltage.upper() - 0.032),
            signal_out=(self.vref1.link().signal + self.vref2.link().signal) / 2 +
                       (self.in_diff_range * self.GAIN),
            impedance=2*Ohm(tol=0)  # range not specified
        ))

    def contents(self):
        super().contents()
        self.footprint(
            'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
            {
                '1': self.inn,
                '2': self.gnd,
                '3': self.vref2,
                # 4 is NC
                '5': self.out,
                '6': self.vs,
                '7': self.vref1,
                '8': self.inp,
            },
            mfr='Analog Devices', part='AD8418AWBRZ',
            datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/ad8418.pdf'
        )
        self.assign(self.lcsc_part, 'C462197')
        self.assign(self.actual_basic_part, False)


class Ad8418a(Sensor, KiCadImportableBlock, Block):
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        assert symbol_name == 'edg_importable:DifferentialAmplifier'
        return {
            '+': self.sense_pos, '-': self.sense_neg,
            'R': self.ref, '3': self.out,
            'V+': self.pwr, 'V-': self.gnd
        }

    @init_in_parent
    def __init__(self, in_diff_range: RangeLike):
        super().__init__()
        self.in_diff_range = self.ArgParameter(in_diff_range)
        self.amp = self.Block(Ad8418a_Device(self.in_diff_range))
        self.sense_pos = self.Export(self.amp.inp)
        self.sense_neg = self.Export(self.amp.inn)

        self.pwr = self.Export(self.amp.vs, [Power])
        self.gnd = self.Export(self.amp.gnd, [Common])
        self.ref = self.Export(self.amp.vref1)  # TODO optional for grounded unidirectional
        self.out = self.Export(self.amp.out)

    def contents(self):
        self.connect(self.ref, self.amp.vref2)
        self.vdd_cap = self.Block(DecouplingCapacitor(
            capacitance=0.1*uFarad(tol=0.2),
        )).connected(self.gnd, self.pwr)
