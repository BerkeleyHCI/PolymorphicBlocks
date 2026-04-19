from typing_extensions import override

from ..abstract_parts import *
from .PassiveConnector_Fpc import Fpc050Bottom


class Ov2640_Fpc24_Device(InternalSubcircuit, Nonstrict3v3Compatible, Block):
    def __init__(self) -> None:
        super().__init__()

        self.dgnd = self.Port(Ground())
        self.agnd = self.Port(Ground())
        self.dovdd = self.Port(
            VoltageSink(
                voltage_limits=self.nonstrict_3v3_compatible.then_else(
                    (1.71, 4.5) * Volt, (1.71, 3.3) * Volt  # Table 6, absolute maximum (Table 5) is 4.5v
                ),
                current_draw=(6, 15) * mAmp,  # active typ to max
            )
        )
        self.dvdd = self.Port(
            VoltageSink(
                voltage_limits=(1.14, 1.26) * Volt,  # Table 6
                current_draw=(30, 60) * mAmp,  # active typ YUV to max compressed
            )
        )
        self.avdd = self.Port(
            VoltageSink(
                voltage_limits=(2.5, 3.0) * Volt,  # Table 6, absolute maximum (Table 5) is 4.5v
                current_draw=(30, 40) * mAmp,  # active max
            )
        )

        dio_model = DigitalBidir.from_supply(
            self.dgnd,
            self.dovdd,
            voltage_limit_tolerance=(-0.3, 1) * Volt,  # Table 5
            input_threshold_abs=(0.54, 1.26) * Volt,
        )
        do_model = DigitalSource.from_bidir(dio_model)
        di_model = DigitalSink.from_bidir(dio_model)

        self.y = self.Port(Vector(DigitalSource.empty()))
        for i in range(10):
            self.y.append_elt(do_model, str(i))

        self.pclk = self.Port(do_model)  # tacked on a 15pF cap
        self.xclk = self.Port(di_model)
        self.href = self.Port(do_model)
        self.pwdn = self.Port(di_model)  # typically pulled down / grounded
        self.vsync = self.Port(do_model)
        self.reset = self.Port(dio_model)

        # formally this is SCCB (serial camera control bus), but is I2C compatible
        # https://e2e.ti.com/support/processors-group/processors/f/processors-forum/6092/sccb-vs-i2c
        # 0x60 for write, 0x61 for read, translated to the 7-bit address
        self.sio = self.Port(I2cTarget(dio_model, [0x30]))

        self.conn = self.Block(Fpc050Bottom(length=24)).connected(
            {
                "10": self.dgnd,
                "23": self.agnd,
                "14": self.dovdd,
                "15": self.dvdd,
                "21": self.avdd,
                "1": self.y["0"],
                "2": self.y["1"],
                "3": self.y["4"],
                "4": self.y["3"],
                "5": self.y["5"],
                "6": self.y["2"],
                "7": self.y["6"],
                "9": self.y["7"],
                "11": self.y["8"],
                "13": self.y["9"],
                "8": self.pclk,
                "12": self.xclk,
                "16": self.href,
                "17": self.pwdn,
                "18": self.vsync,
                "19": self.reset,
                "20": self.sio.scl,
                "22": self.sio.sda,
            }
        )


@abstract_block_default(lambda: Ov2640_Fpc24)
class Ov2640(Camera, Block):
    """OV2640 digital camera with DVP interface, commonly used with ESP32 devices"""

    def __init__(self) -> None:
        super().__init__()
        self.device = self.Block(Ov2640_Fpc24_Device())
        self.gnd = self.Export(self.device.dgnd, [Common])
        self.connect(self.gnd, self.device.agnd)
        self.pwr = self.Export(self.device.dovdd)  # IO power
        self.pwr_analog = self.Export(self.device.avdd)
        self.pwr_digital = self.Export(self.device.dvdd)

        self.dvp8 = self.Port(Dvp8Camera.empty())
        self.sio = self.Export(self.device.sio)

        self.pwdn = self.Port(DigitalSink.empty(), optional=True)
        self.reset = self.Port(DigitalSink.empty(), optional=True)


class Ov2640_Fpc24(Ov2640, GeneratorBlock):
    """OV2640 camera as a 24-pin FPC bottom contact connector, as seems to be common on ESP32 with camera boards.
    Electrical parameters from https://www.uctronics.com/download/OV2640_DS.pdf
    Pinning and interface circuit from https://github.com/Freenove/Freenove_ESP32_WROVER_Board/blob/f710fd6976e76ab76c29c2ee3042cd7bac22c3d6/Datasheet/ESP32_Schematic.pdf
      and https://www.waveshare.com/w/upload/9/99/OV2640-Camera-Board-Schematic.pdf
    On many boards, Y0 and Y1 (LSBs) are left unconnected to save IOs."""

    def __init__(self) -> None:
        super().__init__()
        self.generator_param(self.pwdn.is_connected(), self.reset.is_connected())

    @override
    def contents(self) -> None:
        super().contents()
        self.dovdd_cap = self.Block(DecouplingCapacitor(capacitance=0.1 * uFarad(tol=0.2))).connected(
            self.device.dgnd, self.device.dovdd
        )

        self.reset_cap = self.Block(DigitalCapacitor(capacitance=0.1 * uFarad(tol=0.2))).connected(
            self.gnd, self.device.reset
        )

        self.connect(self.dvp8.xclk, self.device.xclk)
        self.pclk_cap = self.Block(DigitalCapacitor(capacitance=15 * pFarad(tol=0.2))).connected(
            self.gnd, self.device.pclk
        )
        self.connect(self.dvp8.pclk, self.device.pclk)
        self.connect(self.dvp8.href, self.device.href)
        self.connect(self.dvp8.vsync, self.device.vsync)
        self.connect(self.dvp8.y0, self.device.y.request("2"))
        self.connect(self.dvp8.y1, self.device.y.request("3"))
        self.connect(self.dvp8.y2, self.device.y.request("4"))
        self.connect(self.dvp8.y3, self.device.y.request("5"))
        self.connect(self.dvp8.y4, self.device.y.request("6"))
        self.connect(self.dvp8.y5, self.device.y.request("7"))
        self.connect(self.dvp8.y6, self.device.y.request("8"))
        self.connect(self.dvp8.y7, self.device.y.request("9"))

    @override
    def generate(self) -> None:
        super().generate()
        if self.get(self.pwdn.is_connected()):
            self.connect(self.pwdn, self.device.pwdn)
        else:
            self.connect(self.gnd.as_digital_source(), self.device.pwdn)

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.device.reset)
        else:
            self.reset_pull = self.Block(PullupResistor(10 * kOhm(tol=0.05))).connected(self.pwr, self.device.reset)
