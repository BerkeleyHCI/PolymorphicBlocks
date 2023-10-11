from electronics_model import *
from .AbstractFets import SwitchFet, Fet
from .GateDrivers import HalfBridgeDriver


@abstract_block_default(lambda: FetHalfBridge)
class HalfBridge(Block):
    """Half bridge circuit with logic-level inputs and current draw calculated from the output node.
    Two power rails: logic power (which can be used to power gate drivers), and the power rail."""
    def __init__(self):
        super().__init__()

        self.gnd = self.Port(Ground.empty())
        self.pwr = self.Port(VoltageSink.empty())
        self.out = self.Port(VoltageSource.empty())  # TODO should be DigitalSource?

        self.pwr_logic = self.Port(VoltageSink.empty())
        self.low_ctl = self.Port(DigitalSink.empty())
        self.high_ctl = self.Port(DigitalSink.empty())


class FetHalfBridge(HalfBridge):
    """Implementation of a half-bridge with two NFETs and a gate driver."""
    @init_in_parent
    def __init__(self, frequency: RangeLike, fet_rds: RangeLike = (0, 1)*Ohm):
        super().__init__()
        self.frequency = self.ArgParameter(frequency)
        self.fet_rds = self.ArgParameter(fet_rds)

    def contents(self):
        super().contents()
        self.driver = self.Block(HalfBridgeDriver(has_boot_diode=True))
        self.connect(self.driver.gnd, self.gnd)
        self.connect(self.driver.pwr, self.pwr_logic)
        self.connect(self.low_ctl, self.driver.low_in)
        self.connect(self.high_ctl, self.driver.high_in)

        self.low_fet = self.Block(SwitchFet.NFet(
            drain_voltage=self.pwr.link().voltage,
            drain_current=(0, self.out.link().current_drawn.upper()),
            gate_voltage=self.driver.low_out.link().voltage,
            rds_on=self.fet_rds,
            frequency=self.frequency,
            drive_current=self.driver.low_out.link().current_limits
        ))
        self.connect(self.low_fet.source.adapt_to(Ground()), self.gnd)
        self.connect(self.low_fet.gate.adapt_to(DigitalSink()), self.driver.low_out)

        self.high_fet = self.Block(SwitchFet.NFet(
            drain_voltage=self.pwr.link().voltage,
            drain_current=(0, self.out.link().current_drawn.upper()),
            gate_voltage=self.driver.high_out.link().voltage - self.driver.high_gnd.link().voltage,
            rds_on=self.fet_rds,
            frequency=self.frequency,
            drive_current=self.driver.high_out.link().current_limits
        ))
        self.connect(self.high_fet.drain.adapt_to(VoltageSink(
            voltage_limits=self.high_fet.actual_drain_voltage_rating,
            current_draw=self.out.link().current_drawn
        )), self.pwr)
        self.connect(self.high_fet.gate.adapt_to(DigitalSink()), self.driver.high_out)

        # to avoid tolerance stackup, model the switch node as a static voltage
        self.connect(self.low_fet.drain.adapt_to(VoltageSource(
                voltage_out=self.pwr.link().voltage)),
            self.high_fet.source.adapt_to(VoltageSink()),
            self.driver.high_gnd,
            self.out)
