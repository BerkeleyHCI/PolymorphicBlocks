from typing import Optional
from ..abstract_parts import *


class BootstrapCapacitor(InternalBlock, Block):
    """A Capacitor wrapper for bootstrap capacitors, with a negative VoltageSink and a positive VoltageSource.
    This is meant to be used only with bootstrap pins on power conversion chips, that source some voltage and sink the
    boosted voltage. This is not meant to be general-purpose and will not function standalone.
    The negative node is a pure VoltageSink, where the source must model the entire switching voltage range.
    The positive node is a VoltageSource, where the source voltage models the boosted voltage, and the
    reverse voltage models the charging voltage.
    """

    def __init__(self, capacitance: RangeLike):
        super().__init__()

        self.neg = self.Port(VoltageSink())
        self.pos = self.Port(
            VoltageSource(voltage=RangeExpr(), reverse_voltage_limits=RangeExpr.ALL, reverse_current_draw=(0, 0) * Amp)
        )
        boost_voltage = self.pos.link().reverse_voltage - self.neg.link().voltage.lower()

        self.cap = self.Block(Capacitor(capacitance=capacitance, voltage=boost_voltage))
        self.assign(self.pos.voltage, self.neg.link().voltage + boost_voltage)
        self.connect(self.pos.net, self.cap.pos)
        self.connect(self.neg.net, self.cap.neg)

    def connected(
        self, neg: Optional[Port[VoltageLink]] = None, pos: Optional[Port[VoltageLink]] = None
    ) -> "BootstrapCapacitor":
        """Convenience function to connect both ports, returning this object so it can still be given a name."""
        if neg is not None:
            builder.block().connect(neg, self.neg)
        if pos is not None:
            builder.block().connect(pos, self.pos)
        return self
