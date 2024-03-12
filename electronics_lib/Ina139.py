from edg import *  # Importing all from the 'edg' library for electronics design
from typing import Dict, Type

VOLTAGE_LIMIT = 'voltage_limits'
FOOTPRINT = 'footprint'
INA1x9_PARAM = dict(
    Ina139={VOLTAGE_LIMIT:(2.7, 40)*Volt,
            FOOTPRINT:dict(
                    refdes='U', footprint='Package_TO_SOT_SMD:SOT-23-5',
                    mfr='Texas Instruments', 
                    part='INA139NA/3K',
                    datasheet='https://www.ti.com/product/INA139'
                )
            },
    Ina169={VOLTAGE_LIMIT:(2.7, 60)*Volt,
            FOOTPRINT:dict(
                refdes='U', footprint='Package_TO_SOT_SMD:SOT-23-5',
                mfr='Texas Instruments',
                part='INA169NA/3K',
                datasheet='https://www.ti.com/product/INA169'
            )
            },
)

@non_library
class Ina1x9_Device(FootprintBlock):
    DEV_PARAM: Dict
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.vin_plus = self.Port(AnalogSink(voltage_limits=self.DEV_PARAM[VOLTAGE_LIMIT]))
        self.vin_minus = self.Port(AnalogSink(voltage_limits=self.DEV_PARAM[VOLTAGE_LIMIT]))
        self.vout = self.Port(Passive().empty())
        self.vplus = self.Port(VoltageSink(voltage_limits=self.DEV_PARAM[VOLTAGE_LIMIT]))
        self.gnd = self.Port(Ground())
        
    def contents(self):
        super().contents()
        self.footprint(
        pinning=
        {
            '1': self.vout,
            '2': self.gnd,
            '3': self.vin_plus,
            '4': self.vin_minus,
            '5': self.vplus,
        },
        **self.DEV_PARAM[FOOTPRINT])

@non_library
class Ina1x9Base(Sensor, Block):
    DEVICE: Type[Ina1x9_Device]
    @init_in_parent
    def __init__(self, resistor_shunt: RangeLike, gain: RangeLike) -> None:
        super().__init__()
        # Instantiate the INA139 device
        self.ic = self.Block(self.DEVICE())
        self.Rs = self.Block(CurrentSenseResistor(resistance=resistor_shunt))# 0.001Ohm -> 35A, 0.1Ohm -> 3.5A, 1Ohm -> 0.35A
        self.Rl = self.Block(Resistor(resistance=gain))

        self.pwr_in = self.Export(self.Rs.pwr_in)
        self.pwr_out = self.Export(self.Rs.pwr_out)

        self.pwr_logic = self.Export(self.ic.vplus, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

        self.v_signal = self.pwr_out.link().current_drawn * self.Rs.actual_resistance * 1e3*1e-6 * self.Rl.actual_resistance
        self.vout = self.ic.vout.adapt_to(AnalogSource())

    def contents(self):
        self.connect(self.ic.vin_plus, self.Rs.sense_in)
        self.connect(self.ic.vin_minus, self.Rs.sense_out)

        self.connect(self.Rl.a.adapt_to(AnalogSink()), self.vout)
        self.connect(self.Rl.b.adapt_to(VoltageSink()), self.gnd)


@non_library
class Ina1x9(Ina1x9Base):
    @init_in_parent
    def __init__(self, resistor_shunt: RangeLike, gain: RangeLike):
        super().__init__(resistor_shunt, gain)
        self.out = self.Export(self.vout)

@non_library
class Ina1x9WithBuffer(Ina1x9Base):
    @init_in_parent
    def __init__(self, resistor_shunt: RangeLike, gain: RangeLike) -> None:
        # Instantiate the INA139 device
        super().__init__(resistor_shunt, gain)
        self.opa = self.Block(OpampFollower())
        self.out = self.Export(self.opa.output)
        # self.pwr_buffer = self.Export(self.opa.pwr)

    def contents(self):
        super().contents()
        self.connect(self.opa.pwr, self.ic.vplus)
        self.connect(self.opa.gnd, self.ic.gnd)
        self.connect(self.opa.input, self.vout)
        # self.connect(self.opa.inn, self.opa.output)


class Ina139_Device(Ina1x9_Device):
    DEV_PARAM = INA1x9_PARAM['Ina139']


class Ina169_Device(Ina1x9_Device):
    DEV_PARAM = INA1x9_PARAM['Ina169']


class Ina139(Ina1x9):
    DEVICE = Ina139_Device


class Ina169(Ina1x9):
    DEVICE = Ina169_Device


class Ina139WithBuffer(Ina1x9WithBuffer):
    DEVICE = Ina139_Device


class Ina169WithBuffer(Ina1x9WithBuffer):
    DEVICE = Ina169_Device
