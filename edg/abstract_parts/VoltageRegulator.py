from abc import abstractmethod
from typing import Any, Optional

from deprecated import deprecated
from typing_extensions import override

from .Resettable import Resettable
from ..electronics_interfaces import *


@abstract_block_default(lambda: IdealVoltageRegulator)
class VoltageRegulator(PowerConditioner):
    """Structural abstract base class for DC-DC voltage regulators with shared ground (non-isolated).
    This takes some input voltage and produces a stable voltage at output_voltage on its output.

    While this abstract class does not define any limitations on the output voltage, subclasses and concrete
    implementations commonly have restrictions, for example linear regulators can only produce voltages lower
    than the input voltage.
    """

    def __init__(self, output_voltage: RangeLike) -> None:
        super().__init__()

        self.output_voltage = self.ArgParameter(output_voltage)

        self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])
        self.pwr_out = self.Port(VoltageSource.empty(), [Output])
        self.gnd = self.Port(Ground.empty(), [Common])

    @override
    def contents(self) -> None:
        super().contents()

        self.description = DescriptionString(
            "<b>output voltage:</b> ",
            DescriptionString.FormatUnits(self.pwr_out.voltage, "V"),
            " <b>of spec:</b> ",
            DescriptionString.FormatUnits(self.output_voltage, "V"),
            "\n",
            "<b>input voltage:</b> ",
            DescriptionString.FormatUnits(self.pwr_in.link().voltage, "V"),
        )

        self.require(self.pwr_out.voltage.within(self.output_voltage), "Output voltage must be within spec")


@non_library
class VoltageRegulatorEnableWrapper(Resettable, VoltageRegulator, GeneratorBlock):
    """Implementation mixin for a voltage regulator wrapper block where the inner device has a reset/enable pin
    (active-high enable / active-low shutdown) that is automatically tied high if not externally connected.
    Mix this into a VoltageRegulator to automatically handle the reset pin."""

    @abstractmethod
    def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
        """Returns the inner device's reset pin, to be connected in the generator.
        Only called within a generator."""

    @override
    def contents(self) -> None:
        super().contents()
        self.generator_param(self.reset.is_connected())

    @override
    def generate(self) -> None:
        super().generate()
        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self._generator_inner_reset_pin())
        else:  # by default tie high to enable regulator
            self.connect(self.pwr_in.as_digital_source(), self._generator_inner_reset_pin())


class IdealVoltageRegulator(Resettable, VoltageRegulator, IdealModel):
    """Ideal buck-boost / general DC-DC converter producing the spec output voltage
    and drawing input current from conversation of power"""

    @override
    def contents(self) -> None:
        super().contents()
        self.gnd.init_from(Ground())
        self.pwr_in.init_from(
            VoltageSink(
                current_draw=self.output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_draw
            )
        )
        self.pwr_out.init_from(VoltageSource(voltage=self.output_voltage))
        self.reset.init_from(DigitalSink())
