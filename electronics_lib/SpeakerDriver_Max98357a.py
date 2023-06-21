from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Max98357a_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self):
        super().__init__()

        self.vdd = self.Port(VoltageSink(
            voltage_limits=(2.5, 5.5) * Volt,
            current_draw=(0.0006, 3.35 + (3.2/5/0.92)) * mAmp,  # shutdown to maximum (3.2W out @ 5V, 92% efficient)
        ), [Power])
        self.gnd = self.Port(Ground(), [Common])

        din_model = DigitalSink(
            voltage_limits=(-0.3, 6)*Volt,  # abs max ratings
            input_thresholds=(0.6, 0.6)*Volt  # only input low voltage given
        )
        self.i2s = self.Port(I2sTargetReceiver(din_model))

        self.out = self.Port(SpeakerDriverPort(AnalogSource()), [Output])

    def contents(self):
        self.footprint(
            'U', 'Package_BGA:Maxim_WLP-9_1.595x1.415_Layout3x3_P0.4mm_Ball0.27mm_Pad0.25mm_NSMD',
            {
                'A2': self.vdd,
                'C2': self.gnd,
                # 'B2': gain_slot,  # TODO: configurable gain, open = 9dB
                'A1': self.vdd,  # hard tied to left mode only TODO selectable SD_MODE
                'C1': self.i2s.sck,
                'C3': self.i2s.ws,
                'B1': self.i2s.sd,
                'A3': self.out.a,  # outp
                'B3': self.out.b,  # outn
            },
            mfr='Maxim Integrated', part='MAX98357AEWL+T',
            datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf'
        )
        self.assign(self.lcsc_part, 'C2682619')
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
