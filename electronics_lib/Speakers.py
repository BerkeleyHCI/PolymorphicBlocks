from typing import *

from electronics_abstract_parts import *


class Lm4871_Device(DiscreteChip, CircuitBlock):
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(ElectricalSink(
      voltage_limits=(2.0, 5.5) * Volt,
      current_draw=(6.5, 10 + 433) * mAmp,  # TODO better estimate of speaker current than 1.5W into 8-ohm load
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.inp = self.Port(Passive())  # TODO these aren't actually documented w/ specs =(
    self.inm = self.Port(Passive())

    self.vo = self.Port(SpeakerDriverPort(
      impedance=(0, 0)*Ohm  # TODO impedance not given
    ))

    self.byp = self.Port(Passive())

  def contents(self):
    self.footprint(
      'U', 'Package_SO:SO-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.gnd,  # shutdown  # TODO make this a controllable digital pin
        '2': self.byp,  # bypass
        '3': self.inp,  # Vin+
        '4': self.inm,  # Vin-
        '5': self.vo.a,  # spk1
        '6': self.pwr,
        '7': self.gnd,
        '8': self.vo.b,  # spk2
      },
      mfr='Texas Instruments', part='LM4871MX',
      datasheet='https://www.ti.com/lit/ds/symlink/lm4871.pdf'
    )


class Lm4871(IntegratedCircuit):
  def __init__(self):
    super().__init__()
    # TODO should be a SpeakerDriver abstract part

    self.ic = self.Block(Lm4871_Device())
    self.pwr = self.Export(self.ic.pwr, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.sig = self.Port(AnalogSink(  # TODO these aren't actually documented
      # voltage_limits= ,
      # current_draw=(0, 0) * Amp,
      # impedance=,
    ), [Input])
    self.spk = self.Export(self.ic.vo, [Output])


  def contents(self):
    super().contents()
    # TODO size component based on higher level input?

    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=1.0*uFarad(tol=0.2),
    ))
    self.connect(self.pwr, self.in_cap.pwr)
    self.connect(self.gnd, self.in_cap.gnd)

    self.byp_cap = self.Block(Capacitor(  # TODO bypass should be a pseudo source pin, this can be a DecouplingCap
      capacitance=1.0*uFarad(tol=0.2),
      voltage=self.pwr.link().voltage  # TODO actually half the voltage, but needs const prop
    ))
    self.connect(self.gnd, self.byp_cap.neg.as_ground())

    self.sig_cap = self.Block(Capacitor(  # TODO replace with dc-block filter
      capacitance=0.47*uFarad(tol=0.2),
      voltage=self.sig.link().voltage
    ))
    self.sig_res = self.Block(Resistor(
      resistance=20*kOhm(tol=0.2)
    ))
    self.fb_res = self.Block(Resistor(
      resistance=20*kOhm(tol=0.2)
    ))
    self.connect(self.sig, self.sig_cap.neg.as_analog_sink())
    self.connect(self.sig_cap.pos, self.sig_res.a)
    self.connect(self.sig_res.b, self.fb_res.a, self.ic.inm)
    self.connect(self.fb_res.b.as_analog_sink(), self.spk.a)

    self.connect(self.byp_cap.pos, self.ic.inp, self.ic.byp)


class Speaker(DiscreteApplication, CircuitBlock):
  def __init__(self):
    super().__init__()

    # TODO needs a speaker bundle - to work with chaining - also things like power?
    self.input = self.Port(SpeakerPort(
      impedance=8*Ohm
    ), [Input])

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
      {
        '1': self.input.a,
        '2': self.input.b,
      },
      part='Header 2-pos, speaker',
      datasheet='https://www.soberton.com/wp-content/uploads/2018/07/SP-1504-June-2018.pdf'
    )
