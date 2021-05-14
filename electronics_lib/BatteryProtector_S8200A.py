from electronics_abstract_parts import *


class BatteryProtector_S8200A_Device(DiscreteChip, FootprintBlock):
  def __init__(self):
    super().__init__()

    self.vss = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(
      voltage_limits=self.vss.voltage_limits + RangeExpr._to_expr_type((-0.3, 12) * Volt),
      current_draw=(0.7, 5.5) * uAmp
    ))

    self.nc = self.Port(Passive(), optional=True) # no connection
    self.vm = self.Port(Passive())
    self.do = self.Port(Passive())
    self.co = self.Port(Passive())


  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
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

    self.pwr_out = self.Port(VoltageSource())
    self.gnd_out = self.Port(GroundSource())
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=self.battery_protector.vdd.voltage_limits,
    ))
    self.gnd_in = self.Export(self.battery_protector.vss)

    self.do_fet = self.Block(NFet(
      drain_current=self.pwr_in.link().current_drawn,
      power=RangeExpr.ZERO,
      gate_voltage=self.pwr_in.link().voltage.upper(),
      gate_charge=RangeExpr.ALL,
      rds_on=Default((0, 0.1)),
      drain_voltage=self.pwr_in.link().voltage.upper()
    ))
    self.co_fet = self.Block(NFet(
      drain_current=self.pwr_in.link().current_drawn,
      power=RangeExpr.ZERO,
      gate_voltage=self.pwr_in.link().voltage.upper(),
      gate_charge=RangeExpr.ALL,
      rds_on=Default((0, 0.1)),
      drain_voltage=self.pwr_in.link().voltage.upper()
    ))

  def contents(self) -> None:
    super().contents()

    (self.vdd_res, ), _ = self.chain(
      self.pwr_in,
      self.Block(SeriesPowerResistor(330 * Ohm(tol=0.10), (0 * uAmp, self.battery_protector.vdd.current_draw.upper()))), # while 330 is preferred, the actual acceptable range is 150-1k
      self.battery_protector.vdd)

    self.connect(self.pwr_in, self.pwr_out)

    (self.vdd_vss_cap, ), _ = self.chain(
      self.battery_protector.vdd,
      self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.10))),
      self.battery_protector.vss)

    # do fet
    self.connect(self.battery_protector.vss, self.do_fet.source.as_ground())
    self.connect(self.battery_protector.do, self.do_fet.gate)

    # do co
    self.connect(self.do_fet.drain, self.co_fet.drain)

    # co fet
    self.connect(self.gnd_out, self.co_fet.source.as_ground_source())
    self.connect(self.battery_protector.co, self.co_fet.gate)

    (self.vm_res, ), _ = self.chain(
      self.gnd_out,
      self.Block(SeriesPowerResistor(2 * kOhm(tol=0.10), (0 * uAmp, self.battery_protector.vdd.current_draw.upper()))),
      self.battery_protector.vm.as_voltage_sink()
    )
