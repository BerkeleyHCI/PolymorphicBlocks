from typing import Any

from typing_extensions import override

from ..abstract_parts import *
from .JlcPart import JlcPart


class Mp2722_Device(InternalSubcircuit, JlcPart, FootprintBlock):
    def __init__(self, charging_current: RangeLike):
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.sw = self.Port(
            VoltageSource(current_limits=(0, 5) * Amp)  # up to 5A charge / system current
        )  # internal switch specs not defined, only bulk current limit defined
        self.vin = self.Port(
            VoltageSink(
                voltage_limits=(3.9, 26) * Volt,  # abs max up to 26v, UV threshold up to 3.45
                current_draw=self.sw.link().current_drawn,  # TODO quiescent current
            ),
            [Power],
        )
        self.pmid = self.Port(
            VoltageSource(
                voltage_out=self.vin.link().voltage,  # 5.08-5.22v in boost
                current_limits=0 * Amp(tol=0),  # decoupling only
            )
        )
        self.bst = self.Port(
            VoltageSource(
                voltage_out=self.sw.link().voltage + (0, 5) * Volt, current_limits=0 * Amp(tol=0)  # decoupling only
            )
        )

        self.sys = self.Port(
            VoltageSink(  # regulation target typically 3.7-3.94
                voltage_limits=(-0.3, 6.5) * Volt,
                current_draw=charging_current,  # TODO model (reverse) discharge current
            )
        )
        self.batt = self.Port(
            VoltageSink(  # technically bidir
                voltage_limits=(2.6, 4.6) * Volt,  # 2.6 is max UV threshold
                current_draw=self.sys.link().current_drawn,  # TODO model (reverse) charging current
            )
        )
        self.battsns = self.Port(VoltageSink())  # technically analog input

        self.vcc = self.Port(
            VoltageSource(
                voltage_out=3.65 * Volt(tol=0),  # no tolerance given
                current_limits=(0, 5) * mAmp,  # no limit given, can be used to drive stat LEDs
            )
        )

        # DIO valid for SCL, SDA, INT, RST, STAT
        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vcc, voltage_limit_abs=(-0.3, 5) * Volt, input_threshold_abs=(0.4, 1.3) * Volt
        )
        self.rst = self.Port(dio_model, optional=True)  # 200k internal pullup, float if unused
        self.int = self.Port(DigitalSource.low_from_supply(self.gnd), optional=True)
        self.vrntc = self.Port(VoltageSource(voltage_out=self.vcc.voltage_out, current_limits=(0, 5) * mAmp))
        self.ntc1 = self.Port(AnalogSink())  # required, doesn't seem to be any way to disable
        self.stat = self.Port(DigitalSource.low_from_supply(self.gnd), optional=True)  # requires 10k pullup
        self.pg = self.Port(DigitalSource.low_from_supply(self.gnd), optional=True)  # requires 10k pullup

        # i2C up to 5v tolerant
        self.i2c = self.Port(I2cTarget(dio_model))
        self.cc = self.Port(UsbCcPort(), optional=True)
        self.usb = self.Port(UsbDevicePort(), optional=True)  # BC protocol only

    @override
    def contents(self) -> None:
        super().contents()
        self.require(self.vin.current_draw.within((0, 3.2) * Amp), "Iin max limit")

        self.footprint(
            "U",
            "edg:MPS_QFN-22_2.5x3.5mm_P0.4mm",
            {
                "2": self.vin,
                "3": self.pmid,
                "4": self.sw,
                "6": self.bst,
                "13": self.sys,
                "14": self.batt,
                "5": self.gnd,  # PGND
                "18": self.gnd,  # AGND
                "19": self.vcc,
                "12": self.battsns,
                "8": self.int,
                "16": self.i2c.scl,
                "15": self.i2c.sda,
                "1": self.cc.cc1,
                "22": self.cc.cc2,
                "21": self.usb.dp,
                "20": self.usb.dm,
                "17": self.rst,
                "7": self.vrntc,  # powered to Vcc when in operation
                "10": self.ntc1,
                "9": self.pg,
                "11": self.stat,
            },
            mfr="Monolithic Power Systems Inc.",
            part="MP2722GRH-0000-P",
            datasheet="https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MP2722GRH/document_id/10035/",
        )
        self.assign(self.lcsc_part, "C20099550")
        self.assign(self.actual_basic_part, False)


class Mp2722(DiscreteBuckConverter):
    """Single-cell narrow voltage DC (5v Vbus <-> ~3.7v LiIon) with forward buck
    and reverse boost and integrated USB-PD CC controller and BC1.2 over D+/D-."""

    VSYS_MIN_DEFAULT = 3.588  # regulation target, tracks above this

    def __init__(
        self,
        *args: Any,
        frequency: RangeLike = (900, 1280) * kHertz,
        charging_current: RangeLike = (0, 3) * Amp,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self.ic = self.Block(Mp2722_Device(charging_current))
        self.connect(self.gnd, self.ic.gnd)
        self.connect(self.pwr_in, self.ic.vin)
        self.connect(self.pwr_out, self.ic.sys)  # direct output of the buck converter

        self.batt = self.Export(self.ic.batt)

        self.vrntc = self.Export(self.ic.vrntc)
        self.ntc1 = self.Export(self.ic.ntc1)

        # RST isn't a traditional reset pin, but used for eg exiting shipping mode,
        # so this does not use the Resettable base interface
        self.rst = self.Export(self.ic.rst, optional=True)
        self.int = self.Export(self.ic.int, optional=True)
        self.stat = self.Export(self.ic.stat, optional=True)
        self.pg = self.Export(self.ic.pg, optional=True)

        self.i2c = self.Export(self.ic.i2c, optional=True)
        self.usb = self.Export(self.ic.usb, optional=True)
        self.cc = self.Export(self.ic.cc, optional=True)

        self.frequency = self.ArgParameter(frequency)

    @override
    def contents(self) -> None:
        super().contents()

        # TODO only allow subset of frequencies, based on SW_FREQ table
        self.require(self.frequency.within((630, 1680) * kHertz))
        self.assign(self.actual_frequency, self.frequency)

        self.connect(self.ic.batt, self.ic.battsns)  # TODO allow remote sense

        with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            self.vbst_cap = self.Block(Capacitor(capacitance=22 * nFarad(tol=0.2), voltage=(0, 5) * Volt))
            self.connect(self.vbst_cap.neg.adapt_to(VoltageSink()), self.ic.sw)
            self.connect(self.vbst_cap.pos.adapt_to(VoltageSink()), self.ic.bst)

            # decouple to PMID, BATT to PGND
            self.pmid_cap = imp.Block(DecouplingCapacitor((10 * 0.8, float("inf")) * uFarad)).connected(
                pwr=self.ic.pmid
            )
            self.batt_cap = imp.Block(DecouplingCapacitor((20 * 0.8, float("inf")) * uFarad)).connected(
                pwr=self.ic.batt
            )
            # decouple to AGND
            self.vcc_cap = imp.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(pwr=self.ic.vcc)

            vsys_range = (self.VSYS_MIN_DEFAULT + 0.15, self.batt.link().voltage.upper())

            self.power_path = imp.Block(
                BuckConverterPowerPath(
                    self.pwr_in.link().voltage,
                    vsys_range,
                    self.actual_frequency,
                    self.pwr_out.link().current_drawn + self.ic.sys.link().current_drawn,
                    (0, 3.2) * Amp,
                    input_voltage_ripple=self.input_ripple_limit,
                    output_voltage_ripple=self.output_ripple_limit,
                )
            )
            self.connect(self.power_path.pwr_in, self.pwr_in)
            # ForcedVoltage needed to provide a voltage value so current downstream can be calculated
            # and then the power path can generate
            (self.forced_out,), _ = self.chain(
                self.power_path.pwr_out, self.Block(ForcedVoltage(vsys_range)), self.pwr_out
            )
            self.connect(self.power_path.switch, self.ic.sw)
