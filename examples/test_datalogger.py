import unittest

from typing_extensions import override

from edg import *
from .test_high_switch import CalSolPowerConnector, CalSolCanBlock, CanFuse


class Supercap(DiscreteComponent, FootprintBlock):  # TODO actually model supercaps and parts selection
    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(VoltageSink())
        self.neg = self.Port(Ground())

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "C",
            "Capacitor_THT:CP_Radial_D14.0mm_P5.00mm",  # actually 13.5
            {
                "1": self.pos,
                "2": self.neg,
            },
            part="DBN-5R5D334T",  # TODO this is too high resistance
            datasheet="http://www.elna.co.jp/en/capacitor/double_layer/catalog/pdf/dbn_e.pdf",
        )


class BufferedSupply(PowerConditioner):
    """Implements a current limiting source with an opamp for charging a supercap, and a Vf-limited diode
    for discharging

    See https://electronics.stackexchange.com/questions/178605/op-amp-mosfet-constant-current-power-source
    """

    def __init__(self, charging_current: RangeLike, sense_resistance: RangeLike, voltage_drop: RangeLike) -> None:
        super().__init__()

        self.charging_current = self.ArgParameter(charging_current)
        self.sense_resistance = self.ArgParameter(sense_resistance)
        self.voltage_drop = self.ArgParameter(voltage_drop)

        self.pwr = self.Port(VoltageSink.empty(), [Power, Input])
        self.pwr_out = self.Port(VoltageSource.empty(), [Output])
        self.require(
            self.pwr.current_draw.within(
                self.pwr_out.link().current_drawn + (0, self.charging_current.upper()) + (0, 0.05)
            )
        )  # TODO nonhacky bounds on opamp/sense resistor current draw
        self.sc_out = self.Port(VoltageSource.empty(), optional=True)
        self.gnd = self.Port(Ground.empty(), [Common])

        max_in_voltage = self.pwr.link().voltage.upper()
        max_charge_current = self.charging_current.upper()

        # Upstream power domain
        # TODO improve connect modeling everywhere
        with self.implicit_connect(
            ImplicitConnect(self.pwr, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.sense = self.Block(
                Resistor(  # TODO replace with SeriesResistor/CurrentSenseResistor - that propagates current
                    resistance=self.sense_resistance,
                    power=(0, max_charge_current * max_charge_current * self.sense_resistance.upper()),
                )
            )
            self.connect(self.pwr, self.sense.a.adapt_to(VoltageSink(current_draw=(0, max_charge_current))))

            self.fet = self.Block(
                Fet.PFet(
                    drain_voltage=(0, max_in_voltage),
                    drain_current=(0, max_charge_current),
                    gate_voltage=(self.pwr.link().voltage.lower(), max_in_voltage),
                    rds_on=(0, 0.5) * Ohm,  # TODO kind of arbitrary
                    power=(0, max_in_voltage * max_charge_current),
                )
            )
            self.connect(self.fet.source, self.sense.b)

            self.diode = self.Block(
                Diode(
                    reverse_voltage=(0, max_in_voltage),
                    current=self.charging_current,
                    voltage_drop=self.voltage_drop,
                )
            )
            self.connect(
                self.diode.anode.adapt_to(VoltageSink()),
                self.fet.drain.adapt_to(VoltageSource(voltage_out=self.pwr.link().voltage)),
                self.sc_out,
            )

            self.pwr_out_merge = self.Block(MergedVoltageSource()).connected_from(
                self.pwr,
                self.diode.cathode.adapt_to(
                    VoltageSource(
                        voltage_out=(
                            self.pwr.link().voltage.lower() - self.voltage_drop.upper(),
                            self.pwr.link().voltage.upper(),
                        )
                    )
                ),  # TODO replace with SeriesVoltageDiode or something that automatically calculates voltage drops?
            )
            self.connect(self.pwr_out_merge.pwr_out, self.pwr_out)

            # TODO check if this tolerance stackup is stacking in the right direction... it might not
            low_sense_volt_diff = self.charging_current.lower() * self.sense_resistance.lower()
            high_sense_volt_diff = self.charging_current.upper() * self.sense_resistance.upper()
            low_sense_volt = self.pwr.link().voltage.lower() - high_sense_volt_diff
            high_sense_volt = self.pwr.link().voltage.upper() - low_sense_volt_diff

            self.set = imp.Block(
                VoltageDivider(output_voltage=(low_sense_volt, high_sense_volt), impedance=(1, 10) * kOhm)
            )
            self.connect(self.set.input, self.pwr)  # TODO use chain
            self.amp = imp.Block(Opamp())
            self.connect(self.set.output, self.amp.inp)
            self.connect(
                self.amp.inn,
                self.sense.b.adapt_to(
                    AnalogSource(
                        voltage_out=(0, self.pwr.link().voltage.upper()),
                        # TODO calculate operating signal level
                    )
                ),
            )
            self.connect(self.amp.out, self.fet.gate.adapt_to(AnalogSink()))

        self.cap = self.Block(Supercap())
        self.connect(self.sc_out, self.cap.pos)
        self.connect(self.gnd, self.cap.neg)


class Datalogger(BoardTop):
    @override
    def contents(self) -> None:
        super().contents()

        self.pwr_conn = self.Block(CalSolPowerConnector())
        self.usb_conn = self.Block(UsbCReceptacle())

        self.usb_forced_current = self.Block(ForcedVoltageCurrentDraw(forced_current_draw=(0, 0.5) * Amp))
        self.connect(self.usb_conn.pwr, self.usb_forced_current.pwr_in)

        self.bat = self.Block(Cr2032())
        self.gnd = self.connect(self.usb_conn.gnd, self.pwr_conn.gnd, self.bat.gnd)

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            (self.pwr_5v,), _ = self.chain(
                self.pwr_conn.pwr, imp.Block(BuckConverter(output_voltage=(4.85, 5.4) * Volt))
            )
            self.pwr_5v_merge = self.Block(MergedVoltageSource()).connected_from(
                self.usb_forced_current.pwr_out, self.pwr_5v.pwr_out
            )

            (self.buffer, self.pwr_3v3), _ = self.chain(
                self.pwr_5v_merge.pwr_out,
                imp.Block(
                    BufferedSupply(
                        charging_current=(0.3, 0.4) * Amp,
                        sense_resistance=0.47 * Ohm(tol=0.01),
                        voltage_drop=(0, 0.4) * Volt,
                    )
                ),
                imp.Block(LinearRegulator(output_voltage=3.3 * Volt(tol=0.05))),
            )

        self.vin = self.connect(self.pwr_conn.pwr)
        self.v5 = self.connect(self.pwr_5v_merge.pwr_out)
        self.v5_buffered = self.connect(self.buffer.pwr_out)
        self.v3v3 = self.connect(self.pwr_3v3.pwr_out)  # TODO better auto net names

        with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.mcu = imp.Block(IoController())

            # this uses the legacy / simple (non-mixin) USB and CAN IO style
            self.connect(self.mcu.usb.request(), self.usb_conn.usb)

            (self.can,), _ = self.chain(self.mcu.can.request("can"), imp.Block(CalSolCanBlock()))

            # mcu_i2c = self.mcu.i2c.request()  # no devices, ignored for now
            # self.i2c_pullup = imp.Block(I2cPullup())
            # self.connect(self.i2c_pullup.i2c, mcu_i2c)

            self.sd = imp.Block(SdSocket())
            self.connect(self.mcu.spi.request("sd_spi"), self.sd.spi)
            self.connect(self.mcu.gpio.request("sd_cs"), self.sd.cs)
            (self.cd_pull,), _ = self.chain(
                self.mcu.gpio.request("sd_cd_pull"), imp.Block(PullupResistor(4.7 * kOhm(tol=0.05))), self.sd.cd
            )

            self.xbee = imp.Block(Xbee_S3b())
            self.connect(self.mcu.uart.request("xbee_uart"), self.xbee.data)
            (self.xbee_assoc,), _ = self.chain(
                self.xbee.associate, imp.Block(IndicatorLed(current_draw=(0.5, 2) * mAmp))
            )  # XBee DIO current is -2 -> 2 mA

            aux_spi = self.mcu.spi.request("aux_spi")
            self.rtc = imp.Block(Pcf2129())
            self.connect(aux_spi, self.rtc.spi)
            self.connect(self.mcu.gpio.request("rtc_cs"), self.rtc.cs)
            self.connect(self.bat.pwr, self.rtc.pwr_bat)

            self.eink = imp.Block(Waveshare_Epd())
            self.connect(aux_spi, self.eink.spi)
            self.connect(self.mcu.gpio.request("eink_busy"), self.eink.busy)
            self.connect(self.mcu.gpio.request("eink_reset"), self.eink.reset)
            self.connect(self.mcu.gpio.request("eink_dc"), self.eink.dc)
            self.connect(self.mcu.gpio.request("eink_cs"), self.eink.cs)

            self.ext = imp.Block(BlueSmirf())
            self.connect(self.mcu.uart.request("ext_uart"), self.ext.data)
            self.connect(self.mcu.gpio.request("ext_cts"), self.ext.cts)
            self.connect(self.mcu.gpio.request("ext_rts"), self.ext.rts)

            self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # system RGB 1
            self.connect(self.mcu.gpio.request_vector("rgb1"), self.rgb1.signals)

            self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # sd card RGB
            self.connect(self.mcu.gpio.request_vector("rgb2"), self.rgb2.signals)

            self.rgb3 = imp.Block(IndicatorSinkRgbLed())
            self.connect(self.mcu.gpio.request_vector("rgb3"), self.rgb3.signals)

            sw_pull_model = PullupResistor(4.7 * kOhm(tol=0.05))
            (self.sw1, self.sw1_pull), _ = self.chain(
                imp.Block(DigitalSwitch()), imp.Block(sw_pull_model), self.mcu.gpio.request("sw1")
            )
            (self.sw2, self.sw2_pull), _ = self.chain(
                imp.Block(DigitalSwitch()), imp.Block(sw_pull_model), self.mcu.gpio.request("sw2")
            )

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            # TODO update to use VoltageSenseDivider
            div_model = VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)
            (self.v12sense,), _ = self.chain(self.vin, imp.Block(div_model), self.mcu.adc.request("v12sense"))
            (self.v5sense,), _ = self.chain(self.v5, imp.Block(div_model), self.mcu.adc.request("v5sense"))
            (self.vscsense,), _ = self.chain(self.buffer.sc_out, imp.Block(div_model), self.mcu.adc.request("vscsense"))

    @override
    def refinements(self) -> Refinements:
        return super().refinements() + Refinements(
            instance_refinements=[
                (["mcu"], Lpc1549_64),
                (["pwr_5v"], Tps561201),
                (["pwr_3v3"], Ldl1117),
                (["buffer", "amp"], Tlv9061),
            ],
            instance_values=[
                (
                    ["mcu", "pin_assigns"],
                    [
                        "can.txd=51",
                        "can.rxd=53",
                        "sd_spi.sck=17",
                        "sd_spi.mosi=15",
                        "sd_spi.miso=19",
                        "sd_cs=11",
                        "sd_cd_pull=16",
                        "xbee_uart.tx=58",
                        "xbee_uart.rx=50",  # used to be 54, which is ISP_0
                        "aux_spi.sck=5",
                        "aux_spi.mosi=6",
                        "aux_spi.miso=7",
                        "rtc_cs=64",
                        "eink_busy=1",
                        "eink_reset=2",
                        "eink_dc=3",
                        "eink_cs=4",
                        "eink_busy=1",
                        "ext_uart.tx=60",
                        "ext_uart.rx=61",
                        "ext_cts=62",
                        "ext_rts=59",
                        "rgb1_red=31",
                        "rgb1_green=32",
                        "rgb1_blue=30",
                        "rgb2_red=28",
                        "rgb2_green=29",
                        "rgb2_blue=25",
                        "rgb3_red=46",
                        "rgb3_green=39",
                        "rgb3_blue=34",  # used to be 38, which is ISP_1
                        "sw1=33",
                        "sw2=23",
                        "v12sense=10",
                        "v5sense=9",
                        "vscsense=8",
                    ],
                ),
                (["mcu", "swd_swo_pin"], "PIO0_8"),
                (["pwr_5v", "power_path", "inductor", "part"], "NR5040T220M"),  # peg to prior part selection
                (
                    ["pwr_5v", "power_path", "inductor_current_ripple"],
                    Range(0.01, 0.6),
                ),  # trade higher Imax for lower L
                # the hold current wasn't modeled at the time of manufacture and turns out to be out of limits
                (["can", "can_fuse", "fuse", "actual_hold_current"], Range(0.1, 0.1)),
                # JLC does not have frequency specs, must be checked TODO
                (["pwr_5v", "power_path", "inductor", "manual_frequency_rating"], Range.all()),
                # keep netlist footprints as libraries change
                (["buffer", "fet", "footprint_spec"], "Package_TO_SOT_SMD:SOT-223-3_TabPin2"),
                (["eink", "ic", "boost", "sense", "resistance"], Range.from_tolerance(3.3, 0.05)),  # 3R not standard
            ],
            class_refinements=[(Fuse, CanFuse)],
        )


class DataloggerTestCase(unittest.TestCase):
    def test_design(self) -> None:
        compile_board_inplace(Datalogger)
