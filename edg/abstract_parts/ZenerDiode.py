from typing import Any, Dict
from typing_extensions import override
from deprecated import deprecated

from ..electronics_interfaces import *
from .Diode import BaseDiode
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableSelector


@abstract_block
class ZenerDiode(KiCadImportableBlock, BaseDiode, DiscreteSemiconductor):
    """Base class for untyped zeners

    TODO power? capacitance? leakage current?
    """

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        assert symbol_name in ("Device:D_Zener", "Device:D_Zener_Small")
        return {"A": self.anode, "K": self.cathode}

    def __init__(self, zener_voltage: RangeLike) -> None:
        super().__init__()

        self.zener_voltage = self.ArgParameter(zener_voltage)

        self.actual_zener_voltage = self.Parameter(RangeExpr())
        self.actual_power_rating = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()

        self.description = DescriptionString(
            "zener voltage=",
            DescriptionString.FormatUnits(self.actual_zener_voltage, "V"),
            " <b>of spec:</b>",
            DescriptionString.FormatUnits(self.zener_voltage, "V"),
            "\n",
            "power=",
            DescriptionString.FormatUnits(self.actual_power_rating, "W"),
        )


@non_library
class TableZenerDiode(PartsTableSelector, ZenerDiode):
    ZENER_VOLTAGE = PartsTableColumn(Range)
    POWER_RATING = PartsTableColumn(Range)  # tolerable power

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator_param(self.zener_voltage)

    @override
    def _row_filter(self, row: PartsTableRow) -> bool:
        return super()._row_filter(row) and row[self.ZENER_VOLTAGE].fuzzy_in(self.get(self.zener_voltage))

    @override
    def _row_generate(self, row: PartsTableRow) -> None:
        super()._row_generate(row)
        self.assign(self.actual_zener_voltage, row[self.ZENER_VOLTAGE])
        self.assign(self.actual_power_rating, row[self.POWER_RATING])


class ProtectionZenerDiode(Protection):
    """Zener diode reversed across a power rail to provide transient overvoltage protection (and become an incandescent
    indicator on a reverse voltage)"""

    def __init__(self, voltage: RangeLike):
        super().__init__()

        self.pwr = self.Port(
            VoltageSink(voltage_limits=RangeExpr()),
            [Power, InOut],
        )
        self.gnd = self.Port(Ground(), [Common])

        self.voltage = self.ArgParameter(voltage)

    @override
    def contents(self) -> None:
        super().contents()
        self.diode = self.Block(ZenerDiode(zener_voltage=self.voltage))
        self.connect(self.pwr.net, self.diode.cathode)
        self.connect(self.gnd.net, self.diode.anode)
        self.assign(self.pwr.voltage_limits, (0, self.diode.actual_zener_voltage.lower()))


@deprecated("Use AnalogClampResistor, which should be cheaper and cause less signal distortion")
class AnalogClampZenerDiode(Protection, KiCadImportableBlock):
    """Analog overvoltage protection diode to clamp the input voltage"""

    def __init__(self, voltage: RangeLike):
        super().__init__()

        self.diode = self.Block(ZenerDiode(zener_voltage=voltage))

        self.gnd = self.Port(Ground(), [Common])
        self.signal_in = self.Port(AnalogSink(), [Input])
        self.signal_out = self.Port(
            AnalogSource(
                voltage=self.signal_in.link().voltage.intersect(
                    self.gnd.link().voltage + (0, self.diode.actual_zener_voltage.upper())
                ),
                signal=self.signal_in.link().signal,
            ),
            [Output],
        )
        self.assign(self.signal_in.current_draw, self.signal_out.link().current_draw)

        self.connect(self.signal_in.net, self.signal_out.net, self.diode.cathode)
        self.connect(self.gnd.net, self.diode.anode)

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
        assert symbol_name == "edg_importable:AnalogClampZenerDiode"
        return {"IN": self.signal_in, "OUT": self.signal_out, "GND": self.gnd}
