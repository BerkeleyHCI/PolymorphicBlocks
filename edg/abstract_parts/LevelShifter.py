from ..electronics_model import *
from .Categories import *
from .AbstractResistor import PullupResistor
from .AbstractFets import Fet
from .DummyDevices import DummyVoltageSink

class BidirectionaLevelShifter(Interface, GeneratorBlock):
    """Bidirectional level shifter for low(ish) frequency signals.
    Circuit design from Phillips AN97055, https://cdn-shop.adafruit.com/datasheets/an97055.pdf
    When both sides are floating or driving high, the FET is off and the pullups provide the high signal.
    When the LV side drives low, the FET source goes to ground, putting the FET into conduction and pulling HV low.
    When the HV side drives low, the body diode pulls the FET source low, then goes into conduction.

    Use infinity resistance to not generate a resistor, for example if it is known there is already a resistor
    on that side.

    src_hint = 'lv' | 'hv' | '' determines the 'source' side to help the electronics model resolve directionality
    and does not affect circuit generation or functionality.
    If empty, both sides are assumed to be able to drive the shifter and must have voltages and output thresholds
    modeled. TODO: this mode may be brittle
    """
    def __init__(self, lv_res: RangeLike = 4.7*kOhm(tol=0.05), hv_res: RangeLike = 4.7*kOhm(tol=0.05),
                 src_hint: StringLike = '') -> None:
        super().__init__()
        self.lv_pwr = self.Port(VoltageSink.empty())
        self.lv_io = self.Port(DigitalBidir.empty())
        self.hv_pwr = self.Port(VoltageSink.empty())
        self.hv_io = self.Port(DigitalBidir.empty())

        self.lv_res = self.ArgParameter(lv_res)
        self.hv_res = self.ArgParameter(hv_res)
        self.src_hint = self.ArgParameter(src_hint)
        self.generator_param(self.lv_res, self.hv_res, self.src_hint)

    def generate(self) -> None:
        super().generate()

        self.fet = self.Block(Fet.NFet(
            drain_voltage=self.hv_pwr.link().voltage.hull(self.hv_io.link().voltage),
            drain_current=self.lv_io.link().current_drawn.hull(self.hv_io.link().current_drawn),
            gate_voltage=self.lv_pwr.link().voltage - self.lv_io.link().voltage,
            rds_on=(0, 1)*Ohm  # arbitrary
        ))

        if self.get(self.src_hint) == 'lv':  # LV is source, HV model is incomplete
            lv_io_model = DigitalBidir(
                voltage_out=self.lv_pwr.link().voltage,  # this is not driving, effectively only a pullup
                output_thresholds=self.lv_pwr.link().voltage.hull(-float('inf'))
            )
        else:  # HV model is complete, can use its thresholds
            lv_io_model = DigitalBidir(
                voltage_out=self.lv_pwr.link().voltage.hull(self.hv_io.link().voltage.lower()),
                output_thresholds=self.lv_pwr.link().voltage.hull(self.hv_io.link().voltage.lower())
            )

        if self.get(self.src_hint) == 'hv':  # HV is source, LV model is incomplete
            hv_io_model = DigitalBidir(
                voltage_out=self.hv_pwr.link().voltage,  # this is not driving, effectively only a pullup
                output_thresholds=self.hv_pwr.link().voltage.hull(-float('inf'))
            )
        else:  # HV model is complete, can use its thresholds
            hv_io_model = DigitalBidir(
                voltage_out=self.hv_pwr.link().voltage.hull(self.lv_io.link().voltage.lower()),
                output_thresholds=self.hv_pwr.link().voltage.hull(self.lv_io.link().voltage.lower())
            )

        self.connect(self.lv_io, self.fet.source.adapt_to(lv_io_model))
        self.connect(self.hv_io, self.fet.drain.adapt_to(hv_io_model))
        self.connect(self.lv_pwr, self.fet.gate.adapt_to(VoltageSink()))

        if self.get(self.lv_res) != RangeExpr.INF:
            self.lv_pu = self.Block(PullupResistor(self.lv_res)).connected(self.lv_pwr, self.lv_io)
        if self.get(self.hv_res) != RangeExpr.INF:
            self.hv_pu = self.Block(PullupResistor(self.hv_res)).connected(self.hv_pwr, self.hv_io)
        else:
            self.dummy_hv = self.Block(DummyVoltageSink())  # must be connected
            self.connect(self.dummy_hv.pwr, self.hv_pwr)
