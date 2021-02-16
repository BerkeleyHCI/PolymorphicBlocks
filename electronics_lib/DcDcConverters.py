from electronics_abstract_parts import *


class Tps561201_Device(DiscreteChip, CircuitBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()):
    super().__init__()
    self.pwr_in = self.Port(ElectricalSink(
      voltage_limits=(4.5, 17)*Volt,
      current_draw=current_draw
    ))
    self.gnd = self.Port(Ground())
    self.sw = self.Port(ElectricalSource())  # internal switch specs not defined, only bulk current limit defined
    self.fb = self.Port(AnalogSink(impedance=(8000, float('inf')) * kOhm))  # based on input current spec
    self.vbst = self.Port(ElectricalSource())

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.gnd,
        '2': self.sw,
        '3': self.pwr_in,
        '4': self.fb,
        '5': self.pwr_in,  # en
        '6': self.vbst,
      },
      mfr='Texas Instruments', part='TPS561201',
      datasheet='https://www.ti.com/lit/ds/symlink/tps561201.pdf'
    )


class Tps561201(DiscreteBuckConverter, GeneratorBlock):
  """Adjustable synchronous buck converter in SOT-23-6 with integrated switch"""
  def contents(self):
    super().contents()

    self.constrain(self.pwr_out.voltage_out.within((0.76, 17)*Volt))
    self.assign(self.frequency, 580*kHertz(tol=0))
    self.assign(self.efficiency, (0.7, 0.95))  # Efficiency stats from first page for ~>10mA  # TODO dedup w/ worst estimate?

    self.fb = self.Block(FeedbackVoltageDivider(
      output_voltage=(0.749, 0.787) * Volt,
      impedance=(1, 10) * kOhm,
      assumed_input_voltage=self.spec_output_voltage
    ))
    self.assign(self.pwr_out.voltage_out,
                (0.749*Volt / self.fb.selected_ratio.upper(),
                 0.787*Volt / self.fb.selected_ratio.lower()))

    self.generator(self.generate_converter,
                   self.pwr_in.link().voltage, self.pwr_out.voltage_out,
                   self.pwr_out.link().current_drawn,
                   self.frequency, self.output_ripple_limit, self.input_ripple_limit, self.ripple_current_factor,
                   targets=[self.fb, self.pwr_in, self.pwr_out, self.gnd])

  def generate_converter(self, input_voltage: RangeVal, output_voltage: RangeVal,
                         output_current: RangeVal, frequency: RangeVal,
                         spec_output_ripple: float, spec_input_ripple: float, ripple_factor: RangeVal) -> None:
    self.ic = self.Block(Tps561201_Device(
      current_draw=(self.pwr_out.link().current_drawn.lower() * self.pwr_out.voltage_out.lower() / self.pwr_in.link().voltage.upper() / self.efficiency.upper(),
                    self.pwr_out.link().current_drawn.upper() * self.pwr_out.voltage_out.upper() / self.pwr_in.link().voltage.lower() / self.efficiency.lower())
    ))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.gnd, self.ic.gnd)
    self.connect(self.fb.output, self.ic.fb)  # TODO should be in contents, but can't have split nets
    self.connect(self.fb.input, self.pwr_out)
    self.connect(self.fb.gnd, self.gnd)

    self.hf_in_cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # Datasheet 8.2.2.4
    self.connect(self.hf_in_cap.pwr, self.pwr_in)
    self.connect(self.hf_in_cap.gnd, self.gnd)

    self.vbst_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 6) * Volt))
    self.connect(self.vbst_cap.neg.as_electrical_sink(), self.ic.sw)
    self.connect(self.vbst_cap.pos.as_electrical_sink(), self.ic.vbst)

    # TODO dedup across all converters
    inductor_out = self._generate_converter(self.ic.sw, 1.2,
                                            input_voltage=input_voltage, output_voltage=output_voltage,
                                            output_current_max=output_current[1], frequency=frequency,
                                            spec_output_ripple=spec_output_ripple, spec_input_ripple=spec_input_ripple,
                                            ripple_factor=ripple_factor)

    self.connect(self.pwr_out, inductor_out.as_electrical_source(
      voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
      current_limits=(0, 1.2)*Amp
    ))

    # The control mechanism requires a specific capacitor / inductor selection, datasheet 8.2.2.3
    # TODO the ripple current needs to be massively increased
    # self.constrain(self.out_cap.capacitance.within((20, 68)*uFarad(tol=0.2)))
    # self.constrain(self.inductor.inductance.within((3.3, 4.7)*uHenry(tol=0.2)))  # TODO down to 2.2 for lower output voltages


class Tps54202h_Device(DiscreteChip, CircuitBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()):
    super().__init__()
    self.pwr_in = self.Port(ElectricalSink(
      voltage_limits=(4.5, 28)*Volt,
      current_draw=current_draw
    ))
    self.gnd = self.Port(Ground())
    self.sw = self.Port(ElectricalSource(
      current_limits=(0, 2)*Amp  # most conservative figures, low-side limited. TODO: better ones?
    ))  # internal switch specs not defined, only bulk current limit defined
    self.fb = self.Port(AnalogSink(impedance=(float('inf'), float('inf')) * Ohm))  # TODO specs not given
    self.boot = self.Port(ElectricalSource())
    self.en = self.Port(DigitalSink(  # must be connected, floating is disable
      voltage_limits=(-0.1, 7) * Volt,
      input_thresholds=(1.16, 1.35)*Volt
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.gnd,
        '2': self.sw,
        '3': self.pwr_in,
        '4': self.fb,
        '5': self.en,
        '6': self.boot,
      },
      mfr='Texas Instruments', part='TPS54202H',
      datasheet='https://www.ti.com/lit/ds/symlink/tps54202h.pdf'
    )


class Tps54202h(DiscreteBuckConverter, GeneratorBlock):
  """Adjustable synchronous buck converter in SOT-23-6 with integrated switch, 4.5-24v capable"""
  def contents(self):
    super().contents()

    self.assign(self.frequency, (390, 590)*kHertz)
    self.assign(self.efficiency, (0.75, 0.95))  # Efficiency stats from first page for ~>10mA

    self.fb = self.Block(FeedbackVoltageDivider(
      output_voltage=(0.581, 0.611) * Volt,
      impedance=(1, 10) * kOhm,
      assumed_input_voltage=self.spec_output_voltage
    ))
    self.assign(self.pwr_out.voltage_out,
                (0.581*Volt / self.fb.ratio.upper(),
                 0.611*Volt / self.fb.ratio.lower()))

    self.generator(self.generate_converter,
                   self.pwr_in.link().voltage, self.pwr_out.voltage_out,
                   self.pwr_out.link().current_drawn,
                   self.frequency, self.output_ripple_limit, self.input_ripple_limit, self.ripple_current_factor,
                   targets=[self.fb, self.pwr_in, self.pwr_out, self.gnd])

  def generate_converter(self, input_voltage: RangeVal, output_voltage: RangeVal,
                         output_current: RangeVal, frequency: RangeVal,
                         spec_output_ripple: float, spec_input_ripple: float, ripple_factor: RangeVal) -> None:
    self.ic = self.Block(Tps54202h_Device(
      current_draw=(self.pwr_out.link().current_drawn.lower() * self.pwr_out.voltage_out.lower() / self.pwr_in.link().voltage.upper() / self.efficiency.upper(),
                    self.pwr_out.link().current_drawn.upper() * self.pwr_out.voltage_out.upper() / self.pwr_in.link().voltage.lower() / self.efficiency.lower())
    ))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.gnd, self.ic.gnd)

    self.hf_in_cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # Datasheet 8.2.3.1, "optional"?
    self.connect(self.hf_in_cap.pwr, self.pwr_in)
    self.connect(self.hf_in_cap.gnd, self.gnd)

    self.boot_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 6) * Volt))
    self.connect(self.boot_cap.neg.as_electrical_sink(), self.ic.sw)
    self.connect(self.boot_cap.pos.as_electrical_sink(), self.ic.boot)

    self.en_res = self.Block(Resistor(resistance=510*kOhm(tol=0.05), power=0))  # arbitrary tolerance
    # pull-up resistor not used here because the voltage changes
    self.connect(self.pwr_in, self.en_res.a.as_electrical_sink())
    self.connect(self.en_res.b.as_digital_source(), self.ic.en)

    self.connect(self.fb.input, self.pwr_out)
    self.connect(self.fb.gnd, self.gnd)
    self.connect(self.fb.output, self.ic.fb)

    # TODO dedup across all converters
    inductor_out = self._generate_converter(self.ic.sw, 2,
                                            input_voltage=input_voltage, output_voltage=output_voltage,
                                            output_current_max=output_current[1], frequency=frequency,
                                            spec_output_ripple=spec_output_ripple, spec_input_ripple=spec_input_ripple,
                                            ripple_factor=ripple_factor)

    self.connect(self.pwr_out, inductor_out.as_electrical_source(
      voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
      current_limits=(0, 2)*Amp
    ))


class Lmr33630_Device(DiscreteChip, CircuitBlock):
  def __init__(self, current_draw: RangeLike = RangeExpr()):
    super().__init__()
    self.vin = self.Port(ElectricalSink(
      voltage_limits=(3.8, 36)*Volt,
      current_draw=current_draw
    ))
    self.pgnd = self.Port(Ground())
    self.agnd = self.Port(Ground())

    # self.en = self.Port(DigitalSink.from_supply(
    #   self.agnd, self.vin, voltage_limit_tolerance=(-0.3, 0.3)*Volt, current_draw=(0, 0)*Amp,
    #   input_threshold_abs=(0.3, 1.26)*Volt
    # ))
    self.fb = self.Port(AnalogSink(  # 0.985 - 1 - 1.015
      voltage_limits=(-0.3, 5.5)*Volt,
      impedance=(20, float('inf'))*MOhm  # derived from input current, 50nA @ 1V
    ))
    self.boot = self.Port(ElectricalSource())  # bootstrap
    # TODO model limits relative to SW as -0.3 - 5.5

    self.sw = self.Port(ElectricalSource(
      current_limits=(0, 3)*Amp
    ))

    self.vcc = self.Port(ElectricalSource(  # internal 5v LDO
      voltage_out=(4.75, 5.25)*Volt,  # TODO has a UVLO
      current_limits=(0, 0)*Amp  # datasheet 9.2.2.8, "avoid loading this output with any external circuitry"
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.71x3.4mm',
      {
        '1': self.pgnd,
        '2': self.vin,
        '3': self.vin,  # TODO actually en pin, but force tied high until explicit bridging implemented
        # '4': self.pg,  # TODO not defined for now
        '5': self.fb,
        '6': self.vcc,
        '7': self.boot,
        '8': self.sw,
        '9': self.agnd,  # thermal pad
      },
      mfr='Texas Instruments', part='LMR33630BDDAR',
      datasheet='https://www.ti.com/lit/ds/symlink/lmr33630.pdf'
    )


class Lmr33630(DiscreteBuckConverter, GeneratorBlock):
  """Adjustable synchronous buck converter in SOIC-8 EP with integrated switch"""
  DUTYCYCLE_MIN_LIMIT = 0.0
  DUTYCYCLE_MAX_LIMIT = 0.98

  def contents(self):
    super().contents()

    self.constrain(self.pwr_out.voltage_out.within((1, 24)*Volt))
    self.assign(self.frequency, 400*kHertz(tol=0))  # TODO also comes in 1.4 and 2.1MHz versions
    self.assign(self.efficiency, (0.7, 0.98))  # Efficiency stats from first page for ~>10mA

    self.fb = self.Block(FeedbackVoltageDivider(
      output_voltage=(0.985, 1.015) * Volt,  # TODO dedup w/ the definition in the device?
      impedance=(10, 100) * kOhm,
      assumed_input_voltage=self.spec_output_voltage
    ))
    self.assign(self.pwr_out.voltage_out,
                (0.985*Volt / self.fb.ratio.upper(),
                 1.015*Volt / self.fb.ratio.lower()))

    self.generator(self.generate_converter,
                   self.pwr_in.link().voltage, self.pwr_out.voltage_out,
                   self.pwr_out.link().current_drawn,
                   self.frequency, self.output_ripple_limit, self.input_ripple_limit, self.ripple_current_factor,
                   targets=[self.fb, self.pwr_in, self.pwr_out, self.gnd])

  def generate_converter(self, input_voltage: RangeVal, output_voltage: RangeVal,
                         output_current: RangeVal, frequency: RangeVal,
                         spec_output_ripple: float, spec_input_ripple: float, ripple_factor: RangeVal) -> None:
    self.ic = self.Block(Lmr33630_Device(
      current_draw=(self.pwr_out.link().current_drawn.lower() * self.pwr_out.voltage_out.lower() / self.pwr_in.link().voltage.upper() / self.efficiency.upper(),
                    self.pwr_out.link().current_drawn.upper() * self.pwr_out.voltage_out.upper() / self.pwr_in.link().voltage.lower() / self.efficiency.lower())
    ))
    self.connect(self.pwr_in, self.ic.vin)
    self.connect(self.gnd, self.ic.pgnd, self.ic.agnd)

    self.hf_in_cap = self.Block(DecouplingCapacitor(capacitance=0.22*uFarad(tol=0.2)))  # application circuit in 9.2
    self.connect(self.hf_in_cap.pwr, self.pwr_in)
    self.connect(self.hf_in_cap.gnd, self.gnd)

    self.boot_cap = self.Block(Capacitor(
      capacitance=0.1*uFarad(tol=0.2),
      voltage=(0, 10) * Volt))  # datasheet 9.2.2.7
    self.connect(self.boot_cap.pos.as_electrical_sink(), self.ic.boot)
    self.connect(self.boot_cap.neg.as_electrical_sink(), self.ic.sw)

    self.vcc_cap = self.Block(Capacitor(
      capacitance=1*uFarad(tol=0.2),
      voltage=(0, 16) * Volt))  # datasheet 9.2.2.8
    self.connect(self.vcc_cap.pos.as_electrical_sink(), self.ic.vcc)
    self.connect(self.vcc_cap.neg.as_electrical_sink(), self.gnd)


    self.connect(self.fb.input, self.pwr_out)
    self.connect(self.fb.gnd, self.gnd)
    self.connect(self.fb.output, self.ic.fb)

    inductor_out = self._generate_converter(self.ic.sw, 3.0,
                                            input_voltage=input_voltage, output_voltage=output_voltage,
                                            output_current_max=output_current[1], frequency=frequency,
                                            spec_output_ripple=spec_output_ripple, spec_input_ripple=spec_input_ripple,
                                            ripple_factor=ripple_factor)
    self.connect(self.pwr_out, inductor_out.as_electrical_source(
      voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
      current_limits=(0, 3.0)*Amp
    ))


class Ap3012_Device(DiscreteChip, CircuitBlock):
  def __init__(self, current_draw: RangeLike = RangeExpr()):
    # TODO the power path doesn't actually go through Vin, instead it goes through the inductor
    # But this is modeled here to be similar to the buck case, and the macromodel is valid anyways
    super().__init__()
    self.pwr_in = self.Port(ElectricalSink(
      voltage_limits=(2.6, 16)*Volt,
      current_draw=current_draw
    ))
    self.gnd = self.Port(Ground())
    self.sw = self.Port(ElectricalSource(
      current_limits=(0, 500)*mAmp  # TODO how to model sink current limits?!
    ))
    self.fb = self.Port(AnalogSink(impedance=(12500, float('inf')) * kOhm))  # based on input current spec
      # voltage_out=(1.33, 29)*Volt,  # minimum-but-not-minimum from FB max # TODO need const prop range subsetting

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.sw,
        '2': self.gnd,
        '3': self.fb,
        '4': self.pwr_in,  # /SHDN
        '5': self.pwr_in,
      },
      mfr='Diodes Incorporated', part='AP3012KTR-G1',
      datasheet='https://www.diodes.com/assets/Datasheets/AP3012.pdf'
    )


class Ap3012(DiscreteBoostConverter, GeneratorBlock):
  """Adjustable boost converter in SOT-23-5 with integrated switch"""
  def contents(self):
    super().contents()
    self.assign(self.frequency, (1.1, 1.9)*MHertz)
    self.assign(self.efficiency, (0.75, 0.8))  # Efficiency stats from first page for ~>10mA

    self.fb = self.Block(FeedbackVoltageDivider(
      output_voltage=(1.17, 1.33) * Volt,
      impedance=(1, 10) * kOhm,
      assumed_input_voltage=self.spec_output_voltage
    ))
    self.assign(self.pwr_out.voltage_out,
                (1.17*Volt / self.fb.ratio.upper(),
                 1.33*Volt / self.fb.ratio.lower()))

    self.generator(self.generate_converter,
                   self.pwr_in.link().voltage, self.pwr_out.voltage_out,
                   self.pwr_out.link().current_drawn,
                   self.frequency, self.output_ripple_limit, self.input_ripple_limit, self.ripple_current_factor,
                   targets=[self.fb, self.pwr_in, self.pwr_out, self.gnd])


  def generate_converter(self, input_voltage: RangeVal, output_voltage: RangeVal,
                         output_current: RangeVal, frequency: RangeVal,
                         spec_output_ripple: float, spec_input_ripple: float, ripple_factor: RangeVal) -> None:
    self.ic = self.Block(Ap3012_Device(
      current_draw=(self.pwr_out.link().current_drawn.lower() * self.pwr_out.voltage_out.lower() / self.pwr_in.link().voltage.upper() / self.efficiency.upper(),
                    self.pwr_out.link().current_drawn.upper() * self.pwr_out.voltage_out.upper() / self.pwr_in.link().voltage.lower() / self.efficiency.lower())
    ))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.gnd, self.ic.gnd)

    self.connect(self.fb.input, self.pwr_out)
    self.connect(self.fb.gnd, self.gnd)
    self.connect(self.fb.output, self.ic.fb)

    self.rect = self.Block(Diode(
      reverse_voltage=(0, self.pwr_out.voltage_out.upper()),
      current=self.pwr_out.link().current_drawn,
      voltage_drop=(0, 0.4)*Volt,
      reverse_recovery_time=(0, 500) * nSecond  # guess from Digikey's classification for "fast recovery"
    ))
    self.connect(self.ic.sw, self.rect.anode.as_electrical_sink())
    diode_out = self.rect.cathode.as_electrical_source(
      voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
      current_limits=(0, 0.5)*Amp  # TODO proper switch current modeling?
    )
    self.connect(diode_out, self.pwr_out)

    self._generate_converter(self.ic.sw, 0.5,
                             input_voltage=input_voltage, output_voltage=output_voltage,
                             output_current_max=output_current[1], frequency=frequency,
                             spec_output_ripple=spec_output_ripple, spec_input_ripple=spec_input_ripple,
                             ripple_factor=ripple_factor)
