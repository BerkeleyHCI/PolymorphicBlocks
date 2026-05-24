from typing import Any, Dict
from typing_extensions import override

from ..electronics_interfaces import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableSelector
from .StandardFootprint import StandardFootprint, HasStandardFootprint


@non_library
class BaseDiode(DiscreteSemiconductor, HasStandardFootprint):
    """Base class for diodes, with anode and cathode pins, including a very wide range of devices."""

    _STANDARD_FOOTPRINT = lambda: DiodeStandardFootprint

    def __init__(self) -> None:
        super().__init__()

        self.anode = self.Port(Passive.empty())
        self.cathode = self.Port(Passive.empty())


class DiodeStandardFootprint(StandardFootprint["BaseDiode"]):
    REFDES_PREFIX = "D"

    FOOTPRINT_PINNING_MAP = {
        (
            "Diode_SMD:D_MiniMELF",
            "Diode_SMD:D_SOD-123",
            "Diode_SMD:D_SOD-323",
            "Diode_SMD:D_SMA",
            "Diode_SMD:D_SMB",
            "Diode_SMD:D_SMC",
        ): lambda block: {
            "1": block.cathode,
            "2": block.anode,
        },
        (  # TODO are these standard?
            "Package_TO_SOT_SMD:TO-252-2",
            "Package_TO_SOT_SMD:TO-263-2",
        ): lambda block: {
            "1": block.anode,  # sometimes NC
            "2": block.cathode,
            "3": block.anode,
        },
    }


@abstract_block
class Diode(KiCadImportableBlock, BaseDiode):
    """Base class for untyped diodes

    TODO power? capacitance? leakage current?
    """

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        assert symbol_name in ("Device:D", "Device:D_Small")
        return {"A": self.anode, "K": self.cathode}

    def __init__(
        self,
        reverse_voltage: RangeLike,
        current: RangeLike,
        *,
        reverse_voltage_margin: FloatLike = 1.25,
        voltage_drop: RangeLike = Range.all(),
        reverse_recovery_time: RangeLike = Range.all(),
    ) -> None:
        super().__init__()

        self.reverse_voltage = self.ArgParameter(reverse_voltage, doc="operating Vr (reverse voltage across device)")
        self.current = self.ArgParameter(current, doc="operating If (forward current through device)")
        self.voltage_drop = self.ArgParameter(voltage_drop, doc="requirement for forward voltage drop")
        self.reverse_recovery_time = self.ArgParameter(
            reverse_recovery_time, doc="requirement for reverse recovery time"
        )

        self.reverse_voltage_margin = self.ArgParameter(
            reverse_voltage_margin, doc="Vr rating margin, eg 1.25 means voltage rating >=1.25x operating voltage"
        )

        self.actual_voltage_rating = self.Parameter(RangeExpr())
        self.actual_current_rating = self.Parameter(RangeExpr())
        self.actual_voltage_drop = self.Parameter(RangeExpr())
        self.actual_reverse_recovery_time = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()

        self.description = DescriptionString(
            "<b>Vr:</b> ",
            DescriptionString.FormatUnits(self.actual_voltage_rating, "V"),
            " <b>of operating:</b> ",
            DescriptionString.FormatUnits(self.reverse_voltage, "V"),
            "\n",
            "<b>If:</b> ",
            DescriptionString.FormatUnits(self.actual_current_rating, "A"),
            " <b>of operating:</b> ",
            DescriptionString.FormatUnits(self.current, "A"),
            "\n",
            "<b>Vf:</b> ",
            DescriptionString.FormatUnits(self.actual_voltage_drop, "V"),
            " <b>of spec:</b> ",
            DescriptionString.FormatUnits(self.voltage_drop, "V"),
        )


@non_library
class TableDiode(PartsTableSelector, Diode):
    VOLTAGE_RATING = PartsTableColumn(Range)  # tolerable blocking voltages, positive
    CURRENT_RATING = PartsTableColumn(Range)  # tolerable currents, average
    FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
    REVERSE_RECOVERY = PartsTableColumn(Range)  # possible reverse recovery time

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator_param(
            self.reverse_voltage,
            self.current,
            self.reverse_voltage_margin,
            self.voltage_drop,
            self.reverse_recovery_time,
        )

    @override
    def _row_filter(self, row: PartsTableRow) -> bool:
        return (
            super()._row_filter(row)
            and (self.get(self.reverse_voltage) * self.get(self.reverse_voltage_margin)).fuzzy_in(
                row[self.VOLTAGE_RATING]
            )
            and self.get(self.current).fuzzy_in(row[self.CURRENT_RATING])
            and row[self.FORWARD_VOLTAGE].fuzzy_in(self.get(self.voltage_drop))
            and row[self.REVERSE_RECOVERY].fuzzy_in(self.get(self.reverse_recovery_time))
        )

    @override
    def _row_generate(self, row: PartsTableRow) -> None:
        super()._row_generate(row)
        self.assign(self.actual_voltage_rating, row[self.VOLTAGE_RATING])
        self.assign(self.actual_current_rating, row[self.CURRENT_RATING])
        self.assign(self.actual_voltage_drop, row[self.FORWARD_VOLTAGE])
        self.assign(self.actual_reverse_recovery_time, row[self.REVERSE_RECOVERY])
