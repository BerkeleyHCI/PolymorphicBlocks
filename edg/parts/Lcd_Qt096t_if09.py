from typing_extensions import override

from ..abstract_parts import *
from .PassiveConnector_Fpc import Fpc050Bottom


class Qt096t_if09_Device(InternalSubcircuit, Block):
    def __init__(self) -> None:
        super().__init__()

        # both Vdd and VddI
        self.gnd = self.Port(Ground())
        self.vdd = self.Port(
            VoltageSink(
                voltage_limits=(2.5, 4.8) * Volt,  # 2.75v typ
                current_draw=(0.02, 2.02) * mAmp,  # ST7735S Table 7.3, IDDI + IDD, typ - max
            )
        )

        dio_model = DigitalBidir.from_supply(
            self.gnd,
            self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            current_draw=0 * mAmp(tol=0),
            input_threshold_factor=(0.3, 0.7),
        )
        din_model = DigitalSink.from_bidir(dio_model)
        self.reset = self.Port(din_model)
        self.rs = self.Port(din_model)  # data / command selection pin
        self.cs = self.Port(din_model)

        self.spi = self.Port(SpiPeripheral(dio_model))
        self.leda = self.Port(Passive())

        self.conn = self.Block(Fpc050Bottom(length=8)).connected(
            {
                "7": self.vdd,
                "2": self.gnd,
                "3": self.reset,
                "4": self.rs,
                "8": self.cs,
                "6": self.spi.sck,  # scl
                "5": self.spi.mosi,  # sda
                "1": self.leda,
            }
        )


class Qt096t_if09(Lcd, Resettable, Block):
    """ST7735S-based LCD module with a 8-pin 0.5mm-pitch FPC connector"""

    def __init__(self) -> None:
        super().__init__()

        self.device = self.Block(Qt096t_if09_Device())
        self.gnd = self.Export(self.device.gnd, [Common])
        self.pwr = self.Export(self.device.vdd, [Power])
        self.rs = self.Export(self.device.rs)
        self.cs = self.Export(self.device.cs)
        self.spi = self.Export(self.device.spi)
        self.led = self.Port(DigitalSink.empty())

    @override
    def contents(self) -> None:
        super().contents()
        self.connect(self.reset, self.device.reset)
        self.require(self.reset.is_connected())

        self.led_res = self.Block(Resistor(resistance=100 * Ohm(tol=0.05)))  # TODO dynamic sizing, power
        self.connect(
            self.led_res.a.adapt_to(
                DigitalSink(
                    # no voltage limits, since the resistor is autogen'd
                    input_thresholds=(3, 3),  # TODO more accurate model
                    current_draw=(16, 20) * mAmp,  # TODO user-configurable?
                )
            ),
            self.led,
        )
        self.connect(self.led_res.b, self.device.leda)

        self.vdd_cap = self.Block(DecouplingCapacitor(capacitance=1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
