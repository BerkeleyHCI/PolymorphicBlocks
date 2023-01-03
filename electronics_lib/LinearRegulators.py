from electronics_abstract_parts import *
from electronics_lib.JlcPart import JlcPart


class Ld1117_Device(LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (0, 15) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 0.8) * Amp)  # most conservative estimate, up to 1300mA
    self.assign(self.actual_quiescent_current, (5, 10) * mAmp)
    self.assign(self.actual_dropout, (0, 1.2) * Volt)

    self.generator(self.select_part, output_voltage)

  def select_part(self, output_voltage: Range):
    parts = [  # output voltage
      (Range(1.140, 1.260), 'LD1117S12TR', 'C155612'),
      (Range(1.76, 1.84), 'LD1117S18TR', 'C80598'),
      (Range(2.45, 2.55), 'LD1117S25TR', 'C26457'),
      (Range(3.235, 3.365), 'LD1117S33TR', 'C86781'),
      (Range(4.9, 5.1), 'LD1117S50TR', 'C134077'),
    ]
    suitable_parts = [(part_out, part_number, lcsc_part) for part_out, part_number, lcsc_part in parts
                      if part_out.fuzzy_in(output_voltage)]
    assert suitable_parts, f"no regulator with compatible output {output_voltage}"
    part_output_voltage, part_number, lcsc_part = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage)
    self.assign(self.lcsc_part, lcsc_part)
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
      {
        '1': self.gnd,
        '2': self.pwr_out,
        '3': self.pwr_in,
      },
      mfr='STMicroelectronics', part=part_number,
      datasheet='https://www.st.com/content/ccc/resource/technical/document/datasheet/99/3b/7d/91/91/51/4b/be/CD00000544.pdf/files/CD00000544.pdf/jcr:content/translations/en.CD00000544.pdf',
    )


class Ld1117(LinearRegulator):
  def contents(self) -> None:
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ld1117_Device(self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=10 * uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)


class Ldl1117_Device(LinearRegulatorDevice, GeneratorBlock, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2.6, 18) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 1.5) * Amp)  # most conservative estimate, typ up to 2A
    self.assign(self.actual_quiescent_current, (0, 500) * uAmp)  # typ is 250uA
    self.assign(self.actual_dropout, (0, 0.6) * Volt)  # worst-case, typ is 0.35

    self.generator(self.select_part, output_voltage)

  def select_part(self, output_voltage: Range):
    TOLERANCE = 0.03  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [  # output voltage
      (1.185, 'LDL1117S12R'),
      (1.5, 'LDL1117S15R'),
      (1.8, 'LDL1117S18R'),
      (2.5, 'LDL1117S25R'),
      (3.0, 'LDL1117S30R'),
      (3.3, 'LDL1117S33R'),
      (5.0, 'LDL1117S50R'),
    ]
    suitable_parts = [(part_out_nominal, part_number) for part_out_nominal, part_number in parts
                      if Range.from_tolerance(part_out_nominal, TOLERANCE) in output_voltage]
    assert suitable_parts, f"no regulator with compatible output {output_voltage}"
    part_output_voltage_nominal, part_number = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage_nominal * Volt(tol=TOLERANCE))
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
      {
        '1': self.gnd,
        '2': self.pwr_out,
        '3': self.pwr_in,
      },
      mfr='STMicroelectronics', part=part_number,
      datasheet='https://www.st.com/content/ccc/resource/technical/document/datasheet/group3/0e/5a/00/ca/10/1a/4f/a5/DM00366442/files/DM00366442.pdf/jcr:content/translations/en.DM00366442.pdf',
    )


class Ldl1117(LinearRegulator):
  def contents(self) -> None:
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ld1117_Device(self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=4.7 * uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)


class Ap2204k_Device(LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    # Part datasheet, Recommended Operating Conditions
    self.assign(self.pwr_in.voltage_limits, (0, 24) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 0.15) * Amp)
    self.assign(self.actual_quiescent_current, (0.020, 2.5) * mAmp)  # ground current, not including standby current
    self.assign(self.actual_dropout, (0, 0.5) * Volt)  # worst-case, 150mA Iout

    self.en = self.Port(DigitalSink(
      voltage_limits=(0, 24) * Volt,
      current_draw=(0, 1)*uAmp,  # TYP rating, min/max bounds not given
      input_thresholds=(0.4, 2.0)*Volt
    ))

    self.generator(self.select_part, output_voltage)

  def select_part(self, output_voltage: Range):
    TOLERANCE = 0.02
    parts = [
      # output voltage, quiescent current
      (5, 'AP2204K-5.0', 'C112031'),
      (3.3, 'AP2204K-3.3', 'C112032'),
      (3.0, 'AP2204K-3.0', 'C460339'),
      # (2.8, 'AP2204K-2.8'),  # not stocked at JLC
      # (2.5, 'AP2204K-2.5'),
      (1.8, 'AP2204K-1.8', 'C460338'),
      # (1.5, 'AP2204K-1.5'),
    ]
    suitable_parts = [part for part in parts
                      if Range.from_tolerance(part[0], TOLERANCE) in output_voltage]
    assert suitable_parts, f"no regulator with compatible output {output_voltage}"
    part_output_voltage_nominal, part_number, jlc_number = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage_nominal * Volt(tol=TOLERANCE))
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.en,  # EN
        # pin 4 is ADJ/NC
        '5': self.pwr_out,
      },
      mfr='Diodes Incorporated', part=part_number,
      datasheet='https://www.diodes.com/assets/Datasheets/AP2204.pdf'
    )
    self.assign(self.lcsc_part, jlc_number)
    self.assign(self.actual_basic_part, False)


class Ap2204k_Block(Block):
  """AP2204 application circuit with the EN pin available."""
  @init_in_parent
  def __init__(self, output_voltage: RangeLike) -> None:
    super().__init__()

    self.ic = self.Block(Ap2204k_Device(output_voltage))
    self.pwr_in = self.Export(self.ic.pwr_in, [Power])
    self.pwr_out = self.Export(self.ic.pwr_out)
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.en = self.Export(self.ic.en)

    self.in_cap = self.Block(DecouplingCapacitor(capacitance=1.1 * uFarad(tol=0.2)))
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=2.2 * uFarad(tol=0.2)))

    self.connect(self.pwr_in, self.in_cap.pwr)
    self.connect(self.pwr_out, self.out_cap.pwr)
    self.connect(self.gnd, self.in_cap.gnd, self.out_cap.gnd)


class Ap2204k(LinearRegulator):
  """AP2204K block providing the LinearRegulator interface, with EN tied high
  TODO: can there just be one block, with optional EN?
  """
  def contents(self):
    self.ic = self.Block(Ap2204k_Block(self.output_voltage))

    self.connect(self.pwr_out, self.ic.pwr_out)
    self.connect(self.gnd, self.ic.gnd)
    assert self.pwr_in.bridge_type is not None  # TODO get rid of this
    bridge = self.Block(self.pwr_in.bridge_type())
    setattr(self, '(bridge)pwr_in_bridge', bridge)  # TODO there should be a create_bridge or something; setattr used to avoid creating extra hierarchy for netlisting
    self.connect(self.pwr_in, bridge.outer_port)
    self.connect(bridge.inner_link, self.ic.pwr_in)
    self.connect(bridge.inner_link.as_digital_source(), self.ic.en)


class Xc6209_Device(LinearRegulatorDevice, GeneratorBlock, FootprintBlock):
  # Also pin-compatible with MCP1802 and NJM2882F (which has a noise bypass pin)
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2, 10) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 300) * mAmp)
    self.assign(self.actual_quiescent_current, (0.01, 50) * uAmp)  # typ is 250uA

    self.generator(self.select_part, output_voltage)

  def select_part(self, output_voltage: Range):
    TOLERANCE = 0.02  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [  # output voltage, part number, (dropout typ @ 30mA, dropout max @ 100mA), max current
      (1.5, 'XC6209F152MR-G', (0.50, 0.60)),
      (3.3, 'XC6209F332MR-G', (0.06, 0.25)),
      (5.0, 'XC6209F502MR-G', (0.05, 0.21)),
    ]
    suitable_parts = [(part_out_nominal, part_number, part_dropout)
                      for part_out_nominal, part_number, part_dropout in parts
                      if Range.from_tolerance(part_out_nominal, TOLERANCE) in output_voltage]
    assert suitable_parts, f"no regulator with compatible output {output_voltage}"
    part_output_voltage_nominal, part_number, part_dropout = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage_nominal * Volt(tol=TOLERANCE))
    self.assign(self.actual_dropout, part_dropout * Volt)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.pwr_in,  # EN
        # pin 4 is NC
        '5': self.pwr_out,
      },
      mfr='Torex Semiconductor Ltd', part=part_number,
      datasheet='https://www.torexsemi.com/file/en/products/discontinued/-2016/53-XC6209_12.pdf',
    )


class Xc6209(LinearRegulator):
  """XC6209F (F: 300mA version, no pull-down resistor; 2: +/-2% accuracy)
  Low-ESR ceramic cap compatible"""
  def contents(self) -> None:
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Xc6209_Device(output_voltage=self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)


class Ap2210_Device(LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2.5, 13.2) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 300) * mAmp)
    self.assign(self.actual_quiescent_current, (0.01, 15000) * uAmp)  # GND pin current
    self.assign(self.actual_dropout, (15, 500) * mVolt)

    self.generator(self.select_part, output_voltage)

  def select_part(self, output_voltage: Range):
    TOLERANCE = 0.02  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [  # output voltage
      (2.5, 'AP2210K-2.5', 'C460340'),
      # (3.0, 'AP2210K-3.0'),  # JLC part not available
      (3.3, 'AP2210K-3.3', 'C176959'),
      (5.0, 'AP2210K-5.0', 'C500758'),
    ]
    suitable_parts = [part for part in parts
                      if Range.from_tolerance(part[0], TOLERANCE) in output_voltage]
    assert suitable_parts, f"no regulator with compatible output {output_voltage}"
    part_output_voltage_nominal, part_number, jlc_number = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage_nominal * Volt(tol=TOLERANCE))
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.pwr_in,  # EN
        # pin 4 is BYP, optional
        '5': self.pwr_out,
      },
      mfr='Diodes Incorporated', part=part_number,
      datasheet='https://www.diodes.com/assets/Datasheets/AP2210.pdf',
    )
    self.assign(self.lcsc_part, jlc_number)
    self.assign(self.actual_basic_part, False)


class Ap2210(LinearRegulator):
  """AP2210 RF ULDO in SOT-23-5 with high PSRR and high(er) voltage tolerant.
  """
  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ap2210_Device(output_voltage=self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=2.2*uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)


class Lp5907_Device(LinearRegulatorDevice, GeneratorBlock, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2.2, 5.5) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 250) * mAmp)
    self.assign(self.actual_quiescent_current, (0.2, 425) * uAmp)
    self.assign(self.actual_dropout, (50, 250) * mVolt)

    self.generator(self.select_part, output_voltage)

  def select_part(self, output_voltage: Range):
    parts = [  # output voltage, Table in 6.5 tolerance varies by output voltage
      (Range.from_tolerance(1.2, 0.03), 'LP5907MFX-1.2/NOPB '),
      (Range.from_tolerance(1.5, 0.03), 'LP5907MFX-1.5/NOPB'),
      (Range.from_tolerance(1.8, 0.02), 'LP5907MFX-1.8/NOPB'),
      (Range.from_tolerance(2.5, 0.02), 'LP5907MFX-2.5/NOPB'),
      # (Range.from_tolerance(2.8, 0.02), 'LP5907MFX-2.8/NOPB '),
      # (Range.from_tolerance(2.85, 0.02), 'LP5907MFX-2.85/NOPB '),
      # (Range.from_tolerance(2.9, 0.02), 'LP5907MFX-2.9/NOPB'),
      (Range.from_tolerance(3.0, 0.02), 'LP5907MFX-3.0/NOPB'),
      # (Range.from_tolerance(3.1, 0.02), 'LP5907MFX-3.1/NOPB'),
      # (Range.from_tolerance(3.2, 0.02), 'LP5907MFX-3.2/NOPB'),
      (Range.from_tolerance(3.3, 0.02), 'LP5907MFX-3.3/NOPB'),
      (Range.from_tolerance(4.5, 0.02), 'LP5907MFX-4.5/NOPB'),
    ]
    # TODO should prefer parts by closeness to nominal (center) specified voltage
    suitable_parts = [(part_out, part_number) for part_out, part_number in parts
                      if part_out in output_voltage]
    assert suitable_parts, f"no regulator with compatible output {output_voltage}"
    part_output_voltage, part_number = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.pwr_in,  # EN
        # pin 4 is NC
        '5': self.pwr_out,
      },
      mfr='Texas Instruments', part=part_number,
      datasheet='https://www.ti.com/lit/ds/symlink/lp5907.pdf',
    )


class Lp5907(LinearRegulator):
  """High-PSRR LDO in SOT-23-5.
  Other pin-compatible high-PSRR LDOs:
  - LP5907
  - AP139
  - TCR2EF
  """
  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Lp5907_Device(output_voltage=self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)
