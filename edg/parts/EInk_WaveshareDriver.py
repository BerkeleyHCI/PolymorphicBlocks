from typing_extensions import override

from ..abstract_parts import *
from .PassiveConnector_Fpc import Fpc050Bottom
from .EInkBoostPowerPath import EInkBoostPowerPath


class Waveshare_Epd_Device(InternalSubcircuit, Block):
    """24-pin FPC connector compatible across multiple EPDs"""

    def __init__(self) -> None:
        super().__init__()

        self.vss = self.Port(Ground(), [Common])
        self.vdd = self.Port(
            VoltageSink(
                voltage_limits=(2.5, 3.7) * Volt,  # VCI specs, assumed for all logic
                current_draw=(0.001, 2.1) * mAmp,  # sleep max to operating typ
            )
        )
        self.vddio = self.Port(
            VoltageSink(
                voltage_limits=(2.5, 3.7) * Volt,  # VCI specs, assumed for all logic
            )
        )
        self.vdd1v8 = self.Port(
            VoltageSource(
                voltage_out=1.8 * Volt(tol=0),  # specs not given
                current_limits=0 * mAmp(tol=0),  # only for external capacitor
            )
        )

        dio_model = DigitalBidir.from_supply(self.vss, self.vddio, input_threshold_factor=(0.2, 0.8))
        din_model = DigitalSink.from_bidir(dio_model)

        self.gdr = self.Port(DigitalSource.from_supply(self.vss, self.vdd))  # assumed
        self.rese = self.Port(AnalogSink())

        self.vgl = self.Port(
            VoltageSource(
                voltage_out=(-15, -2.5) * Volt,  # inferred from power selection register
                current_limits=0 * mAmp(tol=0),  # only for external capacitor
            )
        )
        self.vgh = self.Port(
            VoltageSource(voltage_out=(2.5, 15) * Volt, current_limits=0 * mAmp(tol=0))  # only for external capacitor
        )
        self.vsh = self.Port(
            VoltageSource(
                voltage_out=(2.4, 15) * Volt,  # inferred from power selection register
                current_limits=0 * mAmp(tol=0),  # only for external capacitor
            )
        )
        self.vsl = self.Port(
            VoltageSource(
                voltage_out=(-15, -2.4) * Volt,  # inferred from power selection register
                current_limits=0 * mAmp(tol=0),  # only for external capacitor
            )
        )

        self.prevgh = self.Port(VoltageSink(voltage_limits=(13, 20) * Volt))
        self.prevgl = self.Port(VoltageSink(voltage_limits=(-20, -13) * Volt))

        self.vcom = self.Port(
            VoltageSource(
                voltage_out=(2.4, 20) * Volt,  # configurable up to VGH
                current_limits=0 * mAmp(tol=0),  # only for external capacitor
            )
        )

        self.bs = self.Port(din_model)
        self.busy = self.Port(din_model, optional=True)
        self.rst = self.Port(din_model)
        self.dc = self.Port(din_model, optional=True)
        self.csb = self.Port(din_model)

        self.spi = self.Port(SpiPeripheral(dio_model))

        self.conn = self.Block(Fpc050Bottom(length=24)).connected(
            {
                "17": self.vss,
                "16": self.vdd,
                "15": self.vddio,
                "18": self.vdd1v8,
                "2": self.gdr,
                "3": self.rese,
                "4": self.vgl,
                "5": self.vgh,
                "20": self.vsh,
                "22": self.vsl,
                "21": self.prevgh,
                "23": self.prevgl,
                "24": self.vcom,
                "8": self.bs,
                "9": self.busy,
                "10": self.rst,
                "11": self.dc,
                "12": self.csb,
                "13": self.spi.sck,  # SCL
                "14": self.spi.mosi,  # SDA
            }
        )


class Waveshare_Epd(EInk, GeneratorBlock):
    """Multi-device-compatible driver circuitry based on the Waveshare E-Paper Driver HAT
    https://www.waveshare.com/wiki/E-Paper_Driver_HAT
    excluding the "clever" reset circuit
    """

    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Waveshare_Epd_Device())
        self.gnd = self.Export(self.device.vss, [Common])
        self.pwr = self.Export(self.device.vdd, [Power])
        self.reset = self.Export(self.device.rst)
        self.spi = self.Export(self.device.spi)
        self.cs = self.Export(self.device.csb)
        self.dc = self.Export(self.device.dc, optional=True)
        self.busy = self.Export(self.device.busy, optional=True)

        self.generator_param(self.dc.is_connected())

    @override
    def contents(self) -> None:
        super().contents()

        self.vdd_cap = self.Block(DecouplingCapacitor(capacitance=1 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.vdd
        )
        self.connect(self.device.vdd, self.device.vddio)

        self.vdd1v8_cap = self.Block(DecouplingCapacitor(capacitance=1 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.vdd1v8
        )

        self.vgl_cap = self.Block(DecouplingCapacitor(capacitance=1 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.vgl
        )
        self.vgh_cap = self.Block(DecouplingCapacitor(capacitance=4.7 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.vgh
        )
        self.vsh_cap = self.Block(DecouplingCapacitor(capacitance=4.7 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.vsh
        )
        self.vsl_cap = self.Block(DecouplingCapacitor(capacitance=4.7 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.vsl
        )
        self.vcom_cap = self.Block(DecouplingCapacitor(capacitance=1 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.vcom
        )

        # current limit based on 200mA saturation current of reference inductor
        self.boost = self.Block(
            EInkBoostPowerPath(
                20 * Volt(tol=0),
                (0, 200) * mAmp,
                68 * uHenry(tol=0.2),
                4.7 * uFarad(tol=0.2),
                4.7 * uFarad(tol=0.2),
                3 * Ohm(tol=0.01),
            )
        )
        self.connect(self.gnd, self.boost.gnd)
        self.connect(self.pwr, self.boost.pwr_in)
        self.connect(self.device.gdr, self.boost.gate)
        self.gate_pdr = self.Block(PulldownResistor(10 * kOhm(tol=0.05))).connected(self.gnd, self.boost.gate)
        self.connect(self.device.rese, self.boost.isense)
        self.connect(self.boost.pos_out, self.device.prevgh)
        self.connect(self.boost.neg_out, self.device.prevgl)

    @override
    def generate(self) -> None:
        super().generate()
        if self.get(self.dc.is_connected()):  # 4-line serial, BS low
            self.connect(self.gnd.as_digital_source(), self.device.bs)
        else:  # 3-line serial, BS high
            self.connect(self.pwr.as_digital_source(), self.device.bs)
