from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


class Vl53l5cx_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

        self.gnd = self.Port(Ground(), [Common])
        self.avdd = self.Port(
            VoltageSink.from_gnd(
                self.gnd,
                voltage_limits=(2.5, 3.6) * Volt,  # 2.8, 3.3v modes
                current_draw=(0.045, 50) * mAmp,  # LP idle typ to active ranging max
            ),
        )
        self.iovdd = self.Port(
            VoltageSink.from_gnd(
                self.gnd,
                voltage_limits=(1.62, 3.6) * Volt,  # 1.8, 2.8, 3.3v modes
                current_draw=(0.0001, 80) * mAmp,  # LP idle typ to active ranging max
            ),
        )

        gpio_model = DigitalBidir.from_supply(
            self.gnd,
            self.iovdd,
            voltage_limit_abs=(-0.3, 3.6),  # not referenced to Vdd; lower in 1.8v node
            input_threshold_factor=(0.35, 0.65),
        )
        self.i2c_rst = self.Port(DigitalSink.from_bidir(gpio_model))
        self.int = self.Port(DigitalSource.low_from_supply(self.gnd))
        self.lpn = self.Port(DigitalSink.from_bidir(gpio_model))  # I2C disable
        self.rsvd6 = self.Port(DigitalSource.low_from_supply(self.gnd))

        self.i2c = self.Port(
            I2cTarget(
                DigitalBidir.from_supply(
                    self.gnd,
                    self.iovdd,
                    voltage_limit_abs=(-0.5, 3.6),  # not referenced to Vdd!
                    input_threshold_abs=(
                        0.3 * self.iovdd.link().voltage.lower() - self.gnd.link().voltage.lower(),
                        1.13,
                    ),
                ),
                addresses=[0x52],  # TODO software remappable
            ),
            [Output],
        )

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "U",
            "edg:ST_VL53L5x",
            {
                "A1": self.i2c_rst,
                "A2": self.gnd,  # RSVD4
                "A3": self.int,  # 47k pullup to IOVDD required
                "A4": self.iovdd,
                "A5": self.lpn,
                "A6": self.gnd,  # RSVD1
                "A7": self.gnd,  # RSVD2
                "B1": self.avdd,
                "B4": self.gnd,  # thermal pad
                "B7": self.avdd,
                "C1": self.gnd,
                "C2": self.rsvd6,
                "C3": self.i2c.sda,
                "C4": self.i2c.scl,
                # "C5": # RSVD5,  NC
                "C6": self.gnd,  # RSVD3
                "C7": self.gnd,
            },
            mfr="STMicroelectronics",
            part="VL53L5CXV0GC/1",
            datasheet="https://www.st.com/resource/en/datasheet/vl53l5cx.pdf",
            pnp_rot=180,
        )
        self.assign(self.lcsc_part, "C3178303")
        self.assign(self.actual_basic_part, False)


class Vl53l5cx(DistanceSensor, Resettable, GeneratorBlock):
    """Time-of-flight 8x8 multizone laser ranging sensor, up to 4m.
    Requires using the ST API, does not have a defined register map.
    Exposed pad must be thermally connected to GND.

    According to the datasheet, I2C pins require a 2.2k pullup to IOVDD, and int requires a 47k pullup to IOVDD.
    The int pullup is auto-generated if not connected.."""

    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Vl53l5cx_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.avdd, [Power])

        self.i2c = self.Export(self.ic.i2c)

        self.int = self.Port(DigitalSource.empty(), optional=True)
        self.generator_param(self.int.is_connected())

    @override
    def generate(self) -> None:
        super().generate()

        self.connect(self.ic.avdd, self.ic.iovdd)

        # Datasheet Figure 5, two decoupling capacitors
        self.avdd_cap = self.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(self.gnd, self.ic.avdd)
        self.iovdd_cap = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.iovdd)

        self.lpn_pull = self.Block(PullupResistor(47 * kOhm(tol=0.05))).connected(self.ic.iovdd, self.ic.lpn)
        self.rsvd6_pull = self.Block(PullupResistor(47 * kOhm(tol=0.05))).connected(self.ic.iovdd, self.ic.rsvd6)
        self.i2c_rst_pull = self.Block(PulldownResistor(47 * kOhm(tol=0.05))).connected(self.gnd, self.ic.i2c_rst)

        if self.get(self.int.is_connected()):
            self.connect(self.int, self.ic.int)
        else:  # required per the datasheet
            self.int_pull = self.Block(PullupResistor(47 * kOhm(tol=0.05))).connected(self.ic.iovdd, self.ic.int)
