import unittest
from typing_extensions import override

from .Rp2040 import Xiao_Rp2040
from ...circuits import *


class OverallocateTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.pwr, [Power]),
            ImplicitConnect(self.gnd.gnd, [Common]),
        ) as imp:
            self.dut = imp.Block(Xiao_Rp2040())

            self.ios = ElementDict[DummyDigitalSource]()
            for i in range(12):  # device only has 11 IOs
                self.ios[i] = self.Block(DummyDigitalSource())
                self.connect(self.ios[i].io, self.dut.gpio.request(str(i)))


class BaseMcuTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.pwr, [Power]),
            ImplicitConnect(self.gnd.gnd, [Common]),
        ) as imp:
            self.dut = imp.Block(Xiao_Rp2040())

            self.ios = ElementDict[DummyDigitalSource]()
            for i in range(2):
                self.ios[i] = self.Block(DummyDigitalSource())
                self.connect(self.ios[i].io, self.dut.gpio.request(str(i)))


class AutoPinsTest(BaseMcuTest):
    pass


class AssignedPinsTest(BaseMcuTest):
    @override
    def refinements(self) -> Refinements:
        return Refinements(instance_values=[(["dut", "pin_assigns"], ["0=1", "1=3"])])


class McuWrapperTestCase(unittest.TestCase):
    def test_overallocate(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(OverallocateTest)

    def test_auto_pins(self) -> None:
        compiled = ScalaCompiler.compile(AutoPinsTest)
        self.assertEqual(compiled.get_value(["dut", "actual_pin_assigns"]), ["0=7", "1=8"])
        self.assertEqual(compiled.get_value(["dut", "model", "actual_pin_assigns"]), ["0=GPIO0, 2", "1=GPIO1, 3"])

    def test_assigned_pins(self) -> None:
        compiled = ScalaCompiler.compile(AssignedPinsTest)
        self.assertEqual(compiled.get_value(["dut", "actual_pin_assigns"]), ["0=1", "1=3"])
        self.assertEqual(compiled.get_value(["dut", "model", "actual_pin_assigns"]), ["0=GPIO26, 38", "1=GPIO28, 40"])
