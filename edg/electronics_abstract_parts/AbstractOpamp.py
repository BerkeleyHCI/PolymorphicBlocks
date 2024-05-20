from typing import Mapping, Tuple, List, NamedTuple

from ...electronics_model import *
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
  def __init__(self):
    super().__init__()
    self.elements = self.PackedPart(PackedBlockArray(OpampElement()))
    self.pwr = self.PackedExport(self.elements.ports_array(lambda x: x.pwr))
    self.gnd = self.PackedExport(self.elements.ports_array(lambda x: x.gnd))
    self.inp = self.PackedExport(self.elements.ports_array(lambda x: x.inp))
    self.inn = self.PackedExport(self.elements.ports_array(lambda x: x.inn))
    self.out = self.PackedExport(self.elements.ports_array(lambda x: x.out))


@non_library
class MultipackOpampGenerator(MultipackOpamp, GeneratorBlock):
  """Skeleton base class that provides scaffolding for common packed opamp definitions"""
  class OpampPorts(NamedTuple):
    gnd: VoltageSink
    pwr: VoltageSink
    amps: List[Tuple[AnalogSink, AnalogSink, AnalogSource]]  # amp-, amp+, out

  def __init__(self):
    super().__init__()
    self.generator_param(self.pwr.requested(), self.gnd.requested(),
                         self.inn.requested(), self.inp.requested(), self.out.requested())

  def _make_multipack_opamp(self) -> OpampPorts:
    """Generates the opamp as a block in self, including any application circuit components like decoupling capacitors.
    Returns (gnd, pwr, [(in-, in+, out)])."""
    raise NotImplementedError  # implement me

  def generate(self):
    super().generate()
    amp_ports = self._make_multipack_opamp()

    self.gnd_merge = self.Block(PackedVoltageSource())
    self.pwr_merge = self.Block(PackedVoltageSource())
    self.connect(self.gnd_merge.pwr_out, amp_ports.gnd)
    self.connect(self.pwr_merge.pwr_out, amp_ports.pwr)

    requested = self.get(self.pwr.requested())
    assert self.get(self.gnd.requested()) == self.get(self.inp.requested()) == \
           self.get(self.inn.requested()) == self.get(self.out.requested()) == requested
    for i, (amp_neg, amp_pos, amp_out) in zip(requested, amp_ports.amps):
      self.connect(self.pwr.append_elt(VoltageSink.empty(), i), self.pwr_merge.pwr_ins.request(i))
      self.connect(self.gnd.append_elt(VoltageSink.empty(), i), self.gnd_merge.pwr_ins.request(i))
      self.connect(self.inn.append_elt(AnalogSink.empty(), i), amp_neg)
      self.connect(self.inp.append_elt(AnalogSink.empty(), i), amp_pos)
      self.connect(self.out.append_elt(AnalogSource.empty(), i), amp_out)
