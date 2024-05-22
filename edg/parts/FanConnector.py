from ..abstract_parts import *


@abstract_block_default(lambda: CpuFan3Pin)
class CpuFanConnector(Connector, Block):
    """Abstract block for a 3-pin CPU fan connector."""
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(VoltageSink(
            voltage_limits=12*Volt(tol=0.05),
            current_draw=(0, 2.2)*Amp,  # section 2.1.2: 2.2A max for up to 2s during startup
        ), [Power])
        self.sense = self.Port(DigitalSingleSource.low_from_supply(self.gnd))  # tolerant up to 12v


@abstract_block_default(lambda: CpuFan4Pin)
class CpuFanPwmControl(BlockInterfaceMixin[CpuFanConnector]):
    """Mixin that adds an PWM control pin (open-collector input) to a CpuFanConnector."""
    def __init__(self):
        super().__init__()
        self.control = self.Port(DigitalBidir(
            voltage_limits=(0, 5.25)*Volt,
            voltage_out=(0, 5.25)*Volt,
            pullup_capable=True,
            input_thresholds=(0.8, 0.8)*Volt,  # only low threshold defined
        ))  # internally pulled up, source drives with open-drain


class CpuFan3Pin(CpuFanConnector, FootprintBlock):
    """3-pin fan controller"""
    def contents(self):
        super().contents()
        self.footprint(
            'J', 'Connector:FanPinHeader_1x03_P2.54mm_Vertical',
            {
                '1': self.gnd,
                '2': self.pwr,
                '3': self.sense,
            },
            part='3-pin CPU fan connector',
        )


class CpuFan4Pin(CpuFanConnector, CpuFanPwmControl, FootprintBlock):
    """3-pin fan controller"""
    def contents(self):
        super().contents()
        self.footprint(
            'J', 'Connector:FanPinHeader_1x04_P2.54mm_Vertical',
            {
                '1': self.gnd,
                '2': self.pwr,
                '3': self.sense,
                '4': self.control,
            },
            part='4-pin CPU fan connector',
            datasheet='https://www.intel.com/content/dam/support/us/en/documents/intel-nuc/intel-4wire-pwm-fans-specs.pdf'
        )
