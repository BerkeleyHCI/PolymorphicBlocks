from typing import *

from electronics_abstract_parts import *


class Ld1117_Device(DiscreteChip, FootprintBlock):
  @init_in_parent
  def __init__(self, part: StringLike = StringExpr(), voltage_out: RangeLike = RangeExpr()):
    super().__init__()
    self.part_in = self.Parameter(StringExpr(part))

    self.quiescent_current = self.Parameter(RangeExpr((5, 10) * mAmp))
    self.dropout = self.Parameter(RangeExpr((0, 1.2) * Volt))

    # Part datasheet, Table 9
    self.vin = self.Port(VoltageSink(
      voltage_limits=(0, 15) * Volt,
      current_draw=RangeExpr()
    ))
    self.vout = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=(0, 0.8) * Amp  # most conservative estimate, up to 1300mA
    ))
    self.assign(self.vin.current_draw, self.vout.link().current_drawn + self.quiescent_current)
    self.gnd = self.Port(Ground())

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
      {
        '1': self.gnd,
        '2': self.vout,
        '3': self.vin,
      },
      mfr='STMicroelectronics', part=self.part_in,
      datasheet='https://www.st.com/content/ccc/resource/technical/document/datasheet/99/3b/7d/91/91/51/4b/be/CD00000544.pdf/files/CD00000544.pdf/jcr:content/translations/en.CD00000544.pdf',
    )


class Ld1117(LinearRegulator, GeneratorBlock):
  def __init__(self, voltage_out: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.generator(self.select_part, self.spec_output_voltage,
                   targets=[self.pwr_in, self.pwr_out, self.gnd])

  def select_part(self, spec_output_voltage: Range):  # TODO can some block params be made available pre-generate?
    parts = [
      # output voltage, quiescent current
      (Range(1.140, 1.260), 'LD1117S12TR'),
      (Range(1.76, 1.84), 'LD1117S18TR'),
      (Range(2.45, 2.55), 'LD1117S25TR'),
      (Range(3.235, 3.365), 'LD1117S33TR'),
      (Range(4.9, 5.1), 'LD1117S50TR'),
    ]
    suitable_parts = [(part_out, part_number)
      for part_out, part_number in parts
      if part_out in spec_output_voltage
    ]
    assert suitable_parts, f"no regulator with compatible output {spec_output_voltage}"
    part_out, part_number = suitable_parts[0]

    self.ic = self.Block(Ld1117_Device(part=part_number, voltage_out=part_out*Volt))
    self.assign(self.dropout, self.ic.dropout)
    self.assign(self.quiescent_current, self.ic.quiescent_current)

    self.in_cap = self.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=10 * uFarad(tol=0.2)))

    # wire things together
    self.connect(self.ic.vin, self.in_cap.pwr, self.pwr_in)
    self.connect(self.ic.vout, self.out_cap.pwr, self.pwr_out)
    self.connect(self.ic.gnd, self.in_cap.gnd, self.out_cap.gnd, self.gnd)


class Ldl1117_Device(DiscreteChip, FootprintBlock):
  @init_in_parent
  def __init__(self, part: StringLike = StringExpr(), voltage_out: RangeLike = RangeExpr()):
    super().__init__()
    self.part_in = self.Parameter(StringExpr(part))

    self.quiescent_current = self.Parameter(RangeExpr((0, 500) * uAmp))  # typ is 250uA
    self.dropout = self.Parameter(RangeExpr((0, 0.6) * Volt))  # worst-case, typ is 0.35

    # Part datasheet, Table 9
    self.vin = self.Port(VoltageSink(
      voltage_limits=(2.6, 18) * Volt,
      current_draw=RangeExpr()
    ))
    self.vout = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=(0, 1.5) * Amp  # most conservative estimate, typ up to 2A
    ))
    self.assign(self.vin.current_draw, self.vout.link().current_drawn + self.quiescent_current)
    self.gnd = self.Port(Ground())

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
      {
        '1': self.gnd,
        '2': self.vout,
        '3': self.vin,
      },
      mfr='STMicroelectronics', part=self.part_in,
      datasheet='https://www.st.com/content/ccc/resource/technical/document/datasheet/group3/0e/5a/00/ca/10/1a/4f/a5/DM00366442/files/DM00366442.pdf/jcr:content/translations/en.DM00366442.pdf',
    )


class Ldl1117(LinearRegulator, GeneratorBlock):
  def __init__(self, voltage_out: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.generator(self.select_part, self.spec_output_voltage,
                   targets=[self.pwr_in, self.pwr_out, self.gnd])

  def select_part(self, spec_output_voltage: Range):  # TODO can some block params be made available pre-generate?
    TOLERANCE = 0.03  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [
      # output voltage, quiescent current
      (1.185, 'LDL1117S12R'),
      (1.5, 'LDL1117S15R'),
      (1.8, 'LDL1117S18R'),
      (2.5, 'LDL1117S25R'),
      (3.0, 'LDL1117S30R'),
      (3.3, 'LDL1117S33R'),
      (5.0, 'LDL1117S50R'),
    ]
    suitable_parts = [(part_out_nominal, part_number)
                      for part_out_nominal, part_number in parts
                      if Range.from_tolerance(part_out_nominal, TOLERANCE) in spec_output_voltage
                      ]
    assert suitable_parts, f"no regulator with compatible output {spec_output_voltage}"
    part_out_nominal, part_number = suitable_parts[0]

    self.ic = self.Block(Ldl1117_Device(part=part_number, voltage_out=part_out_nominal*Volt(tol=TOLERANCE)))
    self.assign(self.dropout, self.ic.dropout)
    self.assign(self.quiescent_current, self.ic.quiescent_current)

    self.in_cap = self.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=4.7 * uFarad(tol=0.2)))

    # wire things together
    self.connect(self.ic.vin, self.in_cap.pwr, self.pwr_in)
    self.connect(self.ic.vout, self.out_cap.pwr, self.pwr_out)
    self.connect(self.ic.gnd, self.in_cap.gnd, self.out_cap.gnd, self.gnd)


class Ap2204k_Device(DiscreteChip, FootprintBlock):
  # note TI compatible devices: TPS709 (w/ EN disconnected); LP2985, LP2992 (16V + BYP)
  @init_in_parent
  def __init__(self, part: StringLike = StringExpr(), voltage_out: RangeLike = RangeExpr()):
    super().__init__()
    self.part_in = self.Parameter(StringExpr(part))

    self.dropout = self.Parameter(RangeExpr((0, 0.5) * Volt))  # worst-case, 150mA Iout
    self.quiescent_current = self.Parameter(RangeExpr((0.020, 2.5) * mAmp))  # ground current, not including standby current

    # Part datasheet, Recommended Operating Conditions
    self.vin = self.Port(VoltageSink(
      voltage_limits=(0, 24) * Volt,
      current_draw=RangeExpr()
    ), [Power])
    self.vout = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=(0, 0.15) * Amp
    ))
    self.assign(self.vin.current_draw, self.vout.link().current_drawn + self.quiescent_current)
    self.en = self.Port(DigitalSink(
      voltage_limits=(0, 24) * Volt,
      current_draw=(0, 1)*uAmp,  # TYP rating, min/max bounds not given
      input_thresholds=(0.4, 2.0)*Volt
    ))
    self.gnd = self.Port(Ground(), [Common])

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.vin,
        '2': self.gnd,
        '3': self.en,  # EN
        # pin 4 is ADJ/NC
        '5': self.vout,
      },
      mfr='Diodes Incorporated', part=self.part_in,
      datasheet='https://www.diodes.com/assets/Datasheets/AP2204.pdf'
    )


class Ap2204k_Block(GeneratorBlock):  # TODO needs better categorization than top-level blocks
  @init_in_parent
  def __init__(self, output_voltage: RangeLike = RangeExpr()):
    super().__init__()

    self.spec_output_voltage = self.Parameter(RangeExpr(output_voltage))

    self.pwr_in = self.Port(VoltageSink(), [Power])
    self.pwr_out = self.Port(VoltageSource())
    self.gnd = self.Port(Ground(), [Common])
    self.en = self.Port(DigitalSink())

    self.dropout = self.Parameter(RangeExpr())
    self.quiescent_current = self.Parameter(RangeExpr())

    self.require(self.pwr_out.voltage_out.within(output_voltage))

    self.generator(self.select_part, self.spec_output_voltage,
                   targets=[self.pwr_in, self.pwr_out, self.gnd, self.en])

  def select_part(self, spec_output_voltage: Range):
    TOLERANCE = 0.02
    parts = [
      # output voltage, quiescent current
      (5, 'AP2204K-5.0'),
      (3.3, 'AP2204K-3.3'),
      (3.0, 'AP2204K-3.0'),
      (2.8, 'AP2204K-2.8'),
      (2.5, 'AP2204K-2.5'),
      (1.8, 'AP2204K-1.8'),
      (1.5, 'AP2204K-1.5'),
    ]
    suitable_parts = [(part_out_nominal, part_number)
                      for part_out_nominal, part_number in parts
                      if Range.from_tolerance(part_out_nominal, TOLERANCE) in spec_output_voltage
                      ]
    assert suitable_parts, f"no regulator with compatible output {spec_output_voltage}"
    part_out_nominal, part_number = suitable_parts[0]

    self.ic = self.Block(Ap2204k_Device(part=part_number, voltage_out=part_out_nominal*Volt(tol=TOLERANCE)))
    self.connect(self.ic.vin, self.pwr_in)
    self.connect(self.ic.vout, self.pwr_out)
    self.connect(self.ic.gnd, self.gnd)
    self.connect(self.ic.en, self.en)
    self.assign(self.dropout, self.ic.dropout)
    self.assign(self.quiescent_current, self.ic.quiescent_current)

    self.in_cap = self.Block(DecouplingCapacitor(capacitance=1.1 * uFarad(tol=0.2)))
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=2.2 * uFarad(tol=0.2)))
    self.connect(self.in_cap.pwr, self.pwr_in)
    self.connect(self.out_cap.pwr, self.pwr_out)
    self.connect(self.in_cap.gnd, self.out_cap.gnd, self.gnd)


class Ap2204k(LinearRegulator):
  # A AP2204 block that provides the LinearRegulator interface, tying the enable high
  # TODO unify with _Block version, with optional en and generators

  def contents(self):
    self.ic = self.Block(Ap2204k_Block(self.spec_output_voltage))
    self.assign(self.dropout, self.ic.dropout)
    self.assign(self.quiescent_current, self.ic.quiescent_current)

    assert self.pwr_in.bridge_type is not None  # TODO get rid of this
    bridge = self.Block(self.pwr_in.bridge_type())
    setattr(self, '(bridge)pwr_in_bridge', bridge)  # TODO there should be a create_bridge or something; setattr used to avoid creating extra hierarchy for netlisting
    self.connect(self.pwr_in, bridge.outer_port)
    self.connect(bridge.inner_link, self.ic.pwr_in)
    self.connect(bridge.inner_link.as_digital_source(), self.ic.en)
    self.connect(self.pwr_out, self.ic.pwr_out)
    self.connect(self.gnd, self.ic.gnd)


class Xc6209_Device(DiscreteChip, FootprintBlock):
  # TODO REVISE ME
  @init_in_parent
  def __init__(self, part: StringLike = StringExpr(), voltage_out: RangeLike = RangeExpr()):
    super().__init__()
    self.part_in = self.Parameter(StringExpr(part))

    self.quiescent_current = self.Parameter(RangeExpr((0, 500) * uAmp))  # typ is 250uA
    self.dropout = self.Parameter(RangeExpr((0, 0.6) * Volt))  # worst-case, typ is 0.35

    # Part datasheet, Table 9
    self.vin = self.Port(VoltageSink(
      voltage_limits=(2.6, 18) * Volt,
      current_draw=RangeExpr()
    ))
    self.vout = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=(0, 1.5) * Amp  # most conservative estimate, typ up to 2A
    ))
    self.assign(self.vin.current_draw, self.vout.link().current_drawn + self.quiescent_current)
    self.gnd = self.Port(Ground())

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
      {
        '1': self.gnd,
        '2': self.vout,
        '3': self.vin,
      },
      mfr='STMicroelectronics', part=self.part_in,
      datasheet='https://www.st.com/content/ccc/resource/technical/document/datasheet/group3/0e/5a/00/ca/10/1a/4f/a5/DM00366442/files/DM00366442.pdf/jcr:content/translations/en.DM00366442.pdf',
    )


class Xc6209(LinearRegulator, GeneratorBlock):
  """XC6209F (F: 300mA version, no pull-down resistor; 2: +/-2% accuracy)"""
  # TODO REVISE ME
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.generator(self.select_part, self.spec_output_voltage,
                   targets=[self.pwr_in, self.pwr_out, self.gnd])

  def select_part(self, spec_output_voltage: Range):  # TODO can some block params be made available pre-generate?
    TOLERANCE = 0.02  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [
      # output voltage, quiescent current
      (1.5, 'XC6209F152MR-G'),
      (3.3, 'XC6209F332MR-G'),
      (5.0, 'XC6209F502MR-G'),
    ]
    suitable_parts = [(part_out_nominal, part_number)
                      for part_out_nominal, part_number in parts
                      if Range.from_tolerance(part_out_nominal, TOLERANCE) in spec_output_voltage
                      ]
    assert suitable_parts, f"no regulator with compatible output {spec_output_voltage}"
    part_out_nominal, part_number = suitable_parts[0]

    self.ic = self.Block(Ldl1117_Device(part=part_number, voltage_out=part_out_nominal*Volt(tol=TOLERANCE)))
    self.assign(self.dropout, self.ic.dropout)
    self.assign(self.quiescent_current, self.ic.quiescent_current)

    self.in_cap = self.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=4.7 * uFarad(tol=0.2)))

    # wire things together
    self.connect(self.ic.vin, self.in_cap.pwr, self.pwr_in)
    self.connect(self.ic.vout, self.out_cap.pwr, self.pwr_out)
    self.connect(self.ic.gnd, self.in_cap.gnd, self.out_cap.gnd, self.gnd)
