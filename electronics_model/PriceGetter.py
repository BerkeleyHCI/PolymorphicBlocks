from typing import List, Tuple, Dict

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil
import os
import csv
import re


class GetPrice:
    def run(lcsc_part_number: str, quantity: int) -> float:
        cur_path = os.path.dirname(__file__)
        parts_library = os.path.relpath(
            '..\\electronics_lib\\resources\\Pruned_JLCPCB SMT Parts Library(20220419).csv', cur_path)

        price_string: str = 'NA'
        with open(parts_library, 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file, 'r')
            for row in csv_reader:
                if row['LCSC Part'] == lcsc_part_number:
                    price_string = row['Price']
                    break
            if price_string == 'NA':
                return -1
            csv_file.close()

        temp = price_string.split(',')  # temp = list of all the qty ranges & prices per range
        for subString in temp:
            quantity_group = re.split("[-:]", subString)
            length = len(quantity_group)
            # for the case when quantity_group is ["lower-bound", "upper-bound", "price per part"]:
            if length == 3 and quantity < int(quantity_group[1]):
                return quantity * float(quantity_group[2])
            # for the case when quantity_group is ["lower-bound", "price per part"]:
            elif length == 2:
                return quantity * float(quantity_group[1])


class PriceTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.part_list: Dict[str, int] = {}

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        lcsc_part_number: str = self.design.get_value(context.path.to_tuple() + ('lcsc_part',)) or None
        if lcsc_part_number is not None:
            try:
                self.part_list[lcsc_part_number] += 1
            except KeyError:
                self.part_list[lcsc_part_number] = 1

    def run(self) -> Dict[str, int]:
        self.transform_design(self.design.design)
        return self.part_list


class GeneratePrice(BaseBackend):      # creates and populates .csv file
    def run(self, design: CompiledDesign, args=None) -> List[Tuple[edgir.LocalPath, str]]:
        if args is None:
            args = {}
        price_list = PriceTransform(design).run()
        total_price = 0
        for lcsc_part_number, quantity in price_list:
            price_list += GetPrice.run(lcsc_part_number, quantity)

        return [
            (edgir.LocalPath(), str(total_price))
        ]
    