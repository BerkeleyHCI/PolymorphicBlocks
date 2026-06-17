import warnings
from typing import Any

from typing_extensions import override

from ....circuits import *
from ....vendor_parts.jlc.JlcPart import JlcPart


class Ina219_Device(InternalSubcircuit, JlcPart, FootprintBlock, GeneratorBlock):
    def __init__(self, addr_lsb: IntLike):
        super().__init__()
        self.addr_lsb = self.ArgParameter(addr_lsb)
        self.generator_param(self.addr_lsb)

        self.vs = self.Port(VoltageSink(voltage_limits=(3, 5.5) * Volt, current_draw=(6 * uAmp, 1 * mAmp)))
        self.gnd = self.Port(Ground())

        self.i2c = self.Port(I2cTarget(DigitalBidir.empty(), addresses=[0x40 + self.addr_lsb]))
        self.i2c.sda.init_from(
            DigitalBidir.from_supply(
                self.gnd, self.vs, voltage_limit_abs=(-0.3, 6.0) * Volt, input_threshold_factor=(0.3, 0.7)
            )
        )
        self.i2c.scl.init_from(
            DigitalSink.from_supply(
                self.gnd, self.vs, voltage_limit_tolerance=(-0.3, 0.3) * Volt, input_threshold_factor=(0.3, 0.7)
            )
        )

        self.in_pos = self.Port(AnalogSink(voltage_limits=(-0.3, 26) * Volt))
        self.in_neg = self.Port(AnalogSink(voltage_limits=(-0.3, 26) * Volt))

    @override
    def generate(self) -> None:
        super().generate()

        sa1_pin, sa0_pin = {
            0: (self.gnd, self.gnd),
            1: (self.gnd, self.vs),
            2: (self.gnd, self.i2c.sda),
            3: (self.gnd, self.i2c.scl),
            4: (self.vs, self.gnd),
            5: (self.vs, self.vs),
            6: (self.vs, self.i2c.sda),
            7: (self.vs, self.i2c.scl),
            8: (self.i2c.sda, self.gnd),
            9: (self.i2c.sda, self.vs),
            10: (self.i2c.sda, self.i2c.sda),
            11: (self.i2c.sda, self.i2c.scl),
            12: (self.i2c.scl, self.gnd),
            13: (self.i2c.scl, self.vs),
            14: (self.i2c.scl, self.i2c.sda),
            15: (self.i2c.scl, self.i2c.scl),
        }[self.get(self.addr_lsb)]

        self.footprint(
            "U",
            "Package_TO_SOT_SMD:SOT-23-8",
            {
                "1": self.in_pos,
                "2": self.in_neg,
                "3": self.gnd,
                "4": self.vs,
                "5": self.i2c.scl,
                "6": self.i2c.sda,
                "7": sa0_pin,  # type: ignore
                "8": sa1_pin,  # type: ignore
            },
            mfr="Texas Instruments",
            part="INA219AIDCNR",
            datasheet="https://www.ti.com/lit/ds/symlink/ina219.pdf",
            pnp_rot=180,
        )
        self.assign(self.lcsc_part, "C87469")
        self.assign(self.actual_basic_part, False)


class Ina219(CurrentSensor, GeneratorBlock):
    """Bidirectional current/voltage/power monitor with I2C interface"""

    def __init__(
        self, shunt_resistor: RangeLike = 2.0 * mOhm(tol=0.05), *, addr_lsb: IntLike = 0, flip_sense: BoolLike = False
    ):
        super().__init__()
        self.flip_sense = self.ArgParameter(flip_sense)
        self.generator_param(self.flip_sense)

        self.ic = self.Block(Ina219_Device(addr_lsb))
        self.pwr = self.Export(self.ic.vs, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c)

        self.Rs = self.Block(
            CurrentSenseResistor(
                resistance=shunt_resistor,
            )
        )

        self.sense_pwr_in = self.Export(self.Rs.pwr_in)
        self.sense_pwr_out = self.Export(self.Rs.pwr_out)

    @override
    def generate(self) -> None:
        super().generate()
        self.vs_cap = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)

        if not self.get(self.flip_sense):
            self.connect(self.Rs.sense_in, self.ic.in_pos)
            self.connect(self.Rs.sense_out, self.ic.in_neg)
        else:
            self.connect(self.Rs.sense_in, self.ic.in_neg)
            self.connect(self.Rs.sense_out, self.ic.in_pos)

    def __getattr__(self, item: str) -> Any:
        if item == "sense_pos":
            warnings.warn(f"Use sense_pwr_in instead.", DeprecationWarning, stacklevel=2)
            return self.sense_pwr_in
        elif item == "sense_neg":
            warnings.warn(f"Use sense_pwr_out instead.", DeprecationWarning, stacklevel=2)
            return self.sense_pwr_out
        else:
            # ideally we'd use super().__getattr__(...), but that's not defined in base classes
            raise AttributeError(item)
