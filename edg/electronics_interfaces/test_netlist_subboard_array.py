# TODO this is in the electronics_interface package because it uses VoltageSink ports,
# but there should be a Passive-typed test in the electronics_model package

import unittest

from typing_extensions import override

from ..electronics_model import *
from .VoltagePorts import VoltageSink
from .test_netlist import NetlistTestCase, TestFakeSource, net_block, Net, net_pin


class TestFakeSinkArray(GeneratorBlock, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.ports = self.Port(Vector(VoltageSink()))
        self.generator_param(self.ports.requested())

    @override
    def generate(self) -> None:
        super().generate()
        pins = {}
        self.ports.defined()
        for port_name in self.get(self.ports.requested()):
            pins[port_name] = self.ports.append_elt(VoltageSink(), port_name)

        self.footprint("R", "Resistor_SMD:R_0603_1608Metric", pins, value="1k")  # load resistor


class SinkArrayWrapperExterior(GeneratorBlock, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.ports = self.Port(Vector(VoltageSink.empty()))  # must remain empty
        self.generator_param(self.ports.requested())

    @override
    def generate(self) -> None:
        super().generate()
        pins = {}
        self.ports.defined()
        for port_name in self.get(self.ports.requested()):
            pins[port_name] = self.ports.append_elt(VoltageSink.empty(), port_name)

        self.footprint(  # only this footprint shows up
            "L",
            "Inductor_SMD:L_0603_1608Metric",  # distinct footprint and value from internal blocks
            pins,
            value="100",
        )


class SinkArrayWrapperBlock(WrapperSubboardBlock):
    """Wrapper block with a single footprint for two internal sinks whose footprints are ignored."""

    def __init__(self) -> None:
        super().__init__()
        self.model = self.Block(TestFakeSinkArray())
        self.ports = self.Export(self.model.ports)

    @override
    def contents(self) -> None:
        super().contents()

        self.wrapper = self.Block(SinkArrayWrapperExterior(), external=True)
        self.export_tap(self.ports, self.wrapper.ports)


class TestArrayWrapperCircuit(DesignTop):
    @override
    def contents(self) -> None:
        super().contents()

        self.source = self.Block(TestFakeSource())
        self.sink = self.Block(SinkArrayWrapperBlock())

        self.vpos = self.connect(self.source.pos, self.sink.ports.request("1"))
        self.gnd = self.connect(self.source.neg, self.sink.ports.request("2"))


class NetlistArrayWrapperTestCase(unittest.TestCase):
    def test_wrapper_netlist(self) -> None:
        net = NetlistTestCase.generate_single_net(TestArrayWrapperCircuit)

        self.assertIn(
            net_block(
                "Inductor_SMD:L_0603_1608Metric",
                "L1",
                "",
                "100",
                ["sink", "wrapper"],
                [
                    "edg.electronics_interfaces.test_netlist_subboard_array.SinkArrayWrapperBlock",
                    "edg.electronics_interfaces.test_netlist_subboard_array.SinkArrayWrapperExterior",
                ],
            ),
            net.blocks,
        )
        self.assertEqual(len(net.blocks), 2)  # should only generate top-level source and sink

        self.assertIn(
            Net(
                "vpos",
                [net_pin(["source"], "1"), net_pin(["sink", "wrapper"], "1")],  # ensure extraneous nets not generated
                [
                    TransformUtil.Path.empty().append_block("source").append_port("pos", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("ports", "1", "net"),
                    TransformUtil.Path.empty().append_block("sink", "model").append_port("ports", "1", "net"),
                    TransformUtil.Path.empty().append_block("sink", "wrapper").append_port("ports", "1", "net"),
                ],
            ),
            net.nets,
        )
        self.assertIn(
            Net(
                "gnd",
                [net_pin(["source"], "2"), net_pin(["sink", "wrapper"], "2")],
                [
                    TransformUtil.Path.empty().append_block("source").append_port("neg", "net"),
                    TransformUtil.Path.empty().append_block("sink").append_port("ports", "2", "net"),
                    TransformUtil.Path.empty().append_block("sink", "model").append_port("ports", "2", "net"),
                    TransformUtil.Path.empty().append_block("sink", "wrapper").append_port("ports", "2", "net"),
                ],
            ),
            net.nets,
        )
        self.assertEqual(len(net.nets), 2)  # ensure empty nets pruned
