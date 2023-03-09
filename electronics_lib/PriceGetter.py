from typing import List, Tuple, Dict, Optional

import edgir
from edg_core import BaseBackend, CompiledDesign, TransformUtil
import csv

from electronics_abstract_parts import PartsTable


class PartQuantityTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.part_list: Dict[str, int] = {}

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        lcsc_part_number: Optional[str] = str(self.design.get_value(context.path.to_tuple() + ('lcsc_part',)))
        if lcsc_part_number != "None":
            if lcsc_part_number not in self.part_list:
                self.part_list[str(lcsc_part_number)] = 0
            self.part_list[str(lcsc_part_number)] += 1

    def run(self) -> Dict[str, int]:
        self.transform_design(self.design.design)
        return self.part_list


class GeneratePrice(BaseBackend):
    # part_number -> [ [lower-bound_1, price_1], [lower-bound_2 (and the previous upperbound), price_2], ... ]
    PRICE_TABLE: Dict[str, List[Tuple[int, float]]] = {}

    @classmethod
    def get_price_table(cls) -> Dict[str, List[Tuple[int, float]]]:
        if not GeneratePrice.PRICE_TABLE:
            parts_library = str(PartsTable.with_source_dir(['Pruned_JLCPCB SMT Parts Library(20220419).csv'],
                                                           'resources')[0])
            with open(parts_library, 'r', newline='', encoding='gb2312') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)    # to skip the header
                for row in csv_reader:
                    full_price_list = row[10]
                    if not full_price_list.strip():
                        print(row[0] + " is missing from the price list.")
                        continue
                    price_and_quantity_groups = full_price_list.split(',')
                    value: List[Tuple[int, float]] = []
                    for price_and_quantity in price_and_quantity_groups:
                        price_and_quantity_list = price_and_quantity.split(':')
                        # this has to be 2 because it will split the quantity range & the cost:
                        assert len(price_and_quantity_list) == 2
                        quantity_range = price_and_quantity_list[0].split('-')
                        # when the length is 1, it's the minimum quantity for a price break (ex: 15000+)
                        assert len(quantity_range) == 1 or len(quantity_range) == 2
                        value.append((int(quantity_range[0]), float(price_and_quantity_list[1])))

                    # sorts each value for PRICE_TABLE by lower-bounds, which is the first int in the Tuple:
                    GeneratePrice.PRICE_TABLE[row[0]] = sorted(value)
        return GeneratePrice.PRICE_TABLE

    def generate_price(self, lcsc_part_number: str, quantity: int) -> float:
        full_price_list = self.get_price_table().get(lcsc_part_number, [(0, 0.0)])
        if full_price_list == [(0, 0.0)]:
            print(lcsc_part_number + " is missing from the price list.")
            return 0
        temp_price = full_price_list[0][1]  # sets price to initial amount (the lowest quantity bracket)
        for (minimum_quantity, price) in full_price_list:
            if quantity >= minimum_quantity:
                temp_price = price
        return quantity * temp_price

    def run(self, design: CompiledDesign, args=None) -> List[Tuple[edgir.LocalPath, str]]:
        assert not args
        price_list = PartQuantityTransform(design).run()
        total_price: float = 0
        for lcsc_part_number in price_list:
            quantity = price_list[lcsc_part_number]
            total_price += round(self.generate_price(lcsc_part_number, quantity), 2)
        return [
            (edgir.LocalPath(), str(total_price))
        ]
