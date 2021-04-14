from electronics_abstract_parts import *


class BatteryProtector_S8200A_Device(DiscreteChip, FootprintBlock):
  def __init__(self):
    super().__init__()

    self.vss = self.Port(Ground()) # voltage_limits=(-0.3, 12) * Volt, current_draw=(0.7, 5.5) * uAmp
    self.vdd = self.Port(VoltageSink(
      voltage_limits=self.vss.voltage_limits + RangeExpr._to_expr_type((-0.3, 12) * Volt),
      current_draw=(0.7, 5.5) * uAmp
    ))

    self.nc = self.Port(Passive(), optional=True)
    self.vm = self.Port(Passive(), optional=True) # voltage_limits=self.vdd.voltage_limits + RangeExpr._to_expr_type((-28, 0.3) * Volt), current_draw=(0.7, 5.5) * uAmp
    self.do = self.Port(Passive(), optional=True) # voltage_limits=(self.vss.voltage_limits.lower() - 0.3 * Volt, self.vdd.voltage_limits.upper() + 0.3 * Volt), current_draw=(0.7, 5.5) * uAmp
    self.co = self.Port(Passive(), optional=True) # voltage_limits=(self.vm.voltage_limits.lower() - 0.3 * Volt, self.vdd.voltage_limits.upper() + 0.3 * Volt), current_draw=(0.7, 5.5) * uAmp


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
      mfr='ABLIC', part='S-8200ABE-M6T1U',
      datasheet='https://www.mouser.com/datasheet/2/360/S8200A_E-1365901.pdf'
    )

class BatteryProtector_S8200A(FootprintBlock):
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.battery_protector = self.Block(BatteryProtector_S8200A_Device())

    self.vdd_res = self.Block(Resistor())
    self.vm_res = self.Block(Resistor())
    self.vdd_vss_cap = self.Block(Capacitor())

    self.do_fet = self.Block(NFet())
    self.co_fet = self.Block(NFet())

    self.ebp = self.Port(VoltageSource())
    self.ebm = self.Port(GroundSource())
    self.vdd = self.Export(self.battery_protector.vdd)
    self.vss = self.Export(self.battery_protector.vss)

  def contents(self) -> None:
    super().contents()

    # i/o connections
    self.connect(self.vm_res.b.as_ground_source(), self.ebm)
    self.connect(self.battery_protector.vdd, self.ebp)
    self.connect(self.vdd_res.b.as_voltage_sink(), self.vdd)

    # vdd resistor
    self.connect(self.battery_protector.vdd, self.vdd_res.a.as_voltage_sink())

    # vm resistor
    self.connect(self.battery_protector.vm, self.vm_res.a)

    # vdd vss cap
    self.connect(self.battery_protector.vdd, self.vdd_vss_cap.pos.as_voltage_sink())
    self.connect(self.battery_protector.vss, self.vdd_vss_cap.neg.as_ground())

    # do fet
    self.connect(self.battery_protector.vss, self.do_fet.source.as_ground())
    self.connect(self.battery_protector.do, self.do_fet.gate)

    # do co
    self.connect(self.do_fet.drain, self.co_fet.drain)

    # co fet
    self.connect(self.ebm, self.co_fet.source.as_ground())
    self.connect(self.battery_protector.co, self.co_fet.gate)