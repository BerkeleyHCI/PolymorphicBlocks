from ..abstract_parts import *
from .JlcPart import JlcPart


class Ina826_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vsp = self.Port(VoltageSink(
      voltage_limits=(3, 36)*Volt, current_draw=(200, 300)*uAmp  # over temperature range, typ to max
    ), [Power])
    self.vsn = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink.from_supply(
      self.vsn, self.vsp,
      voltage_limit_tolerance=(-2, 40)*Volt,  # Vs- - 40 to Vs+ + 40, but down to Vs- - 2 without clamping input res
      signal_limit_tolerance=(0, -1)*Volt,
      impedance=2000*MOhm(tol=0)  # 20 GOhm typ differential
    )
    self.inp = self.Port(analog_in_model)
    self.inn = self.Port(analog_in_model)
    self.ref = self.Port(AnalogSink.from_supply(
      self.vsn, self.vsp,
      signal_limit_tolerance=(0, 0)*Volt,  # V- to V+
      impedance=100*kOhm(tol=0)  # typ
    ))
    self.out = self.Port(AnalogSource.from_supply(
      self.vsn, self.vsp,
      signal_out_bound=(0.1, -0.15),
      current_limits=(-16, 16)*mAmp,  # continuous to Vs/2
      impedance=100*Ohm(tol=0)  # no tolerance bounds given on datasheet; open-loop impedance
    ))

    self.rg2 = self.Port(Passive())
    self.rg3 = self.Port(Passive())

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.inn,
        '2': self.rg2,
        '3': self.rg3,
        '4': self.inp,
        '5': self.vsn,
        '6': self.ref,
        '7': self.out,
        '8': self.vsp,
      },
      mfr='Texas Instruments', part='INA826AIDR',
      datasheet='https://www.ti.com/lit/ds/symlink/ina826.pdf'
    )
    self.assign(self.lcsc_part, 'C38433')
    self.assign(self.actual_basic_part, False)


class Ina826(Block):
  """Cost-effective instrumentation amplifier in SOIC-8, with gain 1-1000 set by single resistor.
  TODO: DiffAmp abstract class
  """
  @init_in_parent
  def __init__(self, gain: RangeLike):
    super().__init__()
    self.ic = self.Block(Ina826_Device())
    self.gnd = self.Export(self.ic.vsn)
    self.pwr = self.Export(self.ic.vsp)

    self.inn = self.Export(self.ic.inn)
    self.inp = self.Export(self.ic.inp)
    self.ref = self.Export(self.ic.ref)
    self.out = self.Export(self.ic.out)

    self.gain = self.ArgParameter(gain)

  def contents(self):
    super().contents()

    # Datasheet section 8.1: decoupling caps placed as close to device pins as possible
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)

    self.require(self.gain.within(Range(1, 1000)))
    self.rg = self.Block(Resistor(49400/(self.gain - 1)))  # TODO proper tolerancing
    self.connect(self.rg.a, self.ic.rg2)
    self.connect(self.rg.b, self.ic.rg3)
