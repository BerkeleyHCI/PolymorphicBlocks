from typing_extensions import override
from ..abstract_parts import *
from .JlcPart import JlcPart


class Max17048_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    """MAX17048 1-Cell Li-Ion Fuel Gauge"""

    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=Range(2.5, 4.5),
            current_draw=(0, 100) * uAmp,  # ~23 uA typ, margin included
        ))
        self.gnd = self.Port(Ground())

        # I2C target interface
        # I/O tolerant to 5.5 V independent of VDD (per datasheet)
        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            voltage_limit_abs=(-0.5 * Volt, 5.5 * Volt),
            input_threshold_factor=(0.3, 0.7)
        )
        self.i2c = self.Port(I2cTarget(dio_model, addresses=ArrayIntExpr()))

        self.alrt = self.Port(DigitalSingleSource(
            voltage_out=Range(0, 5.5),
            output_thresholds=Range(0, 5.5),
            pullup_capable=True,
        ), optional=True)

        self.qstrt = self.Port(Passive())

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            'U', 'Package_DFN_QFN:DFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.6mm',
            {
                '1': self.gnd,
                '3': self.vdd,
                '4': self.gnd,
                '5': self.alrt,
                '6': self.qstrt,
                '7': self.i2c.scl,
                '8': self.i2c.sda,
                '9': self.gnd,
            },
            mfr='Analog Devices (Maxim)', part='MAX17048',
            datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf'
        )
        self.assign(self.lcsc_part, 'C2682616')
        self.assign(self.actual_basic_part, False)


class Max17048(DefaultExportBlock):
    """MAX17048 fuel gauge with decoupling and internal ties"""

    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Max17048_Device())

        self.vdd = self.Export(self.ic.vdd, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c)
        self.alrt = self.Export(self.ic.alrt, optional=True)

        self.addr = self.Parameter(IntExpr(0x36))

    @override
    def contents(self) -> None:
        super().contents()

        # Required local decoupling 0.1 uF from VDD to GND
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)

        # Tie QSTRT to ground unless otherwise needed
        self.connect(self.ic.qstrt.adapt_to(Ground()), self.gnd)

        # Optional pull-up resistor for the alert pin
        self.alrt_pull = self.Block(PullupResistor(10 * kOhm(tol=0.05))).connected(self.vdd, self.ic.alrt)

        # Try to assign the default I2C 7-bit address if the model supports it
        self.assign(self.ic.i2c.addresses, [self.addr])
