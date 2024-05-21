from ..abstract_parts import *
from .JlcPart import JlcPart


class Tlv9061_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(1.8, 5.5)*Volt, current_draw=(538, 800)*uAmp  # quiescent current
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink.from_supply(
      self.vss, self.vcc,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,  # common mode maximum ratings
      signal_limit_tolerance=(-0.1, 0.1)*Volt
    )
    self.vinp = self.Port(analog_in_model)
    self.vinn = self.Port(analog_in_model)
    self.vout = self.Port(AnalogSource.from_supply(
      self.vss, self.vcc,
      signal_out_bound=(0, 0),  # output voltage range V- to V+
      current_limits=(-50, 50)*mAmp,  # for Vs=5V
      impedance=100*Ohm(tol=0)  # no tolerance bounds given on datasheet; open-loop impedance
    ))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.vout,
        '2': self.vss,
        '3': self.vinp,
        '4': self.vinn,
        '5': self.vcc,  # SHDN, active low (pull high to enable)
        '6': self.vcc,
      },
      mfr='Texas Instruments', part='TLV9061S',
      datasheet='https://www.ti.com/lit/ds/symlink/tlv9062-q1.pdf'
    )
    self.assign(self.lcsc_part, 'C2058350')
    self.assign(self.actual_basic_part, False)


class Tlv9061(Opamp):
  """RRIO op-amp in SOT-23-6.
  """
  def contents(self):
    super().contents()

    self.ic = self.Block(Tlv9061_Device())
    self.connect(self.inn, self.ic.vinn)
    self.connect(self.inp, self.ic.vinp)
    self.connect(self.out, self.ic.vout)
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.vss)

    # Datasheet section 11: place 0.1uF bypass capacitors close to the power-supply pins
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)
