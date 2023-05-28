from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block_default(lambda: Ws2812b)
class Neopixel(Light, Block):
    """Abstract base class for Neopixel-type LEDs including the Vdd/Gnd/Din/Dout interface."""
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.din = self.Port(DigitalSink.empty(), [Input])
        self.dout = self.Port(DigitalSource.empty(), optional=True)


class Ws2812b(Neopixel, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd.init_from(VoltageSink(
            voltage_limits=(3.7, 5.3) * Volt,
            current_draw=(0.6, 0.6 + 12*3) * mAmp,
        ))
        self.gnd.init_from(Ground())
        self.din.init_from(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.7),
            input_threshold_abs=(0.7, 2.7),
            # note that a more restrictive input_threshold_abs of (1.5, 2.3) was used previously
        ))
        self.dout.init_from(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0*mAmp(tol=0),
        ))

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
        # this is actually the WS2812E-V5 which shares similar specs to the B version,
        # but brighter reed and weaker blue and is available for JLC's economy assembly process
        # note, XL-5050RGBC-WS2812B is package compatible but the digital logic thresholds are relative to Vdd
        # and Vih at 0.65 Vddmax = 5.5v is 3.575, which is not compatible with the B version
        self.assign(self.lcsc_part, 'C2920042')
        self.assign(self.actual_basic_part, False)


class Sk6812Mini_E(Neopixel, FootprintBlock):
    """SK6812MINI-E reverse-mount Neopixel RGB LED, commonly used for keyboard lighting.
    Note: while listed as JLC C5149201, it seems non-stocked and is standard assembly only."""
    def __init__(self) -> None:
        super().__init__()
        self.vdd.init_from(VoltageSink(
            voltage_limits=(3.7, 5.5) * Volt,
            current_draw=(1, 1 + 12*3) * mAmp,  # 1 mA static type + up to 12mA/ch
        ))
        self.gnd.init_from(Ground())
        self.din.init_from(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.5, 0.5),
            input_threshold_factor=(0.3, 0.7),
        ))
        self.dout.init_from(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0*mAmp(tol=0),
        ))

    def contents(self) -> None:
        self.footprint(
            'D', 'edg:LED_SK6812MINI-E',
            {
                '1': self.vdd,
                '2': self.dout,
                '3': self.gnd,
                '4': self.din
            },
            mfr='Opsco Optoelectronics', part='SK6812MINI-E',
            datasheet='https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf'
        )


class Sk6805_Ec15(Neopixel, JlcPart, FootprintBlock):
    """SK6805-EC15 Neopixel RGB LED in 1.5x1.5 (0606)."""
    def __init__(self) -> None:
        super().__init__()
        self.vdd.init_from(VoltageSink(
            voltage_limits=(3.7, 5.5) * Volt,
            current_draw=(1, 1 + 5*3) * mAmp,  # 1 mA static type + up to 5mA/ch
        ))
        self.gnd.init_from(Ground())
        self.din.init_from(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.5, 0.5),
            input_threshold_factor=(0.3, 0.7),
        ))
        self.dout.init_from(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0*mAmp(tol=0),
        ))

    def contents(self) -> None:
        self.footprint(
            'D', 'LED_SMD:LED_SK6812_EC15_1.5x1.5mm',
            {
                '1': self.din,
                '2': self.vdd,
                '3': self.dout,
                '4': self.gnd,

            },
            mfr='Opsco Optoelectronics', part='SK6805-EC15',
            datasheet='https://cdn-shop.adafruit.com/product-files/4492/Datasheet.pdf'
        )
        self.assign(self.lcsc_part, 'C2890035')
        self.assign(self.actual_basic_part, False)


class NeopixelArray(Light, GeneratorBlock):
    """An array of Neopixels"""

    @init_in_parent
    def __init__(self, count: IntLike):
        super().__init__()
        self.din = self.Port(DigitalSink.empty(), [Input])
        self.dout = self.Port(DigitalSource.empty(), optional=True)
        self.vdd = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])

        self.count = self.ArgParameter(count)
        self.generator_param(self.count)

    def generate(self):
        super().generate()
        self.led = ElementDict[Neopixel]()

        last_signal_pin: Port[DigitalLink] = self.din
        for led_i in range(self.get(self.count)):
            led = self.led[str(led_i)] = self.Block(Neopixel())
            self.connect(last_signal_pin, led.din)
            self.connect(self.vdd, led.vdd)
            self.connect(self.gnd, led.gnd)
            last_signal_pin = led.dout
        self.connect(self.dout, last_signal_pin)
