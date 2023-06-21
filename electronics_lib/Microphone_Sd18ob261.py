from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Sd18ob261_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self):
        super().__init__()

        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.6, 3.6) * Volt,
            current_draw=(10, 350) * uAmp,  # sleep current to max consumption
        ), [Power])
        self.gnd = self.Port(Ground(), [Common])

        self.clk = self.Port(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_abs=(-0.3, 3.6),
            input_threshold_factor=(0.35, 0.65)
        ))
        self.lr = self.Port(DigitalSink(  # select pin
            voltage_limits=(-0.3, 3.6)*Volt,
            input_thresholds=(0.2, self.vdd.link().voltage.lower() - 0.45)
        ))

        self.data = self.Port(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=(-20, 20)*mAmp  # short circuit current for data pin
        ))

    def contents(self):
        self.footprint(
            'U', 'Sensor_Audio:Knowles_LGA-5_3.5x2.65mm',
            {
                '1': self.data,
                '2': self.lr,  # 0 for data valid on CLK low, 1 for data valid on CLK high
                '3': self.gnd,
                '4': self.clk,
                '5': self.vdd,
            },
            mfr='Goertek', part='SD18OB261-060',
            datasheet='https://datasheet.lcsc.com/lcsc/2208241200_Goertek-SD18OB261-060_C2895290.pdf'
        )
        self.assign(self.lcsc_part, 'C2895290')
        self.assign(self.actual_basic_part, False)


class Sd18ob261(Interface, Block):
    """SD18OB261-060 PDM microphone, probably footprint-compatible with similar Knowles devices.
    Application circuit is not specified in the datasheet, this uses the one from SPH0655LM4H
    (single 1uF decap)."""
    @init_in_parent
    def __init__(self):
        super().__init__()

        self.ic = self.Block(Sd18ob261_Device())
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

        self.clk = self.Export(self.ic.clk)
        self.lr = self.Export(self.ic.lr)
        self.data = self.Export(self.ic.data)

    def contents(self):
        super().contents()

        self.pwr_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
