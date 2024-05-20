from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Lmv321_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt, current_draw=(80, 170)*uAmp  # quiescent current
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink.from_supply(
      self.vss, self.vcc,
      voltage_limit_abs=(-0.2, 5.7),
      signal_limit_bound=(0, -1.0*Volt),  # assumed, from Vcc = 2.7v and 5v tables
      current_draw=(0, 0)*pAmp  # TODO: should bias current be modeled here?
    )
    self.vinp = self.Port(analog_in_model)
    self.vinn = self.Port(analog_in_model)
    self.vout = self.Port(AnalogSource.from_supply(
      self.vss, self.vcc,
      signal_out_bound=(0.180*Volt, -0.100*Volt),  # assuming a 10k load, Vcc=2.7v
      current_limits=(-40, 40)*mAmp,  # output short circuit current
    ))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.vinp,
        '2': self.vss,
        '3': self.vinn,
        '4': self.vout,
        '5': self.vcc,
      },
      mfr='Texas Instruments', part='LMV321',
      datasheet='https://www.ti.com/lit/ds/symlink/lmv321.pdf'
    )
    self.assign(self.lcsc_part, 'C7972')
    self.assign(self.actual_basic_part, True)


class Lmv321(Opamp):
  """RRO op-amp in SOT-23-5.
  """
  def contents(self):
    super().contents()

    self.ic = self.Block(Lmv321_Device())
    self.connect(self.inn, self.ic.vinn)
    self.connect(self.inp, self.ic.vinp)
    self.connect(self.out, self.ic.vout)
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.vss)

    # Datasheet section 9: place 0.1uF bypass capacitors close to the power-supply pins
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)
