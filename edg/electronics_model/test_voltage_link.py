import unittest

from typing_extensions import override

from .VoltagePorts import VoltageLink
from . import *


class VoltageTestTop(DesignTop):
    """Test design with single voltage source and sink with valid ranges"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(DummyVoltageSource(voltage_out=5 * Volt(tol=0), current_limits=(0, 1) * Amp))
        self.sink = self.Block(DummyVoltageSink(voltage_limit=5 * Volt(tol=0.1), current_draw=1 * Amp(tol=0)))
        self.connect(self.src.pwr, self.sink.pwr)


class NoSourceVoltageTest(DesignTop):
    """Test design with missing source"""

    def __init__(self) -> None:
        super().__init__()
        self.sink = self.Block(DummyVoltageSink(voltage_limit=5 * Volt(tol=0.1), current_draw=1 * Amp(tol=0)))


class OvervoltageTestTop(DesignTop):
    """Test design with single source and single restrictive sink"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(DummyVoltageSource(voltage_out=5 * Volt(tol=0), current_limits=(0, 1) * Amp))
        self.sink = self.Block(DummyVoltageSink(voltage_limit=3.3 * Volt(tol=0.1), current_draw=1 * Amp(tol=0)))
        self.connect(self.src.pwr, self.sink.pwr)


class OvercurrentTestTop(DesignTop):
    """Test design with single source and single restrictive sink"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(DummyVoltageSource(voltage_out=5 * Volt(tol=0), current_limits=(0, 1) * Amp))
        self.sink1 = self.Block(DummyVoltageSink(voltage_limit=5 * Volt(tol=0.1), current_draw=1 * Amp(tol=0)))
        self.sink2 = self.Block(DummyVoltageSink(voltage_limit=5 * Volt(tol=0.1), current_draw=1 * Amp(tol=0)))
        self.connect(self.src.pwr, self.sink1.pwr, self.sink2.pwr)


class ReverseVoltageTestTop(DesignTop):
    """Test design with valid forward and reverse voltage flows"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(
            DummyVoltageSource(
                voltage_out=5 * Volt(tol=0),
                current_limits=(0, 1) * Amp,
                reverse_voltage_limits=5 * Volt(tol=0.1),
                reverse_current_draw=0 * Amp,
            )
        )
        self.sink = self.Block(
            DummyVoltageSink(
                voltage_limit=5 * Volt(tol=0.1),
                current_draw=0 * Amp,
                reverse_voltage_out=5 * Volt(tol=0),
                reverse_current_limits=(0, 1) * Amp,
            )
        )
        self.sink2 = self.Block(
            DummyVoltageSink(
                voltage_limit=5 * Volt(tol=0.1),
                current_draw=0 * Amp,
            )
        )
        self.connect(self.src.pwr, self.sink.pwr, self.sink2.pwr)
        self.require(self.src.reverse_voltage == 5 * Volt(tol=0))


class ReverseMultiSourceTestTop(DesignTop):
    """Test design with (invalid) multiple reverse voltage sources"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(
            DummyVoltageSource(
                voltage_out=5 * Volt(tol=0),
                current_limits=(0, 1) * Amp,
                reverse_voltage_limits=5 * Volt(tol=0.1),
                reverse_current_draw=0 * Amp,
            )
        )
        self.sink1 = self.Block(
            DummyVoltageSink(
                voltage_limit=5 * Volt(tol=0.1),
                current_draw=0 * Amp,
                reverse_voltage_out=5 * Volt(tol=0),
                reverse_current_limits=(0, 1) * Amp,
            )
        )
        self.sink2 = self.Block(
            DummyVoltageSink(
                voltage_limit=5 * Volt(tol=0.1),
                current_draw=0 * Amp,
                reverse_voltage_out=5 * Volt(tol=0),
                reverse_current_limits=(0, 1) * Amp,
            )
        )
        self.connect(self.src.pwr, self.sink1.pwr, self.sink2.pwr)


class ReverseNoSinkTest(DesignTop):
    """Test design with reverse voltage source but no sink"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(DummyVoltageSource(voltage_out=5 * Volt(tol=0), current_limits=(0, 1) * Amp))
        self.sink = self.Block(
            DummyVoltageSink(
                voltage_limit=5 * Volt(tol=0.1),
                current_draw=0 * Amp,
                reverse_voltage_out=5 * Volt(tol=0),
                reverse_current_limits=(0, 1) * Amp,
            )
        )
        self.connect(self.src.pwr, self.sink.pwr)


class ReverseOvervoltageTestTop(DesignTop):
    """Test design with reverse voltage incompatibility"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(
            DummyVoltageSource(
                voltage_out=3.3 * Volt(tol=0),
                current_limits=(0, 1) * Amp,
                reverse_voltage_limits=3.3 * Volt(tol=0.1),
                reverse_current_draw=0 * Amp,
            )
        )
        self.sink = self.Block(
            DummyVoltageSink(
                voltage_limit=(0, 14) * Volt,
                current_draw=0 * Amp,
                reverse_voltage_out=5 * Volt(tol=0),
                reverse_current_limits=(0, 1) * Amp,
            )
        )
        self.connect(self.src.pwr, self.sink.pwr)
        self.require(self.src.reverse_voltage != RangeExpr.EMPTY)


class ReverseForwardOvervoltageTestTop(DesignTop):
    """Test design with reverse voltage incompatibility with forward limits"""

    def __init__(self) -> None:
        super().__init__()
        self.src = self.Block(
            DummyVoltageSource(
                voltage_out=5 * Volt(tol=0),
                current_limits=(0, 1) * Amp,
                reverse_voltage_limits=(0, 14) * Volt,
                reverse_current_draw=0 * Amp,
            )
        )
        self.sink = self.Block(
            DummyVoltageSink(
                voltage_limit=5 * Volt(tol=0.1),
                current_draw=0 * Amp,
                reverse_voltage_out=12 * Volt(tol=0),
                reverse_current_limits=(0, 1) * Amp,
            )
        )
        self.connect(self.src.pwr, self.sink.pwr)
        self.require(self.src.reverse_voltage != RangeExpr.EMPTY)


class VoltageLinkTestCase(unittest.TestCase):
    def test_voltage(self) -> None:
        ScalaCompiler.compile(VoltageTestTop)

    def test_no_source(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(NoSourceVoltageTest)

    def test_overvoltage(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(OvervoltageTestTop)

    def test_overcurrent(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(OvercurrentTestTop)

    def test_reverse_voltage(self) -> None:
        ScalaCompiler.compile(ReverseVoltageTestTop)

    def test_reverse_multi_source(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(ReverseMultiSourceTestTop)

    def test_reverse_no_sink(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(ReverseNoSinkTest)

    def test_reverse_overvoltage(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(ReverseOvervoltageTestTop)

    def test_reverse_forward_overvoltage(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(ReverseForwardOvervoltageTestTop)
