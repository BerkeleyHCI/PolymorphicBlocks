from electronics_abstract_parts import *


class L293DD_Device(DiscreteChip, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.vss = self.Port(VoltageSink(
            voltage_limits=(4.5, 36)*Volt, current_draw=(16, 60)*mAmp
        ))
        self.vs = self.Port(VoltageSink(
            voltage_limits=(self.vss.link().voltage.lower(), 36*Volt), current_draw=(2, 24)*mAmp
        ))
        self.gnd = self.Port(Ground())

        din_model = DigitalSink.from_supply(self.gnd, self.vss, input_threshold_abs=(1.5, 2.3))

        self.en1 = self.Port(din_model, optional=True)
        self.en2 = self.Port(din_model, optional=True)

        self.in1 = self.Port(din_model, optional=True)
        self.in2 = self.Port(din_model, optional=True)
        self.in3 = self.Port(din_model, optional=True)
        self.in4 = self.Port(din_model, optional=True)

        dout_model = DigitalSource.from_supply(self.gnd, self.vss, current_limits=(-600, 600)*mAmp)

        self.out1 = self.Port(dout_model, optional=True)
        self.out2 = self.Port(dout_model, optional=True)
        self.out3 = self.Port(dout_model, optional=True)
        self.out4 = self.Port(dout_model, optional=True)

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm',
            {
                '1': self.en1,
                '2': self.in1,
                '3': self.out1,
                '4': self.gnd,
                '5': self.gnd,
                '6': self.gnd,
                '7': self.gnd,
                '8': self.out2,
                '9': self.in2,
                '10': self.vs,
                '11': self.en2,
                '12': self.in3,
                '13': self.out3,
                '14': self.gnd,
                '15': self.gnd,
                '16': self.gnd,
                '17': self.gnd,
                '18': self.out4,
                '19': self.in4,
                '20': self.vss
            },
            mfr='STMicroelectronics', part='L293DD',  # actual several compatible variants
            datasheet='https://www.st.com/resource/en/datasheet/l293d.pdf'
        )


class L293DD(Block):
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(L293DD_Device())
        self.vs = self.Export(self.ic.vs)
        self.vss = self.Export(self.ic.vss)
        self.gnd = self.Export(self.ic.gnd, [Common])

        self.en1 = self.Export(self.ic.en1)
        self.en2 = self.Export(self.ic.en2)
        self.in1 = self.Export(self.ic.in1)
        self.in2 = self.Export(self.ic.in2)
        self.in3 = self.Export(self.ic.in3)
        self.in4 = self.Export(self.ic.in4)

        self.out1 = self.Export(self.ic.out1)
        self.out2 = self.Export(self.ic.out2)
        self.out3 = self.Export(self.ic.out3)
        self.out4 = self.Export(self.ic.out4)


    def contents(self) -> None:
        super().contents()

        self.vdd_cap = ElementDict[DecouplingCapacitor]()
        self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.vss)
        self.vdd_cap[1] = self.Block(DecouplingCapacitor(1 * uFarad(tol=0.2))).connected(self.gnd, self.vs)