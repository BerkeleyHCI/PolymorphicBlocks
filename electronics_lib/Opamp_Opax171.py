from electronics_abstract_parts import *
from .JlcPart import JlcPart


@non_library
class Opa171_Base_Device(InternalSubcircuit):
  DEVICES: int

  def _analog_in_model(self):
    return AnalogSink.from_supply(
      self.vn, self.vp,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,  # input common mode absolute maximum ratings
      signal_limit_bound=(-0.1*Volt, -2*Volt),
      impedance=100e6*Ohm(tol=0)  # no tolerance specified; differential impedance
    )

  def _analog_out_model(self):
    return AnalogSource.from_supply(
      self.vn, self.vp,
      signal_out_bound=(0.350*Volt, -0.350*Volt),  # output swing from rail, 10k load, over temperature
      current_limits=(-35, 25)*mAmp,  # short circuit current
      impedance=150*Ohm(tol=0)  # open-loop resistance
    )

  def __init__(self):
    super().__init__()
    self.vn = self.Port(Ground(), [Common])
    self.vp = self.Port(VoltageSink(
      voltage_limits=(4.5, 36)*Volt,
      current_draw=(475 * self.DEVICES, 650 * self.DEVICES)*uAmp  # quiescent current
    ), [Power])


class Opa2171_Device(Opa171_Base_Device, JlcPart, FootprintBlock):
  DEVICES = 2

  def __init__(self):
    super().__init__()

    analog_in_model = self._analog_in_model()
    analog_out_model = self._analog_out_model()
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
      mfr='Texas Instruments', part='OPA2171AIDR',
      datasheet='https://www.ti.com/lit/ds/symlink/opa2171.pdf'
    )
    self.assign(self.lcsc_part, 'C40904')
    self.assign(self.actual_basic_part, False)


class Opa2171(MultipackBlock, GeneratorBlock):
  """Dual precision general purpose RRO opamp.

  TODO infrastructure for packed opamps? Packed opamp abstract class? - shared w/ OPAx333
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
    self.ic = self.Block(Opa2171_Device())

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
