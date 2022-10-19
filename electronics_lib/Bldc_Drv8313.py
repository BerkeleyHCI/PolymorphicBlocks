from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Drv8313_Device(DiscreteChip, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vm = self.Port(VoltageSink(  # one 0.1uF capacitor per supply pin and a bulk Vm capacitor
            voltage_limits=(8, 60)*Volt,  # Table 6.3 Vm
            current_draw=(0.5, 5)*mAmp,  # Table 6.5 Vm sleep typ to operating max
        ))
        self.v3p3 = self.Port(VoltageSource(  # internal regulator, bypass with 6.3v, 0.47uF capacitor
            voltage_out=(3.1, 3.52)*Volt,  # Table 6.5 V3P3 voltage
            current_limits=(0, 10)*mAmp,  # Table 6.3 max V3P3 load current
        ))
        self.vcp = self.Port(Passive())  # charge pump, 16V 0.1uF capacitor to Vm
        self.gnd = self.Port(Ground())

        din_model = DigitalSink(  # nSleep, ENx, INx - internally pulled down 100k (Table 6.5)
            voltage_limits=(-0.3, 5.25)*Volt,  # to input high voltage max
            input_thresholds=(0.7, 2.2)
        )
        self.en1 = self.Port(din_model)
        self.en2 = self.Port(din_model)
        self.en3 = self.Port(din_model)
        self.in1 = self.Port(din_model)
        self.in2 = self.Port(din_model)
        self.in3 = self.Port(din_model)

        self.nreset = self.Port(din_model)
        self.nsleep = self.Port(din_model)

        out_model = DigitalSource.from_supply(
            self.gnd, self.vm,
            current_limits=(-2.5, 2.5)*Amp  # peak current, section 1
        )
        self.out1 = self.Port(out_model)
        self.out2 = self.Port(out_model)
        self.out3 = self.Port(out_model)

        pgnd_model = VoltageSink(
            voltage_limits=(-0.5, 0.5)*Volt,  # Table 6.3 PGNDx voltage
            current_draw=RangeExpr(),
        )
        self.pgnd1 = self.Port(pgnd_model)
        self.pgnd2 = self.Port(pgnd_model)
        self.pgnd3 = self.Port(pgnd_model)

        self.cpl = self.Port(Passive())  # connect Vm rated, 0.01uF ceramic capacitor
        self.cph = self.Port(Passive())

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm_ThermalVias',
            {
                '1': self.cpl,
                '2': self.cph,
                '3': self.vcp,
                '4': self.vm,
                '5': self.out1,
                '6': self.pgnd1,
                '7': self.pgnd2,
                '8': self.out2,
                '9': self.out3,
                '10': self.pgnd3,
                '11': self.vm,
                # '12': self.compp,  # uncommitted comparator input
                # '13': self.compn,  # uncommitted comparator input
                '14': self.gnd,
                '15': self.v3p3,
                '16': self.nreset,
                '17': self.nsleep,
                # '18': self.nfault,  # open-drain fault statuc (requires external pullup)
                # '19': self.ncompo,  # uncommitted comparator output
                '20': self.gnd,
                # '21': self.nc,
                '22': self.en3,
                '23': self.in3,
                '24': self.en2,
                '25': self.in2,
                '26': self.en1,
                '27': self.in1,
                '28': self.gnd,

                '29': self.gnd,  # exposed pad
            },
            mfr='Texas Instruments', part='DRV8313PWP',
            datasheet='https://www.ti.com/lit/ds/symlink/drv8313.pdf'
        )
        self.assign(self.lcsc_part, 'C92482')


class Drv8313(GeneratorBlock):
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Drv8313_Device())
        self.pwr = self.Export(self.ic.vm)
        self.gnd = self.Export(self.ic.gnd, [Common])

        self.en1 = self.Export(self.ic.en1, optional=True)
        self.en2 = self.Export(self.ic.en2, optional=True)
        self.en3 = self.Export(self.ic.en3, optional=True)
        self.in1 = self.Export(self.ic.in1, optional=True)
        self.in2 = self.Export(self.ic.in2, optional=True)
        self.in3 = self.Export(self.ic.in3, optional=True)
        self.nreset = self.Export(self.ic.nreset)
        self.nsleep = self.Export(self.ic.nsleep)

        self.out1 = self.Export(self.ic.out1, optional=True)
        self.out2 = self.Export(self.ic.out2, optional=True)
        self.out3 = self.Export(self.ic.out3, optional=True)

        self.require(self.out1.is_connected().implies(self.en1.is_connected() & self.in1.is_connected()))
        self.require(self.out2.is_connected().implies(self.en2.is_connected() & self.in2.is_connected()))
        self.require(self.out3.is_connected().implies(self.en3.is_connected() & self.in3.is_connected()))

        self.pgnd1 = self.Port(VoltageSink.empty(), optional=True)  # connected in the generator if used
        self.pgnd2 = self.Port(VoltageSink.empty(), optional=True)
        self.pgnd3 = self.Port(VoltageSink.empty(), optional=True)

        self.generator(self.generate,
                       self.pgnd1.is_connected(), self.pgnd2.is_connected(), self.pgnd3.is_connected())

    def generate(self, pgnd1_connected: bool, pgnd2_connected: bool, pgnd3_connected: bool):
        self.vm_cap_bulk = self.Block(DecouplingCapacitor((10*0.8, 100)*uFarad)).connected(self.gnd, self.ic.vm)
        self.vm_cap1 = self.Block(DecouplingCapacitor((0.1*0.8, 100)*uFarad)).connected(self.gnd, self.ic.vm)
        self.vm_cap2 = self.Block(DecouplingCapacitor((0.1*0.8, 100)*uFarad)).connected(self.gnd, self.ic.vm)

        # TODO datasheet recommends 6.3v-rated cap, here we just derive it from the voltage rail
        self.v3p3_cap = self.Block(DecouplingCapacitor(0.47*uFarad(tol=0.2))).connected(self.gnd, self.ic.v3p3)

        vm_voltage = self.pwr.link().voltage - self.gnd.link().voltage
        self.cp_cap = self.Block(Capacitor(0.01*uFarad(tol=0.2), vm_voltage))
        self.connect(self.cp_cap.pos, self.ic.cph)
        self.connect(self.cp_cap.neg, self.ic.cpl)

        self.vcp_cap = self.Block(Capacitor(0.1*uFarad(tol=0.2), (0, 16)*Volt))
        self.connect(self.vcp_cap.pos, self.ic.vcp)
        self.connect(self.vcp_cap.neg.adapt_to(VoltageSink()), self.ic.vm)

        if pgnd1_connected:  # PGND optional if external sensing used, otherwise directly ground
            self.connect(self.ic.pgnd1, self.pgnd1)
        else:
            self.connect(self.ic.pgnd1, self.gnd)

        if pgnd2_connected:
            self.connect(self.ic.pgnd2, self.pgnd2)
        else:
            self.connect(self.ic.pgnd2, self.gnd)

        if pgnd3_connected:
            self.connect(self.ic.pgnd3, self.pgnd3)
        else:
            self.connect(self.ic.pgnd3, self.gnd)
