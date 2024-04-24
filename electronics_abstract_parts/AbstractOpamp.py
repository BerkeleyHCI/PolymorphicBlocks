from typing import Mapping

from electronics_model import *
from .Categories import Analog


@abstract_block
class Opamp(Analog, KiCadInstantiableBlock, Block):
  """Base class for opamps. Parameters need to be more restricted in subclasses.
  """
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name in ('Simulation_SPICE:OPAMP', 'edg_importable:Opamp')
    return {'+': self.inp, '-': self.inn, '3': self.out, 'V+': self.pwr, 'V-': self.gnd}

  @classmethod
  def block_from_symbol(cls, symbol_name: str, properties: Mapping[str, str]) -> 'Opamp':
    return Opamp()

  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.inp = self.Port(AnalogSink.empty())
    self.inn = self.Port(AnalogSink.empty())
    self.out = self.Port(AnalogSource.empty())


class OpampElement(Opamp):
  """Packed opamp element"""


@abstract_block
class MultipackOpamp(Analog, MultipackBlock):
  """Base class for packed opamps - devices that have multiple opamps in a single package,
  with shared power and ground connections. Typically used with the multipack feature to
  fit individual opamps across the design hierarchy into one of these."""
  def __init__(self) -> None:
    super().__init__()
    # TODO IMPLEMENT ME
