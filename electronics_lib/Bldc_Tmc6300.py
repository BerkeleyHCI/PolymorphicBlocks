import functools

from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Tmc6300_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.w = self.Port(DigitalSource())  # to BLDC W
        self.vcp = self.Port(Passive())  # Charge pump voltage, optionally tie to VS using 1nF to 100nF capacitor


        self.uh = self.Port(DigitalSink.empty())
        self.vh = self.Port(DigitalSink.empty())
        self.wh = self.Port(DigitalSink.empty())
        self.ul = self.Port(DigitalSink.empty())
        self.wl = self.Port(DigitalSink.empty())
        self.vl = self.Port(DigitalSink.empty())
        self.vio = self.Port(VoltageSource(
            voltage_out=(2.0, 5.25)*Volt,  # Table 7.1 Operational Range VVIO
            current_limits=(0, 200)*uAmp,  # Table 7.2 DC and Timing Characteristics IVIO
        ))
        self.diag = self.Port(DigitalSingleSource.empty(), optional=True)
        self.vout1v8 = self.Port(VoltageSource())
        self.u = self.Port(DigitalSource())       # to BLDC U
        self.bruv = self.Port(VoltageSink())    # Connect to GND directly or via a sense resistor
        self.v = self.Port(DigitalSource())       # to BLDC V
        self.vs = self.Port(VoltageSink(
            voltage_limits=(2, 11)*Volt,  # Table 7.1 Operational Range vs
            current_draw=(0, 2.4)*Amp, # Table 7.1 Operational Range vs
        ))
        self.brw = self.Port(VoltageSink())


    def contents(self) -> None:
        self.footprint(
            'U', 'Package_DFN_QFN:QFN-20-1EP_3x3mm_P0.4mm_EP1.7x1.7mm',
            {
                '1': self.w,
                '2': self.vcp,
                '3': self.uh,
                '4': self.vh,
                '5': self.wh,
                '6': self.ul,
                '7': self.wl,
                '8': self.gnd,
                '9': self.gnd,
                '10': self.vl,
                '11': self.vio,
                '12': self.diag,
                '13': self.vout1v8,  # 1.8VOUT, attach 100nF ceramic capacitor to GND near to pin for best performance
                '14': self.gnd,
                '15': self.u,
                '16': self.bruv,
                '17': self.v,
                '18': self.vs,
                #'19': nc,  # Leave this pin open
                '20': self.brw,

                'pad': self.gnd,  # Exposed die pad, connect the exposed die pad to a GND plane # TODO: how should we do this?
            },
            mfr='Analog Device', part='TMC6300',
            datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/TMC6300_datasheet_rev1.08.pdf'
        )


class Tmc6300(BldcDriver, Block):
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Tmc6300_Device())
        self.pwr = self.Export(self.ic.vs)
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.diag = self.Export(self.ic.diag, optional=True)

        self.w = self.Export(self.ic.w)
        self.v = self.Export(self.ic.v)
        self.u = self.Export(self.ic.u)

        self.uh = self.Export(self.ic.uh)
        self.ul = self.Export(self.ic.ul)
        self.vh = self.Export(self.ic.vh)
        self.vl = self.Export(self.ic.vl)
        self.wh = self.Export(self.ic.wh)
        self.wl = self.Export(self.ic.wl)

        self.vcc_io = self.Export(self.ic.vio)

        self.bruv = self.Export(self.ic.bruv, optional=True)
        self.brw = self.Export(self.ic.brw, optional=True)

    def contents(self):
        super().contents()
        # U/V/W-H/L resistors

        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.res_uh = imp.Block(Resistor(resistance=100*kOhm(tol=0.01)))
            self.connect(self.ic.uh, self.res_uh.a.adapt_to(DigitalSink()))
            self.res_ul = imp.Block(Resistor(resistance=100*kOhm(tol=0.01)))
            self.connect(self.ic.ul, self.res_ul.a.adapt_to(DigitalSink()))
            self.res_vh = imp.Block(Resistor(resistance=100*kOhm(tol=0.01)))
            self.connect(self.ic.vh, self.res_vh.a.adapt_to(DigitalSink()))
            self.res_vl = imp.Block(Resistor(resistance=100*kOhm(tol=0.01)))
            self.connect(self.ic.vl, self.res_vl.a.adapt_to(DigitalSink()))
            self.res_wh = imp.Block(Resistor(resistance=100*kOhm(tol=0.01)))
            self.connect(self.ic.wh, self.res_wh.a.adapt_to(DigitalSink()))
            self.res_wl = imp.Block(Resistor(resistance=100*kOhm(tol=0.01)))
            self.connect(self.ic.wl, self.res_wl.a.adapt_to(DigitalSink()))

        # VS decoupling capacitors
        self.vs_cap1 = self.Block(DecouplingCapacitor(10*nFarad(tol=0.1))).connected(self.gnd, self.ic.vs)
        self.vs_cap2 = self.Block(DecouplingCapacitor(10*nFarad(tol=0.1))).connected(self.gnd, self.ic.vs)
        vs_voltage = self.pwr.link().voltage - self.gnd.link().voltage
        self.vcp_cap = self.Block(Capacitor(10*nFarad(tol=0.1), vs_voltage))
        self.connect(self.vcp_cap.pos, self.ic.vcp)
        self.connect(self.vcp_cap.neg.adapt_to(VoltageSink()), self.ic.vs)

        # Vio cap
        self.vio_cap = self.Block(DecouplingCapacitor(10.0*nFarad(tol=0.1))).connected(self.gnd, self.ic.vio)

        # vout1v8 cap
        self.vout1v8_cap = self.Block(DecouplingCapacitor(10.0*nFarad(tol=0.1))).connected(self.gnd, self.ic.vout1v8)


        # TODO: set default?
        # # Default Connection for bruv
        # if not self.bruv.is_connected():
        #     self.connect(self.ic.bruv, self.gnd)
        # # Default Connection for brw
        # if not self.brw.is_optional:
        #     self.connect(self.ic.brw, self.gnd)
        #

class Tmc6300WithOpa(Tmc6300):
    R_SENSE = [
        # (R_sense Ohm, Max current Draw)
        (1.50, 0.2),
        (1.00, 0.3),
        (0.75, 0.4),
        (0.50, 0.6),
        (0.330, 0.8),
        (0.270, 1.0),
        (0.220, 1.2),
        (0.150, 1.6),
        (0.120, 1.8),  # in the table says 2.0 A (duplicated)
        (0.100, 2.0)   # Note: Limited by driver max. ratings
    ]
    @init_in_parent
    def __init__(self):
        # Instantiate the INA139 device
        super().__init__()
        self.opa = self.Block(OpampFollower())
        self.opa_pwr = self.Export(self.opa.pwr)
        self.out = self.Export(self.opa.output)






    def contents(self):
        super().contents()
        self.connect(self.opa.gnd, self.ic.gnd)

        pwr_I_max = self.pwr.link().current_drawn.upper()
        r_sesne = self._find_r_sense(pwr_I_max)
        self.Rs = self.Block(Resistor(resistance=r_sesne))

        self.connect(self.bruv, self.Rs.a.adapt_to(VoltageSink()))
        #self.connect(self.brw, self.Rs.a.adapt_to(VoltageSink()))
        self.connect(self.Rs.b.adapt_to(VoltageSink()), self.gnd)

        self.connect(self.opa.input, self.bruv.as_analog_source())

    def _find_r_sense(self, I_max):
        # Find the appropriate R_SENSE using zero order hold
        return .1*Ohm(tol=0.1)
        for r_sense, current in self.R_SENSE:
            if I_max <= current:
                return r_sense * Ohm
        return  self.R_SENSE[-1][0] * Ohm # if more than 2Amp. It is invalid tho