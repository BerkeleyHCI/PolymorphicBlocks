from electronics_model import *
from .AbstractFets import SwitchFet
from .GateDrivers import HalfBridgeDriver


@abstract_block_default(lambda: FetHalfBridge)
class HalfBridge(Block):
    """Half bridge circuit with logic-level inputs and current draw calculated from the output node.
    Two power rails: logic power (which can be used to power gate drivers), and the power rail."""
    def __init__(self):
        super().__init__()

        self.gnd = self.Port(Ground.empty())
        self.pwr = self.Port(VoltageSink.empty())
        self.out = self.Port(DigitalSource.empty())

        self.pwr_logic = self.Port(VoltageSink.empty())
        self.low_ctl = self.Port(DigitalSink.empty())
        self.high_ctl = self.Port(DigitalSink.empty())


class FetHalfBridge(HalfBridge):
    """Implementation of a half-bridge with two NFETs and a gate driver."""
    @init_in_parent
    def __init__(self, frequency: RangeLike = Range.all(), fet_rds: RangeLike = (0, 1)*Ohm):
        super().__init__()
        self.frequency = self.ArgParameter(frequency)
        self.fet_rds = self.ArgParameter(fet_rds)


    def contents(self):
        super().contents()

        self.gate = self.Block(HalfBridgeDriver(has_boot_diode=True))
        self.connect(self.gate.gnd, self.gnd)
        self.connect(self.gate.pwr, self.pwr_logic)
        self.connect(self.low_ctl, self.gate.low_in)
        self.connect(self.high_ctl, self.gate.high_in)

        self.high = self.Block(SwitchFet.NFet(
            drain_voltage=self.pwr.link().voltage,
            drain_current=(0, self.out.link().current_drawn.upper()),
            gate_voltage=self.gate.high_out.link().voltage,
            rds_on=self.fet_rds,
            frequency=self.frequency,
            drive_current=self.gate.high_out.link().current_limits
        ))
        self.low = self.Block(SwitchFet.NFet(
            drain_voltage=self.pwr.link().voltage,
            drain_current=(0, self.out.link().current_drawn.upper()),
            gate_voltage=self.gate.low_out.link().voltage,
            rds_on=self.fet_rds,
            frequency=self.frequency,
            drive_current=self.gate.low_out.link().current_limits
        ))
