from typing import Optional, cast

from electronics_abstract_parts import *


class Supercap(DiscreteComponent, FootprintBlock):  # TODO actually model supercaps and parts selection
  def __init__(self) -> None:
    super().__init__()
    self.pos = self.Port(VoltageSink())
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
  def __init__(self, charging_current: RangeLike, sense_resistance: RangeLike,
               voltage_drop: RangeLike) -> None:
    super().__init__()

    self.charging_current = self.ArgParameter(charging_current)
    self.sense_resistance = self.ArgParameter(sense_resistance)
    self.voltage_drop = self.ArgParameter(voltage_drop)

    self.pwr = self.Port(VoltageSink.empty(), [Power, Input])
    self.pwr_out = self.Port(VoltageSource.empty(), [Output])
    self.require(self.pwr.current_draw.within(self.pwr_out.link().current_drawn +
                                              (0, self.charging_current.upper()) +
                                              (0, 0.05)))  # TODO nonhacky bounds on opamp/sense resistor current draw
    self.sc_out = self.Port(VoltageSource.empty(), optional=True)
    self.gnd = self.Port(Ground.empty(), [Common])

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
        power=(0, max_charge_current * max_charge_current * self.sense_resistance.upper())
      ))
      self.connect(self.pwr, self.sense.a.adapt_to(VoltageSink(
        current_draw=(0, max_charge_current)
      )))

      self.fet = self.Block(Fet.PFet(
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
      self.connect(self.diode.anode.adapt_to(VoltageSink()),
                   self.fet.drain.adapt_to(VoltageSource(
                     voltage_out=self.pwr.link().voltage)
                   ),
                   self.sc_out)

      self.pwr_out_merge = self.Block(MergedVoltageSource()).connected_from(
        self.pwr,
        self.diode.cathode.adapt_to(VoltageSource(
          voltage_out=(self.pwr.link().voltage.lower() - self.voltage_drop.upper(), self.pwr.link().voltage.upper())
        ))  # TODO replace with SeriesVoltageDiode or something that automatically calculates voltage drops?
      )
      self.connect(self.pwr_out_merge.pwr_out, self.pwr_out)

      # TODO check if this tolerance stackup is stacking in the right direction... it might not
      low_sense_volt_diff = self.charging_current.lower() * self.sense_resistance.lower()
      high_sense_volt_diff = self.charging_current.upper() * self.sense_resistance.upper()
      low_sense_volt = self.pwr.link().voltage.lower() - high_sense_volt_diff
      high_sense_volt = self.pwr.link().voltage.upper() - low_sense_volt_diff

      self.set = imp.Block(VoltageDivider(output_voltage=(low_sense_volt, high_sense_volt), impedance=(1, 10) * kOhm))
      self.connect(self.set.input, self.pwr)  # TODO use chain
      self.amp = imp.Block(Opamp())
      self.connect(self.set.output, self.amp.inp)
      self.connect(self.amp.inn, self.sense.b.adapt_to(AnalogSource(
        voltage_out=(0, self.pwr.link().voltage.upper()),
        # TODO calculate operating signal level
      )))
      self.connect(self.amp.out, self.fet.gate.adapt_to(AnalogSink()))

    self.cap = self.Block(Supercap())
    self.connect(self.sc_out, self.cap.pos)
    self.connect(self.gnd, self.cap.neg)


class SingleDiodePowerMerge(PowerConditioner, Block):
  """Single-diode power merge block for two voltage sources, where the lower voltage one is diode-gated and less
  preferred if both are connected.
  """
  @init_in_parent
  def __init__(self, voltage_drop: RangeLike, reverse_recovery_time: RangeLike = RangeExpr.ALL) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink.empty())  # high-priority source
    self.pwr_in_diode = self.Port(VoltageSink.empty())  # low-priority source
    self.pwr_out = self.Port(VoltageSource.empty())

    self.diode = self.Block(Diode(
      reverse_voltage=(0, self.pwr_in.link().voltage.upper() - self.pwr_in_diode.link().voltage.lower()),
      current=self.pwr_out.link().current_drawn,
      voltage_drop=voltage_drop,
      reverse_recovery_time=reverse_recovery_time,
    ))

    self.require(self.pwr_in_diode.link().voltage.upper() - self.diode.voltage_drop.lower() <= self.pwr_in.link().voltage.lower())

    self.connect(self.pwr_in_diode, self.diode.anode.adapt_to(VoltageSink(
      current_draw=self.pwr_out.link().current_drawn
    )))

    self.merge = self.Block(MergedVoltageSource()).connected_from(
      self.pwr_in,
      self.diode.cathode.adapt_to(VoltageSource(
        voltage_out=(self.pwr_in_diode.link().voltage.lower() - self.diode.voltage_drop.upper(),
                     self.pwr_in_diode.link().voltage.upper() - self.diode.voltage_drop.lower()),
        current_limits=(-float('inf'), float('inf'))
      ))
    )
    self.connect(self.merge.pwr_out, self.pwr_out)


class DiodePowerMerge(PowerConditioner, Block):
  """Diode power merge block for two voltage sources.
  """
  @init_in_parent
  def __init__(self, voltage_drop: RangeLike, reverse_recovery_time: RangeLike = (0, float('inf'))) -> None:
    super().__init__()

    self.pwr_in1 = self.Port(VoltageSink.empty())
    self.pwr_in2 = self.Port(VoltageSink.empty())
    self.pwr_out = self.Port(VoltageSource.empty())

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

    self.merge = self.Block(MergedVoltageSource()).connected_from(
      self.diode1.cathode.adapt_to(VoltageSource(
        voltage_out=(self.pwr_in1.link().voltage.lower() - self.diode1.voltage_drop.upper(),
                     self.pwr_in1.link().voltage.upper()),
        current_limits=(-float('inf'), float('inf'))
      )),
      self.diode2.cathode.adapt_to(VoltageSource(
        voltage_out=(self.pwr_in2.link().voltage.lower() - self.diode2.voltage_drop.upper(),
                     self.pwr_in2.link().voltage.upper()),
        current_limits=(-float('inf'), float('inf'))
      ))
    )
    self.connect(self.diode1.anode.adapt_to(VoltageSink(
      voltage_limits=(-float('inf'), float('inf')),
      current_draw=self.pwr_out.link().current_drawn
    )), self.pwr_in1)
    self.connect(self.diode2.anode.adapt_to(VoltageSink(
      voltage_limits=(-float('inf'), float('inf')),
      current_draw=self.pwr_out.link().current_drawn
    )), self.pwr_in2)

    self.connect(self.merge.pwr_out, self.pwr_out)


class PriorityPowerOr(PowerConditioner, KiCadSchematicBlock, Block):
  """Power merge block for two power inputs, where the high priority input (e.g. USB) is higher voltage and
  the low priority input is lower voltage (e.g. battery).
  The higher priority input incurs a diode drop, while the lower priority input has a FET.
  As a side effect, the FET power path also acts as reverse polarity protection.
  """
  @init_in_parent
  def __init__(self, diode_voltage_drop: RangeLike, fet_rds_on: RangeLike) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty())
    self.pwr_hi = self.Port(VoltageSink.empty())  # high-priority higher-voltage source
    self.pwr_lo = self.Port(VoltageSink.empty())  # low-priority lower-voltage source
    self.pwr_out = self.Port(VoltageSource.empty())

    self.diode_voltage_drop = self.ArgParameter(diode_voltage_drop)
    self.fet_rds_on = self.ArgParameter(fet_rds_on)

  def contents(self):
    super().contents()

    # FET behavior requires the high priority path to be higher voltage
    self.require(self.pwr_hi.link().voltage.lower() > self.pwr_lo.link().voltage.upper())

    output_current_draw = self.pwr_out.link().current_drawn
    self.pdr = self.Block(Resistor(10*kOhm(tol=0.01)))
    self.diode = self.Block(Diode(
      reverse_voltage=(0, self.pwr_lo.link().voltage.upper()),
      current=output_current_draw,
      voltage_drop=self.diode_voltage_drop,
    ))
    self.fet = self.Block(Fet.PFet(  # doesn't account for reverse protection
      drain_voltage=(0, self.pwr_hi.link().voltage.upper() - self.pwr_lo.link().voltage.lower()),
      drain_current=output_current_draw,
      # gate voltage accounts for a possible power on transient
      gate_voltage=(-self.pwr_hi.link().voltage.upper(), (self.pwr_hi.link().voltage.upper())),
      rds_on=self.fet_rds_on
    ))

    self.import_kicad(
      self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'pwr_hi': VoltageSink(
          current_draw=output_current_draw
        ),
        'pwr_lo': VoltageSink(
          current_draw=output_current_draw
        ),
        'pwr_out': VoltageSource(
          voltage_out=self.pwr_lo.link().voltage.hull(
            # use the spec voltage drop since using the actual voltage drop causes a circular dependency
            # (where current depends on voltage, but the diode voltage drop depends on the diode selection
            # which depends on the current through)
            self.pwr_hi.link().voltage - self.diode_voltage_drop),
        ),
        'gnd': Ground(),
      })

  def connected_from(self, gnd: Optional[Port[VoltageLink]] = None, pwr_hi: Optional[Port[VoltageLink]] = None,
                     pwr_lo: Optional[Port[VoltageLink]] = None) -> 'PriorityPowerOr':
    """Convenience function to connect ports, returning this object so it can still be given a name."""
    if gnd is not None:
      cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
    if pwr_hi is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_hi, self.pwr_hi)
    if pwr_lo is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_lo, self.pwr_lo)
    return self

class PmosReverseProtection(PowerConditioner, Block):
  """
  , here is a tradeoff between the Gate discharge time and Zener biasing.
  In most cases, 100R-330R is good if there are chances for the appearance of sudden reverse voltage in the circuit.
  But if there are no chances of sudden reverse voltage during the continuous working of the circuit, anything from the 1k-50k resistor value can be used.
  """
  @init_in_parent
  def __init__(self, clamp_voltage: RangeLike, gate_resistor: RangeLike):
    super().__init__()
    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr_in = self.Port(VoltageSink.empty())  # high-priority higher-voltage source
    self.pwr_out = self.Port(VoltageSource.empty())

    self.clamp_voltage = self.ArgParameter(clamp_voltage)
    self.gate_resistor = self.ArgParameter(gate_resistor)
    
  def contents(self):
    super().contents()

    output_current_draw = self.pwr_out.link().current_drawn

    self.fet = self.Block(Fet.PFet(  # doesn't account for reverse protection
      drain_voltage=(0, self.pwr_out.link().voltage.upper()),
      drain_current=output_current_draw,
      # gate voltage accounts for a possible power on transient
      gate_voltage=(self.clamp_voltage.upper(), (self.clamp_voltage.upper())),
    ))

    self.res = self.Block(Resistor(self.gate_resistor))
    self.diode = self.Block(ZenerDiode(self.clamp_voltage))
    self.connect(self.fet.gate, self.res.a)
    self.connect(self.gnd, self.res.b.adapt_to(Ground()))

    self.connect(self.pwr_in, self.fet.source.adapt_to(VoltageSink()))
    self.connect(self.pwr_out, self.fet.drain.adapt_to(VoltageSource()))
    self.connect(self.fet.drain, self.diode.cathode)
    self.connect(self.fet.gate, self.diode.anode)

