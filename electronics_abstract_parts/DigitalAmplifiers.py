from electronics_model import *
from .AbstractFets import SwitchNFet, SwitchPFet
from .AbstractPassives import Resistor


class HighSideSwitch(Block):
  @init_in_parent
  def __init__(self, pull_resistance: RangeLike = 10000*Ohm(tol=0.01), max_rds: FloatLike = 1 * Ohm,
               frequency: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSink(), [Power])  # amplifier voltage
    self.gnd = self.Port(Ground(), [Common])

    self.control = self.Port(DigitalSink(  # logic voltage
      current_draw=(0, 0) * Amp  # TODO model pullup resistor current
      # no voltage limits or threshold, those are constraints to pass into the FETs
    ), [Input])
    self.output = self.Port(DigitalSource(
      voltage_out=(0, self.pwr.link().voltage.upper()),
      # no current limits, current draw is set by the connected load
      output_thresholds=(0, self.pwr.link().voltage.upper()),
    ), [Output])

    self.pull_resistance = self.Parameter(RangeExpr(pull_resistance))
    self.max_rds = self.Parameter(FloatExpr(max_rds))
    self.frequency = self.Parameter(RangeExpr(frequency))

    pwr_voltage = self.pwr.link().voltage
    out_current = self.output.link().current_drawn
    pull_resistance = self.pull_resistance
    pull_current_max = pwr_voltage.upper() / pull_resistance.lower()
    pull_power_max = pwr_voltage.upper() * pwr_voltage.upper() / pull_resistance.lower()

    gate_voltage = (3.0, 3.0) #(self.get(self.control.link().voltage)[1],  # TODO with better const prop we should use output_threshold[1]
    # self.get(self.control.link().voltage)[1])

    low_amp_rds_max = pull_resistance.lower() / 1000

    self.pre = self.Block(SwitchNFet(
      drain_voltage=pwr_voltage,
      drain_current=(0, pull_current_max),
      gate_voltage=gate_voltage,
      rds_on=(0, low_amp_rds_max),  # TODO size on turnon time
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=self.control.link().current_limits  # TODO this is kind of a max drive current
    ))
    self.connect(self.pre.source.as_ground(), self.gnd)
    self.connect(self.pre.gate.as_digital_sink(), self.control)

    self.pull = self.Block(Resistor(
      resistance=pull_resistance,
      power=(0, pull_power_max)
    ))
    self.connect(self.pull.a.as_electrical_sink(), self.pwr)

    self.drv = self.Block(SwitchPFet(
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
    self.connect(self.drv.source.as_electrical_sink(
      current_draw=self.output.link().current_drawn
    ), self.pwr)
    self.connect(self.drv.drain.as_digital_source(), self.output)
    self.connect(self.pre.drain.as_digital_source(), self.drv.gate.as_digital_sink(), self.pull.b.as_digital_bidir())


class HalfBridgeNFet(GeneratorBlock):
  @init_in_parent
  def __init__(self, max_rds: FloatLike = 1*Ohm, frequency: RangeLike = RangeExpr()) -> None:
    super().__init__()  # TODO MODEL ALL THESE
    self.pwr = self.Port(ElectricalSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.gate_high = self.Port(DigitalSink(
      current_draw=(0, 0)*Amp  # voltage limits and thresholds are passed through to the FETs
    ))
    self.gate_low = self.Port(DigitalSink(
      current_draw=(0, 0)*Amp  # voltage limits and thresholds are passed through to the FETs
    ))

    self.output = self.Port(DigitalSource.from_supply(self.gnd, self.pwr))  # current limits from supply

    self.max_rds = self.Parameter(FloatExpr(max_rds))
    self.frequency = self.Parameter(RangeExpr(frequency))

  def generate(self) -> None:
    super().generate()

    pwr_voltage = self.get(self.pwr.link().voltage)
    out_current = self.get(self.output.link().current_drawn)
    assert out_current[0] <= 0, "lower range of output current must be negative (sinking) current"
    assert out_current[1] >= 0, "upper range of output current must be positive (sourcing) current"

    gate_voltage = (5.0, 5.0) #(self.get(self.control.link().voltage)[1],  # TODO with better const prop we should use output_threshold[1]
                    # self.get(self.control.link().voltage)[1])
    max_rds = self.get(self.max_rds)

    self.high = self.Block(SwitchNFet(
      drain_voltage=pwr_voltage * Volt,
      drain_current=(0, out_current[1]) * Amp,
      gate_voltage=gate_voltage * Volt,
      rds_on=(0, max_rds) * Ohm,
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=self.gate_high.link().current_limits  # TODO this is kind of a max drive current
    ))
    self.low = self.Block(SwitchNFet(
      drain_voltage=pwr_voltage * Volt,
      drain_current=(0, -out_current[0]) * Amp,
      gate_voltage=gate_voltage * Volt,
      rds_on=(0, max_rds) * Ohm,
      gate_charge=(0, float('inf')),  # TODO size on turnon time
      power=(0, 0) * Watt,
      frequency=self.frequency,
      drive_current=self.gate_low.link().current_limits  # TODO this is kind of a max drive current
    ))
    self.connect(self.gnd, self.low.source.as_electrical_sink())
    self.connect(self.gate_low, self.low.gate.as_digital_sink())
    self.connect(self.output,
                 self.low.drain.as_digital_bidir(),
                 self.high.source.as_digital_bidir())
    self.connect(self.gate_high, self.high.gate.as_digital_sink())
    self.connect(self.pwr, self.high.drain.as_electrical_sink())
    self.constrain(self.output.current_limits == (  # from individual FET ratings to sink/source currents
      -1 * self.low.drain_current.upper(),
      self.high.drain_current.upper()))
    self.constrain(self.pwr.current_draw == (  # from sink/source current to source only
      0,
      self.output.link().current_drawn.upper().max(-1 * self.output.link().current_drawn.lower())))
