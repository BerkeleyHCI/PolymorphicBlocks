from ..electronics_abstract_parts import *
from .JlcPart import JlcPart


class Apx803s_Device(InternalSubcircuit, FootprintBlock, GeneratorBlock, JlcPart):
    @init_in_parent
    def __init__(self, reset_threshold: RangeLike = (2.59, 2.67)*Volt) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vcc = self.Port(VoltageSink(
            voltage_limits=(1.0, 5.5)*Volt,
            current_draw=(10, 15)*uAmp))
        self.nreset = self.Port(DigitalSingleSource.low_from_supply(self.gnd), [Output])

        self.reset_threshold = self.ArgParameter(reset_threshold)
        self.generator_param(self.reset_threshold)
        self.actual_reset_threshold = self.Parameter(RangeExpr())

    def generate(self) -> None:
        super().generate()
        parts = [  # output range, part number, lcsc
            # (Range(2.21, 2.30), 'APX803S-23SA-7', ''),
            (Range(2.59, 2.67), 'APX803S-26SA-7', 'C526393'),
            (Range(2.89, 2.97), 'APX803S-29SA-7', 'C143831'),
            (Range(3.04, 3.13), 'APX803S-31SA-7', 'C129757'),
            # (Range(3.94, 4.06), 'APX803S-40SA', ''),
            # (Range(4.31, 4.45), 'APX803S-44SA-7', ''),
            # (Range(4.56, 4.70), 'APX803S-46SA-7', ''),
        ]
        suitable_parts = [part for part in parts if part[0] in self.get(self.reset_threshold)]
        assert suitable_parts, "no compatible part"
        part_reset_threshold, part_number, lcsc_part = suitable_parts[0]
        self.assign(self.actual_reset_threshold, part_reset_threshold)

        self.footprint(  # -SA package pinning
            'U', 'Package_TO_SOT_SMD:SOT-23',
            {
                '1': self.gnd,
                '2': self.nreset,
                '3': self.vcc,
            },
            mfr='Diodes Incorporated', part=part_number,
            datasheet='https://www.diodes.com/assets/Datasheets/APX803S.pdf'
        )
        self.assign(self.lcsc_part, lcsc_part)
        self.assign(self.actual_basic_part, False)


class Apx803s(Interface, Block):
    @init_in_parent
    def __init__(self, reset_threshold: RangeLike) -> None:
        super().__init__()
        self.ic = self.Block(Apx803s_Device(reset_threshold))  # datasheet doesn't require decaps
        self.pwr = self.Export(self.ic.vcc, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.nreset = self.Export(self.ic.nreset, [Output])
