from electronics_abstract_parts import *


class BootstrapVoltageAdder(KiCadSchematicBlock, Block):
    """Bipolar (positive and negative) voltage adder using a switched cap circuit.
    """
    @init_in_parent
    def __init__(self, current: RangeLike):
        super().__init__()

        self.gnd = self.Port(Ground())
        self.pwr = self.Port(VoltageSink.empty())  # voltage to be added
        self.pwr_pos = self.Port(VoltageSink.empty())  # ... on top of the positive supply
        self.pwr_neg = self.Port(VoltageSink.empty())  # ... and below the negative supply, can be gnd
        self.pwm = self.Port(DigitalSink.empty())

        self.out_pos = self.Port(VoltageSource.empty())
        self.out_neg = self.Port(VoltageSource.empty())

    def contents(self):
        super().contents()

        diode_model = Diode(reverse_voltage=self.pwm.link().voltage.hull(0*Volt(tol=0)),
                            current=self.out_pos.link().current_drawn.hull(self.out_neg.link().current_drawn))
        cap_fly_model = Capacitor(1*uFarad(tol=0.2), self.pwr_pos.link().voltage + self.pwm.link().voltage)
        cap_bulk_model = Capacitor(10*uFarad(tol=0.2), self.pwm.link().voltage)

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

        self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
                          conversions={
                              'gnd': Ground(),
                              'pwr': VoltageSink(),

                              'pwr_pos': VoltageSink(),
                              'pwr_neg': VoltageSink(),
                              'pwm': DigitalSink(),
                              'out_pos': VoltageSource(),
                              'out_neg': VoltageSource(),
                          })
