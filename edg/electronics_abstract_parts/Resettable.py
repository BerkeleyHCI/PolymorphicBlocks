from ...electronics_model import *


class Resettable(BlockInterfaceMixin[Block]):
    """Mixin for all devices that specifies a digital reset pin (active-low reset / active-high enable).

    THIS IS AN ADVANCED FEATURE - BE SURE TO UNDERSTAND THE RESET REQUIREMENTS OF DEVICES.
    When disconnected (mixin not used or port not connected), reset circuitry is automatically generated if needed.
    When connected, no additional reset circuitry is generated and the system designer is responsible for providing
    appropriate reset signals.
    Note that some chips have built-in pull-ups on their reset lines, these are not affected, but no external reset
    circuitry will be generated.

    Devices may optionally require the reset pin where a power-on reset pulse is required and tying / pulling the
    pin high is insufficient.

    Microcontrollers may generate internal programming connectors that drive this signal, and system designers must
    connect microcontroller resets with this in mind - for example, only driving them in open-drain mode.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset = self.Port(DigitalSink.empty(), optional=True)
