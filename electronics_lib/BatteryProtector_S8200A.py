from electronics_abstract_parts import *


class BatteryProtector_S8200A_Device(InternalSubcircuit, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.vss = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(
      voltage_limits=self.vss.voltage_limits + RangeExpr._to_expr_type((-0.3, 12) * Volt),
      current_draw=(0.7, 5.5) * uAmp
    ))

    self.vm = self.Port(Passive())
    self.do = self.Port(Passive())
    self.co = self.Port(Passive())


  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.do,
        '2': self.vm,
        '3': self.co,
        # '4': no connection pin,
        '5': self.vdd,
        '6': self.vss,
      },
      mfr='ABLIC', part='S-8200ABE-M6T1U',
      datasheet='https://www.mouser.com/datasheet/2/360/S8200A_E-1365901.pdf'
    )

class BatteryProtector_S8200A(PowerConditioner, Block):
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.ic = self.Block(BatteryProtector_S8200A_Device())

    self.pwr_out = self.Port(VoltageSource.empty())
    self.gnd_out = self.Port(GroundSource.empty())
    self.pwr_in = self.Port(VoltageSink.empty())
    self.gnd_in = self.Export(self.ic.vss)

    self.do_fet = self.Block(Fet.NFet(
      drain_current=self.pwr_in.link().current_drawn,
      power=RangeExpr.ZERO,
      gate_voltage=self.pwr_in.link().voltage,
      gate_charge=RangeExpr.ALL,
      rds_on=Default((0, 0.1)),
      drain_voltage=self.pwr_in.link().voltage
    ))
    self.co_fet = self.Block(Fet.NFet(
      drain_current=self.pwr_in.link().current_drawn,
      power=RangeExpr.ZERO,
      gate_voltage=self.pwr_in.link().voltage,
      gate_charge=RangeExpr.ALL,
      rds_on=Default((0, 0.1)),
      drain_voltage=self.pwr_in.link().voltage
    ))

  def contents(self) -> None:
    super().contents()

    self.vdd_res = self.Block(
      SeriesPowerResistor(330 * Ohm(tol=0.10))  # while 330 is preferred, the actual acceptable range is 150-1k
    ).connected(self.pwr_in, self.ic.vdd)

    self.connect(self.pwr_in, self.pwr_out)

    self.vdd_vss_cap = self.Block(
      DecouplingCapacitor(0.1 * uFarad(tol=0.10))
    ).connected(self.ic.vss, self.ic.vdd)

    # do fet
    self.connect(self.ic.vss, self.do_fet.source.adapt_to(Ground()))
    self.connect(self.ic.do, self.do_fet.gate)

    # do co
    self.connect(self.do_fet.drain, self.co_fet.drain)

    # co fet
    self.connect(self.gnd_out, self.co_fet.source.adapt_to(GroundSource()))
    self.connect(self.ic.co, self.co_fet.gate)

    self.vm_res = self.Block(
      SeriesPowerResistor(2 * kOhm(tol=0.10))
    ).connected(self.gnd_out, self.ic.vm.adapt_to(VoltageSink()))
