import unittest

from typing_extensions import override

from .. import FootprintBlock, DesignTop
from ..core import Block, TransformUtil
from .test_netlist import NetlistTestCase, TestFakeSource, TestFakeSink, NetBlock, Net, NetPin
from . import SubboardBlock, WrapperSubboardBlock, VoltageSink, Passive


class SinkWrapperExterior(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(VoltageSink.empty())  # must remain empty
        self.neg = self.Port(VoltageSink.empty())

    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(  # only this footprint shows up
            "L",
            "Inductor_SMD:L_0603_1608Metric",  # distinct footprint and value from internal blocks
            {"1": self.pos, "2": self.neg},
            value="100",
        )


class SinkWrapperBlock(WrapperSubboardBlock):
    """Wrapper block with a single footprint for two internal sinks whose footprints are ignored."""

    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(VoltageSink.empty())
        self.neg = self.Port(VoltageSink.empty())

    @override
    def contents(self) -> None:
        super().contents()

        # these define the modeling and are internal
        self.model1 = self.Block(TestFakeSink())
        self.model2 = self.Block(TestFakeSink())
        self.vpos = self.connect(self.pos, self.model1.pos, self.model2.pos)
        self.gnd = self.connect(self.neg, self.model1.neg, self.model2.neg)

        # these define the external interface block
        self.wrapper = self.Block(SinkWrapperExterior(), external=True)
        self.export_tap(self.pos, self.wrapper.pos)
        self.export_tap(self.neg, self.wrapper.neg)


class TestWrapperCircuit(DesignTop):
    @override
    def contents(self) -> None:
        super().contents()

        self.source = self.Block(TestFakeSource())
        self.sink = self.Block(SinkWrapperBlock())

        self.vpos = self.connect(self.source.pos, self.sink.pos)
        self.gnd = self.connect(self.source.neg, self.sink.neg)


class SinkWrapperPassiveExterior(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(Passive.empty())  # must remain empty
        self.neg = self.Port(Passive.empty())

    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(  # only this footprint shows up
            "L",
            "Inductor_SMD:L_0603_1608Metric",  # distinct footprint and value from internal blocks
            {"1": self.pos, "2": self.neg},
            value="100",
        )


class SinkWrapperPassiveBlock(WrapperSubboardBlock):
    """Wrapper block that taps the passive sub-port on its external port."""

    def __init__(self) -> None:
        super().__init__()

        self.pos = self.Port(VoltageSink.empty())
        self.neg = self.Port(VoltageSink.empty())

    @override
    def contents(self) -> None:
        super().contents()

        # these define the modeling and are internal
        self.model1 = self.Block(TestFakeSink())
        self.model2 = self.Block(TestFakeSink())
        self.vpos = self.connect(self.pos, self.model1.pos, self.model2.pos)
        self.gnd = self.connect(self.neg, self.model1.neg, self.model2.neg)

        # these define the external interface block
        self.wrapper = self.Block(SinkWrapperPassiveExterior(), external=True)
        self.export_tap(self.pos.net, self.wrapper.pos)
        self.export_tap(self.neg.net, self.wrapper.neg)


class TestWrapperPassiveCircuit(DesignTop):
    @override
    def contents(self) -> None:
        super().contents()

        self.source = self.Block(TestFakeSource())
        self.sink = self.Block(SinkWrapperPassiveBlock())

        self.vpos = self.connect(self.source.pos, self.sink.pos)
        self.gnd = self.connect(self.source.neg, self.sink.neg)


class NetlistWrapperTestCase(unittest.TestCase):
    def test_wrapper_netlist(self) -> None:
        net = NetlistTestCase.generate_net(TestWrapperCircuit)

        self.assertIn(
            NetBlock(
                "Inductor_SMD:L_0603_1608Metric",
                "L1",
                "",
                "100",
                ["sink", "wrapper"],
                [
                    "edg.electronics_model.test_netlist_subboard.SinkWrapperBlock",
                    "edg.electronics_model.test_netlist_subboard.SinkWrapperExterior",
                ],
            ),
            net.blocks,
        )
        self.assertEqual(len(net.blocks), 2)  # should only generate top-level source and sink

        self.assertEqual(len(net.nets), 2)  # ensure empty nets pruned
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
            net.nets,
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
            net.nets,
        )

    def test_wrapper_passive_netlist(self) -> None:
        net = NetlistTestCase.generate_net(TestWrapperPassiveCircuit)

        self.assertIn(
            NetBlock(
                "Inductor_SMD:L_0603_1608Metric",
                "L1",
                "",
                "100",
                ["sink", "wrapper"],
                [
                    "edg.electronics_model.test_netlist_subboard.SinkWrapperPassiveBlock",
                    "edg.electronics_model.test_netlist_subboard.SinkWrapperPassiveExterior",
                ],
            ),
            net.blocks,
        )
        self.assertEqual(len(net.blocks), 2)  # should only generate top-level source and sink

        self.assertEqual(len(net.nets), 2)  # ensure empty nets pruned
        self.assertIn(
            Net(
                "vpos",
                [NetPin(["source"], "1"), NetPin(["sink", "wrapper"], "1")],  # ensure extraneous nets not generated
                [
                    TransformUtil.Path.empty().append_block("source").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink", "wrapper").append_port("pos"),
                ],
            ),
            net.nets,
        )
        self.assertIn(
            Net(
                "gnd",
                [NetPin(["source"], "2"), NetPin(["sink", "wrapper"], "2")],
                [
                    TransformUtil.Path.empty().append_block("source").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink", "wrapper").append_port("neg"),
                ],
            ),
            net.nets,
        )
