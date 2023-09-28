from typing import Dict

from electronics_abstract_parts import CurrentSenseResistor, DifferentialAmplifier
from .Categories import Sensor
from .DummyDevices import ForcedAnalogSignal
from electronics_model import *


class OpampCurrentSensor(Sensor, KiCadImportableBlock, Block):
  """Current sensor block using a resistive sense element and an opamp-based differential amplifier.
  For a positive current (flowing from pwr_in -> pwr_out), this generates a positive voltage on the output.
  Output reference can be floating (eg, at Vdd/2) to allow bidirectional current sensing.
  """
  @init_in_parent
  def __init__(self, resistance: RangeLike, ratio: RangeLike, input_impedance: RangeLike):
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
    self.out = self.Port(AnalogSource.empty())


  def contents(self):
    self.connect(self.amp.input_positive, self.sense.sense_in)
    self.connect(self.amp.input_negative, self.sense.sense_out)

    output_swing = self.pwr_out.link().current_drawn * self.sense.actual_resistance * self.amp.actual_ratio
    self.force_signal = self.Block(ForcedAnalogSignal(output_swing + self.ref.link().signal))
    self.connect(self.amp.output, self.force_signal.signal_in)
    self.connect(self.force_signal.signal_out, self.out)

  def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
    assert symbol_name == 'edg_importable:OpampCurrentSensor'
    return {'+': self.pwr_in, '-': self.pwr_out, 'R': self.ref, '3': self.out,
            'V+': self.pwr, 'V-': self.gnd}
