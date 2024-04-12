from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Tlv9152_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vp = self.Port(VoltageSink(
      voltage_limits=(2.7, 16)*Volt, current_draw=(560*2, 750*2)*uAmp  # quiescent current for both amps
    ), [Power])
    self.vn = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink.from_supply(
      self.vn, self.vp,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,  # input common mode absolute maximum ratings
      signal_limit_tolerance=(-0.1, 0.1)*Volt,  # common-mode voltage
      impedance=100*MOhm(tol=0),  # differential input impedance
    )
    analog_out_model = AnalogSource.from_supply(
      self.vn, self.vp,
      signal_out_bound=(55*mVolt, -55*mVolt),  # output swing from rail, assumed at 10k load, Vs=16v
      current_limits=(-75, 75)*mAmp,  # short circuit current
      impedance=525*kOhm(tol=0)  # open loop output impedance
    )
    self.inpa = self.Port(analog_in_model)
    self.inna = self.Port(analog_in_model)
    self.outa = self.Port(analog_out_model)
    self.inpb = self.Port(analog_in_model)
    self.innb = self.Port(analog_in_model)
    self.outb = self.Port(analog_out_model)

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.outa,
        '2': self.inna,
        '3': self.inpa,
        '4': self.vn,
        '5': self.inpb,
        '6': self.innb,
        '7': self.outb,
        '8': self.vp,
      },
      mfr='Texas Instruments', part='TLV9152IDR',
      datasheet='https://www.ti.com/lit/ds/symlink/tlv9152.pdf'
    )
    self.assign(self.lcsc_part, 'C882649')
    self.assign(self.actual_basic_part, False)


class Tlv9152(MultipackBlock, GeneratorBlock):
  """Dual RRIO opamps.

  TODO infrastructure for packed opamps? Packed opamp abstract class?
  """
  def __init__(self):
    super().__init__()
    self.elements = self.PackedPart(PackedBlockArray(OpampElement()))
    self.pwr = self.PackedExport(self.elements.ports_array(lambda x: x.pwr))
    self.gnd = self.PackedExport(self.elements.ports_array(lambda x: x.gnd))
    self.inp = self.PackedExport(self.elements.ports_array(lambda x: x.inp))
    self.inn = self.PackedExport(self.elements.ports_array(lambda x: x.inn))
    self.out = self.PackedExport(self.elements.ports_array(lambda x: x.out))
    self.generator_param(self.pwr.requested(), self.gnd.requested(),
                         self.inp.requested(), self.inn.requested(), self.out.requested())

  def generate(self):
    super().generate()
    self.ic = self.Block(Tlv9152_Device())

    # Datasheet section 9: recommend 0.1uF bypass capacitors close to power supply pins
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.ic.vn, self.ic.vp)

    self.pwr_merge = self.Block(PackedVoltageSource())
    self.gnd_merge = self.Block(PackedVoltageSource())
    self.connect(self.pwr_merge.pwr_out, self.ic.vp)
    self.connect(self.gnd_merge.pwr_out, self.ic.vn)

    ic_ios = [
      (self.ic.inpa, self.ic.inna, self.ic.outa),
      (self.ic.inpb, self.ic.innb, self.ic.outb),
    ]

    requested = self.get(self.pwr.requested())
    assert self.get(self.gnd.requested()) == self.get(self.inp.requested()) == \
           self.get(self.inn.requested()) == self.get(self.out.requested()) == requested
    for i, ic_io in zip(requested, ic_ios):
      self.connect(self.pwr.append_elt(VoltageSink.empty(), i), self.pwr_merge.pwr_ins.request(i))
      self.connect(self.gnd.append_elt(VoltageSink.empty(), i), self.gnd_merge.pwr_ins.request(i))
      self.connect(self.inp.append_elt(AnalogSink.empty(), i), ic_io[0])
      self.connect(self.inn.append_elt(AnalogSink.empty(), i), ic_io[1])
      self.connect(self.out.append_elt(AnalogSource.empty(), i), ic_io[2])
