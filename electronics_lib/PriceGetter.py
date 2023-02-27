from typing import List, Tuple, Dict

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil
import os
import csv


class PriceTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.part_list: Dict[str, int] = {}

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        lcsc_part_number: str = self.design.get_value(context.path.to_tuple() + ('lcsc_part',)) or None
        if lcsc_part_number is not None:
            if lcsc_part_number not in self.part_list:
                self.part_list[lcsc_part_number] = 0
            self.part_list[lcsc_part_number] += 1

    def run(self) -> Dict[str, int]:
        self.transform_design(self.design.design)
        return self.part_list


class GeneratePrice(BaseBackend):
    # part_number -> [ [lower-bound_1, price_1], [lower-bound_2 (and the previous upperbound), price_2], ... ]
    PRICE_TABLE = Dict[str, List[Tuple[int, float]]] = None

    @classmethod
    def get_price_table(cls) -> Dict[str, List[Tuple[int, float]]]:
        if GeneratePrice.PRICE_TABLE is None:
            cur_path = os.path.dirname(__file__)
            parts_library = os.path.relpath('resources/Pruned_JLCPCB SMT Parts Library(20220419).csv', cur_path)
            with open(parts_library, 'r', newline='') as csv_file:
                csv_reader = csv.DictReader(csv_file, 'r')
                for row in csv_reader:
                    full_price_list = row['Price']
                    price_and_quantity_groups = full_price_list.split(',')
                    value: List[Tuple[int, float]] = []
                    for price_and_quantity in price_and_quantity_groups:
                        price_and_quantity_list = price_and_quantity.split(':')
                        assert len(price_and_quantity_list) == 2
                        quantity_range = price_and_quantity_list[0].split('-')
                        assert len(quantity_range) == 1 or len(quantity_range) == 2
                        value.append((int(quantity_range[0]), float(price_and_quantity_list[1])))

                    # sorts each value for PRICE_TABLE by lower-bounds, which is the first int in the Tuple:
                    sorted(value)
                    GeneratePrice.PRICE_TABLE[row['LCSC Part']] = value
        return GeneratePrice.PRICE_TABLE

    def generate_price(self, lcsc_part_number: str, quantity: int) -> float:
        full_price_list = GeneratePrice.PRICE_TABLE[lcsc_part_number]
        for i in range(len(full_price_list)):
            if i == len(full_price_list) - 1:   # if you reached the last group
                return quantity * (full_price_list[i])[1]
            if quantity < (full_price_list[i + 1])[0]:
                return (quantity * full_price_list[i])[1]

    def run(self, design: CompiledDesign, args=None) -> List[Tuple[edgir.LocalPath, str]]:
        assert not args
        price_list = PriceTransform(design).run()
        total_price = 0
        self.get_price_table()
        for lcsc_part_number, quantity in price_list:
            total_price += self.generate_price(lcsc_part_number, quantity)

        return [
            (edgir.LocalPath(), str(total_price))
        ]