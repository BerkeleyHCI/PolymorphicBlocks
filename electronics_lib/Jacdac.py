from typing import Optional

from electronics_abstract_parts import *


class JacdacDataLink(Link):
    """Link for the JD_DATA line"""
    def __init__(self) -> None:
        super().__init__()
        self.nodes = self.Port(Vector(JacdacDataPort(DigitalBidir.empty())))

    def contents(self) -> None:
        super().contents()

        self.jd_data = self.connect(self.nodes.map_extract(lambda node: node.jd_data),
                                    flatten=True)


class JacdacDataPort(Bundle[JacdacDataLink]):
    link_type = JacdacDataLink
    def __init__(self, model: Optional[DigitalBidir] = None) -> None:
        super().__init__()
        if model is None:  # ideal by default
            model = DigitalBidir()
        self.jd_data = self.Port(model)


class JacdacConnectorBare(FootprintBlock, GeneratorBlock):
    """Jacdac connector, in power sink or source mode (both available, but both may not be connected simultaneously).
    This is the bare connector, you should use the non-bare one with the recommended interface circuitry in most cases!

    Requires this KiCad footprint library to be available: https://github.com/mattoppenheim/jacdac

    All specs from from https://microsoft.github.io/jacdac-docs/reference/electrical-spec

    If the power sink (power is sunk into the port and off-board) is connected, is_power_provider
    indicates whether this port should model the maximum downstream current draw
    """
    def __init__(self, is_power_provider: BoolLike = False) -> None:
        super().__init__()
        self.is_power_provider = self.ArgParameter(is_power_provider)

        # ports for power source mode
        self.gnd_src = self.Port(GroundSource(), optional=True)
        self.jd_pwr_src = self.Port(VoltageSource(
            voltage_out=(3.5, 5.5)*Volt,
            current_limits=(0, 900)*mAmp
        ), optional=True)

        self.gnd_sink = self.Port(Ground(), optional=True)
        self.jd_pwr_sink = self.Port(VoltageSink(
            voltage_limits=(4.3, 5.5)*Volt,
            current_draw=self.is_power_provider.then_else((900, 1000)*mAmp, (0, 0)*Amp)
        ), optional=True)

        self.jd_data = self.Port(JacdacDataPort(DigitalBidir(
            voltage_limits=(0, 3.5)*Volt,
            voltage_out=(0, 3.5)*Volt,
            input_thresholds=(0.3, 3.0)*Volt,
            output_thresholds=(0.3, 3.0)*Volt
        )))

        self.generator_param(self.jd_pwr_src.is_connected(), self.gnd_src.is_connected())

    def contents(self):
        super().contents()

        self.require(self.jd_pwr_src.is_connected() | self.jd_pwr_sink.is_connected())
        self.require(self.jd_pwr_src.is_connected().implies(self.gnd_src.is_connected()))
        self.require(self.jd_pwr_sink.is_connected().implies(self.gnd_sink.is_connected()))

    def generate(self):
        super().generate()

        if self.get(self.jd_pwr_src.is_connected()):
            pwr_node: CircuitPort = self.jd_pwr_src
            gnd_node: CircuitPort = self.gnd_src
        else:
            pwr_node = self.jd_pwr_sink
            gnd_node = self.gnd_sink

        self.footprint(
            'EC', 'Jacdac:JD-PEC-02_Prerouted',
            {
                '1': self.jd_data.jd_data,
                '2': gnd_node,
                '3': pwr_node,
            },
        )


class JacdacConnector(Connector, GeneratorBlock):
    """Jacdac connector, in power sink or source mode (both available, but both may not be connected simultaneously).
    This includes the required per-port application circuitry, including status LEDs and ESD diodes.
    This does NOT include device-wide application circuitry like EMI filters.

    Requires this KiCad footprint library to be available: https://github.com/mattoppenheim/jacdac
    """
    def __init__(self, is_power_provider: BoolLike = False) -> None:
        super().__init__()
        self.is_power_provider = self.ArgParameter(is_power_provider)

        # ports for power source mode
        self.gnd_src = self.Port(GroundSource.empty(), optional=True)
        self.jd_pwr_src = self.Port(VoltageSource.empty(), optional=True)

        self.gnd_sink = self.Port(Ground.empty(), optional=True)
        self.jd_pwr_sink = self.Port(VoltageSink.empty(), optional=True)

        self.jd_data = self.Port(JacdacDataPort.empty())

        self.jd_status = self.Port(DigitalSink.empty())  # for status LED

        self.generator_param(self.gnd_src.is_connected(), self.jd_pwr_src.is_connected(),
                             self.gnd_sink.is_connected(), self.jd_pwr_sink.is_connected())

    def generate(self):
        super().contents()
        self.conn = self.Block(JacdacConnectorBare(self.is_power_provider))

        for ext_port, int_port in [
            (self.gnd_src, self.conn.gnd_src),
            (self.jd_pwr_src, self.conn.jd_pwr_src),
            (self.gnd_sink, self.conn.gnd_sink),
            (self.jd_pwr_sink, self.conn.jd_pwr_sink),
        ]:
            if self.get(ext_port.is_connected()):
                self.connect(ext_port, int_port)

        if self.gnd_src.is_connected():
            gnd_node: CircuitPort = self.gnd_src
        else:
            gnd_node = self.gnd_sink

        self.status_led = self.Block(IndicatorLed(Led.Orange))
        self.connect(self.status_led.signal, self.jd_status)
        self.connect(self.status_led.gnd, gnd_node)

        # TODO add ESD diodes


class JacdacDataInterface(Block):
    """Interface from a Jacdac data bus to a device, including protection and EMI filtering.
    Does NOT include per-port circuitry like ESD diodes and status LEDs."""
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Ground.empty(), [Common])
        self.pwr = self.Port(VoltageSink.empty(), [Power])

        self.jd_data = self.Port(JacdacDataPort.empty())
        self.signal = self.Port(DigitalBidir.empty())

    def contents(self):
        super().contents()
        self.ferrite = self.Block(FerriteBead(hf_impedance=(1, float('int'))*kOhm))
        signal_level = self.signal.link().voltage
        self.rc = self.Block(LowPassRc(impedance=220*Ohm(tol=0.05), cutoff_freq=22*MHertz(tol=0.05),
                                       voltage=signal_level))
        clamp_diode_model = Diode(reverse_voltage=(signal_level.upper(), float('inf')),
                                  current=(0, 0))
        self.clamp_hi = self.Block(clamp_diode_model)
        self.clamp_lo = self.Block(clamp_diode_model)

        self.connect(self.jd_data.jd_data, self.ferrite.a.adapt_to(DigitalBidir(
            voltage_out=self.signal.link().voltage,
            voltage_limits=self.signal.link().voltage_limits,
            input_thresholds=self.signal.link().input_thresholds,
            output_thresholds=self.signal.link().output_thresholds
        )))
        self.connect(self.ferrite.b, self.rc.output)
        self.connect(self.rc.input, self.clamp_hi.anode, self.clamp_lo.cathode)
        self.connect(self.gnd, self.rc.gnd.adapt_to(Ground()), self.clamp_lo.anode.adapt_to(Ground()))
        self.connect(self.pwr, self.clamp_hi.cathode.adapt_to(VoltageSink()))
        # inner port is ideal to avoid circular parameter dependencies
        self.connect(self.signal, self.rc.input.adapt_to(DigitalBidir()))


class JacdacMountingData1(FootprintBlock):
    def __init__(self):
        super().__init__()
        self.jd_data = self.Port(JacdacDataPort())  # ideal

    def contents(self):
        self.footprint(
            'MH', 'Jacdac:jacdac_hole_DATA_notched_MH1',
            {
                'MH1': self.jd_data.jd_data,
            },
        )


class JacdacMountingGnd2(FootprintBlock):
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Ground())

    def contents(self):
        self.footprint(
            'MH', 'Jacdac:jacdac_hole_GND_MH2',
            {
                'MH2': self.gnd,
            },
        )


class JacdacMountingGnd4(FootprintBlock):
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Ground())

    def contents(self):
        self.footprint(
            'MH', 'Jacdac:jacdac_hole_GND_MH4',
            {
                'MH4': self.gnd,
            },
        )


class JacdacMountingPwr3(FootprintBlock):
    def __init__(self):
        super().__init__()
        self.jd_pwr = self.Port(VoltageSink())

    def contents(self):
        self.footprint(
            'MH', 'Jacdac:jacdac_hole_PWR_MH3',
            {
                'MH3': self.jd_pwr,
            },
        )