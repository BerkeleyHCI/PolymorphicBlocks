from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Opa197_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(4.5, 36)*Volt, current_draw=(1, 1.5)*mAmp  # quiescent current
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink.from_supply(
      self.vss, self.vcc,
      voltage_limit_tolerance=(-0.5, 0.5),  # input common mode absolute maximum ratings
      impedance=1e13*Ohm(tol=0),  # no tolerance bounds given on datasheet
    )
    self.vinp = self.Port(analog_in_model)
    self.vinn = self.Port(analog_in_model)
    self.vout = self.Port(AnalogSource.from_supply(
      self.vss, self.vcc,
      current_limits=(-65, 65)*mAmp,  # for +/-18V supply
      impedance=375*Ohm(tol=0)  # no tolerance bounds given on datasheet; open-loop impedance
    ))

  def contents(self):
    super().contents()
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
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.vss)

    # Datasheet section 10.1: use a low-ESR 0.1uF capacitor between each supply and ground pin
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)
