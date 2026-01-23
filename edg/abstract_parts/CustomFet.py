from typing import Any

from typing_extensions import override

from ..electronics_model import *
from .AbstractFets import SwitchFet


class CustomFet(SwitchFet, FootprintBlock, GeneratorBlock):
    def __init__(
        self,
        *args: Any,
        footprint_spec: StringLike = "",
        manufacturer_spec: StringLike = "",
        part_spec: StringLike = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.footprint_spec = self.ArgParameter(footprint_spec)  # actual_footprint left to the actual footprint
        self.manufacturer_spec = self.ArgParameter(manufacturer_spec)
        self.part_spec = self.ArgParameter(part_spec)

        self.generator_param(self.footprint_spec)

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
            self.footprint_spec,
            self._standard_footprint()._make_pinning(self, self.get(self.footprint_spec)),
            mfr=self.manufacturer_spec,
            part=self.part_spec,
            value=self.part_spec,
            datasheet="",
        )
