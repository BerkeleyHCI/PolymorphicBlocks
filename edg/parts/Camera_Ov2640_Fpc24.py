from ..abstract_parts import *
from .PassiveConnector_Fpc import Fpc050Bottom


class Ov2640_Fpc24_Device(InternalSubcircuit, Block):
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.Block(Fpc050Bottom(length=24))

        self.dgnd = self.Export(self.conn.pins.request('10').adapt_to(Ground()))
        self.agnd = self.Export(self.conn.pins.request('23').adapt_to(Ground()))
        self.dovdd = self.Export(self.conn.pins.request('14').adapt_to(VoltageSink(
            voltage_limits=(1.71, 3.3)*Volt,  # Table 6, absolute maximum (Table 5) is 4.5v
            current_draw=(6, 15)*mAmp  # active typ to max
        )))
        self.dvdd = self.Export(self.conn.pins.request('15').adapt_to(VoltageSink(
            voltage_limits=(1.24, 1.36)*Volt,  # Table 6
            current_draw=(30, 60)*mAmp  # active typ YUV to max compressed
        )))
        self.avdd = self.Export(self.conn.pins.request('21').adapt_to(VoltageSink(
            voltage_limits=(2.5, 3.0)*Volt,  # Table 6, absolute maximum (Table 5) is 4.5v
            current_draw=(30, 40)*mAmp  # active max
        )))

        dio_model = DigitalBidir.from_supply(self.dgnd, self.dovdd,
                                             voltage_limit_tolerance=(-0.3, 1)*Volt,  # Table 5
                                             input_threshold_abs=(0.54, 1.26)*Volt,
                                             )
        do_model = DigitalSource.from_bidir(dio_model)
        di_model = DigitalSink.from_bidir(dio_model)

        self.y = self.Port(Vector(DigitalSource.empty()))
        self.connect(self.y.append_elt(DigitalSource.empty(), '0'), self.conn.pins.request('1').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '1'), self.conn.pins.request('2').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '4'), self.conn.pins.request('3').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '3'), self.conn.pins.request('4').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '5'), self.conn.pins.request('5').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '2'), self.conn.pins.request('6').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '6'), self.conn.pins.request('7').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '7'), self.conn.pins.request('9').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '8'), self.conn.pins.request('11').adapt_to(do_model))
        self.connect(self.y.append_elt(DigitalSource.empty(), '9'), self.conn.pins.request('13').adapt_to(do_model))

        self.pclk = self.Export(self.conn.pins.request('8').adapt_to(do_model))  # tacked on a 15pF cap
        self.xclk = self.Export(self.conn.pins.request('12').adapt_to(di_model))
        self.href = self.Export(self.conn.pins.request('16').adapt_to(do_model))
        self.pwdn = self.Export(self.conn.pins.request('17').adapt_to(di_model))  # typically pulled down / grounded
        self.vsync = self.Export(self.conn.pins.request('18').adapt_to(do_model))
        self.reset = self.Export(self.conn.pins.request('19').adapt_to(di_model))

        # formally this is SCCB (serial camera control bus), but is I2C compatible
        # https://e2e.ti.com/support/processors-group/processors/f/processors-forum/6092/sccb-vs-i2c
        # 0x60 for write, 0x61 for read, translated to the 7-bit address
        self.sio = self.Port(I2cTarget(DigitalBidir.empty(), [0x30]))
        self.connect(self.sio.scl, self.conn.pins.request('20').adapt_to(dio_model))
        self.connect(self.sio.sda, self.conn.pins.request('22').adapt_to(dio_model))


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

    def contents(self):
        super().contents()
        self.dovdd_cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))\
            .connected(self.device.dgnd, self.device.dovdd)

        self.reset_pull = self.Block(PullupResistor(10*kOhm(tol=0.05))).connected(self.pwr, self.device.reset)
        self.reset_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=self.pwr.link().voltage))
        self.connect(self.reset_cap.neg.adapt_to(Ground()), self.gnd)
        self.connect(self.reset_cap.pos.adapt_to(DigitalSink()), self.device.reset)

        self.connect(self.dvp8.xclk, self.device.xclk)
        self.pclk_cap = self.Block(Capacitor(capacitance=15*pFarad(tol=0.2), voltage=self.device.pclk.link().voltage))
        self.connect(self.pclk_cap.neg.adapt_to(Ground()), self.gnd)
        self.connect(self.dvp8.pclk, self.pclk_cap.pos.adapt_to(DigitalSink()), self.device.pclk)
        self.connect(self.dvp8.href, self.device.href)
        self.connect(self.dvp8.vsync, self.device.vsync)
        self.connect(self.dvp8.y0, self.device.y.request('2'))
        self.connect(self.dvp8.y1, self.device.y.request('3'))
        self.connect(self.dvp8.y2, self.device.y.request('4'))
        self.connect(self.dvp8.y3, self.device.y.request('5'))
        self.connect(self.dvp8.y4, self.device.y.request('6'))
        self.connect(self.dvp8.y5, self.device.y.request('7'))
        self.connect(self.dvp8.y6, self.device.y.request('8'))
        self.connect(self.dvp8.y7, self.device.y.request('9'))

    def generate(self):
        super().generate()
        if self.get(self.pwdn.is_connected()):
            self.connect(self.pwdn, self.device.pwdn)
        else:
            self.connect(self.gnd.as_digital_source(), self.device.pwdn)

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.device.reset)
