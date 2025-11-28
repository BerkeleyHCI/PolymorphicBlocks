from ..abstract_parts import *


class XboxElite2Joystick(FootprintBlock, HumanInterface):
    """Joystick assembly (X/Y analog axes + switch) from the XBox Elite 2 controller.
    Proper polarity for compatibility with hall effect sensors."""
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(VoltageSink(
            voltage_limits=(3.0, 3.6)*Volt,  # assumed, for hall effect sensors
            current_draw=(0, 4)*mAmp  # assumed, for hall effect sensors
        ), [Power])
        self.sw = self.Port(DigitalSource.low_from_supply(self.gnd))
        self.ax1 = self.Port(AnalogSource.from_supply(self.gnd, self.pwr))
        self.ax2 = self.Port(AnalogSource.from_supply(self.gnd, self.pwr))

    @override
    def contents(self) -> None:
        super().contents()

        self.footprint(
            'U', 'edg:Joystick_XboxElite2',
            {
                '1': self.sw,
                '2': self.gnd,

                '3': self.gnd,
                '4': self.ax1,
                '5': self.pwr,

                '6': self.pwr,
                '7': self.ax2,
                '8': self.gnd,
            },
        )
