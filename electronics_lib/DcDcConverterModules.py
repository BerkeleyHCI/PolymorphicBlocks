from electronics_abstract_parts import *
from electronics_lib import SmtNFet
from electronics_lib.DcDcConverters import Tps61023_Device


class Tps61023_Device_Module(FootprintBlock):
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vin = self.Port(VoltageSink(
            voltage_limits=(0.5, 5.5)*Volt,
            current_draw=(0, 0.5) * Amp  # TODO current draw specs, the part doesn't really have a datasheet
        ))
        self.vout = self.Port(VoltageSource())

    def contents(self) -> None:
        super().contents()
        self.dcdc_converter = self.Block(Tps61023_Device())


        # self.vdd_res = self.Block(Resistor())
        # self.vm_res = self.Block(Resistor())
        self.vin_cap = self.Block(Capacitor())
        self.vout_cap = self.Block(Capacitor())
        self.ind = self.Block(Inductor())
        self.vout_r1 = self.Block(Resistor())
        self.vout_r2 = self.Block(Resistor())

        self.footprint(
            'U', 'BatteryProtector_S8200A_Module',
            {
                '1': self.gnd,
                '2': self.vin,
                '3': self.vout,
            }
        )
        # i/o connections
        self.connect(self.dcdc_converter.gnd, self.gnd)
        self.connect(self.dcdc_converter.vin, self.vin)
        self.connect(self.dcdc_converter.vout, self.vout)

        # vin cap
        self.connect(self.dcdc_converter.vin, self.vin_cap.pos.as_voltage_sink())
        self.connect(self.dcdc_converter.gnd, self.vin_cap.neg.as_ground())

        # vout cap
        self.connect(self.dcdc_converter.vout, self.vout_cap.pos.as_voltage_sink())
        self.connect(self.dcdc_converter.gnd, self.vout_cap.neg.as_ground())
        #
        # inductor
        self.connect(self.dcdc_converter.sw, self.ind.a.as_voltage_sink())
        self.connect(self.dcdc_converter.vin, self.ind.b.as_voltage_sink())

        # voltage divider
        self.connect(self.gnd, self.vout_r2.b.as_ground())
        self.connect(self.dcdc_converter.vout, self.vout_r1.a.as_voltage_sink())
        self.connect(self.dcdc_converter.fb, self.vout_r1.b.as_analog_sink())
        self.connect(self.vout_r1.b, self.vout_r2.a)