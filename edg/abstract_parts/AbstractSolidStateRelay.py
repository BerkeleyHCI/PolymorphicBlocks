from typing import Dict

from typing_extensions import override

from ..electronics_model import *
from .MergedBlocks import MergedAnalogSource
from .AbstractResistor import Resistor
from .Categories import Interface


@abstract_block
class SolidStateRelay(Interface, Block):
    """Base class for solid state relays.
    LED pins are passive (like the abstract LED) and the enclosing class should provide
    the circuitry to make it a DigitalSink port.
    """

    def __init__(self) -> None:
        super().__init__()

        self.leda = self.Port(Passive.empty())
        self.ledk = self.Port(Passive.empty())

        self.feta = self.Port(Passive.empty())
        self.fetb = self.Port(Passive.empty())

        # TODO: this is a different way of modeling parts - parameters in the part itself
        # instead of on the ports (because this doesn't have typed ports)
        self.led_forward_voltage = self.Parameter(RangeExpr())
        self.led_current_limit = self.Parameter(RangeExpr())
        self.led_current_recommendation = self.Parameter(RangeExpr())
        self.load_voltage_limit = self.Parameter(RangeExpr())
        self.load_current_limit = self.Parameter(RangeExpr())
        self.load_resistance = self.Parameter(RangeExpr())


class VoltageIsolatedSwitch(Interface, KiCadImportableBlock, Block):
    """Digitally controlled solid state relay that switches a voltage signal.
    Includes a ballasting resistor.

    The ports are not tagged with Input/Output/InOut, because of potential for confusion between
    the digital side and the analog side.
    """

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        assert symbol_name == "edg_importable:VoltageIsolatedSwitch"
        return {"in": self.signal, "gnd": self.gnd, "ain": self.pwr_in, "aout": self.pwr_out}

    def __init__(self) -> None:
        super().__init__()

        self.gnd = self.Port(Ground(), [Common])
        self.pwr_in = self.Port(VoltageSink(voltage_limits=RangeExpr(), current_draw=RangeExpr()))
        self.pwr_out = self.Port(VoltageSource(voltage_out=self.pwr_in.link().voltage, current_limits=RangeExpr()))
        self.signal = self.Port(DigitalSink(current_draw=RangeExpr()))

        self.ic = self.Block(SolidStateRelay())
        self.res = self.Block(
            Resistor(
                resistance=(
                    self.signal.link().voltage.upper() / self.ic.led_current_recommendation.upper(),
                    self.signal.link().output_thresholds.upper() / self.ic.led_current_recommendation.lower(),
                )
            )
        )
        self.connect(self.signal.net, self.ic.leda)
        self.connect(self.res.a, self.ic.ledk)
        self.connect(self.gnd.net, self.res.b)
        self.connect(self.pwr_in.net, self.ic.feta)
        self.connect(self.pwr_out.net, self.ic.fetb)

        self.assign(self.pwr_in.voltage_limits, self.ic.load_voltage_limit)  # TODO: assumed magic ground
        self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)
        self.assign(self.pwr_out.current_limits, self.ic.load_current_limit)
        self.assign(self.signal.current_draw, self.signal.link().voltage / self.res.actual_resistance)


class AnalogIsolatedSwitch(Interface, KiCadImportableBlock, Block):
    """Digitally controlled solid state relay that switches an analog signal.
    Includes a ballasting resistor.

    The ports are not tagged with Input/Output/InOut, because of potential for confusion between
    the digital side and the analog side.

    The output is modeled as if the switch is closed. A weak pull-up (or down) could be modeled by
    combining this device's output with a MergedAnalogSource.
    """

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        assert symbol_name == "edg_importable:AnalogIsolatedSwitch"
        return {"in": self.signal, "gnd": self.gnd, "ain": self.ain, "aout": self.aout}

    def __init__(self) -> None:
        super().__init__()

        self.ic = self.Block(SolidStateRelay())

        self.signal = self.Port(DigitalSink(current_draw=RangeExpr()))
        self.gnd = self.Port(Ground(), [Common])

        self.ain = self.Port(AnalogSink(voltage_limits=RangeExpr(), impedance=RangeExpr()))
        self.aout = self.Port(
            AnalogSource(
                voltage_out=self.ain.link().voltage,
                signal_out=self.ain.link().signal,
                current_limits=self.ic.load_current_limit,
                impedance=self.ain.link().source_impedance + self.ic.load_resistance,
            )
        )
        self.assign(
            self.ain.voltage_limits,
            (
                self.aout.link().voltage.lower() + self.ic.load_voltage_limit.upper(),
                self.aout.link().voltage.upper() - self.ic.load_voltage_limit.lower(),
            ),
        )
        self.assign(self.ain.impedance, self.aout.link().sink_impedance + self.ic.load_resistance)

        self.res = self.Block(
            Resistor(
                resistance=(
                    self.signal.link().voltage.upper() / self.ic.led_current_recommendation.upper(),
                    self.signal.link().output_thresholds.upper() / self.ic.led_current_recommendation.lower(),
                )
            )
        )
        self.assign(self.signal.current_draw, self.signal.link().voltage / self.res.actual_resistance)

        self.connect(self.signal.net, self.ic.leda)
        self.connect(self.res.a, self.ic.ledk)
        self.connect(self.gnd.net, self.res.b)

        self.connect(self.ain.net, self.ic.feta)
        self.connect(self.aout.net, self.ic.fetb)
