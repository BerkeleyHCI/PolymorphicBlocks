import unittest

from .AbstractPowerConverters import BuckConverterPowerPath, BoostConverterPowerPath
from ..electronics_model import *
from .AbstractInductor import Inductor
from .AbstractCapacitor import Capacitor
from .DummyDevices import DummyVoltageSource, DummyVoltageSink, DummyGround


class SwitchingConverterCalculationTest(unittest.TestCase):
    def test_buck_converter(self):
        values_ref = BuckConverterPowerPath._calculate_parameters(
            Range.exact(5), Range.exact(2.5), Range.exact(100e3), Range.exact(1),
            Range.exact(1), Range.exact(0.1), 0.01, 0.001,
            efficiency=Range.exact(1)
        )
        self.assertEqual(values_ref.dutycycle, Range.exact(0.5))
        # validated against https://www.omnicalculator.com/physics/buck-converter
        self.assertEqual(values_ref.inductance, Range.exact(125e-6))

        # test that component values are calculated for worst-case conversion
        values = BuckConverterPowerPath._calculate_parameters(
            Range(4, 5), Range(2.5, 4), Range.exact(100e3), Range.exact(1),
            Range.exact(1), Range.exact(0.1), 0.01, 0.001,
            efficiency=Range.exact(1)
        )
        self.assertEqual(values_ref.inductance, values.inductance)
        self.assertEqual(values_ref.input_capacitance, values.input_capacitance)
        self.assertEqual(values_ref.output_capacitance, values.output_capacitance)

    def test_buck_converter_example(self):
        # using the example from https://passive-components.eu/buck-converter-design-and-calculation/
        values = BuckConverterPowerPath._calculate_parameters(
            Range.exact(12 + 0.4), Range.exact(3.3 + 0.4), Range.exact(500e3), Range.exact(1),
            Range.exact(2), Range.exact(0.35), 1, 0.0165,
            efficiency=Range.exact(1)
        )
        self.assertAlmostEqual(values.dutycycle.upper, 0.298, places=3)
        self.assertAlmostEqual(values.inductance.upper, 14.8e-6, places=7)

        # the example uses a ripple current of 0.346 for the rest of the calculations
        values = BuckConverterPowerPath._calculate_parameters(
            Range.exact(12 + 0.4), Range.exact(3.3 + 0.4), Range.exact(500e3), Range.exact(1),
            Range.exact(2), Range.exact(0.346), 1, 0.0165,
            efficiency=Range.exact(1)
        )
        self.assertAlmostEqual(values.inductor_peak_currents.upper, 1.173, places=3)
        self.assertAlmostEqual(values.output_capacitance.lower, 5.24e-6, places=7)

    def test_boost_converter(self):
        values_ref = BoostConverterPowerPath._calculate_parameters(
            Range.exact(5), Range.exact(10), Range.exact(100e3), Range.exact(0.5),
            Range.exact(2), Range.exact(0.4), 0.01, 0.001,
            efficiency=Range.exact(1)
        )
        self.assertEqual(values_ref.dutycycle, Range.exact(0.5))
        # validated against https://www.omnicalculator.com/physics/boost-converter
        self.assertEqual(values_ref.inductance, Range.exact(62.5e-6))
        self.assertEqual(values_ref.inductor_avg_current, Range.exact(1))

        # test that component values are calculated for worst-case conversion
        values = BoostConverterPowerPath._calculate_parameters(
            Range(5, 8), Range(7, 10), Range.exact(100e3), Range.exact(0.5),
            Range.exact(2), Range.exact(0.4), 0.01, 0.001,
            efficiency=Range.exact(1)
        )
        self.assertEqual(values_ref.inductance, values.inductance)
        self.assertEqual(values_ref.input_capacitance, values.input_capacitance)
        self.assertEqual(values_ref.output_capacitance, values.output_capacitance)

    def test_boost_converter_example(self):
        # using the example from https://passive-components.eu/boost-converter-design-and-calculation/
        values = BoostConverterPowerPath._calculate_parameters(
            Range.exact(5), Range.exact(12 + 0.4), Range.exact(500e3), Range.exact(0.5),
            Range.exact(2), Range.exact(0.35), 1, 1,
            efficiency=Range.exact(1)
        )
        self.assertAlmostEqual(values.dutycycle.upper, 0.597, places=3)
        self.assertAlmostEqual(values.inductance.upper, 13.75e-6, places=7)
        self.assertAlmostEqual(values.inductor_avg_current.upper, 1.24, places=2)

        # the example continues with a normalized inductance of 15uH
        values = BoostConverterPowerPath._calculate_parameters(
            Range.exact(5), Range.exact(12 + 0.4), Range.exact(500e3), Range.exact(0.5),
            Range.exact(2), Range.exact(0.321), 0.01, 0.06,
            efficiency=Range.exact(1)
        )
        self.assertAlmostEqual(values.dutycycle.upper, 0.597, places=3)
        self.assertAlmostEqual(values.inductance.upper, 15.0e-6, places=7)
        self.assertAlmostEqual(values.inductor_peak_currents.upper, 1.44, places=2)
        # the example calculation output is wrong, this is the correct result of the formula
        self.assertAlmostEqual(values.output_capacitance.lower, 9.95e-6, places=7)


class TestCapacitor(Capacitor):
    def contents(self):
        super().contents()
        self.assign(self.actual_capacitance, self.capacitance)
        self.assign(self.actual_voltage_rating, Range.all())


class TestInductor(Inductor):
    def contents(self):
        super().contents()
        self.assign(self.actual_inductance, self.inductance)
        self.assign(self.actual_current_rating, (0, 1.5)*Amp)
        self.assign(self.actual_frequency_rating, Range.all())


class BuckPowerPathTestTop(DesignTop):
    def __init__(self):
        super().__init__()
        self.dut = self.Block(BuckConverterPowerPath(
            input_voltage=Range(4, 6), output_voltage=(2, 3),
            frequency= Range.exact(100e3), output_current=Range(0.2, 1),
            sw_current_limits=Range(0, 2),
            input_voltage_ripple=75*mVolt, output_voltage_ripple=25*mVolt,
        ))
        (self.pwr_in, ), _ = self.chain(self.Block(DummyVoltageSource()), self.dut.pwr_in)
        (self.switch, ), _ = self.chain(self.Block(DummyVoltageSource()), self.dut.switch)
        (self.pwr_out, ), _ = self.chain(self.Block(DummyVoltageSink()), self.dut.pwr_out)
        (self.gnd, ), _ = self.chain(self.Block(DummyGround()), self.dut.gnd)

        self.require(self.dut.actual_dutycycle.contains(Range(0.334, 0.832)))
        self.require(self.dut.actual_inductor_current_ripple.contains(Range(0.433, 0.478)))
        self.require(self.dut.pwr_out.current_limits.contains(Range(0.0, 1.260)))
        self.require(self.dut.switch.current_draw.contains(Range(0.067, 0.832)))

    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[
                (Capacitor, TestCapacitor),
                (Inductor, TestInductor),
            ],
            instance_values=[
                (['dut', 'inductor', 'actual_inductance'], Range.from_tolerance(33e-6, 0.05))
            ]
        )


class BoostPowerPathTestTop(DesignTop):
    def __init__(self):
        super().__init__()
        self.dut = self.Block(BoostConverterPowerPath(
            input_voltage=Range(4, 6), output_voltage=(10, 14),
            frequency=Range.exact(200e3), output_current=Range(0.2, 0.5),
            sw_current_limits=Range(0, 2),
            input_voltage_ripple=75*mVolt, output_voltage_ripple=25*mVolt,
        ))
        (self.pwr_in, ), _ = self.chain(self.Block(DummyVoltageSource()), self.dut.pwr_in)
        (self.pwr_out, ), _ = self.chain(self.Block(DummyVoltageSource()), self.dut.pwr_out)
        (self.switch, ), _ = self.chain(self.Block(DummyVoltageSink()), self.dut.switch)
        (self.gnd, ), _ = self.chain(self.Block(DummyGround()), self.dut.gnd)

        self.require(self.dut.actual_dutycycle.contains(Range(0.4, 0.771)))
        self.require(self.dut.actual_inductor_current_ripple.contains(Range(0.495, 0.546)))
        self.require(self.dut.pwr_in.current_draw.contains(Range(0.334, 2.185)))
        self.require(self.dut.switch.current_limits.contains(Range(0.0, 0.280)))

    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[
                (Capacitor, TestCapacitor),
                (Inductor, TestInductor),
            ],
            instance_values=[
                (['dut', 'inductor', 'actual_inductance'], Range.from_tolerance(33e-6, 0.05))
            ]
        )


class PowerPathBlockTest(unittest.TestCase):
    def test_buck_power_path(self) -> None:
        ScalaCompiler.compile(BuckPowerPathTestTop)

    def test_boost_power_path(self) -> None:
        ScalaCompiler.compile(BoostPowerPathTestTop)
