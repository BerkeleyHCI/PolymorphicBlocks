import csv
import os
from typing import List, Tuple, Dict, Optional

from .. import edgir
from ..abstract_parts import *


class PartQuantityTransform(TransformUtil.Transform):
    def __init__(self, design: CompiledDesign):
        self.design = design
        self.part_list: Dict[str, int] = {}

    def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
        lcsc_part_number = self.design.get_value(context.path.to_tuple() + ('lcsc_part',))
        part = self.design.get_value(context.path.to_tuple() + ('fp_part',))

        if lcsc_part_number:  # non-None (value exists) and nonempty
            assert isinstance(lcsc_part_number, str)
            index = lcsc_part_number
        elif part:  # TODO this is a temporary hacky fix, to support parts not in JLC's library
            assert isinstance(part, str)
            if part.startswith("PinHeader"):
                return  # TODO headers ignored - not supported for now
            index = part
        else:
            return  # ignored, not a part, eg tooling holes and jumper pads
        self.part_list[index] = self.part_list.get(index, 0) + 1

    def run(self) -> Dict[str, int]:
        self.transform_design(self.design.design)
        return self.part_list


class GeneratePrice(BaseBackend):
    # part_number -> price string (pre-parsing everything takes a long time, especially since most rows aren't used)
    PRICE_TABLE: Dict[str, str] = {}

    @staticmethod
    def price_list_from_str(full_price_list: str) -> List[Tuple[int, float]]:
        # returns as [ [lower-bound_1, price_1], [lower-bound_2 (and the previous upperbound), price_2], ... ]
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
        return sorted(value)

    @classmethod
    def get_price_table(cls) -> Dict[str, str]:
        if not GeneratePrice.PRICE_TABLE:
            main_table = PartsTable.with_source_dir(['JLCPCB SMT Parts Library(20220419).csv'], 'resources')[0]
            if not os.path.exists(main_table):
                main_table = PartsTable.with_source_dir(['Pruned_JLCPCB SMT Parts Library(20220419).csv'], 'resources')[0]
            parts_tables = [main_table]

            supplementary_table = PartsTable.with_source_dir(['supplemental_price.csv'], 'resources')[0]
            if os.path.exists(supplementary_table):
                parts_tables.append(supplementary_table)

            for table in parts_tables:
                with open(table, 'r', newline='', encoding='gb2312') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    next(csv_reader)    # to skip the header
                    for row in csv_reader:
                        full_price_list = row[10]
                        if not full_price_list.strip():  # missing price, discard row
                            continue
                        GeneratePrice.PRICE_TABLE[row[0]] = full_price_list
        return GeneratePrice.PRICE_TABLE

    def generate_price(self, lcsc_part_number: str, quantity: int) -> Optional[float]:
        full_price_str = self.get_price_table().get(lcsc_part_number, None)
        if full_price_str is None:
            return None
        full_price_list = self.price_list_from_str(full_price_str)
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
            price = self.generate_price(lcsc_part_number, quantity)
            if price is not None:
                total_price += price
            else:
                print(lcsc_part_number + " is missing from the price list.")

        return [
            (edgir.LocalPath(), str(round(total_price, 2)))
        ]
