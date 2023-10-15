from typing import Dict

from electronics_abstract_parts import *
from electronics_lib.JlcPart import JlcPart


class Ld1117_Device(InternalSubcircuit, LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (0, 15) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 0.8) * Amp)  # most conservative estimate, up to 1300mA
    self.assign(self.actual_quiescent_current, (5, 10) * mAmp)
    self.assign(self.actual_dropout, (0, 1.2) * Volt)

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()
    parts = [  # output voltage
      (Range(1.140, 1.260), 'LD1117S12TR', 'C155612'),
      (Range(1.76, 1.84), 'LD1117S18TR', 'C80598'),
      (Range(2.45, 2.55), 'LD1117S25TR', 'C26457'),
      (Range(3.235, 3.365), 'LD1117S33TR', 'C86781'),
      (Range(4.9, 5.1), 'LD1117S50TR', 'C134077'),
    ]
    suitable_parts = [(part_out, part_number, lcsc_part) for part_out, part_number, lcsc_part in parts
                      if part_out.fuzzy_in(self.get(self.output_voltage))]
    assert suitable_parts, "no regulator with compatible output"
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


class Ldl1117_Device(InternalSubcircuit, LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2.6, 18) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 1.5) * Amp)  # most conservative estimate, typ up to 2A
    self.assign(self.actual_quiescent_current, (0, 500) * uAmp)  # typ is 250uA
    self.assign(self.actual_dropout, (0, 0.6) * Volt)  # worst-case, typ is 0.35

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()
    TOLERANCE = 0.03  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [  # output voltage
      (1.185, 'LDL1117S12R', 'C2926949'),
      # (1.5, 'LDL1117S15R'),  # not listed at JLC
      (1.8, 'LDL1117S18R', 'C2926947'),
      (2.5, 'LDL1117S25R', 'C2926456'),
      (3.0, 'LDL1117S30R', 'C2798214'),
      (3.3, 'LDL1117S33R', 'C435835'),
      (5.0, 'LDL1117S50R', 'C970558'),
    ]
    suitable_parts = [part for part in parts
                      if Range.from_tolerance(part[0], TOLERANCE) in self.get(self.output_voltage)]
    assert suitable_parts, "no regulator with compatible output"
    part_output_voltage_nominal, part_number, jlc_number = suitable_parts[0]

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
    self.assign(self.lcsc_part, jlc_number)
    self.assign(self.actual_basic_part, False)


class Ldl1117(LinearRegulator):
  def contents(self) -> None:
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ldl1117_Device(self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=4.7 * uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)


class Ap2204k_Device(InternalSubcircuit, LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
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

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()

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
                      if Range.from_tolerance(part[0], TOLERANCE) in self.get(self.output_voltage)]
    assert suitable_parts, "no regulator with compatible output"
    part_output_voltage_nominal, part_number, jlc_number = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage_nominal * Volt(tol=TOLERANCE))
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.en,
        # pin 4 is ADJ/NC
        '5': self.pwr_out,
      },
      mfr='Diodes Incorporated', part=part_number,
      datasheet='https://www.diodes.com/assets/Datasheets/AP2204.pdf'
    )
    self.assign(self.lcsc_part, jlc_number)
    self.assign(self.actual_basic_part, False)


class Ap2204k(VoltageRegulatorEnableWrapper, LinearRegulator):
  """AP2204K block providing the LinearRegulator interface and optional enable (tied high if not connected).
  """
  def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
    return self.ic.en

  def contents(self):
    super().contents()
    self.ic = self.Block(Ap2204k_Device(self.output_voltage))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.pwr_out, self.ic.pwr_out)
    self.connect(self.gnd, self.ic.gnd)
    self.in_cap = self.Block(DecouplingCapacitor(capacitance=1.1 * uFarad(tol=0.2)))\
      .connected(self.gnd, self.pwr_in)
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=2.2 * uFarad(tol=0.2)))\
      .connected(self.gnd, self.pwr_out)


class Ap7215_Device(InternalSubcircuit, LinearRegulatorDevice, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    # Part datasheet, Recommended Operating Conditions
    self.assign(self.pwr_in.voltage_limits, (3.3, 5.5) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 0.6) * Amp)
    self.assign(self.actual_quiescent_current, (50, 80) * uAmp)
    self.assign(self.actual_dropout, (0, 0.25) * Volt)  # worst-case @ 100mA Iout
    self.assign(self.actual_target_voltage, (3.234, 3.366) * Volt)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-89-3',
      {
        '1': self.gnd,
        '2': self.pwr_in,
        '3': self.pwr_out,
      },
      mfr='Diodes Incorporated', part='AP7215-33YG-13',
      datasheet='https://www.diodes.com/assets/Datasheets/AP7215.pdf'
    )
    self.assign(self.lcsc_part, 'C460367')
    self.assign(self.actual_basic_part, False)


class Ap7215(LinearRegulator):
  """AP7215 fixed 3.3v LDO in SOT-89 providing the LinearRegulator interface.
  """
  def contents(self):
    super().contents()
    self.ic = self.Block(Ap7215_Device(self.output_voltage))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.pwr_out, self.ic.pwr_out)
    self.connect(self.gnd, self.ic.gnd)
    self.in_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))) \
      .connected(self.gnd, self.pwr_in)
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))) \
      .connected(self.gnd, self.pwr_out)


class Xc6206p_Device(InternalSubcircuit, LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (1.8, 6.0) * Volt)
    self.assign(self.actual_quiescent_current, (1, 3) * uAmp)  # supply current

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()
    parts = [  # output range, part number, (dropout typ @10mA, max @100mA), max current, lcsc, basic part
      # +/-0.03v tolerance for Vout < 1.5v
      (Range.from_abs_tolerance(1.2, 0.03), 'XC6206P122MR-G', (0.46, 0.96), 0.06, 'C424699', False),
      (Range.from_abs_tolerance(1.2, 0.03), 'XC6206P132MR', (0.46, 0.96), 0.06, 'C424700', False),
      (Range.from_tolerance(1.5, 0.02), 'XC6206P152MR', (0.30, 0.86), 0.06, 'C424701', False),
      (Range.from_tolerance(1.8, 0.02), 'XC6206P182MR-G', (0.15, 0.78), 0.08, 'C2831490', False),
      (Range.from_tolerance(1.8, 0.02), 'XC6206P182MR', (0.15, 0.78), 0.08, 'C21659', False),  # non -G version, higher stock

      (Range.from_tolerance(2.0, 0.02), 'XC6206P202MR-G', (0.10, 0.78), 0.12, 'C2891260', False),
      (Range.from_tolerance(2.5, 0.02), 'XC6206P252MR', (0.10, 0.71), 0.15, 'C15906', False),
      (Range.from_tolerance(2.8, 0.02), 'XC6206P282MR', (0.10, 0.71), 0.15, 'C14255', False),

      (Range.from_tolerance(3.0, 0.02), 'XC6206P302MR-G', (0.075, 0.68), 0.20, 'C9972', False),
      (Range.from_tolerance(3.3, 0.02), 'XC6206P332MR', (0.075, 0.68), 0.20, 'C5446', True),  # basic part preferred
      (Range.from_tolerance(3.3, 0.02), 'XC6206P332MR-G', (0.075, 0.68), 0.20, 'C2891264', False),
      (Range.from_tolerance(3.6, 0.02), 'XC6206P362MR-G', (0.075, 0.68), 0.20, 'C34705', False),

      (Range.from_tolerance(4.0, 0.02), 'XC6206P402MR', (0.06, 0.63), 0.25, 'C484266', False),

      (Range.from_tolerance(5.0, 0.02), 'XC6206P502MR', (0.05, 0.60), 0.25, 'C16767', False),
    ]
    suitable_parts = [part for part in parts
                      if part[0] in self.get(self.output_voltage)]
    assert suitable_parts, "no regulator with compatible output"
    part_output_voltage, part_number, part_dropout, part_max_current, lcsc_part, basic_part = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage * Volt)
    self.assign(self.actual_dropout, part_dropout * Volt)
    self.assign(self.pwr_out.current_limits, (0, part_max_current) * Amp)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.gnd,
        '2': self.pwr_out,
        '3': self.pwr_in,
      },
      mfr='Torex Semiconductor Ltd', part=part_number,
      datasheet='https://product.torexsemi.com/system/files/series/xc6206.pdf',
    )
    self.assign(self.lcsc_part, lcsc_part)
    self.assign(self.actual_basic_part, basic_part)


class Xc6206p(LinearRegulator):
  """XC6206P LDOs in SOT-23 which seem popular in some open-source designs and some are JLC basic parts."""
  def contents(self) -> None:
    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Xc6206p_Device(output_voltage=self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)


class Xc6209_Device(InternalSubcircuit, LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  # Also pin-compatible with MCP1802 and NJM2882F (which has a noise bypass pin)
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2, 10) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 300) * mAmp)
    self.assign(self.actual_quiescent_current, (0.01, 50) * uAmp)  # typ is 250uA

    self.ce = self.Port(DigitalSink.from_supply(
      self.gnd, self.pwr_in,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      current_draw=(0.1, 5.0)*uAmp,
      input_threshold_abs=(0.25, 1.6)*Volt
    ))

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()
    TOLERANCE = 0.02  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [  # output voltage, part number, (dropout typ @ 30mA, dropout max @ 100mA), max current, lcsc
      (1.5, 'XC6209F152MR-G', (0.50, 0.60), 'C216623'),
      (3.3, 'XC6209F332MR-G', (0.06, 0.25), 'C216624'),
      (5.0, 'XC6209F502MR-G', (0.05, 0.21), 'C222571'),
    ]
    suitable_parts = [part for part in parts
                      if Range.from_tolerance(part[0], TOLERANCE) in self.get(self.output_voltage)]
    assert suitable_parts, "no regulator with compatible output"
    part_output_voltage_nominal, part_number, part_dropout, lcsc_part = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage_nominal * Volt(tol=TOLERANCE))
    self.assign(self.actual_dropout, part_dropout * Volt)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.ce,
        # pin 4 is NC
        '5': self.pwr_out,
      },
      mfr='Torex Semiconductor Ltd', part=part_number,
      datasheet='https://www.torexsemi.com/file/en/products/discontinued/-2016/53-XC6209_12.pdf',
    )
    self.assign(self.lcsc_part, lcsc_part)
    self.assign(self.actual_basic_part, False)


class Xc6209(VoltageRegulatorEnableWrapper, LinearRegulator):
  """XC6209F (F: 300mA version, no pull-down resistor; 2: +/-2% accuracy)
  Low-ESR ceramic cap compatible"""
  def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
    return self.ic.ce

  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Xc6209_Device(output_voltage=self.output_voltage))
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))
      self.out_cap = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out, self.out_cap.pwr)


class Ap2210_Device(InternalSubcircuit, LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2.5, 13.2) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 300) * mAmp)
    self.assign(self.actual_quiescent_current, (0.01, 15000) * uAmp)  # GND pin current
    self.assign(self.actual_dropout, (15, 500) * mVolt)

    self.en = self.Port(DigitalSink(
      voltage_limits=(0, 15) * Volt,
      current_draw=(0.01, 25)*uAmp,
      input_thresholds=(0.4, 2.0)*Volt
    ))

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()
    TOLERANCE = 0.02  # worst-case -40 < Tj < 125C, slightly better at 25C
    parts = [  # output voltage
      (2.5, 'AP2210K-2.5', 'C460340'),
      (3.0, 'AP2210K-3.0', None),  # JLC part not available
      (3.3, 'AP2210K-3.3', 'C176959'),
      (5.0, 'AP2210K-5.0', 'C500758'),
    ]
    suitable_parts = [part for part in parts
                      if Range.from_tolerance(part[0], TOLERANCE) in self.get(self.output_voltage)]
    assert suitable_parts, "no regulator with compatible output"
    part_output_voltage_nominal, part_number, jlc_number = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage_nominal * Volt(tol=TOLERANCE))
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.en,
        # pin 4 is BYP, optional
        '5': self.pwr_out,
      },
      mfr='Diodes Incorporated', part=part_number,
      datasheet='https://www.diodes.com/assets/Datasheets/AP2210.pdf',
    )
    if jlc_number is not None:
      self.assign(self.lcsc_part, jlc_number)
    self.assign(self.actual_basic_part, False)


class Ap2210(VoltageRegulatorEnableWrapper, LinearRegulator):
  """AP2210 RF ULDO in SOT-23-5 with high PSRR and high(er) voltage tolerant.
  """
  def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
    return self.ic.en

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


class Lp5907_Device(InternalSubcircuit, LinearRegulatorDevice, PartsTableFootprint, PartsTablePart, GeneratorBlock,
                    JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (2.2, 5.5) * Volt)
    self.assign(self.pwr_out.current_limits, (0, 250) * mAmp)
    self.assign(self.actual_quiescent_current, (0.2, 425) * uAmp)
    self.assign(self.actual_dropout, (50, 250) * mVolt)

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage, self.part, self.footprint_spec)

    self.en = self.Port(DigitalSink(
      voltage_limits=(0, 5.5) * Volt,
      current_draw=(0.001, 5.5)*uAmp,
      input_thresholds=(0.4, 1.2)*Volt
    ))

  def generate(self):
    super().generate()
    parts = [  # output voltage, Table in 6.5 tolerance varies by output voltage
      (Range.from_tolerance(1.2, 0.03), 'LP5907MFX-1.2/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C73478'),
      (Range.from_tolerance(1.5, 0.03), 'LP5907MFX-1.5/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C133570'),
      (Range.from_tolerance(1.8, 0.02), 'LP5907MFX-1.8/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C92498'),
      (Range.from_tolerance(2.5, 0.02), 'LP5907MFX-2.5/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C165132'),
      # (Range.from_tolerance(2.8, 0.02), 'LP5907MFX-2.8/NOPB' 'Package_TO_SOT_SMD:SOT-23-5',, 'C186700'),
      # (Range.from_tolerance(2.85, 0.02), 'LP5907MFX-2.85/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C2877840'),  # zero stock JLC
      # (Range.from_tolerance(2.9, 0.02), 'LP5907MFX-2.9/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', None),
      (Range.from_tolerance(3.0, 0.02), 'LP5907MFX-3.0/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C475492'),
      # (Range.from_tolerance(3.1, 0.02), 'LP5907MFX-3.1/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', None),
      # (Range.from_tolerance(3.2, 0.02), 'LP5907MFX-3.2/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', None),
      (Range.from_tolerance(3.3, 0.02), 'LP5907MFX-3.3/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C80670'),
      (Range.from_tolerance(4.5, 0.02), 'LP5907MFX-4.5/NOPB', 'Package_TO_SOT_SMD:SOT-23-5', 'C529554'),

      (Range.from_tolerance(1.8, 0.02), 'LP5907SNX-1.8/NOPB', 'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm', 'C139378'),
      (Range.from_tolerance(2.5, 0.02), 'LP5907SNX-2.5/NOPB', 'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm', 'C133571'),
      (Range.from_tolerance(2.9, 0.02), 'LP5907SNX-2.9/NOPB', 'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm', 'C2870726'),
      (Range.from_tolerance(3.3, 0.02), 'LP5907SNX-3.3/NOPB', 'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm', 'C133572'),
    ]
    # TODO should prefer parts by closeness to nominal (center) specified voltage
    output_voltage_spec = self.get(self.output_voltage)
    footprint_spec = self.get(self.footprint_spec)
    suitable_parts = [part for part in parts
                      if part[0] in output_voltage_spec
                      and (not footprint_spec or footprint_spec == part[2])]
    assert suitable_parts, "no regulator with compatible output"
    part_output_voltage, part_number, footprint, jlc_number = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage)
    if footprint == 'Package_TO_SOT_SMD:SOT-23-5':
      pinning: Dict[str, CircuitPort] = {
        '1': self.pwr_in,
        '2': self.gnd,
        '3': self.en,
        # pin 4 is NC
        '5': self.pwr_out,
      }
    elif footprint == 'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm':
      pinning = {
        '4': self.pwr_in,
        '2': self.gnd,
        '3': self.en,
        '1': self.pwr_out,
        '5': self.gnd,  # optionally grounded for better thermal performance
      }
    else:
      raise ValueError

    self.footprint(
      'U', footprint,
      pinning,
      mfr='Texas Instruments', part=part_number,
      datasheet='https://www.ti.com/lit/ds/symlink/lp5907.pdf',
    )
    self.assign(self.lcsc_part, jlc_number)
    self.assign(self.actual_basic_part, False)


class Lp5907(VoltageRegulatorEnableWrapper, LinearRegulator):
  """High-PSRR LDO in SOT-23-5.
  Other pin-compatible high-PSRR LDOs:
  - LP5907
  - AP139
  - TCR2EF
  """
  def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
    return self.ic.en

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


class L78l_Device(InternalSubcircuit, LinearRegulatorDevice, JlcPart, GeneratorBlock, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()

    parts = [  # output voltage, input max voltage, quiescent current, dropout
      (Range(3.135, 3.465), (0, 30)*Volt, (5.5, 6)*mAmp, (0, 2)*Volt, 'L78L33AC', 'C43116'),
      (Range(4.75, 5.25), (0, 30)*Volt, (5.5, 6)*mAmp, (0, 2)*Volt, 'L78L05AC', 'C43116'),
      (Range(5.7, 6.3), (0, 30)*Volt, (5.5, 6)*mAmp, (0, 1.7)*Volt, 'L78L06AC', 'C81357'),
      (Range(7.6, 8.4), (0, 30)*Volt, (5.5, 6)*mAmp, (0, 1.7)*Volt, 'L78L08AC', 'C39490'),  # low stock
      (Range(8.55, 9.45), (0, 30)*Volt, (5.5, 6)*mAmp, (0, 1.7)*Volt, 'L78L09AC', 'C377943'),  # out of stock
      (Range(9.5, 10.5), (0, 30)*Volt, (5.5, 6)*mAmp, (0, 1.7)*Volt, 'L78L10AC', 'C222250'),
      (Range(11.5, 12.5), (0, 35)*Volt, (6, 6.5)*mAmp, (0, 1.7)*Volt, 'L78L12AC', 'C69601'),
      (Range(14.4, 15.6), (0, 35)*Volt, (6, 6.5)*mAmp, (0, 1.7)*Volt, 'L78L15AC', 'C115285'),
      (Range(17.1, 18.9), (0, 40)*Volt, (6, 6.5)*mAmp, (0, 1.7)*Volt, 'L78L18AC', 'C2802523'),  # out of stock
      (Range(22.8, 25.2), (0, 40)*Volt, (6, 6.5)*mAmp, (0, 1.7)*Volt, 'L78L24AC', 'C130141'),  # low stock
    ]
    suitable_parts = [part for part in parts
                      if part[0] in self.get(self.output_voltage)]
    assert suitable_parts, "no regulator with compatible output"

    self.assign(self.actual_target_voltage, suitable_parts[0][0])
    self.assign(self.pwr_in.voltage_limits, suitable_parts[0][1])
    self.assign(self.pwr_out.current_limits, (0, 100)*mAmp)
    self.assign(self.actual_quiescent_current, suitable_parts[0][2])
    self.assign(self.actual_dropout, suitable_parts[0][3])

    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-89-3',
      {
        '1': self.pwr_out,
        '2': self.gnd,
        '3': self.pwr_in,
      },
      mfr='STMicroelectronics', part=suitable_parts[0][4],
      datasheet='https://www.st.com/resource/en/datasheet/l78l.pdf'
    )
    self.assign(self.lcsc_part, suitable_parts[0][5])
    self.assign(self.actual_basic_part, False)


class L78l(LinearRegulator):
  """L78Lxx high(er) input voltage linear regulator in SOT-89.
  """
  def contents(self):
    super().contents()
    self.ic = self.Block(L78l_Device(self.output_voltage))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.pwr_out, self.ic.pwr_out)
    self.connect(self.gnd, self.ic.gnd)
    self.in_cap = self.Block(DecouplingCapacitor(capacitance=0.33*uFarad(tol=0.2))) \
      .connected(self.gnd, self.pwr_in)
    self.out_cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2))) \
      .connected(self.gnd, self.pwr_out)
