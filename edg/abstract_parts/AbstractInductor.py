from typing import Dict, Optional, cast, Any

from typing_extensions import override

from ..electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow, ExperimentalUserFnPartsTable
from .PartsTablePart import PartsTableSelector
from .Categories import *
from .StandardFootprint import StandardFootprint, HasStandardFootprint


@abstract_block
class Inductor(PassiveComponent, KiCadImportableBlock, HasStandardFootprint):
    _STANDARD_FOOTPRINT = lambda: InductorStandardFootprint

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        assert symbol_name in ("Device:L", "Device:L_Small")
        return {"1": self.a, "2": self.b}

    def __init__(
        self,
        inductance: RangeLike,
        current: RangeLike = RangeExpr.ZERO,
        frequency: RangeLike = RangeExpr.ZERO,
        resistance_dc: RangeLike = (0, 1) * Ohm,  # generic sane choice?
        *,
        experimental_filter_fn: StringLike = "",
    ) -> None:
        super().__init__()

        self.a = self.Port(Passive.empty())
        self.b = self.Port(Passive.empty())

        self.inductance = self.ArgParameter(inductance)
        self.current = self.ArgParameter(current)  # defined as operating current range, non-directioned
        self.frequency = self.ArgParameter(frequency)  # defined as operating frequency range
        self.resistance_dc = self.ArgParameter(resistance_dc)
        self.experimental_filter_fn = self.ArgParameter(experimental_filter_fn)

        self.actual_inductance = self.Parameter(RangeExpr())
        self.actual_current_rating = self.Parameter(RangeExpr())
        self.actual_frequency_rating = self.Parameter(RangeExpr())
        self.actual_resistance_dc = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()

        self.description = DescriptionString(
            "<b>inductance:</b> ",
            DescriptionString.FormatUnits(self.actual_inductance, "H"),
            " <b>of spec:</b> ",
            DescriptionString.FormatUnits(self.inductance, "H"),
            "\n",
            "<b>current rating:</b> ",
            DescriptionString.FormatUnits(self.actual_current_rating, "A"),
            " <b>of operating:</b> ",
            DescriptionString.FormatUnits(self.current, "A"),
            "\n",
            "<b>frequency rating:</b> ",
            DescriptionString.FormatUnits(self.actual_frequency_rating, "Hz"),
            " <b>of operating:</b> ",
            DescriptionString.FormatUnits(self.frequency, "Hz"),
            "\n",
            "<b>dc resistance:</b> ",
            DescriptionString.FormatUnits(self.actual_resistance_dc, "Ω"),
            " <b>of spec:</b> ",
            DescriptionString.FormatUnits(self.resistance_dc, "Ω"),
        )


class InductorStandardFootprint(StandardFootprint[Inductor]):
    REFDES_PREFIX = "L"

    FOOTPRINT_PINNING_MAP = {
        (
            "Inductor_SMD:L_0201_0603Metric",
            "Inductor_SMD:L_0402_1005Metric",
            "Inductor_SMD:L_0603_1608Metric",
            "Inductor_SMD:L_0805_2012Metric",
            "Inductor_SMD:L_1206_3216Metric",
            "Inductor_SMD:L_1210_3225Metric",
            "Inductor_SMD:L_1812_4532Metric",
            "Inductor_SMD:L_2010_5025Metric",
            "Inductor_SMD:L_2512_6332Metric",
            "Inductor_SMD:L_Bourns-SRR1005",
            "Inductor_SMD:L_Bourns_SRR1210A",
            "Inductor_SMD:L_Bourns_SRR1260",
            "Inductor_SMD:L_Bourns_SRP1245A",
            "Inductor_SMD:L_Sunlord_SWPA3010S",
            "Inductor_SMD:L_Sunlord_SWPA3012S",
            "Inductor_SMD:L_Sunlord_SWPA3015S",
            "Inductor_SMD:L_Sunlord_SWPA4010S",
            "Inductor_SMD:L_Sunlord_SWPA4012S",
            "Inductor_SMD:L_Sunlord_SWPA4018S",
            "Inductor_SMD:L_Sunlord_SWPA4020S",
            "Inductor_SMD:L_Sunlord_SWPA4026S",
            "Inductor_SMD:L_Sunlord_SWPA4030S",
            "Inductor_SMD:L_Sunlord_SWPA5012S",
            "Inductor_SMD:L_Sunlord_SWPA5020S",
            "Inductor_SMD:L_Sunlord_SWPA5040S",
            "Inductor_SMD:L_Sunlord_SWPA6020S",
            "Inductor_SMD:L_Sunlord_SWPA6028S",
            "Inductor_SMD:L_Sunlord_SWPA6040S",
            "Inductor_SMD:L_Sunlord_SWPA6045S",
            "Inductor_SMD:L_Sunlord_SWPA8040S",
            "Inductor_SMD:L_Sunlord_SWRB1204S",
            "Inductor_SMD:L_Sunlord_SWRB1205S",
            "Inductor_SMD:L_Sunlord_SWRB1207S",
            "Inductor_SMD:L_Taiyo-Yuden_NR-20xx",
            "Inductor_SMD:L_Taiyo-Yuden_NR-24xx",
            "Inductor_SMD:L_Taiyo-Yuden_NR-30xx",
            "Inductor_SMD:L_Taiyo-Yuden_NR-40xx",
            "Inductor_SMD:L_Taiyo-Yuden_NR-50xx",
            "Inductor_SMD:L_Taiyo-Yuden_NR-60xx",
            "Inductor_SMD:L_Taiyo-Yuden_NR-80xx",
            "Inductor_SMD:L_TDK_SLF6025",
            "Inductor_SMD:L_TDK_SLF6028",
            "Inductor_SMD:L_TDK_SLF6045",
            "Inductor_SMD:L_TDK_SLF7032",
            "Inductor_SMD:L_TDK_SLF7045",
            "Inductor_SMD:L_TDK_SLF7055",
            "Inductor_SMD:L_TDK_SLF10145",
            "Inductor_SMD:L_TDK_SLF10165",
            "Inductor_SMD:L_TDK_SLF12555",
            "Inductor_SMD:L_TDK_SLF12565",
            "Inductor_SMD:L_TDK_SLF12575",
            "Inductor_SMD:L_Vishay_IHLP-1212",
            "Inductor_SMD:L_Vishay_IHLP-1616",
            "Inductor_SMD:L_Vishay_IHLP-2020",
            "Inductor_SMD:L_Vishay_IHLP-2525",
            "Inductor_SMD:L_Vishay_IHLP-4040",
            "Inductor_SMD:L_Vishay_IHLP-5050",
            "Inductor_SMD:L_Vishay_IHLP-6767",
        ): lambda block: {
            "1": block.a,
            "2": block.b,
        },
    }


@non_library
class TableInductor(PartsTableSelector, Inductor):
    INDUCTANCE = PartsTableColumn(Range)  # actual inductance incl. tolerance
    FREQUENCY_RATING = PartsTableColumn(Range)  # tolerable frequencies
    CURRENT_RATING = PartsTableColumn(Range)  # tolerable current
    DC_RESISTANCE = PartsTableColumn(Range)  # actual DCR

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator_param(
            self.inductance, self.current, self.frequency, self.resistance_dc, self.experimental_filter_fn
        )

    @override
    def _row_filter(self, row: PartsTableRow) -> bool:
        filter_fn_str = self.get(self.experimental_filter_fn)
        if filter_fn_str:
            filter_fn = ExperimentalUserFnPartsTable.deserialize_fn(filter_fn_str)
        else:
            filter_fn = None

        return (
            super()._row_filter(row)
            and row[self.INDUCTANCE].fuzzy_in(self.get(self.inductance))
            and self.get(self.current).fuzzy_in(row[self.CURRENT_RATING])
            and row[self.DC_RESISTANCE].fuzzy_in(self.get(self.resistance_dc))
            and self.get(self.frequency).fuzzy_in(row[self.FREQUENCY_RATING])
            and (filter_fn is None or filter_fn(row))
        )

    @override
    def _row_generate(self, row: PartsTableRow) -> None:
        super()._row_generate(row)
        self.assign(self.actual_inductance, row[self.INDUCTANCE])
        self.assign(self.actual_current_rating, row[self.CURRENT_RATING])
        self.assign(self.actual_frequency_rating, row[self.FREQUENCY_RATING])
        self.assign(self.actual_resistance_dc, row[self.DC_RESISTANCE])

    @classmethod
    @override
    def _row_sort_by(cls, row: PartsTableRow) -> Any:
        return row[cls.DC_RESISTANCE].center()


class SeriesPowerInductor(DiscreteApplication):
    """VoltageSource/Sink-typed series inductor for power filtering"""

    def __init__(
        self, inductance: RangeLike, current: RangeLike = RangeExpr.ZERO, frequency: RangeLike = RangeExpr.ZERO
    ) -> None:
        super().__init__()

        self.pwr_out = self.Port(VoltageSource.empty(), [Output])  # forward declaration
        self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])  # forward declaration

        self.ind = self.Block(Inductor(inductance=inductance, current=current, frequency=frequency))

        self.connect(self.pwr_in, self.ind.a.adapt_to(VoltageSink(current_draw=self.pwr_out.link().current_drawn)))
        self.connect(
            self.pwr_out,
            self.ind.b.adapt_to(
                VoltageSource(
                    voltage_out=self.pwr_in.link().voltage,
                )
            ),
        )

    def connected(
        self, pwr_in: Optional[Port[VoltageLink]] = None, pwr_out: Optional[Port[VoltageLink]] = None
    ) -> "SeriesPowerInductor":
        """Convenience function to connect both ports, returning this object so it can still be given a name."""
        if pwr_in is not None:
            cast(Block, builder.get_enclosing_block()).connect(pwr_in, self.pwr_in)
        if pwr_out is not None:
            cast(Block, builder.get_enclosing_block()).connect(pwr_out, self.pwr_out)
        return self
