from ..electronics_model import *
from .Resettable import Resettable
from .AbstractResistor import Resistor, SeriesPowerResistor
from .AbstractFets import SwitchFet, Fet
from .AbstractCapacitor import Capacitor
from .GateDrivers import HalfBridgeDriver, HalfBridgeDriverIndependent, HalfBridgeDriverPwm
from .DigitalAmplifiers import HighSideSwitch
from .ResistiveDivider import VoltageDivider, ResistiveDivider
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

    def generate(self) -> None:
        super().generate()
        self.connect(self.pwm_ctl, self.driver.with_mixin(HalfBridgeDriverPwm()).pwm_in)
        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.driver.with_mixin(Resettable()).reset)


class RampLimiter(KiCadSchematicBlock):
    """PMOS-based ramp limiter that roughly targets a constant-dV/dt ramp.
    The cgd should be specified to swamp (10x+) the parasitic Cgd of the FET to get more controlled parameters.
    The target ramp rate is in volts/second, and for a capacitive load this can be calculated from a target current with
      I = C * dV/dt  => dV/dt = I / C
    The actual ramp rate will vary substantially, the values calculated are based on many assertions.

    A target Vgs can also be specified, this is the final Vgs of the FET after the ramp completes.
    The FET will be constrained to have a Vgs,th below the minimum of this range and a Vgs,max above the maximum.

    A capacitive divider with Cgs will be generated so the target initial Vgs at less than half the FET Vgs,th
    (targeting half Vgs,th at Vin,max).

    TODO: allow control to be optional, eliminating the NMOS with a short

    HOW THIS WORKS:
    When the input voltage rises, the capacitive divider of Cgs, Cgd brings the gate to a subthreshold voltage.
    The gate voltage charges via the divider until it gets to the threshold voltage.
    At around the threshold voltage, the FET begins to turn on, with current flowing into (and charging) the output.
    As the output rises, Cgd causes the gate to be pulled up with the output, keeping Vgs roughly constant.
      (this also keeps the current roughly constant, mostly regardless of transconductance)
    During this stage, if we assume Vgs is constant, then Cgs is constant and can be disregarded.
    For the output to rise, Vgd must rise, which means Cgd must charge, and the current must go through the divider.
    Assuming a constant Vgs (and absolute gate voltage), the current into the divider is constant,
    and this is how the voltage ramp rate is controlled.
    Once the output gets close to the input voltage, Cgd stops charging and Vgs rises, turning the FET fully on.

    Note that Vgs,th is an approximate parameter and the ramp current is likely larger than the Vgs,th current.
    Vgs also may rise during the ramp, meaning some current goes into charging Cgs.

    References: https://www.ti.com/lit/an/slva156/slva156.pdf, https://www.ti.com/lit/an/slyt096/slyt096.pdf,
                https://youtu.be/bOka13RtOXM

    Additional more complex circuits
    https://electronics.stackexchange.com/questions/294061/p-channel-mosfet-inrush-current-limiting
    """
    def __init__(self, *, cgd: RangeLike = 10*nFarad(tol=0.5), target_ramp: RangeLike = 1000*Volt(tol=0.25),
                 target_vgs: RangeLike = (4, 10)*Volt, max_rds: FloatLike = 1*Ohm,
                 _cdiv_vgs_factor: RangeLike = (0.05, 0.75)):
        super().__init__()

        self.gnd = self.Port(Ground.empty(), [Common])
        self.pwr_in = self.Port(VoltageSink.empty(), [Input])
        self.pwr_out = self.Port(VoltageSource.empty(), [Output])
        self.control = self.Port(DigitalSink.empty())

        self.cgd = self.ArgParameter(cgd)
        self.target_ramp = self.ArgParameter(target_ramp)
        self.target_vgs = self.ArgParameter(target_vgs)
        self.max_rds = self.ArgParameter(max_rds)
        self._cdiv_vgs_factor = self.ArgParameter(_cdiv_vgs_factor)

    def contents(self):
        super().contents()

        pwr_voltage = self.pwr_in.link().voltage
        self.drv = self.Block(SwitchFet.PFet(
            drain_voltage=pwr_voltage,
            drain_current=self.pwr_out.link().current_drawn,
            gate_voltage=(0 * Volt(tol=0)).hull(self.target_vgs.upper()),
            gate_threshold_voltage=(0 * Volt(tol=0)).hull(self.target_vgs.lower()),
            rds_on=(0, self.max_rds)
        ))

        self.cap_gd = self.Block(Capacitor(
            capacitance=self.cgd,
            voltage=(0 * Volt(tol=0)).hull(self.pwr_in.link().voltage)
        ))
        # treat Cgs and Cgd as a capacitive divider with Cgs on the bottom
        self.cap_gs = self.Block(Capacitor(
            capacitance=(
                    (1/(self.drv.actual_gate_drive.lower()*self._cdiv_vgs_factor)).shrink_multiply(self.pwr_in.link().voltage) - 1
            ).shrink_multiply(
                self.cap_gd.actual_capacitance
            ),
            voltage=(0 * Volt(tol=0)).hull(self.pwr_in.link().voltage)
        ))
        # dV/dt over a capacitor is I / C => I = Cgd * dV/dt
        # then calculate to get the target I: Vgs,th = I * Reff => Reff = Vgs,th / I = Vgs,th / (Cgd * dV/dt)
        # we assume Vgs,th is exact, and only contributing sources come from elsewhere
        self.div = self.Block(ResistiveDivider(ratio=self.target_vgs.shrink_multiply(1/self.pwr_in.link().voltage),
                                               impedance=(1 / self.target_ramp).shrink_multiply(self.drv.actual_gate_drive.lower() / (self.cap_gd.actual_capacitance))
                                               ))
        div_current_draw = (self.pwr_in.link().voltage/self.div.actual_impedance).hull(0)
        self.ctl_fet = self.Block(SwitchFet.NFet(
            drain_voltage=pwr_voltage,
            drain_current=div_current_draw,
            gate_voltage=(self.control.link().output_thresholds.upper(), self.control.link().voltage.upper())
        ))

        self.import_kicad(
            self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
            conversions={
                'pwr_in': VoltageSink(
                    current_draw=self.pwr_out.link().current_drawn + div_current_draw
                ),
                'pwr_out': VoltageSource(
                    voltage_out=self.pwr_in.link().voltage
                ),
                'control': DigitalSink(),
                'gnd': Ground(),
            })
