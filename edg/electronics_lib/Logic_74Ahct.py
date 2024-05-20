from electronics_abstract_parts import *
from .JlcPart import JlcPart


class L74Ahct1g125_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(4.5, 5.5)*Volt,
      current_draw=(1, 40)*uAmp  # typ to max, TODO propagate current draw from loads
    ))
    # TODO optional OE pin
    self.a = self.Port(DigitalSink.from_supply(
      self.gnd, self.vcc,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,
      input_threshold_abs=(0.8, 2.0)*Volt,
    ), [Input])
    self.y = self.Port(DigitalSource.from_supply(
      self.gnd, self.vcc,
      current_limits=(-8, 8)*mAmp,
    ), [Output])

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.gnd,  # OE
        '2': self.a,
        '3': self.gnd,
        '4': self.y,
        '5': self.vcc,
      },
      mfr='Diodes Incorporated', part='74AHCT1G125W5-7',
      datasheet='https://www.diodes.com/assets/Datasheets/74AHCT1G125.pdf'
    )
    self.assign(self.lcsc_part, 'C842287')


class L74Ahct1g125(Interface, Block):
  """Single buffer, useful as a level shifter"""
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(L74Ahct1g125_Device())
    self.pwr = self.Export(self.ic.vcc, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.input = self.Export(self.ic.a, [Input])
    self.output = self.Export(self.ic.y, [Output])

  def contents(self) -> None:
    super().contents()
    self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
