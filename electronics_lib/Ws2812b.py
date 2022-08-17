from electronics_abstract_parts import *


class Ws2812b(DiscreteChip, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(3.7, 5.3) * Volt,
            current_draw=(0.6, 0.6 + 12 * 3) * mAmp)
        )
        self.gnd = self.Port(Ground())
        self.din = self.Port(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.7),
            input_threshold_abs=(1.5, 2.3))
        )
        self.dout = self.Port(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0 * mAmp),
            optional=True
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


class Ws2812bArray(GeneratorBlock):
    """An array of WS2812B"""

    @init_in_parent
    def __init__(self, count: IntLike):
        super().__init__()
        self.din = self.Port(DigitalSink.empty(), [Input])
        self.dout = self.Port(DigitalSource.empty(), optional=True)
        self.vdd = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty())
        self.generator(self.generate, count)

    def generate(self, count: int):
        self.led = ElementDict[Ws2812b]()

        last_led = self.led["0"] = self.Block(Ws2812b())
        self.connect(self.din, last_led.din)
        self.connect(self.vdd, last_led.vdd)
        self.connect(self.gnd, last_led.gnd)

        for led_i in range(1, count):
            led = self.led[str(led_i)] = self.Block(Ws2812b())
            self.connect(last_led.dout, led.din)
            self.connect(self.vdd, led.vdd)
            self.connect(self.gnd, led.gnd)
            last_led = led

        self.connect(self.dout, last_led.dout)
