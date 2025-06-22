import unittest

from . import *
from .NetlistGenerator import Netlist, NetBlock
from .SvgPcbBackend import arrange_netlist


class PartPlacerTestCase(unittest.TestCase):
    def test_placement(self):
        u1 = NetBlock(
            footprint="Package_QFP:LQFP-48-1EP_7x7mm_P0.5mm_EP3.6x3.6mm", refdes="U1", part="", value="",
            full_path=TransformUtil.Path.empty().append_block("U1"), path=[], class_path=[]
        )
        r1 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric", refdes="R1", part="", value="",
            full_path=TransformUtil.Path.empty().append_block("R1"), path=[], class_path=[]
        )
        r2 = NetBlock(
            footprint="Resistor_SMD:R_0603_1608Metric", refdes="R2", part="", value="",
            full_path=TransformUtil.Path.empty().append_block("R2"), path=[], class_path=[]
        )
        netlist = Netlist(
            blocks=[u1, r1, r2],
            nets=[]
        )
        arranged = arrange_netlist(netlist)
        print(arranged)
