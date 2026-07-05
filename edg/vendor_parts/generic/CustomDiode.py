from typing import Any

from typing_extensions import override

from ...abstract_parts import *


class CustomDiode(Diode, FootprintBlock, GeneratorBlock):
    """Generic diode that automatically assigns footprint pinning."""

    def __init__(
        self,
        *args: Any,
        part: StringLike = "",
        footprint_spec: StringLike = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.part = self.ArgParameter(part)

        self.footprint_spec = self.ArgParameter(footprint_spec)  # actual_footprint left to the actual footprint
        self.generator_param(self.footprint_spec)

        # use ideal specs, which can be overridden with refinements
        self.assign(self.actual_voltage_rating, Range.all())
        self.assign(self.actual_current_rating, Range.all())
        self.assign(self.actual_voltage_drop, Range.zero_to_upper(0))
        self.assign(self.actual_reverse_recovery_time, Range.zero_to_upper(0))

    @override
    def generate(self) -> None:
        self.footprint(
            self._standard_footprint().REFDES_PREFIX,
            self.footprint_spec,
            self._standard_footprint()._make_pinning(self, self.get(self.footprint_spec)),
            part=self.part,
        )
