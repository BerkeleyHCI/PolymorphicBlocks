from electronics_abstract_parts import CurrentSenseResistor, DifferentialAmplifier
from electronics_model import *


class OpampCurrentSensor(Block):
  @init_in_parent
  def __init__(self, resistance: RangeExpr, ratio: RangeExpr, input_impedance: RangeExpr):
    super().__init__()

    self.sense = self.Block(CurrentSenseResistor(
      resistance=resistance
    ))
    self.pwr_in = self.Export(self.sense.pwr_in)
    self.pwr_out = self.Export(self.sense.pwr_out)

    self.amp = self.Block(DifferentialAmplifier(
      ratio=ratio,
      input_impedance=input_impedance
    ))
    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])
    self.ref = self.Export(self.amp.output_reference)
    self.out = self.Export(self.amp.output)

  def contents(self):
    self.connect(self.amp.input_positive, self.sense.sense_in)
    self.connect(self.amp.input_negative, self.sense.sense_out)
