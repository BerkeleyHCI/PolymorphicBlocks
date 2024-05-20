from typing import Optional

from electronics_abstract_parts import *
from .JlcPart import JlcPart


class JacdacDataLink(Link):
    """Link for the JD_DATA line"""
    def __init__(self) -> None:
        super().__init__()
        self.nodes = self.Port(Vector(JacdacDataPort.empty()))
        self.passives = self.Port(Vector(JacdacPassivePort.empty()))

    def contents(self) -> None:
        super().contents()
        self.jd_data = self.connect(self.nodes.map_extract(lambda node: node.jd_data),
                                    self.passives.map_extract(lambda node: node.jd_data),
                                    flatten=True)
        self.require(self.nodes.length() > 1, "jd_data connection required")


class JacdacDataPort(Bundle[JacdacDataLink]):
    link_type = JacdacDataLink
    def __init__(self, model: Optional[DigitalBidir] = None) -> None:
        super().__init__()
        if model is None:  # ideal by default
            model = DigitalBidir()
        self.jd_data = self.Port(model)


class JacdacPassivePort(Bundle[JacdacDataLink]):
    link_type = JacdacDataLink
    def __init__(self) -> None:
        super().__init__()
        self.jd_data = self.Port(DigitalSink())  # needs to be typed but is as close to passive as possible


@abstract_block
class JacdacSubcircuit(Interface):
    """Category for Jacdac subcircuits"""
    pass


class JacdacEdgeConnectorBare(JacdacSubcircuit, FootprintBlock, GeneratorBlock):
    """Jacdac connector, in power sink or source mode (both available, but both may not be connected simultaneously).
    This is the bare connector, you should use the non-bare one with the recommended interface circuitry in most cases!
    Uses the recessed connector, which is the default used by the device outline generator.

    Requires this KiCad footprint library to be available: https://github.com/mattoppenheim/jacdac

    All specs from from https://microsoft.github.io/jacdac-docs/reference/electrical-spec

    If the power sink (power is sunk into the port and off-board) is connected, is_power_provider
    indicates whether this port should model the maximum downstream current draw
    """
    @init_in_parent
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
            # if not a power provider, extend the voltage range to directly connect to a power source edge
            voltage_limits=self.is_power_provider.then_else((4.3, 5.5)*Volt, (3.5, 5.5)*Amp),
            current_draw=self.is_power_provider.then_else((900, 1000)*mAmp, (0, 0)*Amp)
        ), optional=True)

        # TODO this should be a JacdacDataPort, this is being lazy to avoid defining a bridge and diode adapter
        self.jd_data = self.Port(DigitalBidir(
            voltage_limits=(0, 3.5)*Volt,
            voltage_out=(0, 3.5)*Volt,
            input_thresholds=(0.3, 3.0)*Volt,
            output_thresholds=(0.3, 3.0)*Volt
        ))

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

        self.footprint(  # EC refdes for edge connector
            'EC', 'Jacdac:JD-PEC-02_Prerouted_recessed',
            {
                '1': self.jd_data,
                '2': gnd_node,
                '3': pwr_node,
            },
        )


class Rclamp0521p(TvsDiode, FootprintBlock, JlcPart):
    """RCLAMP0521P-N TVS diode in 0402 package, recommended in the Jacdac DDK."""
    def contents(self):
        super().contents()
        self.require(self.working_voltage.within(self.actual_working_voltage))
        self.require(self.actual_capacitance.within(self.capacitance))

        self.assign(self.actual_working_voltage, (-5, 5)*Volt)
        self.assign(self.actual_breakdown_voltage, (-5.8, 5.8)*Volt)
        self.assign(self.actual_capacitance, 0.3*pFarad(tol=0))  # only typ given

        self.footprint(
            'D', 'Diode_SMD:D_0402_1005Metric',
            {
                '1': self.cathode,
                '2': self.anode,
            },
        )
        self.assign(self.lcsc_part, 'C2827711')
        self.assign(self.actual_basic_part, False)


class JacdacEdgeConnector(Connector, JacdacSubcircuit, GeneratorBlock):
    """Jacdac edge connector, in power sink or source mode (both available, but both may not be connected simultaneously).
    This includes the required per-port application circuitry, including status LEDs and ESD diodes.
    This does NOT include device-wide application circuitry like EMI filters.

    Requires this KiCad footprint library to be available: https://github.com/mattoppenheim/jacdac
    """
    @init_in_parent
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
        self.conn = self.Block(JacdacEdgeConnectorBare(self.is_power_provider))

        self.connect(self.jd_data.jd_data, self.conn.jd_data)

        if self.get(self.gnd_src.is_connected()):
            gnd_node = self.connect(self.gnd_src, self.conn.gnd_src)
        else:
            gnd_node = self.connect(self.gnd_sink, self.conn.gnd_sink)

        if self.get(self.jd_pwr_src.is_connected()):
            jd_pwr_node = self.connect(self.jd_pwr_src, self.conn.jd_pwr_src)
        else:
            jd_pwr_node = self.connect(self.jd_pwr_sink, self.conn.jd_pwr_sink)

        with self.implicit_connect(
            ImplicitConnect(gnd_node, [Common]),
        ) as imp:
            (self.status_led, ), _ = self.chain(self.jd_status, imp.Block(IndicatorLed(Led.Orange)))
            (self.tvs_jd_pwr, ), _ = self.chain(jd_pwr_node,
                                                imp.Block(ProtectionTvsDiode(working_voltage=(0, 5)*Volt)))
            # "ideally less than 1pF but certainly no more than 4pF"
            (self.tvs_jd_data, ), _ = self.chain(self.jd_data.jd_data,
                                                 imp.Block(DigitalTvsDiode(working_voltage=(0, 3.3)*Volt,
                                                                           capacitance=(0, 1)*pFarad)))


class JacdacDataInterface(JacdacSubcircuit, Block):
    """Interface from a Jacdac data bus to a device, including protection and EMI filtering.
    Does NOT include per-port circuitry like ESD diodes and status LEDs."""
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Ground.empty(), [Common])
        self.pwr = self.Port(VoltageSink.empty(), [Power])

        self.signal = self.Port(DigitalBidir.empty(), [Input])
        self.jd_data = self.Port(JacdacDataPort.empty(), [Output])

    def contents(self):
        super().contents()
        self.ferrite = self.Block(FerriteBead(hf_impedance=(1, float('inf'))*kOhm))
        signal_level = self.signal.link().voltage
        self.rc = self.Block(LowPassRc(impedance=220*Ohm(tol=0.05), cutoff_freq=22*MHertz(tol=0.12),
                                       voltage=signal_level))
        clamp_diode_model = Diode(reverse_voltage=(0, signal_level.upper()),
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


class JacdacMountingData1(JacdacSubcircuit, FootprintBlock):
    """Jacdac mounting hole for data, with a passive-typed port so it doesn't count as a connection
    for validation purposes."""
    def __init__(self):
        super().__init__()
        self.jd_data = self.Port(JacdacPassivePort())

    def contents(self):
        self.footprint(
            'MH', 'Jacdac:jacdac_hole_DATA_notched_MH1',
            {
                'MH1': self.jd_data.jd_data,
            },
        )


class JacdacMountingGnd2(JacdacSubcircuit, FootprintBlock):
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


class JacdacMountingGnd4(JacdacSubcircuit, FootprintBlock):
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


class JacdacMountingPwr3(JacdacSubcircuit, FootprintBlock):
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


class JacdacDeviceTop(DesignTop):
    """Template for a Jacdac device. Nets jd_data, jd_pwr, gnd, and jd_status are provided and must be
    connected externally.

    Recommend connecting to the nets, instead of connecting directly to the created Blocks and their Ports."""

    def contents(self):
        super().contents()
        self.edge = self.Block(JacdacEdgeConnector())
        self.jd_mh1 = self.Block(JacdacMountingData1())
        self.jd_mh2 = self.Block(JacdacMountingGnd2())
        self.jd_mh3 = self.Block(JacdacMountingPwr3())
        self.jd_mh4 = self.Block(JacdacMountingGnd4())

        self.jd_data = self.connect(self.edge.jd_data, self.jd_mh1.jd_data)
        self.jd_pwr = self.connect(self.edge.jd_pwr_src, self.jd_mh3.jd_pwr)
        self.gnd = self.connect(self.edge.gnd_src, self.jd_mh2.gnd, self.jd_mh4.gnd)
        self.jd_status = self.connect(self.edge.jd_status)

    def create_edge(self) -> JacdacEdgeConnector:
        """Utility function, creates a new edge connector (in power sink mode) and connects it to the net.
        The edge connector Block is returned and must be assigned a name."""
        new_edge = self.Block(JacdacEdgeConnector())
        self.connect(self.jd_data, new_edge.jd_data)
        self.connect(self.jd_status, new_edge.jd_status)
        self.connect(self.jd_pwr, new_edge.jd_pwr_sink)
        self.connect(self.gnd, new_edge.gnd_sink)
        return new_edge
