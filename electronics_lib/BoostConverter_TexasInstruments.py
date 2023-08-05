from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Tps61040_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.vfb = self.Parameter(RangeExpr((1.208, 1.258)*Volt))

    self.sw = self.Port(VoltageSource())  # internal switch specs not defined, only bulk current limit defined
    self.gnd = self.Port(Ground(), [Common])
    self.fb = self.Port(AnalogSink(impedance=(self.vfb.lower() / 1*uAmp, float('inf'))))  # based on bias current
    self.vin = self.Port(VoltageSink(
      voltage_limits=(1.8, 6)*Volt,
      current_draw=(0.1, 50)*uAmp  # quiescent current
    ), [Power])
    self.en = self.Port(DigitalSink.from_supply(
      self.gnd, self.vin,
      voltage_limit_tolerance=(-0.3, 0.3),
      input_threshold_abs=(0.4, 1.3)*Volt
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.sw,
        '2': self.gnd,
        '3': self.fb,
        '4': self.en,
        '5': self.vin,
      },
      mfr='Texas Instruments', part='TPS61040DBVR',
      datasheet='https://www.ti.com/lit/ds/symlink/tps61040.pdf'
    )
    self.assign(self.lcsc_part, 'C7722')
    self.assign(self.actual_basic_part, False)


class Tps61040(VoltageRegulatorEnableWrapper, DiscreteBoostConverter, GeneratorBlock):
  """PFM (DCM, discontinuous mode) boost converter in SOT-23-5"""
  def _generator_inner_enable_pin(self) -> Port[DigitalLink]:
    return self.ic.en

  def contents(self):
    super().contents()

    self.assign(self.frequency, 1*MHertz(tol=0))  # up to 1 MHz, can be lower

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Tps61040_Device())

      self.fb = imp.Block(FeedbackVoltageDivider(
        output_voltage=self.ic.vfb,
        impedance=(10, 183) * kOhm,  # datasheet recommends typ R2 <= 200k, max R1 2.2M
        assumed_input_voltage=self.output_voltage
      ))
      self.connect(self.fb.input, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

      # TODO 10pF is the datasheet-suggested starting, point, but equation also available
      self.cff = self.Block(Capacitor(10*pFarad(tol=0.2), voltage=(0, self.pwr_in.link().voltage)))
      self.connnect(self.cff.pos.adapt_to(VoltageSink()), self.pwr_out)
      self.connnect(self.cff.neg.adapt_to(AnalogSink()), self.ic.fb)

  def generate(self):
    super().generate()
    # power path calculation here - we don't use BoostConverterPowerPath since this IC operates in DCM
    # and has different component sizing guidelines
    vin = self.get(self.pwr_in.link().voltage)
    vout = self.get(self.pwr_out.link().voltage)
    vl = vout - vin  # voltage across inductor in steady-state
    iload = self.get(self.pwr_out.link().current_drawn)

    ilim = (350, 450)*mAmp  # current limit determined by chip
    off_prop_delay = 100*nSecond  # internal turn-off propagation delay, typ
    max_on_time = (4, 7.5)*uSecond
    min_off_time = (250, 550)*nSecond

    # peak current is IC current limit + 100ns (typ) internal propagation delay
    ipeak = self.ic.ilim + vin * off_prop_delay

    # recommended inductance 2.2uH to 47uH, depending on application
    # calculate inductance limits to allow achieving peak current within 6ns max
    # inductor equation: v = L di/dt  =>  imax = 1/L int(v dt) + i0  = > L = v * t / imax for constant v
    ramp_l_range = (2.2*uHenry*0.8,  # recommended min, plus allowing 20% inductors
                    vin.lower() * max_on_time.lower() / ilim.upper())

    # best achievable switching frequency, from inductor charging and discharging rates are:
    # ton = L * ip / Vin,  toff = L * ip / (Vout - Vin)
    # fs = 1/(ton + toff) = 1 / ( L*ip/Vin + L*ip/(Vout-Vin) )
    #   => 1 / ( L*ip*(Vout-Vin)/Vin*(Vout-Vin) + L*ip*Vin/((Vout-Vin)*Vin) )
    #   => 1 / ( L*ip*(Vout-Vin+Vin)/Vin*(Vout-Vin) )
    #   => Vin*(Vout-Vin) / (L*ipVout)
    # limited at 1MHz
    # max current delivered at this frequency is
    # charge per cycle is ip / 2 * toff = L * ip^2 / (2 * (Vout - Vin))
    # current is charge per cycle * switching frequency
    # => L * ip^2 / (2 * (Vout - Vin)) * Vin*(Vout-Vin) / (L*ipVout)
    # => L * ip^2 / (2 * Vin) * Vin*(Vout-Vin) / (L*ipVout)


    # note boost converter duty cycle equation D = 1 - (Vin/Vout) * eff

    # inductor choice must be within the maximum switching frequency
    # from datasheet: fs_max = Vin_min * (Vout - Vin) / (i_p * L * Vout)

    # self.ind = self.Block(Inductor(l_range, ipeak, self.frequency))

