# this class lives in electronics_abstract_parts since it requires the Resistor
import unittest

# to avoid re-defining NetBlock, this makes specific imports instead of 'from . import *'
from ..core import *
from ..electronics_model import Passive, FootprintBlock
from ..electronics_interfaces.test_netlist import NetlistTestCase, Net, net_pin, net_block
from ..electronics_interfaces.test_kicad_import_blackbox import KiCadBlackboxBlock
from .Resistor import Resistor


class PassiveDummy(Block):
    def __init__(self) -> None:
        super().__init__()
        self.port = self.Port(Passive(), [InOut])


class KiCadBlackboxTop(Block):
    def __init__(self) -> None:
        super().__init__()
        self.dut = self.Block(KiCadBlackboxBlock())
        (self.dummypwr,), _ = self.chain(self.dut.pwr, self.Block(PassiveDummy()))
        (self.dummygnd,), _ = self.chain(self.dut.gnd, self.Block(PassiveDummy()))
        (self.dummyout,), _ = self.chain(self.dut.out, self.Block(PassiveDummy()))


class DummyResistor(Resistor, FootprintBlock):
    def __init__(self) -> None:
        super().__init__(Range.all())
        self.footprint(
            "R",
            "Resistor_SMD:R_0603_1608Metric",
            {
                "1": self.a,
                "2": self.b,
            },
        )


class KiCadImportBlackboxTestCase(unittest.TestCase):
    def test_netlist(self) -> None:
        net = NetlistTestCase.generate_single_net(
            KiCadBlackboxTop,
            refinements=Refinements(
                class_refinements=[
                    (Resistor, DummyResistor),
                ]
            ),
        )
        # note, dut pruned out from paths since it's the only block in the top-level
        self.assertIn(
            Net(
                "dut.pwr",
                [net_pin(["dut", "U1"], "1")],
                [
                    TransformUtil.Path.empty().append_block("dut").append_port("pwr"),
                    TransformUtil.Path.empty().append_block("dut", "U1").append_port("ports", "1"),
                    TransformUtil.Path.empty().append_block("dummypwr").append_port("port"),
                ],
            ),
            net.nets,
        )
        self.assertIn(
            Net(
                "dut.gnd",
                [net_pin(["dut", "U1"], "3")],
                [
                    TransformUtil.Path.empty().append_block("dut").append_port("gnd"),
                    TransformUtil.Path.empty().append_block("dut", "U1").append_port("ports", "3"),
                    TransformUtil.Path.empty().append_block("dummygnd").append_port("port"),
                ],
            ),
            net.nets,
        )
        self.assertIn(
            Net(
                "dut.node",
                [net_pin(["dut", "U1"], "2"), net_pin(["dut", "res"], "1")],
                [
                    TransformUtil.Path.empty().append_block("dut", "U1").append_port("ports", "2"),
                    TransformUtil.Path.empty().append_block("dut", "res").append_port("a"),
                ],
            ),
            net.nets,
        )
        self.assertIn(
            Net(
                "dut.out",
                [net_pin(["dut", "res"], "2")],
                [
                    TransformUtil.Path.empty().append_block("dut").append_port("out"),
                    TransformUtil.Path.empty().append_block("dut", "res").append_port("b"),
                    TransformUtil.Path.empty().append_block("dummyout").append_port("port"),
                ],
            ),
            net.nets,
        )
        self.assertIn(
            net_block(
                "Package_TO_SOT_SMD:SOT-23",
                "U1",
                # expected value is wonky because netlisting combines part and value
                "Sensor_Temperature:MCP9700AT-ETT",
                "MCP9700AT-ETT",
                ["dut", "U1"],
                [
                    "edg.electronics_interfaces.test_kicad_import_blackbox.KiCadBlackboxBlock",
                    "edg.electronics_model.KiCadSchematicBlock.KiCadBlackbox",
                ],
            ),
            net.blocks,
        )
        self.assertIn(
            net_block(
                "Symbol:Symbol_ESD-Logo_CopperTop",
                "SYM1",
                # expected value is wonky because netlisting combines part and value
                "Graphic:SYM_ESD_Small",
                "SYM_ESD_Small",
                ["dut", "SYM1"],
                [
                    "edg.electronics_interfaces.test_kicad_import_blackbox.KiCadBlackboxBlock",
                    "edg.electronics_model.KiCadSchematicBlock.KiCadBlackbox",
                ],
            ),
            net.blocks,
        )
        self.assertIn(
            net_block(
                "Resistor_SMD:R_0603_1608Metric",
                "R1",
                "",
                "",
                ["dut", "res"],
                [
                    "edg.electronics_interfaces.test_kicad_import_blackbox.KiCadBlackboxBlock",
                    "edg.abstract_parts.test_kicad_import_netlist.DummyResistor",
                ],
            ),
            net.blocks,
        )
