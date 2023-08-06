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
    efficiency_est = Range(0.7, 0.85)  # given by datasheet

    ilim = (350, 450)*mAmp  # current limit determined by chip
    off_prop_delay = 100*nSecond  # internal turn-off propagation delay, typ
    max_on_time = (4, 7.5)*uSecond
    min_off_time = (250, 550)*nSecond

    # peak current is IC current limit + 100ns (typ) internal propagation delay
    ipeak = self.ic.ilim + vin * off_prop_delay

    # recommended inductance 2.2uH to 47uH, depending on application
    # calculate inductance limits to allow achieving peak current within 6ns max
    # inductor equation: v = L di/dt  =>  imax = 1/L int(v dt) + i0  = > L = v * t / imax for constant v
    ramp_l_max = vin.lower() * max_on_time.lower() / ilim.upper()

    # best achievable switching frequency, from inductor charging and discharging rates are:
    # ton = L * ip / Vin,  toff = L * ip / (Vout - Vin)
    # fs = 1/(ton + toff) = 1 / ( L*ip/Vin + L*ip/(Vout-Vin) )
    #   => 1 / ( L*ip*(Vout-Vin)/Vin*(Vout-Vin) + L*ip*Vin/((Vout-Vin)*Vin) )
    #   => 1 / ( L*ip*(Vout-Vin+Vin)/Vin*(Vout-Vin) )
    #   => Vin*(Vout-Vin) / (L*ip*Vout)
    # and fs <= 1MHz
    # note, above equation has maxima at Vin = Vout/2, Vout maximum
    vout_fs_max = vout.upper()
    if vin.lower() <= vout_fs_max / 2 and vin.upper() >= vout_fs_max / 2:
      vin_fs_max = vout_fs_max / 2
    elif vin.lower() > vout_fs_max / 2:
      vin_fs_max = vin.lower()
    else:
      vin_fs_max = vin.upper()
    ramp_l_min = vin_fs_max * (vout_fs_max - vin_fs_max) / (1*MHertz * ipeak.lower() * vout_fs_max)

    self.ind = self.Block(Inductor((ramp_l_min, ramp_l_max), ipeak, self.frequency))

    # max current delivered at this frequency is
    # charge per cycle is ip / 2 * toff = L * ip^2 / (2 * (Vout - Vin))
    # current is charge per cycle * switching frequency
    # => L * ip^2 / (2 * (Vout - Vin)) * Vin*(Vout-Vin) / (L*ip*Vout)
    # => ip / 2 * Vin / Vout
    # => ip * Vin / (2 * Vout)
    max_current = efficiency_est * ipeak * vin / (2 * vout)
    self.require(self.pwr_out.link().current_drawn.within((0, max_current.lower())))

    self.in_cap = self.Block(DecouplingCapacitor(  # recommended by the datasheet
      capacitance=4.7*uFarad(tol=0.2)
    )).connected(self.gnd, self.pwr_in)

    # capacitor i=C dv/dt => dv = i*dt / C = q / C
    # using charge per cycle above: dv = L * ip^2 / (2 * (Vout - Vin)) / C
    # C = 1/dv * L * ip^2 / (2 * (Vout - Vin))
    # TODO: is this simplified model correct? the datasheet accounts for current draw during the ton period,
    #   in addition to charge pumped during the toff cycle; but also qin must be balanced with qout
    # TODO: could also reduce the capacitance by subtracting output draw during the t_off period
    # C = 1/dv * [(L * ip^2 / (2 * (Vout - Vin)) - iout * toff]
    #  => 1/dv * [(L * ip^2 / (2 * (Vout - Vin)) - iout * L * ip / (Vout - Vin)]
    #  => (L * ip)/dv * [(ip / (2 * (Vout - Vin)) - iout / (Vout - Vin)
    #  => (L * ip)/(dv*(Vout - Vin) * [ip/2 - iout]
    # note, this ripple is on top of the reference voltage hysteresis / tolerances, reflected in the
    # output voltage tolerance
    # this is substantially equivalent to the Output Capacitor Selection datasheet equation, minus capcitor ESR
    output_capacitance = Range.from_lower(
      self.ind.actual_inductance.upper() * ipeak.upper() / (
        self.output_ripple_limit * (vout.lower - vin.upper()))
      * (ipeak.upper() / 2 - iload.lower())
    )
    self.in_cap = self.Block(DecouplingCapacitor(  # recommended by the datasheet
      capacitance=output_capacitance * Farad
    )).connected(self.gnd, self.pwr_in)
