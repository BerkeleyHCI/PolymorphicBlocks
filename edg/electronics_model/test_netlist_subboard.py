import unittest

from typing_extensions import override

from .NetlistGenerator import NetlistTransform
from .. import FootprintBlock, DesignTop, ScalaCompiler, RefdesRefinementPass
from ..core import TransformUtil
from .test_netlist import TestFakeSource, TestFakeSink, NetBlock, Net, NetPin
from . import SubboardBlock, VoltageSink


class SinkSubboardExterior(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(VoltageSink.empty())  # must remain empty
        self.neg = self.Port(VoltageSink.empty())

    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(  # only this footprint shows up
            "R",
            "Resistor_SMD:R_0603_1608Metric",
            {"1": self.pos, "2": self.neg},
            value="200",
        )


class SinkSubboardBlock(SubboardBlock):
    """Subboard block with a single footprint for two internal sinks whose footprints are ignored."""

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
        self.wrapper = self.Block(SinkSubboardExterior(), external=True)
        self.export_tap(self.pos, self.wrapper.pos)
        self.export_tap(self.neg, self.wrapper.neg)


class TestSubboardCircuit(DesignTop):
    @override
    def contents(self) -> None:
        super().contents()

        self.source = self.Block(TestFakeSource())
        self.sink = self.Block(SinkSubboardBlock())

        self.vpos = self.connect(self.source.pos, self.sink.pos)
        self.gnd = self.connect(self.source.neg, self.sink.neg)


class NetlistSubboardTestCase(unittest.TestCase):
    def test_subboard_netlist(self) -> None:
        compiled = ScalaCompiler.compile(TestSubboardCircuit)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        board_netlists = NetlistTransform(compiled).run()

        top_net = board_netlists[TransformUtil.Path.empty()]

        self.assertIn(
            NetBlock(
                "Resistor_SMD:R_0603_1608Metric",
                "R3",
                "",
                "200",
                ["sink", "wrapper"],
                [
                    "edg.electronics_model.test_netlist_subboard.SinkSubboardBlock",
                    "edg.electronics_model.test_netlist_subboard.SinkSubboardExterior",
                ],
            ),
            top_net.blocks,
        )
        self.assertEqual(len(top_net.blocks), 2)  # should only generate top-level source and sink

        self.assertIn(
            Net(
                "vpos",
                [NetPin(["source"], "1"), NetPin(["sink", "wrapper"], "1")],  # ensure extraneous nets not generated
                [
                    TransformUtil.Path.empty().append_block("source").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink", "wrapper").append_port("pos", "net"),
                ],
            ),
            top_net.nets,
        )
        self.assertIn(
            Net(
                "gnd",
                [NetPin(["source"], "2"), NetPin(["sink", "wrapper"], "2")],
                [
                    TransformUtil.Path.empty().append_block("source").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink", "wrapper").append_port("neg", "net"),
                ],
            ),
            top_net.nets,
        )
        self.assertEqual(len(top_net.nets), 2)  # ensure empty nets pruned

        inner_net = board_netlists[TransformUtil.Path.empty().append_block("sink")]
        self.assertIn(
            NetBlock(
                "Resistor_SMD:R_0603_1608Metric",
                "R1",
                "",
                "1k",
                ["sink", "inner1"],
                [
                    "edg.electronics_model.test_netlist_subboard.SinkSubboardBlock",
                    "edg.electronics_model.test_netlist.TestFakeSink",
                ],
            ),
            inner_net.blocks,
        )
        self.assertIn(
            NetBlock(
                "Resistor_SMD:R_0603_1608Metric",
                "R2",
                "",
                "1k",
                ["sink", "inner2"],
                [
                    "edg.electronics_model.test_netlist_subboard.SinkSubboardBlock",
                    "edg.electronics_model.test_netlist.TestFakeSink",
                ],
            ),
            inner_net.blocks,
        )
        self.assertEqual(len(inner_net.blocks), 2)

        self.assertIn(
            Net(
                "sink.inner1.pos",
                [NetPin(["sink", "inner1"], "1"), NetPin(["sink", "inner2"], "1")],
                [
                    TransformUtil.Path.empty().append_block("sink", "inner1").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink", "inner2").append_port("pos", "net"),
                ],
            ),
            inner_net.nets,
        )
        self.assertIn(
            Net(
                "sink.inner1.neg",
                [NetPin(["sink", "inner1"], "2"), NetPin(["sink", "inner2"], "2")],
                [
                    TransformUtil.Path.empty().append_block("sink", "inner1").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink", "inner2").append_port("neg", "net"),
                ],
            ),
            inner_net.nets,
        )
        self.assertEqual(len(inner_net.nets), 2)  # ensure empty nets pruned
