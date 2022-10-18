from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Drv8313_Device(DiscreteChip, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vm = self.Port(VoltageSink(
            voltage_limits=(2.7, 10.8)*Volt, current_draw=RangeExpr())
        )
        self.gnd = self.Port(Ground())
        self.vint = self.Port(VoltageSource(  # internal supply bypass
            voltage_out=(0, 6.3)*Volt,  # inferred from capacitor rating, actual voltage likely lower
            current_limits=0*mAmp(tol=0)  # external draw not allowed
        ))
        self.vcp = self.Port(Passive())

        din_model = DigitalSink(  # all pins pulled down by default
            voltage_limits=(-0.3, 5.75)*Volt,
            input_thresholds=(0.7, 2)
        )

        dout_model = DigitalSource.from_supply(self.gnd, self.vm, current_limits=(-1.5, 1.5)*Amp)

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm_ThermalVias',
            {
                '1': self.nsleep,
                '2': self.aout1,
                '3': self.gnd,  # AISEN
                '4': self.aout2,
                '5': self.bout2,
                '6': self.gnd,  # BISEN
                '7': self.bout1,
                # '8': self.nfault,  # TODO at some point
                '9': self.bin1,
                '10': self.bin2,
                '11': self.vcp,
                '12': self.vm,
                '13': self.gnd,
                '14': self.vint,
                '15': self.ain2,
                '16': self.ain1,
                '17': self.gnd,  # exposed pad
            },
            mfr='Texas Instruments', part='DRV8313PWP',
            datasheet='https://www.ti.com/lit/ds/symlink/drv8313.pdf'
        )
        self.assign(self.lcsc_part, 'C92482')


class Drv8313(Block):
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Drv8313_Device())
        self.pwr = self.Export(self.ic.vm)
        self.gnd = self.Export(self.ic.gnd, [Common])

    def contents(self) -> None:
        super().contents()

        # the upper tolerable range of these caps is extended to allow search flexibility when voltage derating
        self.vm_cap = self.Block(DecouplingCapacitor((10*0.8, 100)*uFarad)).connected(self.gnd, self.ic.vm)
        self.vint_cap = self.Block(DecouplingCapacitor((2.2*0.8, 10)*uFarad)).connected(self.gnd, self.ic.vint)
        self.vcp_cap = self.Block(Capacitor(0.01*uFarad(tol=0.2), (0, 16)*Volt))
        self.connect(self.vcp_cap.pos, self.ic.vcp)
        self.connect(self.vcp_cap.neg.adapt_to(VoltageSink()), self.ic.vm)
