from typing import List, Tuple
import os

import edgir
from edg_core import CompiledDesign, TransformUtil, BaseBackend

import csv


class BomItem:
    def __init__(self, designator, quantity, value, footprint, manufacturer, part_number, datasheet):
        self.designator = designator
        self.quantity = quantity
        self.value = value
        self.footprint = footprint
        self.manufacturer = manufacturer
        self.part_number = part_number
        self.datasheet = datasheet


class BomBackend(BaseBackend):      # creates and populates .csv file
    def run(self, design: CompiledDesign) -> List[Tuple[edgir.LocalPath, str]]:
        bom_list = BomTransform(design).run()
        name = 'BOM.csv' # fix filename: os.path.splitext(__file__)[0]
        with open(name, 'w', newline='') as f:
            fieldnames = ['Ref Des', 'Quantity', 'Value', 'Footprint', 'Manufacturer', 'Part Number', 'Datasheet']
            thewriter = csv.DictWriter(f, fieldnames=fieldnames)

            thewriter.writeheader()      # creates the header

            for item in bom_list:
                thewriter.writerow({'Ref Des' : item.designator, 'Quantity' : item.quantity, 'Value' : item.value,
                                    'Footprint' : item.footprint, 'Manufacturer' : item.manufacturer,
                                    'Part Number' : item.part_number, 'Datasheet' : item.datasheet})

        return [
            (edgir.LocalPath(), "BOM.csv")
        ]


class BomTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.bom_list: List[BomItem] = []  # populated in traversal order

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        tracker = True
        for item in self.bom_list:   # checks for multiple occurrences of the same component
            if str(self.design.get_value(context.path.to_tuple() + ('fp_footprint',))) == item.footprint:
                item.designator += ' ' + str(self.design.get_value(context.path.to_tuple() + ('fp_refdes',)))
                item.quantity += 1
                tracker = False
                break

        if tracker:
            bom = BomItem(str(self.design.get_value(context.path.to_tuple() + ('fp_refdes',))), 1,
                          str(self.design.get_value(context.path.to_tuple() + ('fp_value',))),
                          str(self.design.get_value(context.path.to_tuple() + ('fp_footprint',))),
                          str(self.design.get_value(context.path.to_tuple() + ('fp_mfr',))),
                          str(self.design.get_value(context.path.to_tuple() + ('fp_part',))),
                          str(self.design.get_value(context.path.to_tuple() + ('fp_datasheet',))))

            self.bom_list.append(bom)

    def run(self) -> List[BomItem]:
        self.transform_design(self.design.design)
        return self.bom_list
