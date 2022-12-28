from typing import List

from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Cbmud1200l_Device(JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.gnd1 = self.Port(VoltageSink())  # can be any voltage
    self.vdd1 = self.Port(VoltageSink.from_gnd(
      self.gnd1,
      voltage_limits=(2.5, 5.5)*Volt,
      current_draw=(280, 300)*uAmp + 2*((0, 26)*mAmp)  # 2.5-5v static to maximum dynamic power
    ))
    in_model = DigitalSink.from_supply(
      self.gnd1, self.vdd1,
      voltage_limit_tolerance=(-0.3, 0.5),
      input_threshold_factor=(0.3, 0.7)
    )
    self.via = self.Port(in_model)
    self.vib = self.Port(in_model)

    self.gnd2 = self.Port(VoltageSink())  # can be any voltage
    self.vdd2 = self.Port(VoltageSink.from_gnd(  # assumed the same as vdd1 ratings
      self.gnd2,
      voltage_limits=(2.5, 5.5)*Volt,
      current_draw=(280, 300)*uAmp + 2*((0, 26)*mAmp)  # 2.5-5v static to maximum dynamic power
    ))
    out_model = DigitalSource.from_supply(
      self.gnd2, self.vdd2,
      current_limits=(-50, 50)*mAmp
    )
    self.voa = self.Port(out_model)
    self.vob = self.Port(out_model)

  def contents(self):
    self.footprint(
      'U', 'Package_SO:SO-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.vdd1,
        '2': self.via,
        '3': self.vib,
        '4': self.gnd1,
        '5': self.gnd2,
        '6': self.vob,
        '7': self.voa,
        '8': self.vdd2,
      },
      mfr='Corebai', part='CBMuD1200L',
      datasheet='http://corebai.com/en/UploadFiles/20220908/142534811.pdf'
    )
    self.assign(self.lcsc_part, 'C476470')
    self.assign(self.actual_basic_part, False)


class Cbmud1200l(DigitalIsolator, GeneratorBlock):
  def __init__(self):
    super().__init__()
    self.generator(self.generate, self.in_a.requested(), self.out_b.requested(),
                   self.in_b.requested(), self.out_a.requested())

  def contents(self):
    super().contents()
    self.ic = self.Block(Cbmud1200l_Device())
    self.connect(self.pwr_a, self.ic.vdd1)
    self.connect(self.gnd_a, self.ic.gnd1)
    self.connect(self.pwr_b, self.ic.vdd2)
    self.connect(self.gnd_b, self.ic.gnd2)

  def generate(self, in_a_elts: List[str], out_b_elts: List[str], in_b_elts: List[str], out_a_elts: List[str]):
    assert in_a_elts == out_b_elts, f"in_a={in_a_elts} and out_b={out_b_elts} must be equal"
    assert not in_b_elts and not out_a_elts, f"in_b={in_b_elts} and out_a={out_a_elts} must be empty, device has no b->a channels"
    channel_pairs = [
      (self.ic.via, self.ic.voa),
      (self.ic.vib, self.ic.vob),
    ]

    self.cap_a = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd_a, self.pwr_a)
    self.cap_b = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd_b, self.pwr_b)

    for elt_name, (in_a_port, out_b_port) in zip(in_a_elts, channel_pairs):
      self.connect(self.in_a.append_elt(DigitalSink.empty(), elt_name), in_a_port)
      self.connect(self.out_b.append_elt(DigitalSource.empty(), elt_name), out_b_port)

    self.out_a.defined()
    self.in_b.defined()
