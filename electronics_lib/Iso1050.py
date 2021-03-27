from typing import *

from electronics_abstract_parts import *


class Iso1050dub_Device(DiscreteChip, CircuitBlock):
  def __init__(self):
    super().__init__()
    # Table 6.3, recommended operating conditions
    self.vcc1 = self.Port(VoltageSink(
      voltage_limits=(3, 5.5) * Volt, current_draw=(0, 3.6) * mAmp
    ))
    self.vcc2 = self.Port(VoltageSink(
      voltage_limits=(4.75, 5.25) * Volt, current_draw=(0, 73)*mAmp
    ))
    self.gnd1 = self.Port(Ground())
    self.gnd2 = self.Port(Ground())

    self.controller = self.Port(CanTransceiverPort(DigitalBidir(
      voltage_limits=(-0.5 * Volt, self.vcc1.link().voltage.lower() + 0.5 * Volt),
      voltage_out=(0 * Volt, self.vcc1.link().voltage.lower()),
      current_draw=(0, 0),  # TODO actually an unspecified default
      current_limits=(-5, 5) * uAmp,
      input_thresholds=(0.8, 2) * Volt,
      output_thresholds=(0 * Volt, self.vcc1.link().voltage.lower())
    )))

    self.can = self.Port(CanDiffPort(DigitalBidir(
      voltage_limits=(-7, 7) * Volt,  # TODO: need better model of differential pins where there can be a common-mode offset
      voltage_out=(0.8, 4.5) * Volt,
      current_draw=(-4, 4) * mAmp, current_limits=(-70, 70) * mAmp
    )))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOP-8_6.62x9.15mm_P2.54mm',
      {
        '1': self.vcc1,
        '2': self.controller.rxd,
        '3': self.controller.txd,
        '4': self.gnd1,
        '5': self.gnd2,
        '6': self.can.canl,
        '7': self.can.canh,
        '8': self.vcc2,
      },
      mfr='Texas Instruments', part='ISO1050DUB',
      datasheet='https://www.ti.com/lit/ds/symlink/iso1050.pdf'
    )



class Iso1050dub(IsolatedCanTransceiver):
  def contents(self):
    super().contents()
    self.ic = self.Block(Iso1050dub_Device())
    self.connect(self.ic.controller, self.controller)
    self.connect(self.ic.can, self.can)

    self.logic_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    ))
    self.connect(self.pwr, self.ic.vcc1, self.logic_cap.pwr)
    self.connect(self.gnd, self.ic.gnd1, self.logic_cap.gnd)

    self.can_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    ))
    self.connect(self.can_pwr, self.ic.vcc2, self.can_cap.pwr)
    self.connect(self.can_gnd, self.ic.gnd2, self.can_cap.gnd)
