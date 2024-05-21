from ..abstract_parts import *


class EInkBoostPowerPath(Interface, KiCadSchematicBlock):
  """Boost converter power path for e-ink displays with negative voltage generation through
  a bootstrap switched-cap circuit.
  Current is the peak current through the FET and diodes."""
  @init_in_parent
  def __init__(self, voltage_out: RangeLike, current: RangeLike, inductance: RangeLike,
               in_capacitance: RangeLike, out_capacitance: RangeLike, resistance: RangeLike,
               diode_voltage_drop: RangeLike = (0, 0.5)*Volt):
    super().__init__()
    self.gnd = self.Port(Ground.empty())
    self.pwr_in = self.Port(VoltageSink.empty())
    self.pos_out = self.Port(VoltageSource.empty())
    self.neg_out = self.Port(VoltageSource.empty())

    self.gate = self.Port(Passive.empty())
    self.isense = self.Port(Passive.empty(), optional=True)

    self.voltage_out = self.ArgParameter(voltage_out)
    self.current = self.ArgParameter(current)
    self.inductance = self.ArgParameter(inductance)
    self.in_capacitance = self.ArgParameter(in_capacitance)
    self.out_capacitance = self.ArgParameter(out_capacitance)
    self.resistance = self.ArgParameter(resistance)
    self.diode_voltage_drop = self.ArgParameter(diode_voltage_drop)

  def contents(self):
    super().contents()

    self.fet = self.Block(Fet.NFet(
      drain_voltage=self.voltage_out.hull((0, 0)*Volt),
      drain_current=self.current,
      gate_voltage=(0, 5)*Volt,
      rds_on=(0, 400)*mOhm
    ))
    self.inductor = self.Block(Inductor(
      inductance=self.inductance,
      current=self.current
    ))
    self.sense = self.Block(Resistor(
      resistance=self.resistance
    ))
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=self.in_capacitance
    ))

    diode_model = Diode(
      reverse_voltage=self.voltage_out.hull((0, 0)*Volt), current=self.current.hull((0, 0)*Volt),
      voltage_drop=self.diode_voltage_drop,
      reverse_recovery_time=(0, 500e-9)  # guess from Digikey's classification for "fast recovery"
    )
    self.diode = self.Block(diode_model)
    self.boot_neg_diode = self.Block(diode_model)
    self.boot_gnd_diode = self.Block(diode_model)

    self.boot_cap = self.Block(Capacitor(
      capacitance=self.out_capacitance, voltage=self.voltage_out
    ))
    out_cap_model = DecouplingCapacitor(
      capacitance=self.out_capacitance
    )
    self.out_cap = self.Block(out_cap_model)
    self.neg_out_cap = self.Block(out_cap_model)

    self.import_kicad(
      self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'inductor.1': VoltageSink(),
        'diode.K': VoltageSource(
          voltage_out=self.voltage_out,
        ),
        'boot_neg_diode.A': VoltageSource(
          voltage_out=-self.voltage_out,
        ),
        'boot_gnd_diode.K': Ground(),
        'sense.2': Ground(),
      })
