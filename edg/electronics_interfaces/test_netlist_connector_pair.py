import unittest

from typing_extensions import override

from ..electronics_model import *
from ..electronics_model.NetlistGenerator import NetlistTransform
from .VoltagePorts import VoltageSink
from .test_netlist import TestFakeSource, TestFakeSink, net_block, Net, net_pin


class SinkExteriorConnector(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(Passive.empty())  # must remain empty
        self.neg = self.Port(Passive.empty())

    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(  # only this footprint shows up
            "J",
            "Connector_PinSocket_2.54mm:PinSocket_1x02_P2.54mm_Vertical",
            {"1": self.pos, "2": self.neg},
        )


class SinkInternalConnector(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(Passive.empty())  # must remain empty
        self.neg = self.Port(Passive.empty())

    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(  # only this footprint shows up
            "J",
            "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
            {"1": self.pos, "2": self.neg},
        )


class SinkConnectorPair(SubboardConnectorPair):
    def __init__(self) -> None:
        super().__init__()

        self.ext = self.Block(SinkExteriorConnector(), external=True)
        self.int = self.Block(SinkInternalConnector())
        self.pos = self.Export(self.int.pos)
        self.neg = self.Export(self.int.neg)
        self.export_tap(self.pos, self.ext.pos)
        self.export_tap(self.neg, self.ext.neg)


class SinkConnectorPairBlock(SubboardBlock):
    """Subboard block with a connector pair and internal circuits."""

    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(VoltageSink.empty())
        self.neg = self.Port(VoltageSink.empty())

    @override
    def contents(self) -> None:
        super().contents()

        # these blocks are part of the sub-board
        self.inner1 = self.Block(TestFakeSink())
        self.inner2 = self.Block(TestFakeSink())
        self.vpos = self.connect(self.pos, self.inner1.pos, self.inner2.pos)
        self.gnd = self.connect(self.neg, self.inner1.neg, self.inner2.neg)

        # these define the external interface block
        self.conn = self.Block(SinkConnectorPair(), external=True)
        self.export_tap(self.pos.net, self.conn.pos)
        self.export_tap(self.neg.net, self.conn.neg)


class TestConnectorPairCircuit(DesignTop):
    @override
    def contents(self) -> None:
        super().contents()

        self.source = self.Block(TestFakeSource())
        self.sink = self.Block(SinkConnectorPairBlock())

        self.vpos = self.connect(self.source.pos, self.sink.pos)
        self.gnd = self.connect(self.source.neg, self.sink.neg)


class NetlistConnectorPairTestCase(unittest.TestCase):
    def test_subboard_netlist(self) -> None:
        compiled = ScalaCompiler.compile(TestConnectorPairCircuit)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        board_netlists = NetlistTransform(compiled).run()

        top_net = board_netlists[TransformUtil.Path.empty()]

        self.assertIn(
            net_block(
                "Connector_PinSocket_2.54mm:PinSocket_1x02_P2.54mm_Vertical",
                "J1",
                "",
                "",
                ["sink", "conn", "ext"],
                [
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkConnectorPairBlock",
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkConnectorPair",
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkExteriorConnector",
                ],
            ),
            top_net.blocks,
        )
        self.assertEqual(len(top_net.blocks), 2)  # should only generate top-level source and sink

        self.assertIn(
            Net(
                "vpos",
                [
                    net_pin(["source"], "1"),
                    net_pin(["sink", "conn", "ext"], "1"),
                ],
                [
                    TransformUtil.Path.empty().append_block("source").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink", "conn").append_port("pos"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "int").append_port("pos"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "ext").append_port("pos"),
                ],
            ),
            top_net.nets,
        )
        self.assertIn(
            Net(
                "gnd",
                [net_pin(["source"], "2"), net_pin(["sink", "conn", "ext"], "2")],
                [
                    TransformUtil.Path.empty().append_block("source").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink", "conn").append_port("neg"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "int").append_port("neg"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "ext").append_port("neg"),
                ],
            ),
            top_net.nets,
        )
        self.assertEqual(len(top_net.nets), 2)  # ensure empty nets pruned

        inner_net = board_netlists[TransformUtil.Path.empty().append_block("sink")]
        self.assertIn(
            net_block(
                "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
                "J2",
                "",
                "",
                ["sink", "conn", "int"],
                [
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkConnectorPairBlock",
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkConnectorPair",
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkInternalConnector",
                ],
            ),
            inner_net.blocks,
        )
        self.assertIn(
            net_block(
                "Resistor_SMD:R_0603_1608Metric",
                "R1",
                "",
                "1k",
                ["sink", "inner1"],
                [
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkConnectorPairBlock",
                    "edg.electronics_interfaces.test_netlist.TestFakeSink",
                ],
            ),
            inner_net.blocks,
        )
        self.assertIn(
            net_block(
                "Resistor_SMD:R_0603_1608Metric",
                "R2",
                "",
                "1k",
                ["sink", "inner2"],
                [
                    "edg.electronics_interfaces.test_netlist_connector_pair.SinkConnectorPairBlock",
                    "edg.electronics_interfaces.test_netlist.TestFakeSink",
                ],
            ),
            inner_net.blocks,
        )
        self.assertEqual(len(inner_net.blocks), 3)

        self.assertIn(
            Net(
                "sink.vpos",
                [
                    net_pin(["sink", "inner1"], "1"),
                    net_pin(["sink", "inner2"], "1"),
                    net_pin(["sink", "conn", "int"], "1"),
                ],
                [
                    TransformUtil.Path.empty().append_block("sink").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink", "conn").append_port("pos"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "int").append_port("pos"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "ext").append_port("pos"),
                    TransformUtil.Path.empty().append_block("sink", "inner1").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink", "inner2").append_port("pos", "net"),
                ],
            ),
            inner_net.nets,
        )
        self.assertIn(
            Net(
                "sink.gnd",
                [
                    net_pin(["sink", "inner1"], "2"),
                    net_pin(["sink", "inner2"], "2"),
                    net_pin(["sink", "conn", "int"], "2"),
                ],
                [
                    TransformUtil.Path.empty().append_block("sink").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink", "conn").append_port("neg"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "int").append_port("neg"),
                    TransformUtil.Path.empty().append_block("sink", "conn", "ext").append_port("neg"),
                    TransformUtil.Path.empty().append_block("sink", "inner1").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink", "inner2").append_port("neg", "net"),
                ],
            ),
            inner_net.nets,
        )
        self.assertEqual(len(inner_net.nets), 2)  # ensure empty nets pruned
