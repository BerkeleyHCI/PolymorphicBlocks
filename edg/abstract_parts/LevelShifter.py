from ..electronics_model import *
from .Categories import *
from .AbstractResistor import PullupResistor
from .AbstractFets import Fet
from .DummyDevices import DummyGround, DummyVoltageSink

class BidirectionaLevelShifter(Interface, GeneratorBlock):
    """Bidirectional level shifter for low frequency (ish) signals, probably good for up to ~1MHz.
    Circuit design from Phillips AN97055, https://cdn-shop.adafruit.com/datasheets/an97055.pdf
    When both sides are floating or driving high, the FET is off and the pullups provide the high signal.
    When the LV side drives low, the FET source goes to ground, putting the FET into conduction and  pulling HV low.
    When the HV side drives low, the body diode pulls the FET source low, then goes into conduction.

    Use infinity resistance to not generate a resistor, for example if it is known there is already a resistor
    on that side.
    """
    @init_in_parent
    def __init__(self, lv_res: RangeLike = 4.7*kOhm(tol=0.05), hv_res: RangeLike = 4.7*kOhm(tol=0.05)) -> None:
        super().__init__()
        self.gnd = self.Port(Ground.empty(), [Common])
        self.lv_pwr = self.Port(VoltageSink.empty())
        self.lv_io = self.Port(DigitalBidir.empty())
        self.hv_pwr = self.Port(VoltageSink.empty())
        self.hv_io = self.Port(DigitalBidir.empty())

        self.lv_res = self.ArgParameter(lv_res)
        self.hv_res = self.ArgParameter(hv_res)
        self.generator_param(self.lv_res, self.hv_res)

    def generate(self) -> None:
        super().generate()

        self.dummy_gnd = self.Block(DummyGround())  # must be connected, TODO pull ground data from IOs
        self.connect(self.dummy_gnd.gnd, self.gnd)

        self.fet = self.Block(Fet.NFet(
            drain_voltage=VoltageLink._supply_voltage_range(self.gnd, self.hv_pwr).hull((0, 0)),
            drain_current=(0, 0)*Amp,  # TODO signal modeling?
            gate_voltage=VoltageLink._supply_voltage_range(self.gnd, self.lv_pwr).hull((0, 0)),
            rds_on=(0, 1)*Ohm  # arbitrary
        ))
        # TODO more detailed modeling
        self.connect(self.lv_io, self.fet.source.adapt_to(DigitalBidir.from_supply(self.gnd, self.lv_pwr)))
        self.connect(self.hv_io, self.fet.drain.adapt_to(DigitalBidir.from_supply(self.gnd, self.hv_pwr)))
        self.connect(self.lv_pwr, self.fet.gate.adapt_to(VoltageSink()))

        if self.get(self.lv_res) != RangeExpr.INF:
            self.lv_pu = self.Block(PullupResistor(self.lv_res)).connected(self.lv_pwr, self.lv_io)
        if self.get(self.hv_res) != RangeExpr.INF:
            self.hv_pu = self.Block(PullupResistor(self.hv_res)).connected(self.hv_pwr, self.hv_io)
        else:
            self.dummy_hv = self.Block(DummyVoltageSink())  # must be connected
            self.connect(self.dummy_hv.pwr, self.hv_pwr)
