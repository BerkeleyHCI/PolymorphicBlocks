from typing_extensions import override
from ..abstract_parts import *
from .JlcPart import JlcPart


class Max17048_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(
            VoltageSink(
                voltage_limits=Range(2.5, 4.5),
                current_draw=(0.5, 40) * uAmp,  # ~23 uA typ
            )
        )
        self.gnd = self.Port(Ground())

        # I2C target interface
        # I/O tolerant to 5.5 V independent of pwr (per datasheet)
        dio_model = DigitalBidir.from_supply(
            self.gnd, self.pwr, voltage_limit_abs=(-0.3, 5.5) * Volt, input_threshold_abs=(0.5, 1.4) * Volt
        )
        self.i2c = self.Port(I2cTarget(dio_model, addresses=[0x36]))

        self.alrt = self.Port(
            DigitalSource.low_from_supply(self.gnd),
            optional=True,
        )

        self.qstrt = self.Port(Passive())

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "U",
            "Package_DFN_QFN:DFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.6mm",
            {
                "1": self.gnd,
                "3": self.pwr,
                "4": self.gnd,
                "5": self.alrt,
                "6": self.qstrt,
                "7": self.i2c.scl,
                "8": self.i2c.sda,
                "9": self.gnd,
            },
            mfr="Analog Devices (Maxim)",
            part="MAX17048",
            datasheet="https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf",
        )
        self.assign(self.lcsc_part, "C2682616")
        self.assign(self.actual_basic_part, False)


class Max17048(DefaultExportBlock):
    """1-Cell Li-Ion voltage based fuel gauge. Senses its pwr as the battery voltage."""

    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Max17048_Device())

        self.pwr = self.Export(self.ic.pwr, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c)
        self.alrt = self.Export(self.ic.alrt, optional=True)

    @override
    def contents(self) -> None:
        super().contents()

        # Required local decoupling 0.1 uF from pwr to GND
        self.pwr_cap = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.pwr)

        # Tie QSTRT to ground unless otherwise needed
        self.connect(self.ic.qstrt.adapt_to(Ground()), self.gnd)
