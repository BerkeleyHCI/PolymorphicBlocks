from typing import Any

from typing_extensions import override

from ...abstract_parts import *


class CustomFet(SwitchFet, FootprintBlock, GeneratorBlock):

    def __init__(
        self,
        *args: Any,
        part: StringLike = "",
        part_footprint: StringLike = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.part = self.ArgParameter(part)

        self.part_footprint = self.ArgParameter(part_footprint)  # actual_footprint left to the actual footprint
        self.generator_param(self.part_footprint)

        # use ideal specs, which can be overridden with refinements
        self.assign(self.actual_drain_voltage_rating, Range.all())
        self.assign(self.actual_drain_current_rating, Range.all())
        self.assign(self.actual_gate_voltage_rating, Range.all())
        self.assign(self.actual_gate_drive, Range.zero_to_upper(0))
        self.assign(self.actual_power_rating, Range.all())
        self.assign(self.actual_rds_on, Range.zero_to_upper(0))
        self.assign(self.actual_gate_charge, Range.zero_to_upper(0))

    @override
    def generate(self) -> None:
        self.footprint(
            self._standard_footprint().REFDES_PREFIX,
            self.part_footprint,
            self._standard_footprint()._make_pinning(self, self.get(self.part_footprint)),
            part=self.part,
        )
