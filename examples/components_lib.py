import unittest
from typing import Optional, cast

from edg import *

from .test_multimeter import FetPowerGate


class OrPowerGate(PowerConditioner, Block):
    @init_in_parent
    def __init__(self, diode_voltage_drop: RangeLike, fet_rds_on: RangeLike) -> None:
        super().__init__()
        self.pwr_out = self.Port(VoltageSource.empty())
        self.gnd = self.Port(Ground.empty(), [Common])
        self.pwr_hi = self.Port(VoltageSink().empty(),)
        self.pwr_lo = self.Port(VoltageSink().empty(),)

        self.btn_out = self.Port(DigitalSingleSource.empty())
        self.control = self.Port(DigitalSink.empty())  # digital level control - gnd-referenced NFET gate


        self.diode_voltage_drop = self.ArgParameter(diode_voltage_drop)
        self.fet_rds_on = self.ArgParameter(fet_rds_on)

    def contents(self):
        super().contents()
        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.fuse, self.gate, self.prot, self.tp), _ = self.chain(
                self.pwr_lo,
                imp.Block(SeriesPowerPptcFuse((2, 4)*Amp)),
                imp.Block(FetPowerGate()),
                imp.Block(ProtectionZenerDiode(voltage=(4.5, 6.0)*Volt)),
                self.Block(VoltageTestPoint()))
            self.vbatt = self.connect(self.gate.pwr_out)  # downstream of fuse

            self.pwr_or = self.Block(PriorityPowerOr(  # also does reverse protection
                self.diode_voltage_drop, self.fet_rds_on
            )).connected_from(self.gnd, self.pwr_hi, self.gate.pwr_out)

            self.connect(self.pwr_or.pwr_out, self.pwr_out)

            # Power gait
            self.connect(self.gate.control, self.control)
            self.connect(self.gate.btn_out, self.btn_out)

    def connected_from(self, gnd: Optional[Port[VoltageLink]] = None, pwr_hi: Optional[Port[VoltageLink]] = None,
                       pwr_lo: Optional[Port[VoltageLink]] = None) -> 'OrPowerGate':
        """Convenience function to connect ports, returning this object so it can still be given a name."""
        if gnd is not None:
            cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
        if pwr_hi is not None:
            cast(Block, builder.get_enclosing_block()).connect(pwr_hi, self.pwr_hi)
        if pwr_lo is not None:
            cast(Block, builder.get_enclosing_block()).connect(pwr_lo, self.pwr_lo)
        return self


class ProtectedVoltageRegulator(VoltageRegulator, Block):
    @init_in_parent
    def __init__(self, output_voltage: RangeLike, zener_diode_voltage: RangeLike, test_point: BoolLike=True) -> None:
        super().__init__(output_voltage)
        self.zener_diode_voltage = self.ArgParameter(zener_diode_voltage)

        self.test_point = self.ArgParameter(test_point)
    #
        # self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])
        # self.pwr_out = self.Port(VoltageSource.empty(), [Output])
        # self.gnd = self.Port(Ground.empty(), [Common])

    def contents(self):
        super().contents()
        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.reg, self.prot, self.tp), _ = self.chain(
                self.pwr_in,
                imp.Block(VoltageRegulator(self.output_voltage)),
                imp.Block(ProtectionZenerDiode(self.zener_diode_voltage)),
                self.Block(VoltageTestPoint()),
            )

        self.connect(self.reg.pwr_out, self.pwr_out)


class LipoCharger(Block):
    @init_in_parent
    def __init__(self, charging_current:RangeLike) -> None:
        super().__init__()
        self.charging_current = self.ArgParameter(charging_current)

        self.chg = self.Port(VoltageSource.empty(), [Output])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.vusb = self.Port(VoltageSink().empty(), [Power, Input])

    def contents(self):
        super().contents()
        # POWER
        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.charger, ), _ = self.chain(
                self.vusb, imp.Block(Mcp73831(self.charging_current)), self.chg
            )
            (self.charge_led, ), _ = self.chain(
                self.Block(IndicatorSinkLed(Led.Yellow)), self.charger.stat
            )
            self.connect(self.vusb, self.charge_led.pwr)


