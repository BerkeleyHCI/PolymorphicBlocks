import io
from typing import List, Tuple, Dict, NamedTuple

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil

import csv


class BomItem(NamedTuple):
    footprint: str
    value: str
    jlc_number: str


class GenerateBom(BaseBackend):      # creates and populates .csv file
    def run(self, design: CompiledDesign, args=None) -> List[Tuple[edgir.LocalPath, str]]:
        if args is None:
            args = {}
        bom_list = BomTransform(design).run()

        bom_string = io.StringIO()
        csv_data = ['Id', 'Designator', 'Footprint', 'Quantity',
                    'Designation', 'Supplier and Ref', 'JLCPCB Part #']  # populates headers
        writer = csv.writer(bom_string, lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(csv_data)
        for index, (key, value) in enumerate(bom_list.items(), 1):  # populates the rest of the rows
            csv_data = [str(index), ','.join(bom_list[key]), key.footprint,
                        str(len(bom_list[key])), key.value, '', key.jlc_number]
            writer.writerow(csv_data)

        return [
            (edgir.LocalPath(), bom_string.getvalue())
        ]


class BomTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.bom_list: Dict[BomItem, List[str]] = {}  # BomItem -> list of refdes

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        footprint = self.design.get_value(context.path.to_tuple() + ('fp_footprint',))
        refdes = self.design.get_value(context.path.to_tuple() + ('fp_refdes',))
        if footprint is not None and refdes is not None:
            value = self.design.get_value(context.path.to_tuple() + ('fp_value',)) or ''
            jlc_number = self.design.get_value(context.path.to_tuple() + ('lcsc_part',)) or ''
            assert isinstance(footprint, str) and isinstance(refdes, str) \
                   and isinstance(jlc_number, str) and isinstance(value, str)
            bom_item = BomItem(footprint=footprint, value=value, jlc_number=jlc_number)
            self.bom_list.setdefault(bom_item, []).append(refdes)

    def run(self) -> Dict[BomItem, List[str]]:
        self.transform_design(self.design.design)
        return self.bom_list
