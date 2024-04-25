import unittest

from edg import *


class ProtectedCharger(JlcBoardTop):
    """A Lipo charger that does not blowup with reverse polarity from the battery
    Key features:
    - A type C Lipo charger
    - Charging capable reverse polarity protection with PMOS
    - A Port for load
    """

    def contents(self) -> None:
        super().contents()

        self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3) * Amp))
        self.vusb = self.connect(self.usb.pwr)

        self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2) * Volt))

        self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
            self.usb.gnd, self.batt.gnd
        )
        self.gnd = self.connect(self.gnd_merge.pwr_out)
        self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.gnd_merge.pwr_out)

        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.tp,), _ = self.chain(self.batt.pwr, self.Block(VoltageTestPoint()), )
            self.pmos = imp.Block(PmosChargerReverseProtection())

            (self.charger,), _ = self.chain(
                self.vusb, imp.Block(Mcp73831(200 * mAmp(tol=0.2))), self.pmos.chg_in
            )
            self.connect(self.pmos.pwr_in, self.batt.pwr)
            self.connect(self.pmos.chg_out, self.batt.chg)

            (self.charge_led,), _ = self.chain(
                self.Block(IndicatorSinkLed(Led.Yellow)), self.charger.stat
            )
            self.connect(self.vusb, self.charge_led.pwr)

            self.pmos_load = imp.Block(PmosReverseProtection(gate_resistor=300 * Ohm(tol=0.05)))

        self.pwr_pins = self.Block(PassiveConnector(length=3))
        self.connect(self.pwr_pins.pins.request('1').adapt_to(Ground()), self.gnd)
        self.connect(self.pmos.pwr_out, self.pmos_load.pwr_in)
        self.connect(self.pmos_load.pwr_out,
                     self.pwr_pins.pins.request('2').adapt_to(VoltageSink(current_draw=(0, 2.0) * Amp)))
        self.connect(self.pwr_pins.pins.request('3').adapt_to(Ground()), self.gnd)

    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
            ],
            instance_values=[
                (['pmos', 'mp2', 'drain_current'], Range(0.0, 4.0)),
            ],
            class_refinements=[
                (PassiveConnector, JstPhKHorizontal),  # default connector series unless otherwise specified
                (TestPoint, CompactKeystone5015),
            ],
            class_values=[
                (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
            ],
        )


class ProtectedChargerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(ProtectedCharger)
