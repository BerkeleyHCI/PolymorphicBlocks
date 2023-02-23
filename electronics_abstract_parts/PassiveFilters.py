from math import pi
from typing import Optional, cast, List

from electronics_model import *
from .AbstractResistor import Resistor
from .AbstractCapacitor import Capacitor
from .Categories import *


class LowPassRc(AnalogFilter, GeneratorBlock):
  """Passive-typed low-pass RC specified by the resistor value (impedance) and -3dB (~70%) cutoff frequency."""
  @init_in_parent
  def __init__(self, impedance: RangeLike, cutoff_freq: RangeLike,
               voltage: RangeLike):
    super().__init__()
    self.impedance = self.ArgParameter(impedance)
    self.cutoff_freq = self.ArgParameter(cutoff_freq)
    self.voltage = self.ArgParameter(voltage)

    self.input = self.Port(Passive.empty())
    self.output = self.Port(Passive.empty())
    self.gnd = self.Port(Passive.empty())

    self.generator(self.generate_rc, self.cutoff_freq, self.impedance)

  def generate_rc(self, cutoff_freq: Range, impedance: Range) -> None:
    self.r = self.Block(Resistor(resistance=self.impedance))  # TODO maybe support power?
    # cutoff frequency is 1/(2 pi R C)
    capacitance = Range.cancel_multiply(1 / (2 * pi * impedance), 1 / cutoff_freq)

    self.c = self.Block(Capacitor(capacitance=capacitance*Farad, voltage=self.voltage))
    self.connect(self.input, self.r.a)
    self.connect(self.r.b, self.c.pos, self.output)  # TODO support negative voltages?
    self.connect(self.c.neg, self.gnd)


class PullupDelayRc(DigitalFilter, Block):
  """Pull-up resistor with capacitor for delay.
  """
  @init_in_parent
  def __init__(self, impedance: RangeLike, time_constant: RangeLike):
    super().__init__()
    self.input = self.Port(VoltageSink.empty(), [Power])
    self.time_constant = self.ArgParameter(time_constant)

    self.rc = self.Block(LowPassRc(impedance=impedance, cutoff_freq=1/(2 * pi * self.time_constant),
                                   voltage=self.input.link().voltage))

    self.connect(self.input, self.rc.input.adapt_to(VoltageSink()))
    self.io = self.Export(self.rc.output.adapt_to(DigitalSingleSource.high_from_supply(self.input)), [Output])
    self.gnd = self.Export(self.rc.gnd.adapt_to(Ground()), [Common])

  def connected(self, io: Optional[Port[DigitalLink]] = None) -> 'PullupDelayRc':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if io is not None:
      cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalLowPassRc(DigitalFilter, Block):
  """Low-pass RC filter attached to a digital line.
  Does not change the signal, only performs filtering
  """
  @init_in_parent
  def __init__(self, impedance: RangeLike, cutoff_freq: RangeLike):
    super().__init__()
    self.input = self.Port(DigitalSink.empty(), [Input])
    self.output = self.Port(DigitalSource.empty(), [Output])

    self.rc = self.Block(LowPassRc(impedance=impedance, cutoff_freq=cutoff_freq,
                                   voltage=self.input.link().voltage))
    self.connect(self.input, self.rc.input.adapt_to(DigitalSink(
      current_draw=self.output.link().current_drawn
    )))
    self.connect(self.output, self.rc.output.adapt_to(DigitalSource(
      current_limits=RangeExpr.ALL,
      voltage_out=self.input.link().voltage,
      output_thresholds=self.input.link().output_thresholds
    )))

    self.gnd = self.Export(self.rc.gnd.adapt_to(Ground()), [Common])


class DigitalLowPassRcArray(DigitalFilter, GeneratorBlock):
  """Array of DigitalLowPassRc, currently takes its size from the output.
  TODO: properly size when either input or output is sized?
  """
  @init_in_parent
  def __init__(self, impedance: RangeLike, cutoff_freq: RangeLike):
    super().__init__()
    self.input = self.Port(Vector(DigitalSink.empty()), [Input])
    self.output = self.Port(Vector(DigitalSource.empty()), [Output])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.impedance = self.ArgParameter(impedance)
    self.cutoff_freq = self.ArgParameter(cutoff_freq)

    self.generator(self.generate, self.output.requested())

  def generate(self, outputs: List[str]):
    self.elts = ElementDict[DigitalLowPassRc]()
    model = DigitalLowPassRc(self.impedance, self.cutoff_freq)
    for requested in outputs:
      self.elts[requested] = elt = self.Block(model)
      self.connect(self.input.append_elt(DigitalSink.empty(), requested), elt.input)
      self.connect(self.output.append_elt(DigitalSource.empty(), requested), elt.output)
      self.connect(self.gnd, elt.gnd)


class LowPassRcDac(DigitalToAnalog, Block):
  """Low-pass RC filter used as a simple DAC by filtering out a PWM signal.
  The cutoff frequency of the filter should be sufficiently beneath the PWM frequency,
  but enough above baseband to not distort the signal.
  Lower frequencies will result in either higher impedance or larger caps.
  This must be manually specified, since PWM frequency data is not part of the electronics model.
  """
  @init_in_parent
  def __init__(self, impedance: RangeLike, cutoff_freq: RangeLike):
    super().__init__()
    self.input = self.Port(DigitalSink.empty(), [Input])
    self.output = self.Port(AnalogSource.empty(), [Output])

    self.rc = self.Block(LowPassRc(impedance=impedance, cutoff_freq=cutoff_freq,
                                   voltage=self.input.link().voltage))
    self.connect(self.input, self.rc.input.adapt_to(DigitalSink(
      current_draw=self.output.link().current_drawn
    )))
    self.connect(self.output, self.rc.output.adapt_to(AnalogSource(
      current_limits=RangeExpr.ALL,
      voltage_out=self.input.link().voltage,
      impedance=impedance  # TODO use selected resistance from RC filter
    )))

    self.gnd = self.Export(self.rc.gnd.adapt_to(Ground()), [Common])
