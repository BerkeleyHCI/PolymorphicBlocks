from typing import Dict

from ..abstract_parts import *
from .JlcPart import JlcPart


class Max98357a_Device(InternalSubcircuit, JlcPart, PartsTableFootprint, PartsTablePart,
                       GeneratorBlock, FootprintBlock):
    def __init__(self):
        super().__init__()

        self.vdd = self.Port(VoltageSink(
            voltage_limits=(2.5, 5.5) * Volt,
            current_draw=(0.0006, 3.35 + (3.2/5/0.92)*1000) * mAmp,  # shutdown to maximum (3.2W out @ 5V, 92% efficient)
        ), [Power])
        self.gnd = self.Port(Ground(), [Common])

        din_model = DigitalSink(
            voltage_limits=(-0.3, 6)*Volt,  # abs max ratings
            input_thresholds=(0.6, 0.6)*Volt  # only input low voltage given
        )
        self.i2s = self.Port(I2sTargetReceiver(din_model))

        self.out = self.Port(SpeakerDriverPort(AnalogSource()), [Output])

        self.generator_param(self.part, self.footprint_spec)

    def generate(self):
        super().generate()
        if not self.get(self.footprint_spec) or \
                self.get(self.footprint_spec) == 'Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm':
            footprint = 'Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm'
            pinning: Dict[str, CircuitPort] = {
                '4': self.vdd,  # hard tied to left mode only TODO selectable SD_MODE
                '7': self.vdd,
                '8': self.vdd,
                '9': self.out.a,  # outp
                '1': self.i2s.sd,
                # '2': gain_slot,  # TODO: configurable gain, open = 9dB
                '10': self.out.b,  # outn
                '16': self.i2s.sck,
                '3': self.gnd,
                '11': self.gnd,
                '15': self.gnd,
                '14': self.i2s.ws,
                '17': self.gnd,  # EP, optionally grounded for thermal dissipation
            }
            part = 'MAX98357AETE+T'
            jlc_part = 'C910544'
        elif self.get(self.footprint_spec) == 'Package_BGA:Maxim_WLP-9_1.595x1.415_Layout3x3_P0.4mm_Ball0.27mm_Pad0.25mm_NSMD':
            footprint = 'Package_BGA:Maxim_WLP-9_1.595x1.415_Layout3x3_P0.4mm_Ball0.27mm_Pad0.25mm_NSMD'
            pinning = {
                    'A1': self.vdd,  # hard tied to left mode only TODO selectable SD_MODE
                    'A2': self.vdd,
                    'A3': self.out.a,  # outp
                    'B1': self.i2s.sd,
                    # 'B2': gain_slot,  # TODO: configurable gain, open = 9dB
                    'B3': self.out.b,  # outn
                    'C1': self.i2s.sck,
                    'C2': self.gnd,
                    'C3': self.i2s.ws,
                }
            part = 'MAX98357AEWL+T'
            jlc_part = 'C2682619'
        else:
            raise ValueError()

        self.footprint(
            'U', footprint,
            pinning,
            mfr='Maxim Integrated', part=part,
            datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf'
        )
        self.assign(self.lcsc_part, jlc_part)
        self.assign(self.actual_basic_part, False)

class Max98357a(Interface, Block):
    """MAX98357A I2S speaker driver with default gain."""
    @init_in_parent
    def __init__(self):
        super().__init__()

        self.ic = self.Block(Max98357a_Device())
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

        self.i2s = self.Export(self.ic.i2s, [Input])
        self.out = self.Export(self.ic.out, [Output])

    def contents(self):
        super().contents()

        with self.implicit_connect(
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common])
        ) as imp:
            self.pwr_cap0 = imp.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2)))
            self.pwr_cap1 = imp.Block(DecouplingCapacitor(10*uFarad(tol=0.2)))
