from electronics_abstract_parts import *

class Imu_Lsm6ds3trc_Device(DiscreteChip, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.71, 3.6) * Volt,
            current_draw=(0.29, 0.9) * mAmp  # typical values for low-power and high-performance modes
        ))
        self.vddio = self.Port(VoltageSink(
            voltage_limits=(1.62, self.vdd.voltage.upper()+0.1) * Volt
        ))
        self.gnd = self.Port(Ground())

        # TODO figure out how to initialize pins
        self.sda = self.Port(DigitalBidir.from_supply(
            self.gnd, self.vddio,
        ))
        self.sa0 = self.Port(DigitalBidir.from_supply(
            self.gnd, self.vddio,
        ))

        self.scl = self.Port(DigitalSink.from_supply(
            self.gnd, self.vddio,
        ))
        self.cs = self.Port(DigitalSink.from_supply(
            self.gnd, self.vddio,
        ))
        self.int1 = self.Port(DigitalSource.from_supply(
            self.gnd, self.vddio,
        ))
        self.int2 = self.Port(DigitalSource.from_supply(
            self.gnd, self.vddio,
        ))

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
                '13': self.scl,
                '14': self.sda,
            },
            mfr='STMicroelectronics', part='LSM6DS3TR-C',
            datasheet='https://datasheet.lcsc.com/lcsc/2102261805_STMicroelectronics-LSM6DS3TR-C_C967633.pdf'
        )

class Imu_Lsm6ds3trc(Block):
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Imu_Lsm6ds3trc_Device())
        self.vdd = self.Export(self.ic.vdd)
        self.vddio = self.Export(self.ic.vddio)
        self.gnd = self.Export(self.ic.gnd, [Common])

    def contents(self):
        super().contents()
        self.connect(self.pwr, self.ic.vdd)
        self.vdd_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.1))).connected(self.gnd, self.ic.vdd)
        self.vddio_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.1))).connected(self.gnd, self.ic.vddio)
        self.scl_res = self.Block(PullupResistor(10*kOhm(tol=0.01))).connected(self.ic.vddio, self.ic.scl)
        self.sda_res = self.Block(PullupResistor(10*kOhm(tol=0.01))).connected(self.ic.vddio, self.ic.sda)
