from electronics_abstract_parts import *


class Imu_Lsm6ds3trc_Device(DiscreteChip, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.71, 3.6)*Volt,
            current_draw=(0.29, 0.9)*mAmp  # typical values for low-power and high-performance modes
        ))
        self.vddio = self.Port(VoltageSink(
            voltage_limits=(1.62*Volt, self.vdd.voltage_limits.upper()+0.1)
        ))
        self.gnd = self.Port(Ground())

        # TODO figure out how to initialize pins
        i2c_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            current_limits=(-3, 0)*mAmp,
            voltage_limit_abs=(0.3*Volt, self.vddio.voltage_limits.upper()+0.3),
            input_threshold_factor=(0.3, 0.3)
        )
        self.i2c = self.Port(I2cSlave(i2c_model))

        self.sa0 = self.Port(DigitalBidir.from_supply(self.gnd, self.vddio, current_limits=(0, 4)*mAmp))
        self.cs = self.Port(DigitalSink.from_supply(self.gnd, self.vddio, current_draw=(0, 4)*mAmp))

        dout_model = DigitalSource.from_supply(self.gnd, self.vddio, current_limits=(0, 4)*mAmp)
        self.int1 = self.Port(dout_model, optional=True)
        self.int2 = self.Port(dout_model, optional=True)

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y',
            {
                '1': self.sa0,
                '2': self.gnd,  # not used in mode 1
                '3': self.gnd,  # not used in mode 1
                '4': self.int1,
                '5': self.vddio,
                '6': self.gnd,
                '7': self.gnd,
                '8': self.vdd,
                '9': self.int2,
                # '10': self.nc,  # leave unconnected
                # '11': self.nc,  # leave unconnected
                '12': self.cs,
                '13': self.i2c.scl,
                '14': self.i2c.sda,
            },
            mfr='STMicroelectronics', part='LSM6DS3TR-C',
            datasheet='https://datasheet.lcsc.com/lcsc/2102261805_STMicroelectronics-LSM6DS3TR-C_C967633.pdf'
        )


class Imu_Lsm6ds3trc(Block):
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Imu_Lsm6ds3trc_Device())
        self.vdd = self.Export(self.ic.vdd, [Power])
        self.vddio = self.Export(self.ic.vddio, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

    def contents(self):
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.1))).connected(self.gnd, self.ic.vdd)
        self.vddio_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.1))).connected(self.gnd, self.ic.vddio)
        self.scl_res = self.Block(PullupResistor(10*kOhm(tol=0.01))).connected(self.ic.vddio, self.ic.i2c.scl)
        self.sda_res = self.Block(PullupResistor(10*kOhm(tol=0.01))).connected(self.ic.vddio, self.ic.i2c.sda)
