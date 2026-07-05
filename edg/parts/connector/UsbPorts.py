from typing_extensions import override

from ...circuits import *
from ...util import deprecated_param_remap
from ...vendor_parts.jlc.JlcPart import JlcPart


class UsbAReceptacle(UsbHostConnector, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.pwr.init_from(VoltageSink(voltage_limits=self.USB2_VOLTAGE_RANGE, current_draw=self.USB2_CURRENT_LIMITS))
        self.gnd.init_from(Ground())

        self.usb.init_from(UsbDevicePort())

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "J",
            "Connector_USB:USB_A_Molex_105057_Vertical",
            {
                "1": self.pwr,
                "4": self.gnd,
                "2": self.usb.dm,
                "3": self.usb.dp,
                "5": self.gnd,  # shield
            },
            mfr="Molex",
            part="105057",
            datasheet="https://www.molex.com/pdm_docs/sd/1050570001_sd.pdf",
        )


class UsbCReceptacle_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    """Raw generic USB Type-C Receptacle
    Pullup capable indicates whether this port (or more accurately, the device on the other side) can pull
    up the signal. In UFP (upstream-facing, device) mode the power source should pull up CC."""

    @deprecated_param_remap(("voltage_out", "voltage"))
    def __init__(
        self,
        voltage: RangeLike = UsbConnector.USB2_VOLTAGE_RANGE,  # allow custom PD voltage and current
        current_limits: RangeLike = UsbConnector.USB2_CURRENT_LIMITS,
    ) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.pwr = self.Port(VoltageSource(voltage=voltage, current_limits=current_limits), optional=True)

        self.usb = self.Port(UsbHostPort(), optional=True)
        self.shield = self.Port(Ground(), optional=True)

        self.cc = self.Port(UsbCcPort(), optional=True)

    @override
    def contents(self) -> None:
        super().contents()

        self.assign(self.lcsc_part, "C165948")  # note, many other pin-compatible parts also available
        self.assign(self.actual_basic_part, False)
        self.footprint(
            "J",
            "Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11",
            {
                ("A1", "B12", "B1", "A12"): self.gnd,
                ("A4", "B9", "B4", "A9"): self.pwr,
                ("A6", "B6"): self.usb.dp,
                ("A7", "B7"): self.usb.dm,
                # 'A8': sbu1,
                # 'B8': sbu2
                "A5": self.cc.cc1,
                "B5": self.cc.cc2,
                "S1": self.shield,
            },
            part="USB-C Receptacle",
            pnp_rot=0,
            pnp_offset=(0, -1.25),
        )


class UsbCReceptacle(UsbDeviceConnector, GeneratorBlock):
    """USB Type-C Receptacle that automatically generates the CC resistors if CC is not connected."""

    @deprecated_param_remap(("voltage_out", "voltage"))
    def __init__(
        self,
        voltage: RangeLike = UsbConnector.USB2_VOLTAGE_RANGE,  # allow custom PD voltage and current
        current_limits: RangeLike = UsbConnector.USB2_CURRENT_LIMITS,
        *,
        generate_esd_diode: BoolLike = True,
    ) -> None:
        super().__init__(generate_esd_diode=generate_esd_diode)

        self.conn = self.Block(UsbCReceptacle_Device(voltage=voltage, current_limits=current_limits))
        self.connect(self.gnd, self.conn.gnd)
        self.connect(self.pwr, self.conn.pwr)
        self.connect(self.usb, self.conn.usb)
        self.cc = self.Port(UsbCcPort.empty(), optional=True)  # external connectivity defines the circuit

        self.generator_param(
            self.pwr.is_connected(), self.usb.is_connected(), self.cc.is_connected(), self.generate_esd_diode
        )

    @override
    def generate(self) -> None:
        super().generate()

        if self.usb.is_connected():
            if self.get(self.generate_esd_diode):
                self.esd = self.Block(UsbEsdDiode())
                self.connect(self.esd.gnd, self.gnd)
                self.connect(self.esd.usb, self.usb)

        if self.get(self.cc.is_connected()):  # if CC externally connected, connect directly to USB port
            self.connect(self.cc, self.conn.cc)
            self.require(
                self.cc.is_connected().implies(self.pwr.is_connected()), "USB power not used when CC connected"
            )
        elif self.get(self.pwr.is_connected()):  # otherwise generate the pulldown resistors for USB2 mode
            (self.cc_pull,), _ = self.chain(self.conn.cc, self.Block(UsbCcPulldownResistor()))
            self.connect(self.cc_pull.gnd, self.gnd)
            self.require(
                self.pwr.voltage == UsbConnector.USB2_VOLTAGE_RANGE,
                "when CC not connected, port restricted to USB 2.0 voltage",
            )
            # note that the DFP (power source) can provide the max current, however the UFP (device)
            # should sense the voltage at CC to determine the amount of current allowed

        # TODO there does not seem to be full agreement on what to do with the shield pin, we arbitrarily ground it
        self.connect(self.gnd, self.conn.shield)


class UsbAPlugPads(UsbDeviceConnector, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()

    @override
    def contents(self) -> None:
        super().contents()
        self.pwr.init_from(VoltageSource(voltage=self.USB2_VOLTAGE_RANGE, current_limits=self.USB2_CURRENT_LIMITS))
        self.gnd.init_from(Ground())
        self.usb.init_from(UsbHostPort())

        self.footprint(
            "J",
            "edg:USB_A_Pads",
            {
                "1": self.pwr,
                "2": self.usb.dm,
                "3": self.usb.dp,
                "4": self.gnd,
            },
            part="USB A pads",
        )


class Molex_105017_0001_Device(InternalSubcircuit, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.pwr = self.Port(
            VoltageSource(voltage=UsbConnector.USB2_VOLTAGE_RANGE, current_limits=UsbConnector.USB2_CURRENT_LIMITS)
        )
        self.usb = self.Port(UsbHostPort())
        self.shield = self.Port(Ground(), optional=True)

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            "J",
            "Connector_USB:USB_Micro-B_Molex-105017-0001",
            {
                "1": self.pwr,
                "5": self.gnd,
                "2": self.usb.dm,
                "3": self.usb.dp,
                # '4': TODO: ID pin
                "6": self.shield,
            },
            mfr="Molex",
            part="105017-0001",
            datasheet="https://www.molex.com/pdm_docs/sd/1050170001_sd.pdf",
        )


class UsbMicroBReceptacle(UsbDeviceConnector, GeneratorBlock):
    def __init__(self, *, generate_esd_diode: BoolLike = True) -> None:
        super().__init__(generate_esd_diode=generate_esd_diode)

        self.conn = self.Block(Molex_105017_0001_Device())
        self.connect(self.gnd, self.conn.gnd)
        self.connect(self.pwr, self.conn.pwr)
        self.connect(self.usb, self.conn.usb)

        self.generator_param(self.usb.is_connected(), self.generate_esd_diode)

    @override
    def generate(self) -> None:
        super().generate()

        if self.usb.is_connected():
            if self.get(self.generate_esd_diode):
                self.esd = self.Block(UsbEsdDiode())
                self.connect(self.esd.gnd, self.gnd)
                self.connect(self.esd.usb, self.usb)

        # TODO there does not seem to be full agreement on what to do with the shield pin, we arbitrarily ground it
        self.connect(self.gnd, self.conn.shield)


class UsbCcPulldownResistor(InternalSubcircuit, Block):
    """Pull-down resistors on the CC lines for a device to request power from a type-C UFP port,
    without needing a USB PD IC."""

    def __init__(self) -> None:
        super().__init__()
        self.cc = self.Port(UsbCcPort(), [Input])
        self.gnd = self.Port(Ground(), [Common])

    @override
    def contents(self) -> None:
        super().contents()
        pdr_model = Resistor(resistance=5.1 * kOhm(tol=0.01))
        self.cc1 = self.Block(pdr_model)
        self.cc2 = self.Block(pdr_model)
        self.connect(self.gnd.net, self.cc1.a, self.cc2.a)
        self.connect(self.cc1.b, self.cc.cc1)
        self.connect(self.cc2.b, self.cc.cc2)


class Tpd2e009(UsbEsdDiode, FootprintBlock, JlcPart):
    @override
    def contents(self) -> None:
        # Note, also compatible: https://www.diodes.com/assets/Datasheets/DT1452-02SO.pdf
        # PESD5V0X1BT,215 (different architecture, but USB listed as application)
        super().contents()
        self.gnd.init_from(Ground())
        self.usb.init_from(UsbPassivePort())
        self.footprint(
            "U",
            "Package_TO_SOT_SMD:SOT-23",
            {
                "1": self.usb.dm,
                "2": self.usb.dp,
                "3": self.gnd,
            },
            mfr="Texas Instruments",
            part="TPD2E009",
            datasheet="https://www.ti.com/lit/ds/symlink/tpd2e009.pdf",
        )


class Pesd5v0x1bt(UsbEsdDiode, FootprintBlock, JlcPart):
    """Ultra low capacitance ESD protection diode (0.9pF typ), suitable for USB and GbE"""

    @override
    def contents(self) -> None:
        super().contents()
        self.gnd.init_from(Ground())
        self.usb.init_from(UsbPassivePort())
        self.assign(self.lcsc_part, "C456094")
        self.assign(self.actual_basic_part, False)
        self.footprint(
            "U",
            "Package_TO_SOT_SMD:SOT-23",
            {
                "1": self.usb.dm,
                "2": self.usb.dp,
                "3": self.gnd,
            },
            mfr="Nexperia",
            part="PESD5V0X1BT",
            datasheet="https://assets.nexperia.com/documents/data-sheet/PESD5V0X1BT.pdf",
        )


class Pgb102st23(UsbEsdDiode, FootprintBlock, JlcPart):
    """ESD suppressor, suitable for high speed protocols including USB2.0, 0.12pF typ"""

    @override
    def contents(self) -> None:
        super().contents()
        self.gnd.init_from(Ground())
        self.usb.init_from(UsbPassivePort())
        self.assign(self.lcsc_part, "C126830")
        self.assign(self.actual_basic_part, False)
        self.footprint(
            "U",
            "Package_TO_SOT_SMD:SOT-23",
            {
                "1": self.usb.dm,
                "2": self.usb.dp,
                "3": self.gnd,
            },
            mfr="Littelfuse",
            part="PGB102ST23",
            datasheet="https://www.littelfuse.com/~/media/electronics/datasheets/pulseguard_esd_suppressors/littelfuse_pulseguard_pgb1_datasheet.pdf.pdf",
            pnp_rot=90,
        )
