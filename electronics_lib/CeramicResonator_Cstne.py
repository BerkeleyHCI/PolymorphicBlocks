from electronics_abstract_parts import *
from electronics_lib.JlcPart import JlcPart


class Cstne(CeramicResonator, GeneratorBlock, JlcPart, FootprintBlock):
    @init_in_parent
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gnd.init_from(Ground())
        self.generator_param(self.frequency)

    def generate(self):
        super().generate()
        parts = [  # tolerance is total stackup: initial temperature, aging
            (Range.from_tolerance(8e6, 0.0025), 'CSTNE8M00GH5L000R0', 'C882602', 'https://www.murata.com/en/products/productdata/8801161805854/SPEC-CSTNE8M00GH5L000R0.pdf'),
        ]
        suitable_parts = [part for part in parts if part[0].fuzzy_in(self.get(self.frequency))]
        assert suitable_parts, "no compatible part"
        part_freq, part_number, lcsc_part, part_datasheet = suitable_parts[0]

        self.assign(self.crystal.frequency, part_freq)
        self.assign(self.lcsc_part, lcsc_part)
        self.assign(self.actual_basic_part, False)
        self.footprint(
            'U', 'Crystal:Resonator_SMD_Murata_CSTxExxV-3Pin_3.0x1.1mm',
            {
                '1': self.crystal.xtal_in,
                '2': self.gnd,
                '3': self.crystal.xtal_out,
            },
            mfr='Murata Electronics', part=part_number,
            datasheet=part_datasheet,
        )
