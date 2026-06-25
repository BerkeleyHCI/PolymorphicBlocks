from typing import Any

from deprecated import deprecated
from typing_extensions import override

from ...circuits import *
from .Jst import JstShSmHorizontal
from ...util import deprecated_param_remap


@abstract_block
class PowerBarrelJack(Connector, PowerSource, Block):
    """Barrel jack that models a configurable voltage / max current power supply."""

    @deprecated_param_remap(("voltage_out", "voltage"))
    def __init__(self, voltage: RangeLike = RangeExpr(), current_limits: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSource(voltage=voltage, current_limits=current_limits))
        self.gnd = self.Port(Ground())


class Pj_102ah(PowerBarrelJack, FootprintBlock):
    """Barrel jack for 2.1mm ID and 5.5mm OD"""

    @override
    def contents(self) -> None:
        super().contents()
        self.require(self.pwr.voltage.within((0, 24) * Volt))  # datasheet ratings for connector
        self.require(self.pwr.current_limits.within((0, 2.5) * Amp))
        self.footprint(
            "J",
            "Connector_BarrelJack:BarrelJack_CUI_PJ-102AH_Horizontal",
            {
                "1": self.pwr,
                "2": self.gnd,
                # '3': # TODO optional switch
            },
            mfr="CUI Devices",
            part="PJ-102AH",
            datasheet="https://www.cui.com/product/resource/digikeypdf/pj-102a.pdf",
        )


class Pj_036ah(PowerBarrelJack, FootprintBlock):
    """SMT Barrel jack for 2.1mm ID and 5.5mm OD"""

    @override
    def contents(self) -> None:
        super().contents()
        self.require(self.pwr.voltage.within((0, 24) * Volt))  # datasheet ratings for connector
        self.require(self.pwr.current_limits.within((0, 5) * Amp))

        self.footprint(
            "J",
            "Connector_BarrelJack:BarrelJack_CUI_PJ-036AH-SMT_Horizontal",
            {
                "1": self.pwr,
                "2": self.gnd,
                # '3': # TODO optional switch
            },
            mfr="CUI Devices",
            part="PJ-036AH-SMT",
            datasheet="https://www.cuidevices.com/product/resource/pj-036ah-smt-tr.pdf",
        )


class LipoConnector(Connector, Battery):
    """PassiveConnector (abstract connector) that is expected to have a LiPo on one end.
    Both the voltage specification and the actual voltage can be specified as parameters.
    THERE IS NO STANDARD LIPO PINNING OR CONNECTOR - MAKE SURE TO VERIFY THIS!
    BE PREPARED FOR REVERSE POLARITY CONNECTIONS.
    Default pinning has ground being pin 1, and power being pin 2.

    Connector type not specified, up to the user through a refinement."""

    def __init__(
        self,
        voltage: RangeLike = (2.5, 4.2) * Volt,
        *args: Any,
        actual_voltage: RangeLike = (2.5, 4.2) * Volt,
        charge_tolerance: RangeLike = (1.0, 1.01) * Ratio,
        **kwargs: Any,
    ) -> None:
        super().__init__(voltage, *args, **kwargs)

        self.gnd.init_from(Ground())
        self.pwr.init_from(
            VoltageSource(
                voltage=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
                current_limits=(0, 5.5) * Amp,  # arbitrary assuming low capacity, 10 C discharge
                reverse_voltage_limits=actual_voltage * RangeExpr._to_expr_type(charge_tolerance),
                reverse_current_draw=(0, 0) * Amp,
            )
        )

        self.conn = self.Block(PassiveConnector()).connected({"1": self.gnd, "2": self.pwr})

        self.assign(self.actual_capacity, (500, 600) * mAmp)  # arbitrary

    @property
    @deprecated(f"chg is deprecated and unified with sink-capable (bidirectional) pwr")
    def chg(self) -> VoltageSource:
        return self.pwr


class QwiicTarget(Connector):
    """A Qwiic (https://www.sparkfun.com/qwiic) connector to a I2C target.
    This would be on a board with a host controller."""

    def __init__(self) -> None:
        super().__init__()

        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(
            VoltageSink(
                voltage_limits=3.3 * Volt(tol=0.05),  # required 3.3v per the spec, tolerance assumed
                current_draw=(0, 226) * mAmp,  # per the Qwiic FAQ, max current for the cable
            ),
            [Power],
        )
        self.i2c = self.Port(I2cTarget(), [InOut])

        self.conn = self.Block(JstShSmHorizontal(4)).connected(
            {"1": self.gnd, "2": self.pwr, "3": self.i2c.sda, "4": self.i2c.scl}
        )
