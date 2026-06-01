import unittest
from typing_extensions import override

from . import Er_Oled_096_1_1
from ....vendor_parts.generic import *
from ...connector import Fpc050Bottom, HiroseFh12sh
from ....circuits import *
from ....abstract_parts.IdealIoController import IdealIoController


class OledI2cTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.io, [Power]),
            ImplicitConnect(self.gnd.io, [Common]),
        ) as imp:
            self.dut = imp.Block(Er_Oled_096_1_1())

            self.rst = self.Block(DummyDigitalSource()).connected(self.dut.reset)

            self.mcu = imp.Block(IdealIoController())
            self.i2c_pull = imp.Block(I2cPullup())
            self.connect(self.mcu.i2c.request(), self.dut.i2c, self.i2c_pull.i2c)

    @override
    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[
                (Resistor, GenericChipResistor),
                (Capacitor, GenericMlcc),
                (Fpc050Bottom, HiroseFh12sh),
            ],
            class_values=[(IdealModel, ["allow_ideal"], True)],
        )


class OledSpiTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Block(DummyVoltageSource(voltage_out=3.3 * Volt(tol=0)))
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.pwr.io, [Power]),
            ImplicitConnect(self.gnd.io, [Common]),
        ) as imp:
            self.dut = imp.Block(Er_Oled_096_1_1())

            self.rst = self.Block(DummyDigitalSource()).connected(self.dut.reset)

            self.mcu = imp.Block(IdealIoController())
            self.connect(self.mcu.spi.request(), self.dut.spi)
            self.cs = self.Block(DummyDigitalSource()).connected(self.dut.cs)
            self.dc = self.Block(DummyDigitalSource()).connected(self.dut.dc)

    @override
    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[
                (Resistor, GenericChipResistor),
                (Capacitor, GenericMlcc),
                (Fpc050Bottom, HiroseFh12sh),
            ],
            class_values=[(IdealModel, ["allow_ideal"], True)],
        )


class OledInterfacesTestCase(unittest.TestCase):
    def test_oled_i2c(self) -> None:
        compiled = ScalaCompiler.compile(OledI2cTest)

    def test_oled_spi(self) -> None:
        compiled = ScalaCompiler.compile(OledSpiTest)
