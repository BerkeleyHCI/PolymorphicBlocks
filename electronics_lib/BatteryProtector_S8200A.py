from electronics_abstract_parts import *
from electronics_lib import SmtInductor, SmtNFet


class BatteryProtector_S8200A(DiscreteChip, FootprintBlock):
  def __init__(self):
    super().__init__()

    # only required pins are Vcc, GND, DOUT, DIN
    # also need RTS, DTR for serial firmware updates
    # DNC pins that are not in use
    self.vdd = self.Port(VoltageSource())

    self.vss = self.Port(VoltageSink(
      voltage_limits=(4.95, 32) * Volt,
      current_draw=(0, 3.5) * mAmp  # 2.5uA sleep, 29mA receive, 290 mA max transmit
    ), [Power])

    digital_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # TODO speculative default
      current_draw=(0, 0),  # TODO actually an unspecified default
      current_limits=(-2, 2) * mAmp,
      input_threshold_factor=(0.3, 0.7),
      output_threshold_factor=(0.05, 0.95)
    )

    # adc_model = AnalogSink(
    #   voltage_limits=(2.65, 2.75) * Volt,
    #   current_draw=(35, 100) * nAmp,
    #   impedance=100*kOhm  # TODO no specs
    # )
    #
    # pull_up_model = DigitalSink.from_supply(
    #   self.vin, self.gnd,
    #   voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # TODO: FIX
    #   current_draw=(0, 0)*Amp,
    #   input_threshold_abs=(0.8, 2)*Volt
    # )  # TODO: FIX

    self.nc = self.Port(Passive(), optional=True)
    self.do = self.Port(VoltageSink(digital_model), optional=True)
    self.vm = self.Port(VoltageSink(digital_model), optional=True)
    self.co = self.Port(VoltageSink(digital_model), optional=True)


  def contents(self):
    super().contents()
    self.footprint(
      'U', 'BatteryProtector_S8200A',
      {
        '1': self.do,
        '2': self.vm,
        '3': self.co,
        '4': self.nc,
        '5': self.vdd,
        '6': self.vss,
      },
      # mfr='Digi International', part='XBP9B-*',
      # datasheet='https://www.digi.com/resources/documentation/digidocs/pdfs/90002173.pdf'
    )

class BatteryProtector_S8200A_Module(FootprintBlock):
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.vdd = self.Port(VoltageSource())
    self.vss = self.Port(VoltageSink(
      voltage_limits=(0.5, 5.5)*Volt,
      current_draw=(0, 0.5) * Amp  # TODO current draw specs, the part doesn't really have a datasheet
    ))

  def contents(self) -> None:
    super().contents()
    self.battery_protector = self.Block(BatteryProtector_S8200A())

    self.vdd_res = self.Block(Resistor())
    self.vm_res = self.Block(Resistor())
    self.vdd_vss_cap = self.Block(Capacitor())

    self.do_fet = self.Block(SmtNFet())
    self.co_fet = self.Block(SmtNFet())

    self.footprint(
      'U', 'BatteryProtector_S8200A_Module',
      {
        '1': self.gnd,
        '2': self.vdd,
        '3': self.vss,
      }
    )
    # i/o connections
    self.connect(self.vm_res.b.as_ground(), self.gnd)
    self.connect(self.vdd_res.b.as_voltage_sink(), self.vdd)
    self.connect(self.battery_protector.vss, self.vss)

    # vdd resistor
    self.connect(self.battery_protector.vdd, self.vdd_res.a.as_voltage_sink())

    # vm resistor
    self.connect(self.battery_protector.vm, self.vm_res.a.as_voltage_sink())

    # vdd vss cap
    self.connect(self.battery_protector.vdd, self.vdd_vss_cap.pos.as_voltage_sink())
    self.connect(self.battery_protector.vss, self.vdd_vss_cap.neg.as_voltage_sink())

    # do fet
    self.connect(self.battery_protector.vss, self.do_fet.source.as_voltage_sink())
    self.connect(self.battery_protector.do, self.do_fet.gate.as_voltage_sink())

    # do co
    self.connect(self.do_fet.drain, self.co_fet.drain)

    # co fet
    self.connect(self.gnd, self.co_fet.source.as_ground())
    self.connect(self.battery_protector.co, self.co_fet.gate.as_voltage_sink())