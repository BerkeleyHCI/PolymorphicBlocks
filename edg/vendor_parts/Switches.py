from typing_extensions import override

from ..abstract_parts import *


class SmtSwitch(TactileSwitch, FootprintBlock):
    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(
            "SW",
            "Button_Switch_SMD:SW_Push_SPST_NO_Alps_SKRK",  # 3.9mm x 2.9mm
            # 'Button_Switch_SMD:SW_SPST_CK_KXT3',  # 3.0mm x 2.0mm
            {
                "1": self.sw,
                "2": self.com,
            },
            part="3.9x2.9mm Switch",
        )
        # the P/N isn't standardized, but these have been used in the past:
        # PTS820 J25K SMTR LFS, 2.5mm actuator height (from board)


class SmtSwitchRa(TactileSwitch, FootprintBlock):
    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(
            "SW",
            "Button_Switch_SMD:SW_SPST_EVQP7C",  # 3.5mm x 2.9/3.55mm w/ boss
            {
                "1": self.sw,
                "2": self.com,
            },
            part="EVQ-P7C01P",
        )


class KailhSocket(MechanicalKeyswitch, FootprintBlock):
    """Kailh mechanical keyboard hotswap socket.
    Requires an external library, Keyswitch Kicad Library, available on the KiCad Plugin and Content Manager (PCM).
    This footprint uses the path when installed via the PCM.
    """

    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(
            "SW",
            "PCM_Switch_Keyboard_Hotswap_Kailh:SW_Hotswap_Kailh_MX",
            {
                "1": self.sw,
                "2": self.com,
            },
            mfr="Kailh",
            part="PG151101S11",
            datasheet="https://github.com/keyboardio/keyswitch_documentation/raw/master/datasheets/Kailh/PG151101S11-MX-Socket.pdf",
        )
