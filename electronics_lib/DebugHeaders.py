from electronics_abstract_parts import *


class SwdCortexTargetHeader(SwdCortexTargetWithSwoTdiConnector, FootprintBlock):
  def contents(self):
    super().contents()

    self.footprint(
      'J', 'Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD',  # TODO: pattern needs shroud
      {
        '1': self.pwr,
        '2': self.swd.swdio,
        '3': self.gnd,
        '4': self.swd.swclk,
        '5': self.gnd,
        '6': self.swo,
        # '7': ,  # key pin technically doesn't exist
        '8': self.tdi,  # or NC
        '9': self.gnd,
        '10': self.swd.reset,
      },
      mfr='CNC Tech', part='3220-10-0300-00',
      value='SWD'
    )


class SwdCortexTargetTc2050(SwdCortexTargetWithSwoTdiConnector, FootprintBlock):
  def contents(self):
    super().contents()

    self.footprint(
      'J', 'Connector:Tag-Connect_TC2050-IDC-FP_2x05_P1.27mm_Vertical',
      {
        '1': self.pwr,
        '10': self.swd.swdio,
        '2': self.gnd,
        '9': self.swd.swclk,
        '3': self.gnd,
        '8': self.swo,
        # '4': ,  # key pin technically doesn't exist
        '7': self.tdi,  # or NC
        '5': self.gnd,
        '6': self.swd.reset,
      },
      value='SWD'
    )


# TODO dedup most with legged version
class SwdCortexTargetTc2050Nl(SwdCortexTargetWithSwoTdiConnector, FootprintBlock):
  def contents(self):
    super().contents()

    self.footprint(
      'J', 'Connector:Tag-Connect_TC2050-IDC-NL_2x05_P1.27mm_Vertical',
      {
        '1': self.pwr,
        '10': self.swd.swdio,
        '2': self.gnd,
        '9': self.swd.swclk,
        '3': self.gnd,
        '8': self.swo,
        # '4': ,  # key pin technically doesn't exist
        '7': self.tdi,  # or NC
        '5': self.gnd,
        '6': self.swd.reset,
      },
      value='SWD'
    )


class SwdCortexSourceHeaderHorizontal(ProgrammingConnector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])  # TODO pin at 0v
    self.swd = self.Port(SwdTargetPort(), [Input])
    self.swo = self.Port(DigitalBidir(), optional=True)
    self.tdi = self.Port(DigitalBidir(), optional=True)

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'edg:PinHeader_2x05_P1.27mm_Horizontal_Shrouded',
      {
        '1': self.pwr,
        '2': self.swd.swdio,
        '3': self.gnd,
        '4': self.swd.swclk,
        '5': self.gnd,
        '6': self.swo,
        # '7': ,  # key pin technically doesn't exist
        '8': self.tdi,  # or NC
        '9': self.gnd,
        '10': self.swd.reset,
      },
      mfr='CNC Tech', part='3220-10-0200-00',
      value='SWD'
    )
