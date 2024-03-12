from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Opa197_Device(InternalSubcircuit, JlcPart, FootprintBlock):

  PARTS = [('OPA197IDR', 'C79274'), ('OPA189IDR', 'C781811') ]
  def __init__(self):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(4.5, 36)*Volt, current_draw=(1, 1.5)*mAmp  # quiescent current
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink.from_supply(
      self.vss, self.vcc,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,  # input common mode absolute maximum ratings
      signal_limit_tolerance=(-0.1, 0.1)*Volt,
      impedance=1e13*Ohm(tol=0),  # no tolerance bounds given on datasheet
    )
    self.vinp = self.Port(analog_in_model)
    self.vinn = self.Port(analog_in_model)
    self.vout = self.Port(AnalogSource.from_supply(
      self.vss, self.vcc,
      signal_out_bound=(0.125*Volt, -0.125*Volt),  # output swing from rail, assumed at 10k load
      current_limits=(-65, 65)*mAmp,  # for +/-18V supply
      impedance=375*Ohm(tol=0)  # no tolerance bounds given on datasheet; open-loop impedance
    ))

  def contents(self):
    super().contents()
    part, lcsc_part = self.PARTS[0]
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        # 1 is NC
        '2': self.vinn,
        '3': self.vinp,
        '4': self.vss,
        # 5 is NC
        '6': self.vout,
        '7': self.vcc,
        # 8 is NC
      },
      mfr='Texas Instruments', part=part,
      datasheet='https://www.ti.com/lit/ds/symlink/opa197.pdf'
    )
    self.assign(self.lcsc_part, lcsc_part)
    self.assign(self.actual_basic_part, False)


class Opa197(Opamp):
  """High voltage opamp (4.5-36V) in SOIC-8.
  (part also available in SOT-23-5)
  """
  def contents(self):
    super().contents()

    self.ic = self.Block(Opa197_Device())
    self.connect(self.inn, self.ic.vinn)
    self.connect(self.inp, self.ic.vinp)
    self.connect(self.out, self.ic.vout)
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.vss)

    # Datasheet section 10.1: use a low-ESR 0.1uF capacitor between each supply and ground pin
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)


class Opa2197_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vp = self.Port(VoltageSink(
      voltage_limits=(4.5, 36)*Volt, current_draw=(2, 3)*mAmp  # 2x quiescent current
    ), [Power])
    self.vn = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink.from_supply(
      self.vn, self.vp,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # input common mode absolute maximum ratings
      signal_limit_tolerance=(-0.1, 0.1)*Volt,
      impedance=6.66e9*Ohm(tol=0),  # guess from input bias current
    )
    analog_out_model = AnalogSource.from_supply(
      self.vn, self.vp,
      signal_out_bound=(70*mVolt, -70*mVolt),  # output swing from rail, assumed at 10k load
      current_limits=(-5, 5)*mAmp,  # short circuit current
      impedance=2*kOhm(tol=0)  # open loop output impedance
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
      mfr='Texas Instruments', part='OPA2197IDR',
      datasheet='https://www.ti.com/lit/ds/symlink/opa197.pdf'
    )
    self.assign(self.lcsc_part, 'C139363')
    self.assign(self.actual_basic_part, False)


class Opa2197(MultipackBlock, GeneratorBlock):
  """Dual precision RRO opamps.

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
    self.ic = self.Block(Opa2197_Device())

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
