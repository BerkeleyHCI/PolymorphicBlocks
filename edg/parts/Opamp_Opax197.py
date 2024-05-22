from ..abstract_parts import *
from .JlcPart import JlcPart


@non_library
class Opa197_Base_Device(InternalSubcircuit):
  DEVICES: int

  def _analog_in_model(self):
    return AnalogSink.from_supply(
      self.vn, self.vp,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,  # input common mode absolute maximum ratings
      signal_limit_tolerance=(-0.1, 0.1)*Volt,
      impedance=1e13*Ohm(tol=0)  # no tolerance bounds given on datasheet
    )

  def _analog_out_model(self):
    return AnalogSource.from_supply(
      self.vn, self.vp,
      signal_out_bound=(0.125*Volt, -0.125*Volt),  # output swing from rail, assumed at 10k load
      current_limits=(-65, 65)*mAmp,  # for +/-18V supply
      impedance=375*Ohm(tol=0)  # no tolerance bounds given on datasheet; open-loop impedance
    )

  def __init__(self):
    super().__init__()
    self.vn = self.Port(Ground(), [Common])
    self.vp = self.Port(VoltageSink(
      voltage_limits=(4.5, 36)*Volt,
      current_draw=(1 * self.DEVICES, 1.5 * self.DEVICES)*mAmp  # quiescent current
    ), [Power])


class Opa197_Device(Opa197_Base_Device, JlcPart, FootprintBlock):
  DEVICES = 1

  def __init__(self):
    super().__init__()
    analog_in_model = self._analog_in_model()
    self.vinp = self.Port(analog_in_model)
    self.vinn = self.Port(analog_in_model)
    self.vout = self.Port(self._analog_out_model())

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        # 1 is NC
        '2': self.vinn,
        '3': self.vinp,
        '4': self.vn,
        # 5 is NC
        '6': self.vout,
        '7': self.vp,
        # 8 is NC
      },
      mfr='Texas Instruments', part='OPA197IDR',
      datasheet='https://www.ti.com/lit/ds/symlink/opa197.pdf'
    )
    self.assign(self.lcsc_part, 'C79274')
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
    self.connect(self.pwr, self.ic.vp)
    self.connect(self.gnd, self.ic.vn)

    # Datasheet section 10.1: use a low-ESR 0.1uF capacitor between each supply and ground pin
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)


class Opa2197_Device(Opa197_Base_Device, JlcPart, FootprintBlock):
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
      mfr='Texas Instruments', part='OPA2197IDR',
      datasheet='https://www.ti.com/lit/ds/symlink/opa197.pdf'
    )
    self.assign(self.lcsc_part, 'C139363')
    self.assign(self.actual_basic_part, False)


class Opa2197(MultipackOpampGenerator):
  """Dual precision RRO opamps.
  """
  def _make_multipack_opamp(self) -> MultipackOpampGenerator.OpampPorts:
    self.ic = self.Block(Opa2197_Device())
    # Datasheet section 9: recommend 0.1uF bypass capacitors close to power supply pins
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.ic.vn, self.ic.vp)

    return self.OpampPorts(self.ic.vn, self.ic.vp, [
      (self.ic.inna, self.ic.inpa, self.ic.outa),
      (self.ic.innb, self.ic.inpb, self.ic.outb),
    ])
