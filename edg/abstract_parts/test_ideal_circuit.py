import unittest

from ..electronics_interfaces import *
from .IoController import IoController
from .LinearRegulator import LinearRegulator
from .SwitchingVoltageRegulator import BoostConverter


class IdealCircuitTestTop(Block):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Block(DummyGround())
        with self.implicit_connect(
            ImplicitConnect(self.gnd.io, [Common]),
        ) as imp:
            self.reg = imp.Block(LinearRegulator(2 * Volt(tol=0)))
            self.pwr = self.Block(DummyVoltageSource(5 * Volt(tol=0))).connected(self.reg.pwr_in)
            self.reg_draw = self.Block(DummyVoltageSink(current_draw=1 * Amp(tol=0))).connected(self.reg.pwr_out)

            self.boost = imp.Block(BoostConverter(4 * Volt(tol=0)))
            self.connect(self.boost.pwr_in, self.reg.pwr_out)
            self.boost_draw = self.Block(DummyVoltageSink(current_draw=1 * Amp(tol=0))).connected(self.boost.pwr_out)

            self.mcu = imp.Block(IoController())
            self.connect(self.mcu.pwr, self.reg.pwr_out)
            self.mcu_io = self.Block(DummyDigitalSink()).connected(self.mcu.gpio.request("test"))

        self.require(self.pwr.current_draw == 3 * Amp(tol=0))
        self.require(self.reg_draw.voltage == 2 * Volt(tol=0))


class IdealCircuitTest(unittest.TestCase):
    def test_ideal_circuit(self) -> None:
        ScalaCompiler.compile(
            IdealCircuitTestTop, refinements=Refinements(class_values=[(IdealModel, ["allow_ideal"], True)])
        )
