import unittest

from typing_extensions import override

from ..abstract_parts import *
from .OpampCircuits import Amplifier


class TestOpamp(Opamp):
    @override
    def contents(self) -> None:
        super().contents()
        self.pwr.init_from(VoltageSink())
        self.gnd.init_from(Ground())
        self.inp.init_from(AnalogSink())
        self.inn.init_from(AnalogSink())
        self.out.init_from(AnalogSource())


class TestResistor(Resistor):
    @override
    def contents(self) -> None:
        super().contents()
        self.assign(self.actual_resistance, self.resistance)


class AmplifierTestTop(Block):
    def __init__(self) -> None:
        super().__init__()
        self.dut = self.Block(Amplifier(amplification=Range.from_tolerance(2, 0.05)))
        self.dummygnd = self.Block(DummyGround()).connected(self.dut.gnd)
        self.dummypwr = self.Block(DummyVoltageSource()).connected(self.dut.pwr)
        self.dummyin = self.Block(DummyAnalogSource()).connected(self.dut.input)
        self.dummyref = self.Block(DummyAnalogSource()).connected(self.dut.reference)
        self.dummyout = self.Block(DummyAnalogSink()).connected(self.dut.output)


class OpampCircuitTest(unittest.TestCase):
    def test_opamp_amplifier(self) -> None:
        compiled = ScalaCompiler.compile(
            AmplifierTestTop,
            refinements=Refinements(
                class_refinements=[
                    (Opamp, TestOpamp),
                    (Resistor, TestResistor),
                ]
            ),
        )

        self.assertEqual(compiled.get_value(["dut", "r1", "resistance"]), Range.from_tolerance(100e3, 0.01))
        self.assertEqual(compiled.get_value(["dut", "r2", "resistance"]), Range.from_tolerance(100e3, 0.01))
