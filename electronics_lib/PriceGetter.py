import sys
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
    PRICE_TABLE: Dict[str, List[Tuple[int, float]]] = {}

    @classmethod
    def get_price_table(cls) -> Dict[str, List[Tuple[int, float]]]:
        if not GeneratePrice.PRICE_TABLE:
            current_path = os.getcwd()
            parts_library = current_path + "\PolymorphicBlocks\electronics_lib\\resources\Pruned_JLCPCB SMT Parts Library(20220419).csv"
            with open(parts_library, 'r', newline='') as csv_file:
                csv_reader = csv.reader(csv_file, dialect='excel')
                next(csv_reader)
                for row in csv_reader:
                    full_price_list = row[10]
                    if full_price_list == " ":
                        print("Part " + row[0] + " is missing from the price list.")
                        value = ([(0, 0.0), (20000, 0.0)])
                    else:
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
                    GeneratePrice.PRICE_TABLE[row[0]] = value
        return GeneratePrice.PRICE_TABLE

    def generate_price(self, lcsc_part_number: str, quantity: int) -> float:
        if lcsc_part_number in GeneratePrice.PRICE_TABLE:
            full_price_list = GeneratePrice.PRICE_TABLE[lcsc_part_number]
            for i in range(len(full_price_list)):
                if i == len(full_price_list) - 1:   # if you reached the last group
                    return quantity * (full_price_list[i])[1]
                if quantity < (full_price_list[i + 1])[0]:
                    return (quantity * full_price_list[i])[1]
        else:
            print(lcsc_part_number + " is missing from the price list.")
            return 0

    def run(self, design: CompiledDesign, args=None) -> List[Tuple[edgir.LocalPath, str]]:
        assert not args
        price_list = PriceTransform(design).run()
        total_price = 0
        self.get_price_table()
        for lcsc_part_number in price_list:
            quantity = price_list[lcsc_part_number]
            print(lcsc_part_number + ": quantity = " + str(quantity))
            total_price += round(self.generate_price(lcsc_part_number, quantity), 2)
        print("total price: " + str(total_price))
        return [
            (edgir.LocalPath(), str(total_price))
        ]
