from ..abstract_parts import *
from .JlcPart import JlcPart


class Sn65hvd230_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(3, 3.6) * Volt, current_draw=(0.370, 17) * mAmp
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.controller = self.Port(CanTransceiverPort(DigitalBidir(
      voltage_limits=(-0.5 * Volt, self.vcc.link().voltage.lower() + 0.5 * Volt),
      voltage_out=(0 * Volt, self.vcc.link().voltage.lower()),
      current_draw=(0, 0),
      current_limits=(-8, 8) * mAmp,  # driver pin actually -40-48mA
      input_thresholds=(0.8, 2) * Volt,
      output_thresholds=(0 * Volt, self.vcc.link().voltage.lower())
    )))

    self.can = self.Port(CanDiffPort(DigitalBidir(
      voltage_limits=(-2.5, 7.5) * Volt,
      voltage_out=(0.5 * Volt, self.vcc.link().voltage.lower()),
      current_draw=(-30, 30) * uAmp, current_limits=(-250, 250) * mAmp
    )))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.controller.txd,
        '2': self.gnd,
        '3': self.vcc,
        '4': self.controller.rxd,
        # '5': ,  # Vref = Vcc/2 output pin
        '6': self.can.canl,
        '7': self.can.canh,
        '8': self.gnd,  # Gs, set to GND for high speed mode
      },
      mfr='Texas Instruments', part='SN65HVD230DR',
      datasheet='www.ti.com/lit/ds/symlink/sn65hvd230.pdf'
    )
    self.assign(self.lcsc_part, 'C12084')
    self.assign(self.actual_basic_part, True)


class Sn65hvd230(CanTransceiver):
  def contents(self):
    super().contents()
    self.ic = self.Block(Sn65hvd230_Device())
    self.connect(self.ic.controller, self.controller)
    self.connect(self.ic.can, self.can)
    self.connect(self.ic.gnd, self.gnd)
    self.connect(self.ic.vcc, self.pwr)

    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)
