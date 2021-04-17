from typing import *

from math import pi

from electronics_model import *
from .AbstractPassives import Resistor, Capacitor
from .Categories import *


class LowPassRc(AnalogFilter, GeneratorBlock):
  @init_in_parent
  def __init__(self, impedance: RangeLike = RangeExpr(), cutoff_freq: RangeLike = RangeExpr(),
               voltage: RangeLike = RangeExpr()):
    super().__init__()
    self.impedance = self.Parameter(RangeExpr(impedance))
    self.cutoff_freq = self.Parameter(RangeExpr(cutoff_freq))
    self.voltage = self.Parameter(RangeExpr(voltage))

    self.input = self.Port(Passive())
    self.output = self.Port(Passive())
    self.gnd = self.Port(Passive())

    self.generator(self.generate_rc, self.cutoff_freq, self.impedance)

  def generate_rc(self, cutoff_freq: RangeVal, impedance: RangeVal) -> None:
    super().generate()
    self.r = self.Block(Resistor(resistance=self.impedance))  # TODO maybe support power?
    # cutoff frequency is 1/(2 pi R C)
    f_min, f_max = cutoff_freq
    r_min, r_max = impedance
    c_min = 1 / (2 * pi * r_min * f_max)
    c_max = 1 / (2 * pi * r_max * f_min)
    assert c_min <= c_max, "tighter cutoff frequency tolerance than resistor tolerance"

    self.c = self.Block(Capacitor(capacitance=(c_min, c_max)*Farad, voltage=self.voltage))
    self.connect(self.input, self.r.a)
    self.connect(self.r.b, self.c.pos, self.output)  # TODO support negative voltages?
    self.connect(self.c.neg, self.gnd)


class DigitalLowPassRc(DigitalFilter, Block):
  @init_in_parent
  def __init__(self, impedance: RangeLike = RangeExpr(), cutoff_freq: RangeLike = RangeExpr()):
    super().__init__()
    self.rc = self.Block(LowPassRc(impedance=impedance, cutoff_freq=cutoff_freq))
    self.input = self.Export(self.rc.input.as_digital_sink(
      current_draw=RangeExpr()
    ), [Input])
    self.output = self.Export(self.rc.output.as_digital_source(
      current_limits=RangeExpr.ALL,
      voltage_out=self.input.link().voltage,
      output_thresholds=self.input.link().output_thresholds
    ), [Output])
    self.assign(self.input.current_draw, self.output.link().current_drawn)

    self.assign(self.rc.voltage, self.input.link().voltage)

    self.gnd = self.Export(self.rc.gnd.as_ground(), [Common])
