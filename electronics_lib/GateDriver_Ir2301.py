from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ir2301_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.com = self.Port(Ground(), [Common])
    self.vcc = self.Port(VoltageSink.from_gnd(
      self.com,
      voltage_limits=(5, 20)*Volt,  # recommended operating conditions
      current_draw=(50, 190)*uAmp  # quiescent current only, TODO model gate current
    ))

    input_model = DigitalSink.from_supply(
      self.com, self.vcc,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # absolute maximum ratings
      input_threshold_abs=(0.8, 2.9)*Volt  # static electrical characteristics
    )
    self.lin = self.Port(input_model)
    self.hin = self.Port(input_model)

    self.lo = self.Port(DigitalSource.from_supply(
      self.com, self.vcc,
      current_limits=(-250, 120)*mAmp)  # static electrical characteristics: output short circuit pulsed current
    )

    self.vs = self.Port(VoltageSink.from_gnd(
      self.com,
      voltage_limits=(-5, 600)  # no current draw since this is a "ground" pin
    ))
    self.vb = self.Port(VoltageSink.from_gnd(
      self.vs,
      voltage_limits=(5, 20)*Volt,
      current_draw=(50, 190)*uAmp  # quiescent current only, TODO model gate current
    ))
    self.ho = self.Port(DigitalSource.from_supply(
      self.vs, self.vb,
      current_limits=(-250, 120)*mAmp  # static electrical characteristics: output short circuit pulsed current
    ))

  def contents(self):
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.vcc,
        '2': self.hin,
        '3': self.lin,
        '4': self.com,
        '5': self.lo,
        '6': self.vs,
        '7': self.ho,
        '8': self.vb,
      },
      mfr='Infineon Technologies', part='IR2301',
      datasheet='https://www.infineon.com/dgdl/ir2301.pdf?fileId=5546d462533600a4015355c97bb216dc'
    )
    self.assign(self.lcsc_part, 'C413500')
    self.assign(self.actual_basic_part, False)


class Ir2301(HalfBridgeDriver):
  """IR2301 half-bridge driver supporting 600V offset, 5-20v input, external boot diode,
  no shoot through protect, no deadtime."""
  def contents(self):
    super().contents()

    self.ic = self.Block(Ir2301_Device())
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.com)
    self.connect(self.low_in, self.ic.lin)
    self.connect(self.high_in, self.ic.hin)
    self.connect(self.low_out, self.ic.lo)
    self.connect(self.high_pwr, self.ic.vb)
    self.connect(self.high_gnd, self.ic.vs)
    self.connect(self.high_out, self.ic.ho)

    self.cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    # serves as both boot cap and decoupling cap
    self.high_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.high_gnd, self.high_pwr)
