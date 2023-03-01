from typing import Dict

from electronics_model import *
from .MergedBlocks import MergedAnalogSource
from .AbstractResistor import Resistor
from .Categories import Interface


@abstract_block
class SolidStateRelay(Interface, Block):
  """Base class for solid state relays.
  LED pins are passive (like the abstract LED) and the enclosing class should provide
  the circuitry to make it a DigitalSink port.
  """
  def __init__(self) -> None:
    super().__init__()

    self.leda = self.Port(Passive.empty())
    self.ledk = self.Port(Passive.empty())

    self.feta = self.Port(Passive.empty())
    self.fetb = self.Port(Passive.empty())

    # TODO: this is a different way of modeling parts - parameters in the part itself
    # instead of on the ports (because this doesn't have typed ports)
    self.led_forward_voltage = self.Parameter(RangeExpr())
    self.led_current_limit = self.Parameter(RangeExpr())
    self.led_current_recommendation = self.Parameter(RangeExpr())
    self.load_voltage_limit = self.Parameter(RangeExpr())
    self.load_current_limit = self.Parameter(RangeExpr())
    self.load_resistance = self.Parameter(RangeExpr())


class AnalogIsolatedSwitch(Interface, KiCadImportableBlock, Block):
  """Digitally controlled solid state relay that switches an analog signal.
  Includes a ballasting resistor.

  The ports are not tagged with Input/Output/InOut, because of potential for confusion between
  the digital side and the analog side.

  A separate output-side pull port allows modeling the output switch standoff voltage
  when the switch is off.
  """
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'edg_importable:AnalogIsolatedSwitch'
    return {'in': self.signal, 'gnd': self.gnd,
            'ain': self.ain, 'apull': self.apull, 'aout': self.aout}

  def __init__(self) -> None:
    super().__init__()

    self.signal = self.Port(DigitalSink.empty())
    self.gnd = self.Port(Ground.empty(), [Common])

    self.apull = self.Port(AnalogSink.empty())
    self.ain = self.Port(AnalogSink.empty())
    self.aout = self.Port(AnalogSource.empty())

    self.ic = self.Block(SolidStateRelay())
    self.res = self.Block(Resistor(
      resistance=(self.signal.link().voltage.upper() / self.ic.led_current_recommendation.upper(),
                  self.signal.link().output_thresholds.upper() / self.ic.led_current_recommendation.lower())
    ))
    self.connect(self.signal, self.ic.leda.adapt_to(DigitalSink(
      current_draw=self.signal.link().voltage / self.res.actual_resistance
    )))
    self.connect(self.res.a, self.ic.ledk)
    self.connect(self.res.b.adapt_to(Ground()), self.gnd)

    self.connect(self.ain, self.ic.feta.adapt_to(AnalogSink(
      voltage_limits=self.apull.link().voltage + self.ic.load_voltage_limit,
      impedance=self.aout.link().sink_impedance + self.ic.load_resistance
    )))
    self.pull_merge = self.Block(MergedAnalogSource()).connected_from(
      self.apull,
      self.ic.fetb.adapt_to(AnalogSource(
        voltage_out=self.ain.link().voltage,
        current_limits=self.ic.load_current_limit,
        impedance=self.ain.link().source_impedance + self.ic.load_resistance
    )))
    self.connect(self.pull_merge.output, self.aout)
