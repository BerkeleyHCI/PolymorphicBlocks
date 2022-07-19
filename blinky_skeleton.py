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
    self.description = "The voltage of this block is {voltage}V"



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
        self.mcu = self.Block(Lpc1549_48())
        self.mag = self.Block(Lf21215tmr_Device())


if __name__ == "__main__":
    compile_board_inplace(BlinkyExample)
