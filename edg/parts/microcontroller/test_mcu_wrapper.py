import unittest
from typing_extensions import override

from .Esp32c3 import Xiao_Esp32c3
from ...vendor_parts.generic import GenericChipResistor
from ...circuits import *

# these tests use the Xiao ESP32C3 since it has few usable IOs and is one of the more complex wrappers


class OverallocateTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.io, [Power]),
            ImplicitConnect(self.gnd.io, [Common]),
        ) as imp:
            self.dut = imp.Block(Xiao_Esp32c3())

            self.ios = ElementDict[DummyDigitalSource]()
            for i in range(7):  # device only has 6 IOs
                self.ios[i] = self.Block(DummyDigitalSource()).connected(self.dut.gpio.request(str(i)))


class FullMcuTest(DesignTop):
    # this uses all the pins, to catch potential automatic allocation errors
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.io, [Power]),
            ImplicitConnect(self.gnd.io, [Common]),
        ) as imp:
            self.dut = imp.Block(Xiao_Esp32c3())

            self.ios = ElementDict[DummyDigitalSource]()
            for i in range(6):
                self.ios[i] = self.Block(DummyDigitalSource()).connected(self.dut.gpio.request(str(i)))


class BaseMcuTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.io, [Power]),
            ImplicitConnect(self.gnd.io, [Common]),
        ) as imp:
            self.dut = imp.Block(Xiao_Esp32c3())

            self.ios = ElementDict[DummyDigitalSource]()
            for i in range(2):
                self.ios[i] = self.Block(DummyDigitalSource()).connected(self.dut.gpio.request(str(i)))


class AssignedPinsTest(BaseMcuTest):
    @override
    def refinements(self) -> Refinements:
        return Refinements(instance_values=[(["dut", "pin_assigns"], ["0=3", "1=5"])])


class AssignedInvalidNameTest(BaseMcuTest):
    @override
    def refinements(self) -> Refinements:
        return Refinements(instance_values=[(["dut", "pin_assigns"], ["0=GPIO0"])])


class AssignedInvalidPinNumberTest(BaseMcuTest):
    @override
    def refinements(self) -> Refinements:
        return Refinements(instance_values=[(["dut", "pin_assigns"], ["0=16"])])  # in the IC but not module


class AssignedI2cTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.io, [Power]),
            ImplicitConnect(self.gnd.io, [Common]),
        ) as imp:
            self.dut = imp.Block(Xiao_Esp32c3())

            self.i2c = self.Block(I2cControllerBitBang())
            self.i2c_pull = imp.Block(I2cPullup())
            self.connect(self.i2c.scl, self.dut.gpio.request("0"))
            self.connect(self.i2c.sda, self.dut.gpio.request("1"))
            self.connect(self.i2c.i2c, self.i2c_pull.i2c, self.dut.i2c_target.request("i2c"))

    @override
    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[(Resistor, GenericChipResistor)],
            instance_values=[(["dut", "pin_assigns"], ["i2c.sda=5", "i2c.scl=6"])],
        )


class McuWrapperTestCase(unittest.TestCase):
    def test_overallocate(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(OverallocateTest)

    def test_auto_pins(self) -> None:
        ScalaCompiler.compile(FullMcuTest)  # check that it compiles without error

    def test_assigned_pins(self) -> None:
        compiled = ScalaCompiler.compile(AssignedPinsTest)
        self.assertEqual(compiled.get_value(["dut", "actual_pin_assigns"]), ["0=MTMS, 3", "1=MTCK, 5"])
        self.assertEqual(compiled.get_value(["dut", "model", "actual_pin_assigns"]), ["0=MTMS, 9", "1=MTCK, 12"])

    def test_assigned_invalid_name(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(AssignedInvalidNameTest)

    def test_assigned_invalid_pinnumber(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(AssignedInvalidPinNumberTest)

    def test_assigned_i2c(self) -> None:
        compiled = ScalaCompiler.compile(AssignedI2cTest)
        self.assertEqual(
            compiled.get_value(["dut", "actual_pin_assigns"]),
            ["i2c=I2C_T", "i2c.scl=MTDO, 6", "i2c.sda=MTCK, 5", "0=GPIO3, 2", "1=MTMS, 3"],
        )
        self.assertEqual(
            compiled.get_value(["dut", "model", "actual_pin_assigns"]),
            ["i2c=I2C_T", "i2c.scl=MTDO, 13", "i2c.sda=MTCK, 12", "0=GPIO3, 8", "1=MTMS, 9"],
        )
