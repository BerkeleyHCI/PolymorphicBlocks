from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Lm4871_Device(InternalSubcircuit, FootprintBlock):
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=(2.0, 5.5) * Volt,
      current_draw=(6.5, 10 + 433) * mAmp,  # TODO better estimate of speaker current than 1.5W into 8-ohm load
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.inp = self.Port(Passive())  # TODO these aren't actually documented w/ specs =(
    self.inm = self.Port(Passive())

    speaker_port = AnalogSource(
      impedance=RangeExpr.ZERO
    )
    self.vo1 = self.Port(speaker_port)
    self.vo2 = self.Port(speaker_port)

    self.byp = self.Port(Passive())

  def contents(self):
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.gnd,  # shutdown  # TODO make this a controllable digital pin
        '2': self.byp,  # bypass
        '3': self.inp,  # Vin+
        '4': self.inm,  # Vin-
        '5': self.vo1,
        '6': self.pwr,
        '7': self.gnd,
        '8': self.vo2,
      },
      mfr='Texas Instruments', part='LM4871MX',
      datasheet='https://www.ti.com/lit/ds/symlink/lm4871.pdf'
    )


class Lm4871(Interface, Block):
  def __init__(self):
    super().__init__()
    # TODO should be a SpeakerDriver abstract part

    self.ic = self.Block(Lm4871_Device())
    self.pwr = self.Export(self.ic.pwr, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.sig = self.Port(AnalogSink.empty(), [Input])
    self.spk = self.Port(SpeakerDriverPort(AnalogSource.empty()), [Output])

  def contents(self):
    super().contents()
    # TODO size component based on higher level input?

    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=1.0*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)

    self.byp_cap = self.Block(Capacitor(  # TODO bypass should be a pseudo source pin, this can be a DecouplingCap
      capacitance=1.0*uFarad(tol=0.2),
      voltage=self.pwr.link().voltage  # TODO actually half the voltage, but needs const prop
    ))
    self.connect(self.gnd, self.byp_cap.neg.adapt_to(Ground()))

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
    self.connect(self.sig, self.sig_cap.neg.adapt_to(AnalogSink()))
    self.connect(self.sig_cap.pos, self.sig_res.a)
    self.connect(self.sig_res.b, self.fb_res.a, self.ic.inm)
    self.connect(self.spk.a, self.ic.vo1, self.fb_res.b.adapt_to(AnalogSink()))
    self.connect(self.spk.b, self.ic.vo2)

    self.connect(self.byp_cap.pos, self.ic.inp, self.ic.byp)


class Tpa2005d1_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=(2.5, 5.5) * Volt,
      current_draw=(2.2, 260) * mAmp,  # quiescent current to maximum supply current (at 1.1W) in Figure 6
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    input_port = AnalogSink.from_supply(self.gnd, self.pwr,
                                        voltage_limit_tolerance=(-0.3, 0.3)*Volt,
                                        impedance=(142, 158)*kOhm)
    self.inp = self.Port(input_port)
    self.inn = self.Port(input_port)

    speaker_port = AnalogSource(
      impedance=RangeExpr.ZERO  # TODO output impedance not given, but maximum Rl of 3.2-6.4ohm
    )
    self.vo1 = self.Port(speaker_port)
    self.vo2 = self.Port(speaker_port)

  def contents(self):
    self.footprint(
      'U', 'Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.68x1.88mm_ThermalVias',
      {
        '7': self.gnd,
        '4': self.inp,  # Vin+
        '3': self.inn,  # Vin-
        # pin 2 is NC
        '1': self.pwr,  # /SHDN
        '9': self.gnd,  # exposed pad, "must be soldered to a grounded pad"
        '6': self.pwr,
        '8': self.vo1,
        '5': self.vo2,
      },
      mfr='Texas Instruments', part='TPA2005D1',
      datasheet='https://www.ti.com/lit/ds/symlink/tpa2005d1.pdf'
    )
    self.assign(self.lcsc_part, 'C27396')
    self.assign(self.actual_basic_part, False)


class Tpa2005d1(Interface, GeneratorBlock):
  """TPA2005D1 configured in single-ended input mode.
  Possible semi-pin-compatible with PAM8302AASCR (C113367), but which has internal resistor."""
  @init_in_parent
  def __init__(self, gain: RangeLike = Range.from_tolerance(20, 0.2)):
    super().__init__()
    # TODO should be a SpeakerDriver abstract part

    self.ic = self.Block(Tpa2005d1_Device())
    self.pwr = self.Export(self.ic.pwr, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.sig = self.Port(AnalogSink.empty(), [Input])
    self.spk = self.Port(SpeakerDriverPort(AnalogSource.empty()), [Output])

    self.generator(self.generate, gain)

  def generate(self, gain: Range):
    import math
    super().contents()

    self.pwr_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),  # recommended Vcc cap per 11.1
    )).connected(self.gnd, self.pwr)
    self.bulk_cap = self.Block(DecouplingCapacitor(
      capacitance=(2.2*0.8, 10*1.2)*uFarad,
    )).connected(self.gnd, self.pwr)  # "charge reservoir" recommended cap per 11.1, 2.2-10uF (+20% tolerance)

    # Note, gain = 2 * (142k to 158k)/Ri, recommended gain < 20V/V
    res_value = Range.cancel_multiply(2 * Range(142e3, 158e3), 1 / gain)
    in_res_model = Resistor(
      resistance=res_value
    )
    # TODO: the tolerance stackup here is pretty awful since it has a wide bound from the resistor spec
    # Instead, a better approach would be to select the resistor, THEN the capacitor (or a coupled RC selector)
    fc = Range(1, 20)  # arbitrary, right on the edge of audio frequency
    cap_value = Range.cancel_multiply(1 / (2 * math.pi * res_value), 1 / fc)
    if cap_value.lower < 1e-6 * 0.8:  # account for 20% capacitor tolerance
      assert cap_value.upper >= 1e-6, f"input coupling cap {cap_value} below recommended 1uF, datasheet 10.2.2.2.1"
      cap_value.lower = 1e-6 * 0.8
    in_cap_model = Capacitor(
      capacitance=cap_value,
      voltage=self.sig.link().voltage
    )

    self.inp_cap = self.Block(in_cap_model)
    self.inp_res = self.Block(in_res_model)
    self.connect(self.sig, self.inp_cap.neg.adapt_to(AnalogSink()))
    self.connect(self.inp_cap.pos, self.inp_res.a)
    self.connect(self.inp_res.b.adapt_to(AnalogSource()), self.ic.inp)

    self.inn_cap = self.Block(in_cap_model)
    self.inn_res = self.Block(in_res_model)
    self.connect(self.gnd, self.inn_cap.neg.adapt_to(Ground()))
    self.connect(self.inn_cap.pos, self.inn_res.a)
    self.connect(self.inn_res.b.adapt_to(AnalogSource()), self.ic.inn)

    self.connect(self.spk.a, self.ic.vo1)
    self.connect(self.spk.b, self.ic.vo2)


@abstract_block
class Speaker(HumanInterface):
  """Abstract speaker part with speaker input port."""
  def __init__(self):
    super().__init__()
    self.input = self.Port(SpeakerPort().empty(), [Input])


class ConnectorSpeaker(Speaker):
  """Speaker that delegates to a PassiveConnector and with configurable impedance."""
  @init_in_parent
  def __init__(self, impedance: RangeLike = 8*Ohm(tol=0)):
    super().__init__()

    self.conn = self.Block(PassiveConnector())

    self.connect(self.input.a, self.conn.pins.request('1').adapt_to(AnalogSink(
      impedance=impedance)
    ))
    self.connect(self.input.b, self.conn.pins.request('2').adapt_to(AnalogSink(
      impedance=impedance)
    ))
