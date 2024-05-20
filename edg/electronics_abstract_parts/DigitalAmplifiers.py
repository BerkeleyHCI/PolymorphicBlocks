from typing import Dict

from ...electronics_model import *
from .AbstractFets import SwitchFet
from .AbstractResistor import Resistor
from .AbstractDiodes import ZenerDiode
from .Categories import PowerSwitch


class HighSideSwitch(PowerSwitch, KiCadSchematicBlock, GeneratorBlock):
  """A high-side FET switch, using a two switch architecture, a main pass PFET with a amplifier NFET to drive its gate.
  If clamp_voltage is nonzero, a zener clamp is generated to limit the PFET gate voltage.
  The clamp resistor is specified as a ratio from the pull resistance.

  TODO: clamp_voltage should be compared against the actual voltage so the clamp is automatically generated,
  but generators don't support link terms (yet?)"""
  @init_in_parent
  def __init__(self, pull_resistance: RangeLike = 10000*Ohm(tol=0.05), max_rds: FloatLike = 1*Ohm,
               frequency: RangeLike = RangeExpr.ZERO, *,
               clamp_voltage: RangeLike = RangeExpr.ZERO, clamp_resistance_ratio: FloatLike = 10) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])  # amplifier voltage
    self.gnd = self.Port(Ground.empty(), [Common])

    self.control = self.Port(DigitalSink.empty(), [Input])
    self.output = self.Port(VoltageSource.empty(), [Output])

    self.pull_resistance = self.ArgParameter(pull_resistance)
    self.max_rds = self.ArgParameter(max_rds)
    self.frequency = self.ArgParameter(frequency)

    self.clamp_voltage = self.ArgParameter(clamp_voltage)
    self.clamp_resistance_ratio = self.ArgParameter(clamp_resistance_ratio)
    self.generator_param(self.clamp_voltage)

  def generate(self):
    super().generate()

    pwr_voltage = self.pwr.link().voltage
    pull_resistance = self.pull_resistance
    pull_current_max = pwr_voltage.upper() / pull_resistance.lower()
    pull_power_max = pwr_voltage.upper() * pwr_voltage.upper() / pull_resistance.lower()

    low_amp_rds_max = pull_resistance.lower() / 1000

    self.pre = self.Block(SwitchFet.NFet(
      drain_voltage=pwr_voltage,
      drain_current=(0, pull_current_max),
      gate_voltage=(self.control.link().output_thresholds.upper(), self.control.link().voltage.upper()),
      rds_on=(0, low_amp_rds_max),  # TODO size on turnon time
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=self.control.link().current_limits  # TODO this is kind of a max drive current
    ))
    self.pull = self.Block(Resistor(
      resistance=pull_resistance,
      power=(0, pull_power_max),
      voltage=(0, pwr_voltage.upper())
    ))

    clamp_voltage = self.get(self.clamp_voltage)
    if clamp_voltage == Range(0, 0):  # no clamp
      pass_gate_voltage = pwr_voltage
    else:
      pass_gate_voltage = self.clamp_voltage

    self.drv = self.Block(SwitchFet.PFet(
      drain_voltage=pwr_voltage,
      drain_current=self.output.link().current_drawn,
      gate_voltage=pass_gate_voltage,
      rds_on=(0, self.max_rds),
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=(-1 * pwr_voltage.lower() / pull_resistance.upper(),
                     pwr_voltage.lower() / low_amp_rds_max)  # TODO simultaneously solve both FETs
    ))

    conversions: Dict[str, CircuitPort] = {
      'pwr': VoltageSink(
        current_draw=self.output.link().current_drawn
      ),
      'output': VoltageSource(
        voltage_out=self.pwr.link().voltage,
        current_limits=self.drv.actual_drain_current_rating,
      ),
      'control': DigitalSink(),  # TODO model pullup resistor current
      'gnd': Ground(),
    }

    if clamp_voltage == Range(0, 0):  # no clamp
      self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
                                       conversions=conversions)
    else:
      self.zener = self.Block(ZenerDiode(self.clamp_voltage))
      zlim_resistance = self.pull_resistance / self.clamp_resistance_ratio
      zlim_voltage_max = pwr_voltage.upper() - self.clamp_voltage.lower()
      zlim_power_max = zlim_voltage_max * zlim_voltage_max / zlim_resistance.lower()
      self.zlim = self.Block(Resistor(
        resistance=pull_resistance / self.clamp_resistance_ratio,
        power=(0, zlim_power_max),
        voltage=(0, zlim_voltage_max)
      ))
      self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}_Zener.kicad_sch"),
                        conversions=conversions)


class OpenDrainDriver(PowerSwitch, Block):
  """NFET configured as an open-drain driver. Potentially useful for voltage translation applications."""
  @init_in_parent
  def __init__(self, max_rds: FloatLike = 1*Ohm, frequency: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.control = self.Port(DigitalSink.empty(), [Input])
    self.output = self.Port(DigitalSingleSource.empty(), [Output])

    self.max_rds = self.ArgParameter(max_rds)
    self.frequency = self.ArgParameter(frequency)

  def contents(self):
    super().contents()
    
    self.drv = self.Block(SwitchFet.NFet(
      drain_voltage=self.output.link().voltage,
      drain_current=self.output.link().current_drawn,
      gate_voltage=self.control.link().voltage,
      rds_on=(0, self.max_rds),
      frequency=self.frequency,
      drive_current=self.control.link().current_limits
    ))
    self.connect(self.drv.drain.adapt_to(DigitalSingleSource.low_from_supply(self.gnd
    )), self.output)
    self.connect(self.drv.source.adapt_to(Ground()), self.gnd)
    self.connect(self.drv.gate.adapt_to(DigitalSink()),
                 self.control)
