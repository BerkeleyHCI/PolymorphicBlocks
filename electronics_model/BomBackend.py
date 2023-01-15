from typing import List, Tuple, Dict, NamedTuple
import os

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil

import csv


class BomItem(NamedTuple):
    footprint: str
    value: str


class GenerateBom(BaseBackend):      # creates and populates .csv file
    def run(self, design: CompiledDesign, args=None) -> List[Tuple[edgir.LocalPath, str]]:
        if args is None:
            args = {}
        bom_list = BomTransform(design).run()
        name = os.path.splitext(os.path.basename(__file__))[0] + '_bom.csv'

        with open(name, 'w', newline='') as f:  # writes to a csv file
            fieldnames = ['Id', 'Designator', 'Package', 'Quantity', 'Value', 'Designation']    # header values
            thewriter = csv.DictWriter(f, fieldnames=fieldnames)
            thewriter.writeheader()      # creates the header

            for index, (key, value) in enumerate(bom_list.items(), 1):
                thewriter.writerow({'Id': str(index),
                                    'Designator': ','.join(bom_list[key]),
                                    'Package': key.footprint,
                                    'Quantity': len(bom_list[key]),
                                    'Value': key.value,
                                    'Designation': ''})
            f.close()

        text = open(name, "r")
        bom_string = ''.join([row for row in text])
        text.close()

        os.remove(name)     # gets rid of temporary .csv file

        return [
            (edgir.LocalPath(), bom_string)
        ]


class BomTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.bom_list: Dict[BomItem, List[str]] = {}  # BomItem -> list of refdes

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        if self.design.get_value(context.path.to_tuple() + ('fp_footprint',)) is not None:
            bom_item = BomItem(footprint=str(self.design.get_value(context.path.to_tuple() + ('fp_footprint',))),
                               value=str(self.design.get_value(context.path.to_tuple() + ('fp_value',))),)
            refdes = self.design.get_value(context.path.to_tuple() + ('fp_refdes',))
            self.bom_list.setdefault(bom_item, []).append(refdes)

    def run(self) -> Dict[BomItem, List[str]]:
        self.transform_design(self.design.design)
        return self.bom_list
