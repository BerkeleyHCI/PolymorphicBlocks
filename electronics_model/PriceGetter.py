import io
from typing import List, Tuple, Dict, NamedTuple

import edgir
import electronics_lib.resources
from edg_core import BaseBackend, CompiledDesign, TransformUtil
import os
import csv
import re


class GetPrice:
    def run(self, lcsc_part_number: str, quantity: int) -> float:
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
