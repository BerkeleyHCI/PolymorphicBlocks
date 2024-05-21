from ..electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ref30xx_Device(InternalSubcircuit, LinearRegulatorDevice, GeneratorBlock, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()

    self.assign(self.pwr_in.voltage_limits, (0, 5.5) * Volt)  # table 7.3
    self.assign(self.pwr_out.current_limits, (0, 25) * mAmp)  # table 7.3, load current
    self.assign(self.actual_quiescent_current, (42, 59) * uAmp)  # table 7.5
    self.assign(self.actual_dropout, (1, 50) * mVolt)  # table 7.5

    self.output_voltage = self.ArgParameter(output_voltage)
    self.generator_param(self.output_voltage)

  def generate(self):
    super().generate()
    parts = [  # output voltage, table 7.5
      (Range(1.2475, 1.2525), 'REF3012', 'C34674'),  # REF3012AIDBZR
      (Range(2.044, 2.052), 'REF3020', 'C26804'),  # REF3020AIDBZR
      (Range(2.495, 2.505), 'REF3025', 'C11334'),  # REF3025AIDBZR
      (Range(2.994, 3.006), 'REF3030', 'C38423'),  # REF3030AIDBZR
      (Range(3.294, 3.306), 'REF3033', 'C36658'),  # REF3033AIDBZR
      (Range(4.088, 4.104), 'REF3040', 'C19415'),  # REF3040AIDBZR
    ]
    suitable_parts = [(part_out, part_number, lcsc_part) for part_out, part_number, lcsc_part in parts
                      if part_out.fuzzy_in(self.get(self.output_voltage))]
    assert suitable_parts, "no regulator with compatible output"
    part_output_voltage, part_number, lcsc_part = suitable_parts[0]

    self.assign(self.actual_target_voltage, part_output_voltage)
    self.assign(self.lcsc_part, lcsc_part)
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.pwr_in,
        '2': self.pwr_out,
        '3': self.gnd,
      },
      mfr='Texas Instruments', part=part_number,
      datasheet='https://www.ti.com/lit/ds/symlink/ref3030.pdf',
    )


class Ref30xx(VoltageReference):
  def contents(self) -> None:
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ref30xx_Device(self.output_voltage))
      # Section 9.1: 0.47uF cap recommended; no output cap required
      self.in_cap = imp.Block(DecouplingCapacitor(capacitance=0.47 * uFarad(tol=0.2)))

      self.connect(self.pwr_in, self.ic.pwr_in, self.in_cap.pwr)
      self.connect(self.pwr_out, self.ic.pwr_out)
