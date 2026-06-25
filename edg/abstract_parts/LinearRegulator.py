from typing_extensions import override

from ..electronics_interfaces import *
from .Resettable import Resettable
from .VoltageRegulator import VoltageRegulator


@abstract_block_default(lambda: IdealLinearRegulator)
class LinearRegulator(VoltageRegulator):
    """Structural abstract base class for linear regulators, a voltage regulator that can produce some
    output voltage lower than its input voltage (minus some dropout) by 'burning' the excess voltage as heat.

    Compared to switching converters like buck and boost converters, linear regulators usually have lower
    complexity, lower parts count, and higher stability. However, depending on the application, they are
    typically less efficient, and at higher loads may require thermal design considerations."""


@abstract_block
class VoltageReference(LinearRegulator):
    """Voltage reference, generally provides high accuracy but limited current"""


class IdealLinearRegulator(Resettable, LinearRegulator, IdealModel):
    """Ideal linear regulator, draws the output current and produces spec output voltage limited by input voltage"""

    @override
    def contents(self) -> None:
        super().contents()
        effective_output_voltage = self.output_voltage.intersect((0, self.pwr_in.link().voltage.upper()))
        self.gnd.init_from(Ground())
        self.pwr_in.init_from(VoltageSink(current_draw=self.pwr_out.link().current_draw))
        self.pwr_out.init_from(VoltageSource(voltage_out=effective_output_voltage))
        self.reset.init_from(DigitalSink())


@non_library
class LinearRegulatorDevice(Block):
    """Abstract base class that provides a default model with common functionality for a linear regulator chip.
    Does not include supporting components like capacitors.
    """

    def __init__(self) -> None:
        super().__init__()

        # these device model parameters must be provided by subtypes
        self.actual_dropout = self.Parameter(RangeExpr())
        self.actual_quiescent_current = self.Parameter(RangeExpr())

        self.gnd = self.Port(Ground(), [Common])
        self.pwr_in = self.Port(
            VoltageSink(voltage_limits=RangeExpr(), current_draw=RangeExpr()),  # parameters set by subtype
            [Power, Input],
        )
        self.pwr_out = self.Port(
            VoltageSource(voltage_out=self.RangeExpr(), current_limits=RangeExpr()),  # parameters set by subtype
            [Output],
        )
        self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_draw + self.actual_quiescent_current)

        self.require(
            self.pwr_out.voltage_out.lower() + self.actual_dropout.upper() <= self.pwr_in.link().voltage.lower(),
            "excessive dropout",
        )
