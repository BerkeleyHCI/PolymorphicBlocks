from electronics_model import *
from .AbstractFets import SwitchFet
from .AbstractResistor import Resistor
from .Categories import PowerSwitch


class HighSideSwitch(PowerSwitch, KiCadSchematicBlock):
  @init_in_parent
  def __init__(self, pull_resistance: RangeLike = 10000*Ohm(tol=0.01), max_rds: FloatLike = 1*Ohm,
               frequency: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])  # amplifier voltage
    self.gnd = self.Port(Ground.empty(), [Common])

    self.control = self.Port(DigitalSink.empty(), [Input])
    self.output = self.Port(DigitalSource.empty(), [Output])

    self.pull_resistance = self.ArgParameter(pull_resistance)
    self.max_rds = self.ArgParameter(max_rds)
    self.frequency = self.ArgParameter(frequency)

  def contents(self):
    super().contents()

    pwr_voltage = self.pwr.link().voltage
    pull_resistance = self.pull_resistance
    pull_current_max = pwr_voltage.upper() / pull_resistance.lower()
    pull_power_max = pwr_voltage.upper() * pwr_voltage.upper() / pull_resistance.lower()

    gate_voltage = (3.0, 3.0) #(self.get(self.control.link().voltage)[1],  # TODO with better const prop we should use output_threshold[1]

    low_amp_rds_max = pull_resistance.lower() / 1000

    self.pre = self.Block(SwitchFet.NFet(
      drain_voltage=pwr_voltage,
      drain_current=(0, pull_current_max),
      gate_voltage=gate_voltage,
      rds_on=(0, low_amp_rds_max),  # TODO size on turnon time
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=self.control.link().current_limits  # TODO this is kind of a max drive current
    ))
    self.pull = self.Block(Resistor(
      resistance=pull_resistance,
      power=(0, pull_power_max)
    ))
    self.drv = self.Block(SwitchFet.PFet(
      drain_voltage=pwr_voltage,
      drain_current=self.output.link().current_drawn,
      gate_voltage=pwr_voltage,
      rds_on=(0, self.max_rds),
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=(-1 * pwr_voltage.lower() / pull_resistance.upper(),
                     pwr_voltage.lower() / low_amp_rds_max)  # TODO simultaneously solve both FETs
    ))

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
                                     conversions={
                                       'pwr': VoltageSink(
                                         current_draw=self.output.link().current_drawn
                                       ),
                                       'output': DigitalSource(
                                         voltage_out=(0, self.pwr.link().voltage.upper()),
                                         current_limits=self.drv.actual_drain_current_rating,
                                         output_thresholds=(0, self.pwr.link().voltage.upper()),
                                       ),
                                       'control': DigitalSink(
                                         current_draw=(0, 0)*Amp  # TODO model pullup resistor current
                                         # no voltage limits or threshold, those are constraints to pass into the FETs
                                       ),
                                       'gnd': Ground(),
                                     })


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
