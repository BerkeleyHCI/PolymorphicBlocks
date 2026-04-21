import unittest
from csv import DictReader
from io import StringIO
from typing import Type, override

from .BomBackend import GenerateBom
from .NetlistGenerator import Netlist
from .RefdesRefinementPass import RefdesRefinementPass
from .test_netlist import TestBasicCircuit, TestMultisinkCircuit
from .CircuitBlock import FootprintBlock
from ..core import *


class TestPnpRotOffset(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "U",
            "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
            {},
            value="",
            pnp_rot=90.0,
            pnp_offset=(1.0, 2.0),
        )


class BomTestCase(unittest.TestCase):
    @staticmethod
    def generate_bom(design: Type[Block], refinements: Refinements = Refinements()) -> Netlist:
        compiled = ScalaCompiler.compile(design, refinements)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        return GenerateBom().run(compiled)

    def test_basic_bom(self) -> None:
        boms = self.generate_bom(TestBasicCircuit)
        assert len(boms) == 1
        f = StringIO(boms[0][1])
        bom_csv_reader = DictReader(f)
        bom_csv_dict = list(bom_csv_reader)
        self.assertEqual(bom_csv_dict[0]["Designator"], "C1")
        self.assertEqual(bom_csv_dict[0]["Footprint"], "Capacitor_SMD:C_0603_1608Metric")
        self.assertEqual(bom_csv_dict[0]["Quantity"], "1")
        self.assertEqual(bom_csv_dict[0]["PNP Rotation Offset"], "")  # unspecified
        self.assertEqual(bom_csv_dict[0]["PNP Offset Y"], "")  # unspecified
        self.assertEqual(bom_csv_dict[0]["PNP Offset X"], "")  # unspecified
        self.assertEqual(bom_csv_dict[1]["Designator"], "R1")
        self.assertEqual(bom_csv_dict[1]["Footprint"], "Resistor_SMD:R_0603_1608Metric")
        self.assertEqual(bom_csv_dict[1]["Quantity"], "1")
        self.assertEqual(bom_csv_dict[1]["PNP Rotation Offset"], "")  # unspecified
        self.assertEqual(bom_csv_dict[1]["PNP Offset Y"], "")  # unspecified
        self.assertEqual(bom_csv_dict[1]["PNP Offset X"], "")  # unspecified

    def test_multisink_bom(self) -> None:
        # test aggregation of similar components
        boms = self.generate_bom(TestMultisinkCircuit)
        assert len(boms) == 1
        f = StringIO(boms[0][1])
        bom_csv_reader = DictReader(f)
        bom_csv_dict = list(bom_csv_reader)
        self.assertEqual(bom_csv_dict[0]["Designator"], "C1")
        self.assertEqual(bom_csv_dict[0]["Footprint"], "Capacitor_SMD:C_0603_1608Metric")
        self.assertEqual(bom_csv_dict[0]["Quantity"], "1")
        self.assertEqual(bom_csv_dict[1]["Designator"], "R1,R2")
        self.assertEqual(bom_csv_dict[1]["Footprint"], "Resistor_SMD:R_0603_1608Metric")
        self.assertEqual(bom_csv_dict[1]["Quantity"], "2")

    def test_pnp_bom(self) -> None:
        # test aggregation of similar components
        boms = self.generate_bom(TestPnpRotOffset)
        assert len(boms) == 1
        f = StringIO(boms[0][1])
        bom_csv_reader = DictReader(f)
        bom_csv_dict = list(bom_csv_reader)
        self.assertEqual(bom_csv_dict[0]["Designator"], "U1")
        self.assertEqual(bom_csv_dict[0]["PNP Rotation Offset"], "90.0")
        self.assertEqual(bom_csv_dict[0]["PNP Offset X"], "1.0")
        self.assertEqual(bom_csv_dict[0]["PNP Offset Y"], "2.0")
