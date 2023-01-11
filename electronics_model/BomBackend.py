from typing import List, Tuple, NamedTuple, Dict
import os

import edgir
from edg_core import CompiledDesign, TransformUtil, BaseBackend

import csv


class BomItem(NamedTuple):
    value: str
    footprint: str
    manufacturer: str
    part_number: str
    datasheet: str
    # possibly add a run function to easily populate .csv string?


class GenerateBom(BaseBackend):      # creates and populates .csv file
    def run(self, design: CompiledDesign) -> List[Tuple[edgir.LocalPath, str]]:
        bom_list = BomTransform(design).run()
        name = os.path.splitext(os.path.basename(__file__))[0] + '_bom.csv'

        with open(name, 'w', newline='') as f:
            fieldnames = ['Ref Des', 'Quantity', 'Value', 'Footprint', 'Manufacturer', 'Part Number', 'Datasheet']
            thewriter = csv.DictWriter(f, fieldnames=fieldnames)
            thewriter.writeheader()      # creates the header

            for key in bom_list:
                thewriter.writerow({'Ref Des': ', '.join(bom_list[key]), 'Quantity': len(bom_list[key]),
                                    'Value': key.value, 'Footprint': key.footprint, 'Manufacturer': key.manufacturer,
                                    'Part Number': key.part_number, 'Datasheet': key.datasheet})

        return [
            (edgir.LocalPath(), name)
        ]


class BomTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.bom_list: Dict[BomItem, List[str]] = {}  # BomItem -> list of refdes

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        if self.design.get_value(context.path.to_tuple() + ('fp_footprint',)) is not None:
            bom_item = BomItem(value=str(self.design.get_value(context.path.to_tuple() + ('fp_value',))),
                               footprint=str(self.design.get_value(context.path.to_tuple() + ('fp_footprint',))),
                               manufacturer=str(self.design.get_value(context.path.to_tuple() + ('fp_mfr',))),
                               part_number=str(self.design.get_value(context.path.to_tuple() + ('fp_part',))),
                               datasheet=str(self.design.get_value(context.path.to_tuple() + ('fp_datasheet',))))
            refdes = self.design.get_value(context.path.to_tuple() + ('fp_refdes',))
            self.bom_list.setdefault(bom_item, []).append(refdes)

    def run(self) -> List[BomItem]:
        self.transform_design(self.design.design)
        return self.bom_list
