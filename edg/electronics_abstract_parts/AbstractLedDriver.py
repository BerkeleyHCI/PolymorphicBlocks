from electronics_abstract_parts import *


@abstract_block
class LedDriver(PowerConditioner, Interface):
    """Abstract current-regulated high-power LED driver.
    LED ports are passive and should be directly connected to the LED (or LED string)."""
    @init_in_parent
    def __init__(self, max_current: RangeLike):
        super().__init__()

        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])

        self.leda = self.Port(Passive())
        self.ledk = self.Port(Passive())

        self.max_current = self.ArgParameter(max_current)


class LedDriverSwitchingConverter(BlockInterfaceMixin[LedDriver]):
    """LED driver mixin indicating that the LED driver is a switching converter and with a peak-peak ripple limit."""
    @init_in_parent
    def __init__(self, *args, ripple_limit: FloatLike = float('inf'), **kwargs):
        super().__init__(*args, **kwargs)
        self.ripple_limit = self.ArgParameter(ripple_limit)


class LedDriverPwm(BlockInterfaceMixin[LedDriver]):
    """LED driver mixin with PWM input for dimming control."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pwm = self.Port(DigitalSink.empty(), optional=True)
