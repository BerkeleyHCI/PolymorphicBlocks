from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


class Qmc5883l_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(
            VoltageSink(
                voltage_limits=(2.16, 3.6) * Volt,
                current_draw=(3 * uAmp, 2.6 * mAmp),  # standby to peak active, assuming it's all on Vdd
            )
        )
        self.vddio = self.Port(VoltageSink(voltage_limits=(1.65, 3.6) * Volt))
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd,
            self.vddio,
            voltage_limit_abs=(-0.3 * Volt, self.vddio.voltage_limits.upper() + 0.3),
            input_threshold_factor=(0.3, 0.7),
        )
        self.i2c = self.Port(I2cTarget(dio_model))
        self.drdy = self.Port(DigitalSource.from_bidir(dio_model), optional=True)

        self.setp = self.Port(Passive())
        self.setc = self.Port(Passive())
        self.c1 = self.Port(VoltageSource(voltage_out=self.vdd.link().voltage, current_limits=(0, 0) * Amp))  # assumed

    @override
    def contents(self) -> None:
        self.footprint(
            "U",
            "Package_LGA:LGA-16_3x3mm_P0.5mm",
            {
                "1": self.i2c.scl,
                "2": self.vdd,
                # '3': NC
                "4": self.vddio,  # S1, "tie top VddIO
                # '5': NC
                # '6': NC
                # '7': NC
                "8": self.setp,
                "9": self.gnd,
                "10": self.c1,
                "11": self.gnd,
                "12": self.setc,
                "13": self.vddio,
                # '14': NC
                "15": self.drdy,
                "16": self.i2c.sda,
            },
            mfr="QST",
            part="QMC5883L",
            datasheet="https://www.filipeflop.com/img/files/download/Datasheet-QMC5883L-1.0%20.pdf",  # first result on Google
            pnp_rot=-90,
        )
        self.assign(self.lcsc_part, "C976032")
        self.assign(self.actual_basic_part, False)


class Qmc5883l(Magnetometer, DefaultExportBlock):
    """3-axis magnetometer.

    This part may be obsolete and harder to source.

    This part seems to be a licensed semi-copy of the HMC5883L which is no longer in production.
    It might be hardware drop-in compatible though the firmware protocol differs.
    """

    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Qmc5883l_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.pwr_io = self.Export(self.ic.vddio, default=self.pwr, doc="TODO")
        self.i2c = self.Export(self.ic.i2c)
        self.drdy = self.Export(self.ic.drdy, optional=True)

    @override
    def contents(self) -> None:
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
        self.set_cap = self.Block(Capacitor(0.22 * uFarad(tol=0.2), voltage=self.pwr.link().voltage))
        self.connect(self.set_cap.pos, self.ic.setp)
        self.connect(self.set_cap.neg, self.ic.setc)
        self.c1 = self.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(self.gnd, self.ic.c1)


class Qmc5883p_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(
            VoltageSink(
                voltage_limits=(2.5, 3.6) * Volt,
                current_draw=(22, 2200) * uAmp,  # suspend to continuous
            )
        )
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd,
            self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # assumed form Vdd absolute maximum rating
            input_threshold_factor=(0.3, 0.7),
        )
        self.i2c = self.Port(I2cTarget(dio_model))
        self.c1 = self.Port(VoltageSource(voltage_out=self.vdd.link().voltage, current_limits=(0, 0) * Amp))  # assumed

    @override
    def contents(self) -> None:
        self.footprint(
            "U",
            "Package_LGA:LGA-16_3x3mm_P0.5mm",
            {
                "1": self.i2c.scl,
                "2": self.vdd,
                # 3-8: NC
                "9": self.gnd,
                "10": self.c1,
                "11": self.gnd,
                # 12-15: NC
                "16": self.i2c.sda,
            },
            mfr="QST",
            part="QMC5883P",
            datasheet="https://www.qstcorp.com/upload/pdf/202512/2C939E5AA0704285BC3BE71132B8629B.pdf",
            pnp_rot=-90,
        )
        self.assign(self.lcsc_part, "C2847467")
        self.assign(self.actual_basic_part, False)


class Qmc5883p(Magnetometer, Block):
    """3-axis magnetometer, seemingly the successor to the QMC5883L which may be harder to source."""

    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Qmc5883p_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.i2c = self.Export(self.ic.i2c)

    @override
    def contents(self) -> None:
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
        self.c1 = self.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(self.gnd, self.ic.c1)
