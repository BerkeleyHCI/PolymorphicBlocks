from electronics_abstract_parts import *


class Opa197_Device(DiscreteChip, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(4.5, 36)*Volt, current_draw=(1, 1.5)*mAmp  # quiescent current
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink(
      voltage_limits=(-0.1, self.vcc.link().voltage.lower() + 0.1),  # inferred, from common-mode voltage range
      impedance=1e13*Ohm(tol=0),  # no tolerance bounds given on datasheet
      current_draw=(0, 0)*pAmp  # TODO: should bias current be modeled here?
    )
    self.vinp = self.Port(analog_in_model)
    self.vinn = self.Port(analog_in_model)
    self.vout = self.Port(AnalogSource(
      (0.125, self.vcc.link().voltage.lower() - 0.125),  # assuming a 10k load
      current_limits=(-65, 65)*mAmp,  # for +/-18V supply
      impedance=375*Ohm(tol=0)  # no tolerance bounds given on datasheet; open-loop impedance
    ))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SO-8_3.9x4.9mm_P1.27mm',
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
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap = imp.Block(DecouplingCapacitor(
        capacitance=0.1*uFarad(tol=0.2),
      ))
