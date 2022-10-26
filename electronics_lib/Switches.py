from electronics_abstract_parts import *


class SmtSwitch(Switch, FootprintBlock):
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Button_Switch_SMD:SW_Push_SPST_NO_Alps_SKRK',  # 3.9mm x 2.9mm
      # 'Button_Switch_SMD:SW_SPST_CK_KXT3',  # 3.0mm x 2.0mm
      {
        '1': self.b,
        '2': self.a,
      },
      part='3.9x2.9mm Switch'
    )
    # the P/N isn't standardized, but these have been used in the past:
    # PTS820 J25K SMTR LFS, 2.5mm actuator height (from board)


class SmtSwitchRa(Switch, FootprintBlock):
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Button_Switch_SMD:SW_SPST_EVQP7C',  # 3.5mm x 2.9/3.55mm w/ boss
      {
        '1': self.b,
        '2': self.a,
      },
      part='EVQ-P7C01P'
    )


class KailhSocket(Switch, FootprintBlock):
  """Kailh mechanical keyboard hotswap socket.
  Requires an external library, Keyswitch Kicad Library, can be installed from the
  KiCad Plugin and Content Manager, or from GitHub https://github.com/perigoso/keyswitch-kicad-library
  """
  def contents(self) -> None:
    super().contents()

    self.footprint(
      'SW', 'Switch_Keyboard_Hotswap_Kailh:SW_Hotswap_Kailh_MX',
      {
        '1': self.b,
        '2': self.a,
      },
      mfr='Kailh', part='PG151101S11',
      datasheet='https://github.com/keyboardio/keyswitch_documentation/raw/master/datasheets/Kailh/PG151101S11-MX-Socket.pdf',
    )
