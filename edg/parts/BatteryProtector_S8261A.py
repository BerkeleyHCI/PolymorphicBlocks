from ..abstract_parts import *
from .JlcPart import JlcPart


class S8261A_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.vss = self.Port(Ground())
    self.vdd = self.Port(VoltageSink.from_gnd(
      self.vss,
      voltage_limits=(-0.3, 12) * Volt,
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
      mfr='ABLIC', part='S-8261ABJMD-G3JT2S',
      datasheet='https://www.mouser.com/datasheet/2/360/S8200A_E-1365901.pdf'
    )
    self.assign(self.lcsc_part, 'C28081')
    self.assign(self.actual_basic_part, False)

class S8261A(PowerConditioner, Block):
  """1-cell LiIon/LiPo Battery protection IC protecting against overcharge, overdischarge, over current.
  """
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.ic = self.Block(S8261A_Device())

    self.gnd_in = self.Export(self.ic.vss)
    self.pwr_in = self.Port(VoltageSink.empty())
    self.gnd_out = self.Port(Ground.empty())
    self.pwr_out = self.Port(VoltageSource.empty())

    self.do_fet = self.Block(Fet.NFet(
      drain_current=self.pwr_in.link().current_drawn,
      power=RangeExpr.ZERO,
      gate_voltage=self.pwr_in.link().voltage,
      gate_charge=RangeExpr.ALL,
      rds_on=(0, 0.1)*Ohm,
      drain_voltage=self.pwr_in.link().voltage
    ))
    self.co_fet = self.Block(Fet.NFet(
      drain_current=self.pwr_in.link().current_drawn,
      power=RangeExpr.ZERO,
      gate_voltage=self.pwr_in.link().voltage,
      gate_charge=RangeExpr.ALL,
      rds_on=(0, 0.1)*Ohm,
      drain_voltage=self.pwr_in.link().voltage
    ))

  def contents(self) -> None:
    super().contents()

    self.vdd_res = self.Block(
      SeriesPowerResistor(470 * Ohm(tol=0.10))  # while 470 is preferred, the actual acceptable range is 300-1k
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
    self.connect(self.gnd_out, self.co_fet.source.adapt_to(Ground()))
    self.connect(self.ic.co, self.co_fet.gate)

    self.vm_res = self.Block(Resistor(2 * kOhm(tol=0.10)))
    self.connect(self.vm_res.a.adapt_to(Ground()), self.gnd_out)
    self.connect(self.vm_res.b, self.ic.vm)
