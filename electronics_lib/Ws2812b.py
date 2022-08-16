from electronics_abstract_parts import *


class Ws2812b(DiscreteChip, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(3.7, 5.3) * Volt,
            current_draw=(0.6, 0.6+12*3)*mAmp)
        )
        self.gnd = self.Port(Ground())
        self.din = self.Port(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.7),
            input_threshold_abs=(1.5, 2.3))
        )
        self.dout = self.Port(DigitalSource.from_supply(
            self.gnd, self.vss,
            current_limits=0*mAmp)
        )

    def contents(self) -> None:
        self.footprint(
            'D', 'LED_SMD:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm',
            {
                '1': self.vdd,
                '2': self.dout,
                '3': self.gnd,
                '4': self.din
            },
            mfr='Worldsemi', part='WS2812B',
            datasheet='https://datasheet.lcsc.com/lcsc/2106062036_Worldsemi-WS2812B-B-W_C2761795.pdf'
        )
