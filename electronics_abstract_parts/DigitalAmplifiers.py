from electronics_model import *
from .AbstractFets import SwitchFet
from .AbstractResistor import Resistor
from .Categories import PowerSwitch


class HighSideSwitch(PowerSwitch, Block):
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

    pwr_voltage = self.pwr.link().voltage
    out_current = self.output.link().current_drawn
    pull_resistance = self.pull_resistance
    pull_current_max = pwr_voltage.upper() / pull_resistance.lower()
    pull_power_max = pwr_voltage.upper() * pwr_voltage.upper() / pull_resistance.lower()

    gate_voltage = (3.0, 3.0) #(self.get(self.control.link().voltage)[1],  # TODO with better const prop we should use output_threshold[1]
    # self.get(self.control.link().voltage)[1])

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
    self.connect(self.pre.source.adapt_to(Ground()), self.gnd)
    self.connect(self.pre.gate.adapt_to(DigitalSink(
      current_draw=(0, 0) * Amp  # TODO model pullup resistor current
      # no voltage limits or threshold, those are constraints to pass into the FETs
    )), self.control)

    self.pull = self.Block(Resistor(
      resistance=pull_resistance,
      power=(0, pull_power_max)
    ))
    self.connect(self.pull.a.adapt_to(VoltageSink()), self.pwr)

    self.drv = self.Block(SwitchFet.PFet(
      drain_voltage=pwr_voltage,
      drain_current=out_current,
      gate_voltage=pwr_voltage,
      rds_on=(0, self.max_rds),
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=(-1 * pwr_voltage.lower() / pull_resistance.upper(),
                     pwr_voltage.lower() / low_amp_rds_max)  # TODO simultaneously solve both FETs
    ))
    self.connect(self.drv.source.adapt_to(VoltageSink(
      current_draw=self.output.link().current_drawn
    )), self.pwr)
    self.connect(self.drv.drain.adapt_to(DigitalSource(
      voltage_out=(0, self.pwr.link().voltage.upper()),
      current_limits=self.drv.actual_drain_current_rating,
      output_thresholds=(0, self.pwr.link().voltage.upper()),
    )), self.output)
    self.connect(self.pre.drain.adapt_to(DigitalSource()),
                 self.drv.gate.adapt_to(DigitalSink()),
                 self.pull.b.adapt_to(DigitalBidir()))


class HalfBridgeNFet(PowerSwitch, Block):
  @init_in_parent
  def __init__(self, max_rds: FloatLike = 1*Ohm, frequency: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()  # TODO MODEL ALL THESE
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.gate_high = self.Port(DigitalSink.empty())
    self.gate_low = self.Port(DigitalSink.empty())

    self.output = self.Port(DigitalSource.empty())  # current limits from supply

    self.max_rds = self.ArgParameter(max_rds)
    self.frequency = self.ArgParameter(frequency)

    pwr_voltage = self.pwr.link().voltage
    out_current = self.output.link().current_drawn
    self.require(out_current.lower() <= 0, "lower range of output current must be negative (sinking) current")
    self.require(out_current.upper() >= 0, "upper range of output current must be positive (sourcing) current")

    gate_voltage = (5.0, 5.0) * Volt #(self.get(self.control.link().voltage)[1],  # TODO with better const prop we should use output_threshold[1]
                    # self.get(self.control.link().voltage)[1])
    max_rds = self.max_rds

    self.high = self.Block(SwitchFet.NFet(
      drain_voltage=pwr_voltage,
      drain_current=(0, out_current.upper()),
      gate_voltage=gate_voltage,
      rds_on=(0, max_rds),
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=self.gate_high.link().current_limits  # TODO this is kind of a max drive current
    ))
    self.low = self.Block(SwitchFet.NFet(
      drain_voltage=pwr_voltage,
      drain_current=(0, -1 * out_current.lower()),
      gate_voltage=gate_voltage,
      rds_on=(0, max_rds),
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=self.gate_low.link().current_limits  # TODO this is kind of a max drive current
    ))
    self.connect(self.gnd, self.low.source.adapt_to(Ground()))
    self.connect(self.gate_low, self.low.gate.adapt_to(DigitalSink(
      current_draw=(0, 0)*Amp  # voltage limits and thresholds are passed through to the FETs
    )))
    self.connect(self.output,
                 self.low.drain.adapt_to(DigitalBidir(
                   voltage_out=(self.gnd.link().voltage.lower(), self.pwr.link().voltage.upper()),
                   current_limits=(-1 * self.low.drain_current.upper(), self.high.drain_current.upper()),
                   output_thresholds=(self.gnd.link().voltage.upper(), self.pwr.link().voltage.lower())
                 )),
                 self.high.source.adapt_to(DigitalBidir(
                   # unmodeled, the parameters are modeled by the low side FET
                 )))
    self.connect(self.gate_high, self.high.gate.adapt_to(DigitalSink(
      current_draw=(0, 0)*Amp  # voltage limits and thresholds are passed through to the FETs
    )))
    self.connect(self.pwr, self.high.drain.adapt_to(VoltageSink(
      current_draw=(0,  # from sink/source current to source only
                    self.output.link().current_drawn.upper().max(-1 * self.output.link().current_drawn.lower()))
    )))


class OpenDrainDriver(Block):
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
