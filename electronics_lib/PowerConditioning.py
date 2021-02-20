from electronics_abstract_parts import *


class Supercap(DiscreteComponent, CircuitBlock):  # TODO actually model supercaps and parts selection
  def __init__(self) -> None:
    super().__init__()
    self.pos = self.Port(ElectricalSink())
    self.neg = self.Port(Ground())

  def contents(self):
    super().contents()
    self.footprint(
      'C', 'Capacitor_THT:CP_Radial_D14.0mm_P5.00mm',  # actually 13.5
      {
        '1': self.pos,
        '2': self.neg,
      },
      part='DBN-5R5D334T',  # TODO this is too high resistance
      datasheet='http://www.elna.co.jp/en/capacitor/double_layer/catalog/pdf/dbn_e.pdf',
    )


class BufferedSupply(PowerConditioner):
  """Implements a current limiting source with an opamp for charging a supercap, and a Vf-limited diode
  for discharging

  See https://electronics.stackexchange.com/questions/178605/op-amp-mosfet-constant-current-power-source
  """
  @init_in_parent
  def __init__(self, charging_current: RangeLike = RangeExpr(), sense_resistance: RangeLike = RangeExpr(),
               voltage_drop: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.charging_current = self.Parameter(RangeExpr(charging_current))
    self.sense_resistance = self.Parameter(RangeExpr(sense_resistance))
    self.voltage_drop = self.Parameter(RangeExpr(voltage_drop))

    self.pwr = self.Port(ElectricalSink(), [Power, Input])
    self.pwr_out = self.Port(ElectricalSource(), [Output])
    self.require(self.pwr.current_draw.within(self.pwr_out.link().current_drawn +
                                              (0, self.charging_current.upper()) +
                                              (0, 0.05)))  # TODO nonhacky bounds on opamp/sense resistor current draw
    self.sc_out = self.Port(ElectricalSource(), optional=True)
    self.gnd = self.Port(Ground(), [Common])

    max_in_voltage = self.pwr.link().voltage.upper()
    max_charge_current = self.charging_current.upper()

    # Upstream power domain
    # TODO improve connect modeling everywhere
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.sense = self.Block(Resistor(  # TODO replace with SeriesResistor/CurrentSenseResistor - that propagates current
        resistance=self.sense_resistance,
        power=max_charge_current * max_charge_current * self.sense_resistance.upper()
      ))
      self.connect(self.pwr, self.sense.a.as_electrical_sink(
        current_draw=(0, max_charge_current)))

      self.fet = self.Block(PFet(
        drain_voltage=(0, max_in_voltage), drain_current=(0, max_charge_current),
        gate_voltage=(self.pwr.link().voltage.lower(), max_in_voltage),
        rds_on=(0, 0.5)*Ohm,  # TODO kind of arbitrary
        gate_charge=(0, float('inf')),
        power=(0, max_in_voltage * max_charge_current)
      ))
      self.connect(self.fet.source, self.sense.b)

      self.diode = self.Block(Diode(
        reverse_voltage=(0, max_in_voltage), current=self.charging_current, voltage_drop=self.voltage_drop,
        reverse_recovery_time=(0, float('inf'))
      ))
      self.connect(self.diode.anode.as_electrical_sink(),
                   self.fet.drain.as_electrical_source(
                     voltage_out=self.pwr.link().voltage),
                   self.sc_out)

      self.pwr_out_merge = self.Block(MergedElectricalSource())
      self.connect(self.pwr_out_merge.sink1, self.pwr)
      self.connect(self.pwr_out_merge.sink2, self.diode.cathode.as_electrical_source(
        voltage_out=(self.pwr.link().voltage.lower() - self.voltage_drop.upper(), self.pwr.link().voltage.upper())
      ))  # TODO replace with SeriesElectricalDiode or something that automatically calculates voltage drops?
      self.connect(self.pwr_out_merge.source, self.pwr_out)

      # TODO check if this tolerance stackup is stacking in the right direction... it might not
      low_sense_volt_diff = self.charging_current.lower() * self.sense_resistance.lower()
      high_sense_volt_diff = self.charging_current.upper() * self.sense_resistance.upper()
      low_sense_volt = self.pwr.link().voltage.lower() - high_sense_volt_diff
      high_sense_volt = self.pwr.link().voltage.upper() - low_sense_volt_diff

      self.set = imp.Block(VoltageDivider(output_voltage=(low_sense_volt, high_sense_volt), impedance=(1, 10) * kOhm))
      self.connect(self.set.input, self.pwr)  # TODO use chain
      self.amp = imp.Block(Opamp())
      self.connect(self.set.output, self.amp.inp)
      self.connect(self.amp.inn, self.sense.b.as_analog_source(
        voltage_out=(0, self.pwr.link().voltage.upper()),
        impedance=0*Ohm(tol=0)
      ))
      self.connect(self.amp.out, self.fet.gate.as_analog_sink())

    self.cap = self.Block(Supercap())
    self.connect(self.sc_out, self.cap.pos)
    self.connect(self.gnd, self.cap.neg)


class SingleDiodePowerMerge(PowerConditioner, Block):
  """Single-diode power merge block for two voltage sources, where the lower voltage one is diode-gated and less
  preferred if both are connected.
  """
  @init_in_parent
  def __init__(self, voltage_drop: RangeLike = RangeExpr(), reverse_recovery_time: RangeLike = (0, float('inf'))) -> None:
    super().__init__()

    self.pwr_in = self.Port(ElectricalSink())  # high-priority source
    self.pwr_in_diode = self.Port(ElectricalSink())  # low-priority source
    self.pwr_out = self.Port(ElectricalSource())

    self.diode = self.Block(Diode(
      reverse_voltage=(0, self.pwr_in.link().voltage.upper() - self.pwr_in_diode.link().voltage.lower()),
      current=self.pwr_out.link().current_drawn,
      voltage_drop=voltage_drop,
      reverse_recovery_time=reverse_recovery_time,
    ))

    self.require(self.pwr_in_diode.link().voltage.upper() - self.diode.voltage_drop.lower() <= self.pwr_in.link().voltage.lower())

    self.connect(self.pwr_in_diode, self.diode.anode.as_electrical_sink(
      current_draw=self.pwr_out.link().current_drawn
    ))

    self.merge = self.Block(MergedElectricalSource())
    self.connect(self.pwr_in, self.merge.sink1)
    self.connect(self.diode.cathode.as_electrical_source(
      voltage_out=(self.pwr_in_diode.link().voltage.lower() - self.diode.voltage_drop.upper(),
                   self.pwr_in_diode.link().voltage.upper() - self.diode.voltage_drop.lower()),
      current_limits=(-float('inf'), float('inf'))
    ), self.merge.sink2)

    self.connect(self.merge.source, self.pwr_out)


class DiodePowerMerge(PowerConditioner, Block):
  """Diode power merge block for two voltage sources.
  """
  @init_in_parent
  def __init__(self, voltage_drop: RangeLike = RangeExpr(), reverse_recovery_time: RangeLike = (0, float('inf'))) -> None:
    super().__init__()

    self.pwr_in1 = self.Port(ElectricalSink())
    self.pwr_in2 = self.Port(ElectricalSink())
    self.pwr_out = self.Port(ElectricalSource())

    output_lower = self.pwr_in1.link().voltage.lower().min(self.pwr_in2.link().voltage.lower()) - RangeExpr._to_expr_type(voltage_drop).upper()
    self.diode1 = self.Block(Diode(
      reverse_voltage=(0, self.pwr_in1.link().voltage.upper() - output_lower),
      current=self.pwr_out.link().current_drawn,
      voltage_drop=voltage_drop,
      reverse_recovery_time=reverse_recovery_time,
    ))
    self.diode2 = self.Block(Diode(
      reverse_voltage=(0, self.pwr_in2.link().voltage.upper() - output_lower),
      current=self.pwr_out.link().current_drawn,
      voltage_drop=voltage_drop,
      reverse_recovery_time=reverse_recovery_time,
    ))

    self.merge = self.Block(MergedElectricalSource())
    self.connect(self.diode1.cathode.as_electrical_source(
      voltage_out=(self.pwr_in1.link().voltage.lower() - self.diode1.voltage_drop.upper(),
                   self.pwr_in1.link().voltage.upper()),
      current_limits=(-float('inf'), float('inf'))
    ), self.merge.sink1)
    self.connect(self.diode2.cathode.as_electrical_source(
      voltage_out=(self.pwr_in2.link().voltage.lower() - self.diode2.voltage_drop.upper(),
                   self.pwr_in2.link().voltage.upper()),
      current_limits=(-float('inf'), float('inf'))
    ), self.merge.sink2)

    self.connect(self.diode1.anode.as_electrical_sink(
      voltage_limits=(-float('inf'), float('inf')),
      current_draw=self.pwr_out.link().current_drawn
    ), self.pwr_in1)
    self.connect(self.diode2.anode.as_electrical_sink(
      voltage_limits=(-float('inf'), float('inf')),
      current_draw=self.pwr_out.link().current_drawn
    ), self.pwr_in2)

    self.connect(self.merge.source, self.pwr_out)
