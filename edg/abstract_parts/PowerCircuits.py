from ..electronics_model import *
from .Resettable import Resettable
from .AbstractResistor import Resistor, SeriesPowerResistor
from .AbstractFets import SwitchFet
from .GateDrivers import HalfBridgeDriver, HalfBridgeDriverIndependent, HalfBridgeDriverPwm
from .DigitalAmplifiers import HighSideSwitch
from .Categories import PowerConditioner
from .MergedBlocks import MergedVoltageSource
from .DummyDevices import ForcedVoltageCurrentDraw


@abstract_block_default(lambda: FetHalfBridgeIndependent)
class HalfBridge(PowerConditioner, Block):
    """Half bridge circuit with logic-level inputs and current draw calculated from the output node.
    Two power rails: logic power (which can be used to power gate drivers), and the power rail."""
    def __init__(self):
        super().__init__()

        self.gnd = self.Port(Ground.empty())
        self.pwr = self.Port(VoltageSink.empty())
        self.out = self.Port(VoltageSource.empty())  # TODO should be DigitalSource?

        self.pwr_logic = self.Port(VoltageSink.empty())


@abstract_block_default(lambda: FetHalfBridgeIndependent)
class HalfBridgeIndependent(BlockInterfaceMixin[HalfBridge]):
    def __init__(self):
        super().__init__()
        self.low_ctl = self.Port(DigitalSink.empty())
        self.high_ctl = self.Port(DigitalSink.empty())


@abstract_block_default(lambda: FetHalfBridgePwmReset)
class HalfBridgePwm(BlockInterfaceMixin[HalfBridge]):
    def __init__(self):
        super().__init__()
        self.pwm_ctl = self.Port(DigitalSink.empty())


@abstract_block
class FetHalfBridge(HalfBridge):
    """Implementation of a half-bridge with two NFETs and a gate driver."""
    @init_in_parent
    def __init__(self, frequency: RangeLike, fet_rds: RangeLike = (0, 1)*Ohm,
                 gate_res: RangeLike = 22*Ohm(tol=0.05)):
        super().__init__()
        self.frequency = self.ArgParameter(frequency)
        self.fet_rds = self.ArgParameter(fet_rds)
        self.gate_res = self.ArgParameter(gate_res)

        self.actual_current_limits = self.Parameter(RangeExpr())

    def contents(self):
        super().contents()
        self.driver = self.Block(HalfBridgeDriver(has_boot_diode=True))
        self.connect(self.driver.gnd, self.gnd)
        self.connect(self.driver.pwr, self.pwr_logic)

        gate_res_model = Resistor(self.gate_res)

        self.low_fet = self.Block(SwitchFet.NFet(
            drain_voltage=self.pwr.link().voltage,
            drain_current=(0, self.out.link().current_drawn.upper()),
            gate_voltage=self.driver.low_out.link().voltage,
            rds_on=self.fet_rds,
            frequency=self.frequency,
            drive_current=self.driver.low_out.link().current_limits
        ))
        self.connect(self.low_fet.source.adapt_to(Ground()), self.gnd)
        self.low_gate_res = self.Block(gate_res_model)
        self.connect(self.low_gate_res.a.adapt_to(DigitalSink(
            current_draw=self.low_fet.actual_gate_charge * self.frequency.hull((0, 0))
        )), self.driver.low_out)
        self.connect(self.low_gate_res.b, self.low_fet.gate)

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
        self.high_gate_res = self.Block(gate_res_model)
        self.connect(self.high_gate_res.a.adapt_to(DigitalSink(
            current_draw=self.high_fet.actual_gate_charge * self.frequency.hull((0, 0))
        )), self.driver.high_out)
        self.connect(self.high_gate_res.b, self.high_fet.gate)

        # to avoid tolerance stackup, model the switch node as a static voltage
        self.connect(self.low_fet.drain, self.high_fet.source)
        self.connect(self.low_fet.drain.adapt_to(VoltageSource(
            voltage_out=self.pwr.link().voltage)),
            self.out)
        self.connect(self.out.as_ground((0, 0)*Amp), self.driver.high_gnd)  # TODO model driver current

        self.assign(self.actual_current_limits, self.low_fet.actual_drain_current_rating.intersect(
            self.high_fet.actual_drain_current_rating))


class FetHalfBridgeIndependent(FetHalfBridge, HalfBridgeIndependent):
    def contents(self):
        super().contents()
        driver_mixin = self.driver.with_mixin(HalfBridgeDriverIndependent())
        self.connect(self.low_ctl, driver_mixin.low_in)
        self.connect(self.high_ctl, driver_mixin.high_in)


class FetHalfBridgePwmReset(FetHalfBridge, HalfBridgePwm, Resettable, GeneratorBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator_param(self.reset.is_connected())

    def generate(self):
        super().generate()
        self.connect(self.pwm_ctl, self.driver.with_mixin(HalfBridgeDriverPwm()).pwm_in)
        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.driver.with_mixin(Resettable()).reset)


class FetPrecharge(Block):
    """Precharge circuit that limits inrush current with an resistor, then provides low supply impedance
    by closing a power FET.

    TODO: calculate power rating needed for some capacitance instead of spec'ing for DC"""
    @init_in_parent
    def __init__(self, *, precharge_resistance: RangeLike = 100*Ohm(tol=0.1),
                 pull_resistance: RangeLike = 10*kOhm(tol=0.05),
                 max_rds: FloatLike = 1*Ohm, clamp_voltage: RangeLike = RangeExpr.ZERO):
        super().__init__()
        self.gnd = self.Port(Ground.empty(), [Common])
        self.pwr_in = self.Port(VoltageSink.empty(), [Input, Power])
        self.pwr_out = self.Port(VoltageSource.empty(), [Output])
        self.control = self.Port(DigitalSink.empty())

        self.precharge_resistance = self.ArgParameter(precharge_resistance)
        self.pull_resistance = self.ArgParameter(pull_resistance)
        self.max_rds = self.ArgParameter(max_rds)
        self.clamp_voltage = self.ArgParameter(clamp_voltage)

    def contents(self):
        super().contents()

        self.switch = self.Block(HighSideSwitch(
            pull_resistance=self.pull_resistance, max_rds=self.max_rds, clamp_voltage=self.clamp_voltage))
        self.connect(self.switch.gnd, self.gnd)
        self.connect(self.switch.pwr, self.pwr_in)
        self.connect(self.switch.control, self.control)

        (self.res_forcein, self.res, self.res_forceout), _ = self.chain(
            self.pwr_in,
            self.Block(ForcedVoltageCurrentDraw(0*Amp(tol=0))),  # current draw modeled by switch
            self.Block(SeriesPowerResistor(resistance=self.precharge_resistance)),
            self.Block(ForcedVoltageCurrentDraw(
                VoltageLink._supply_voltage_range(self.gnd, self.pwr_in) / self.precharge_resistance)),
        )

        self.merge = self.Block(MergedVoltageSource()).connected_from(
            self.switch.output, self.res_forceout.pwr_out
        )
        self.connect(self.merge.pwr_out, self.pwr_out)
