from electronics_abstract_parts import *
from .Iso1050 import Iso1050dub
from .LinearRegulators import Ap2204k


@abstract_block
class CalSolSubcircuit(SpecificApplicationSubcircuit):
  pass


class CalSolCanBlock(CalSolSubcircuit):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.can_pwr = self.Port(ElectricalSource(), optional=True)
    self.can_gnd = self.Port(GroundSource(), optional=True)

    self.controller = self.Port(CanTransceiverPort(), [Input])
    self.can = self.Port(CanDiffPort(), optional=True)

  def contents(self):
    super().contents()

    self.conn = self.Block(CalSolCanConnector())
    self.connect(self.can, self.conn.differential)

    self.can_fuse = self.Block(CanFuse())
    self.connect(self.conn.pwr, self.can_pwr, self.can_fuse.pwr_in)
    self.connect(self.conn.gnd, self.can_gnd)

    with self.implicit_connect(
        ImplicitConnect(self.can_fuse.pwr_out, [Power]),
        ImplicitConnect(self.can_gnd, [Common]),
    ) as imp:
      self.reg = imp.Block(Ap2204k(5*Volt(tol=0.05)))  # TODO: replace with generic LinearRegulator?

      self.esd = imp.Block(CanEsdDiode())
      self.connect(self.esd.can, self.can)

    with self.implicit_connect(  # Logic-side implicit
      ImplicitConnect(self.pwr, [Power]),
      ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.transceiver = imp.Block(Iso1050dub())
      self.connect(self.transceiver.controller, self.controller)
      self.connect(self.transceiver.can, self.can)
      self.connect(self.transceiver.can_pwr, self.reg.pwr_out)
      self.connect(self.transceiver.can_gnd, self.can_gnd)


class CanFuse(PptcFuse, CircuitBlock):
  def contents(self):
    super().contents()

    # TODO parameter models

    self.footprint(
      'F', 'Resistor_SMD:R_0603_1608Metric',
      {
        '1': self.pwr_in,
        '2': self.pwr_out,
      },
      part='0ZCM0005FF2G'
    )


class CanEsdDiode(TvsDiode, CircuitBlock):
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground(), [Common])
    self.can = self.Port(CanDiffPort(), [InOut])

  def contents(self):
    super().contents()

    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.can.canl,  # TODO technically 1, 2 can be swapped
        '2': self.can.canh,
        '3': self.gnd,
      },
      part='PESD1CAN,215')


class CalSolPowerConnector(Connector, CalSolSubcircuit, CircuitBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSource(
      voltage_out=12 * Volt(tol=0.1),
      current_limits=(0, 3) * Amp  # TODO get actual limits from LVPDB?
    ))
    self.gnd = self.Port(GroundSource())

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_vert_3pin',
      {
        '1': self.gnd,
        '2': self.pwr,
        '3': self.gnd,
      },
      mfr='Molex', part='5600200320'
    )


class CalSolCanConnector(Connector, CalSolSubcircuit, CircuitBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSource(
      voltage_out=(7, 14) * Volt,  # TODO get limits from CAN power brick?
      current_limits=(0, 0.15) * Amp  # TODO get actual limits from ???
    ))
    self.gnd = self.Port(GroundSource())
    self.differential = self.Port(CanDiffPort(), [Output])

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_vert_5pin',
      {
        # 1 is SHLD
        '2': self.pwr,
        '3': self.gnd,
        '4': self.differential.canh,
        '5': self.differential.canl,
      },
      mfr='Molex', part='5600200520'
    )


class CalSolCanConnectorRa(Connector, CalSolSubcircuit, CircuitBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSource(
      voltage_out=(7, 14) * Volt,  # TODO get limits from CAN power brick?
      current_limits=(0, 0.15) * Amp  # TODO get actual limits from ???
    ))
    self.gnd = self.Port(GroundSource())
    self.differential = self.Port(CanDiffPort(), [Output])

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_502352_1x05_P2.00mm_Horizontal',
      {
        # 1 is SHLD
        '2': self.pwr,
        '3': self.gnd,
        '4': self.differential.canh,
        '5': self.differential.canl,
      },
      mfr='Molex', part='5023520500'
    )


class M12CanConnector(Connector, CalSolSubcircuit, CircuitBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSource(
      voltage_out=(7, 14) * Volt,  # TODO get limits from CAN power brick?
      current_limits=(0, 0.15) * Amp  # TODO get actual limits from ???
    ))
    self.gnd = self.Port(GroundSource())
    self.differential = self.Port(CanDiffPort(), [Output])

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:PhoenixContact_M12-5_Pin_SACC-DSIV-MS-5CON-L90',
      {
        # 1 is SHLD
        '2': self.pwr,
        '3': self.gnd,
        '4': self.differential.canh,
        '5': self.differential.canl,
      },
      mfr='Phoenix Contact', part='SACC-DSIV-MS-5CON-L90'
    )
