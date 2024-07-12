from ..abstract_parts import *
from .JlcPart import JlcPart


class Ucc27282_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vss = self.Port(Ground(), [Common])
    self.vdd = self.Port(VoltageSink.from_gnd(
      self.vss,
      voltage_limits=(5.5, 16)*Volt,  # recommended operating conditions
      current_draw=RangeExpr()
    ))

    input_model = DigitalSink.from_supply(
      self.vss, self.vdd,
      voltage_limit_abs=(-5, 20)*Volt,
      input_threshold_abs=(0.9, 2.4)*Volt
    )
    self.li = self.Port(input_model)
    self.hi = self.Port(input_model)

    self.lo = self.Port(DigitalSource.from_supply(
      self.vss, self.vdd,
      current_limits=(-3, 3)*Amp  # peak pullup and pulldown current
    ))

    self.hs = self.Port(Ground.from_gnd(
      self.vss,
      voltage_limits=(-8, 100)  # looser negative rating possible with pulses
    ))
    self.hb = self.Port(VoltageSource(
      voltage_out=self.hs.link().voltage + self.vdd.link().voltage,
    ))
    self.ho = self.Port(DigitalSource.from_supply(
      self.hs, self.hb,
      current_limits=(-3, 3)*Amp  # peak pullup and pulldown current
    ))

    # quiescent to operating, vdd and hb, plus output draw
    self.assign(self.vdd.current_draw,
                (0.3, 4.5)*mAmp + (0.2, 4)*mAmp + self.lo.link().current_drawn + self.ho.link().current_drawn)

  def contents(self):
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.vdd,
        '2': self.hb,
        '3': self.ho,
        '4': self.hs,
        '5': self.hi,
        '6': self.li,
        '7': self.vss,
        '8': self.lo,
      },
      mfr='Texas Instruments', part='UCC27282DR',
      datasheet='https://www.ti.com/lit/ds/symlink/ucc27282-q1.pdf'
    )
    self.assign(self.lcsc_part, 'C2867844')
    self.assign(self.actual_basic_part, False)


class Ucc27282(HalfBridgeDriver, HalfBridgeDriverIndependent):
  """UCC27282 half-bridge driver supporting 100V offset, 5.5-16v input, internal boot diode,
  shoot through protect, no deadtime."""
  def contents(self):
    super().contents()

    self.require(self.has_boot_diode)
    self.require(~self.high_pwr.is_connected())  # not supported

    self.ic = self.Block(Ucc27282_Device())
    self.connect(self.pwr, self.ic.vdd)
    self.connect(self.gnd, self.ic.vss)
    self.connect(self.low_in, self.ic.li)
    self.connect(self.high_in, self.ic.hi)
    self.connect(self.low_out, self.ic.lo)
    self.connect(self.high_gnd, self.ic.hs)
    self.connect(self.high_out, self.ic.ho)

    self.cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.boot_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.ic.hs, self.ic.hb)
