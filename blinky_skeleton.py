from edg import *


class Lf21215tmr_Device(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vcc = self.Port(
      VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0, 1.5)*uAmp))
    self.gnd = self.Port(Ground())

    self.vout = self.Port(DigitalSource.from_supply(
      self.gnd, self.vcc,
      output_threshold_offset=(0.2, -0.3)
    ))

    self.voltage = 5.0
    self.description = "The capacitance of the capacitor is {capacitance}F, \n and the voltage is about {voltage}"




def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.vcc,
        '2': self.vout,
        '3': self.gnd,
      },
      mfr='Littelfuse', part='LF21215TMR',
      datasheet='https://www.littelfuse.com/~/media/electronics/datasheets/magnetic_sensors_and_reed_switches/littelfuse_tmr_switch_lf21215tmr_datasheet.pdf.pdf'
    )


class BlinkyExample(BoardTop):
    def contents(self) -> None:
        super().contents()
        self.mag = self.Block(Lf21215tmr_Device())
        self.cap = self.Block(UnpolarizedCapacitor(capacitance=0.1*uFarad(tol=0.2), voltage=5*Volt(tol=0.10)))
        self.res = self.Block(Resistor(resistance=5*Ohm(tol=0.10)))
        self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
        self.ind = self.Block(JlcInductor(inductance=5*Henry(tol=0.10), current=1*Amp(tol=0.05), frequency=100*Hertz(tol=0.01)))
        self.div = self.Block(ResistiveDivider())

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
        instance_refinements=[
            (['buck'], Tps561201),
        ])


if __name__ == "__main__":
    compile_board_inplace(BlinkyExample)
