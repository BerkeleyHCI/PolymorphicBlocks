from edg.abstract_parts import *
from edg.parts.JlcPart import JlcPart


class Tle5012b_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(3.0, 5.5) * Volt,
            current_draw=(5 * uAmp, 16 * mAmp)
        ))
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            input_threshold_factor=(0.3, 0.7),
            current_limits=(5 * uAmp, 25 * mAmp)
        )
        dio_model_sck = DigitalSink.from_supply(self.gnd, self.vdd,
                                                voltage_limit_tolerance=(-0.3, 0.3) * Volt)
        self.sck = self.Port(dio_model_sck)
        self.csq = self.Port(dio_model_sck)
        self.data = self.Port(DigitalSink.from_bidir(dio_model))

        if_dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            input_threshold_factor=(0.3, 0.7),
            current_limits=(5 * uAmp, 15 * mAmp)
        )

        self.ifa = self.Port(DigitalSource.from_bidir(if_dio_model), optional=True)
        self.ifb = self.Port(DigitalSource.from_bidir(if_dio_model), optional=True)
        self.ifc = self.Port(DigitalSource.from_bidir(if_dio_model), optional=True)

    def contents(self) -> None:
        self.footprint(
            'U', 'fp:SO8_PG-DSO-8_INF',
            {
                '1': self.ifc,
                '2': self.sck,
                '3': self.csq,
                '4': self.data,
                '5': self.ifa,
                '6': self.vdd,
                '7': self.gnd,
                '8': self.ifb
            },
            mfr='Infineon', part='Tle5012b',
            datasheet='https://www.infineon.com/cms/en/product/sensor/magnetic-sensors/magnetic-position-sensors/angle-sensors/tle5012b-e1000/'
        )
        self.assign(self.lcsc_part, 'C123083')
        self.assign(self.actual_basic_part, False)


class Tle5012b(Magnetometer, DefaultExportBlock):
    """Angle sensor based on Giant Magneto Resistance (GMR) for precise angular position sensing."""

    def __init__(self):
        super().__init__()
        self.ic = self.Block(Tle5012b_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])

        self.sck = self.Export(self.ic.sck, optional=True)
        self.csq = self.Export(self.ic.csq, optional=True)
        self.data = self.Export(self.ic.data, optional=True)

        self.ifa = self.Export(self.ic.ifa, optional=True,
                               doc="IIF Phase A / Hall Switch Signal 1 / PWM / SPC output (input for SPC trigger only)")
        self.ifb = self.Export(self.ic.ifb, optional=True, doc="IIF Phase B / Hall Switch Signal 2")
        self.ifc = self.Export(self.ic.ifc, optional=True, doc="External Clock / IIF Index / Hall Switch Signal 3")

    def contents(self):
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(100 * nFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
