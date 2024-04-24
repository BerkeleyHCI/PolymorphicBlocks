from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Opa2333_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vp = self.Port(VoltageSink(
      voltage_limits=(1.8, 5.5)*Volt, current_draw=(17*2, 28*2)*uAmp  # quiescent current for both amps
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
      mfr='Texas Instruments', part='OPA2333AIDR',
      datasheet='https://www.ti.com/lit/ds/symlink/opa2333.pdf'
    )
    self.assign(self.lcsc_part, 'C38732')
    self.assign(self.actual_basic_part, False)


class Opa2333(MultipackOpamp, GeneratorBlock):
  """Dual precision RRIO (including negative input) opamps.
  """
  def _make_multipack_opamp(self) -> MultipackOpamp.OpampPorts:
    self.ic = self.Block(Opa2333_Device())
    # Datasheet section 9: recommend 0.1uF bypass capacitors close to power supply pins
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.ic.vn, self.ic.vp)

    return MultipackOpamp.OpampPorts(self.ic.vn, self.ic.vp, [
      (self.ic.inna, self.ic.inpa, self.ic.outa),
      (self.ic.innb, self.ic.inpb, self.ic.outb),
    ])
