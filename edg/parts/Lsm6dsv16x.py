from ..abstract_parts import *
from .JlcPart import JlcPart


class Lsm6dsv16x_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.71, 3.6)*Volt,
            current_draw=(2.6*uAmp, 0.65*mAmp)  # Values for low-power and high-performance modes
        ))
        self.vddio = self.Port(VoltageSink(
            voltage_limits=(1.08, 3.6) *Volt # Extended range
        ))
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vddio,
            voltage_limit_abs=(-0.3*Volt, self.vddio.voltage_limits.upper()+0.3),
            # datasheet states abs volt to be [0.3, VDD_IO+0.3], likely a typo
            current_limits=(-4, 4)*mAmp,
            input_threshold_factor=(0.3, 0.7)
        )
        self.i2c = self.Port(I2cTarget(dio_model))

        dout_model = DigitalSource.low_from_supply(self.gnd)
        self.int1 = self.Port(dout_model, optional=True, doc="can be configured as push-pull / open-drain")
        self.int2 = self.Port(dout_model, optional=True, doc="can be configured as push-pull / open-drain")

        self.qvar1 = self.Port(Passive(), optional=True)
        self.qvar2 = self.Port(Passive(), optional=True)

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm',
            {
                '1': self.gnd,  # sa0
                '2': self.qvar1,  # not used in mode 1
                '3': self.qvar2,  # not used in mode 1
                '4': self.int1,
                '5': self.vddio,
                '6': self.gnd,
                '7': self.gnd,
                '8': self.vdd,
                '9': self.int2,
                # '10': self.nc,  # leave unconnected
                # '11': self.nc,  # leave unconnected
                '12': self.vddio,  # cs pin
                '13': self.i2c.scl,
                '14': self.i2c.sda,
            },
            mfr='STMicroelectronics', part='LSM6DSV16X',
            datasheet='https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf'
        )
        self.assign(self.lcsc_part, 'C5267406')
        self.assign(self.actual_basic_part, False)

class Lsm6dsv16x(Accelerometer, Gyroscope, DefaultExportBlock):
    """Integrated High-edn smartphone 3d accelerometer (ranging over +/- 2/4/8/16 g) and 3d gyroscope
    (ranging over +/- 125/250/500/1000/2000 dps). Onboard sensor fusion for quaternion calculation.
    Supports external qvar for tap detections, etc."""
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Lsm6dsv16x_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.pwr_io = self.Export(self.ic.vddio, default=self.pwr, doc="IO supply voltage")

        self.i2c = self.Export(self.ic.i2c)
        self.int1 = self.Export(self.ic.int1, optional=True, doc="Programmable interrupt")
        self.int2 = self.Export(self.ic.int2, optional=True, doc="Programmable interrupt")

        self.qvar1 = self.Export(self.ic.qvar1, optional=True, doc="qvar input pin 1")
        self.qvar2 = self.Export(self.ic.qvar2, optional=True, doc="qvar input pin 2")

    def contents(self):
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
        self.vddio_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vddio)

