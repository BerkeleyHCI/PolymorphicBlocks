from ..electronics_abstract_parts import *
from electronics_lib.JlcPart import JlcPart


class Cstne(CeramicResonator, GeneratorBlock, JlcPart, FootprintBlock):
    def contents(self):
        super().contents()
        self.gnd.init_from(Ground())
        self.generator_param(self.frequency)

    def generate(self):
        super().generate()
        parts = [  # tolerance is total stackup: initial temperature, aging
            (Range.from_tolerance(8e6, 0.0007 + 0.0011 + 0.0007), 'CSTNE8M00GH5L000R0', 'C882602',
             'https://www.murata.com/en/products/productdata/8801161805854/SPEC-CSTNE8M00GH5L000R0.pdf'),
            (Range.from_tolerance(8e6, 0.0007 + 0.0013 + 0.0007), 'CSTNE8M00GH5C000R0', 'C341525',
             'https://www.murata.com/en/products/productdata/8801161773086/SPEC-CSTNE8M00GH5C000R0.pdf'),
            (Range.from_tolerance(12e6, 0.0007 + 0.0011 + 0.0007), 'CSTNE12M0GH5L000R0', 'C2650803',
             'https://www.murata.com/en/products/productdata/8801162133534/SPEC-CSTNE12M0GH5L000R0.pdf'),
            (Range.from_tolerance(12e6, 0.0007 + 0.0013 + 0.0007), 'CSTNE12M0GH5C000R0', 'C2659460',
             'https://www.murata.com/en/products/productdata/8801162100766/SPEC-CSTNE12M0GH5C000R0.pdf'),
            (Range.from_tolerance(16e6, 0.0007 + 0.0013 + 0.0007), 'CSTNE16M0VH3C000R0', 'C882605',
             'https://www.murata.com/en/products/productdata/8801162264606/SPEC-CSTNE16M0VH3C000R0.pdf'),
            (Range.from_tolerance(20e6, 0.0007 + 0.0011 + 0.0007), 'CSTNE20M0VH3L000R0', 'C2650766',
             'https://www.murata.com/en/products/productdata/8801161576478/SPEC-CSTNE20M0VH3L000R0.pdf'),
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
