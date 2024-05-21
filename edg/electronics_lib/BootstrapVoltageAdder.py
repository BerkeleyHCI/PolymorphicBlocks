from ..electronics_abstract_parts import *


class BootstrapVoltageAdder(KiCadSchematicBlock, PowerConditioner, Block):
    """Bipolar (positive and negative) voltage adder using a switched cap circuit.
    """
    @init_in_parent
    def __init__(self, frequency: RangeExpr = 250*kHertz(tol=0), ripple_limit: FloatExpr = 25*mVolt):
        super().__init__()

        self.gnd = self.Port(Ground.empty())
        self.pwr = self.Port(VoltageSink.empty())  # voltage to be added
        self.pwr_pos = self.Port(VoltageSink.empty())  # ... on top of the positive supply
        self.pwr_neg = self.Port(VoltageSink.empty())  # ... and below the negative supply, can be gnd
        self.pwm = self.Port(DigitalSink.empty())

        self.out_pos = self.Port(VoltageSource.empty())
        self.out_neg = self.Port(VoltageSource.empty())

        self.frequency = self.ArgParameter(frequency)
        self.ripple_limit = self.ArgParameter(ripple_limit)

    def contents(self):
        super().contents()

        # TODO model diode forward voltage drops
        out_current = self.out_pos.link().current_drawn.hull(self.out_neg.link().current_drawn)
        diode_model = Diode(reverse_voltage=self.pwm.link().voltage.hull(0*Volt(tol=0)),
                            current=out_current, voltage_drop=(0, 0.5)*Volt)
        cap_fly_model = Capacitor(1*uFarad(tol=0.2), voltage=self.pwr_pos.link().voltage + self.pwm.link().voltage)
        cap_bulk_model = Capacitor(1*uFarad(tol=0.2), voltage=self.pwm.link().voltage)

        self.d_pos_1 = self.Block(diode_model)
        self.d_pos_2 = self.Block(diode_model)
        self.d_neg_1 = self.Block(diode_model)
        self.d_neg_2 = self.Block(diode_model)
        self.d_prot_high = self.Block(diode_model)
        self.d_prot_neg = self.Block(diode_model)

        self.c_fly_pos = self.Block(cap_fly_model)
        self.c_fly_neg = self.Block(cap_fly_model)

        self.c_pos = self.Block(cap_bulk_model)
        self.c_neg = self.Block(cap_bulk_model)

        # TODO verify calculations
        # for current, from dQ = C * dV, so I = C * dV * f
        # we assume (perhaps wrongly) that it will discharge to ripple_limit every cycle
        # and that the switching cap action will bring it back up by 1/2 ripple_limit,
        # for dV = ripple_limit/2
        self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
                          conversions={
                              'gnd': Ground(),  # protection only, no draw
                              'pwr': VoltageSink(),

                              'pwr_pos': VoltageSink(
                                  current_draw=out_current
                              ),
                              'pwr_neg': VoltageSink(
                                  current_draw=out_current
                              ),
                              'pwm': DigitalSink(
                                  current_draw=(-out_current.upper(), out_current.upper())
                              ),
                              'out_pos': VoltageSource(
                                  self.pwr_pos.link().voltage + self.pwm.link().output_thresholds.upper(),
                                  # NOTE - assumes flying cap = bulk cap
                                  current_limits=(0, (self.c_pos.actual_capacitance * self.ripple_limit / 2 * self.frequency).lower())
                              ),
                              'out_neg': VoltageSource(
                                  self.pwr_neg.link().voltage - self.pwm.link().output_thresholds.upper(),
                                  # NOTE - assumes flying cap = bulk cap
                                  current_limits=(0, (self.c_neg.actual_capacitance * self.ripple_limit / 2 * self.frequency).lower())
                              ),
                          })
