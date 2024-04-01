from typing import Dict

from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ad8418a_Device(JlcPart, FootprintBlock):
    GAIN = Range.from_tolerance(20, 0.0015)
    def __init__(self):
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
        self.out = self.Port(AnalogSource(
            voltage_out=(0.032, self.vs.link().voltage.upper() - 0.032),
            signal_out=(0.032, self.vs.link().voltage.upper() - 0.032),  # unknown at chip level
            impedance=2*Ohm(tol=0)  # range not specified
        ))
        ref_model = AnalogSink.from_supply(self.gnd, self.vs)  # not specified, surprisingly
        self.vref1 = self.Port(ref_model)
        self.vref2 = self.Port(ref_model)

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
    @init_in_parent
    def __init__(self, resistance: RangeLike):
        super().__init__()

        self.sense = self.Block(CurrentSenseResistor(resistance=resistance))
        self.pwr_in = self.Export(self.sense.pwr_in)
        self.pwr_out = self.Export(self.sense.pwr_out)

        self.amp = self.Block(Ad8418a_Device())
        self.pwr_logic = self.Export(self.amp.vs, [Power])
        self.gnd = self.Export(self.amp.gnd, [Common])
        self.ref = self.Export(self.amp.vref1)  # TODO optional for grounded unidirectional
        self.out = self.Port(AnalogSource.empty())

    def contents(self):
        self.connect(self.ref, self.amp.vref2)
        self.connect(self.amp.inp, self.sense.sense_in)
        self.connect(self.amp.inn, self.sense.sense_out)

        output_swing = self.pwr_out.link().current_drawn * self.sense.actual_resistance * self.amp.GAIN
        self.force_signal = self.Block(ForcedAnalogSignal(output_swing + self.ref.link().signal))
        self.connect(self.amp.out, self.force_signal.signal_in)
        self.connect(self.force_signal.signal_out, self.out)

    def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
        assert symbol_name == 'edg_importable:OpampCurrentSensor'
        return {'+': self.pwr_in, '-': self.pwr_out, 'R': self.ref, '3': self.out,
                'V+': self.pwr_logic, 'V-': self.gnd}
