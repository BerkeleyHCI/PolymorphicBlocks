import unittest
from typing import Mapping, Dict

from edg.abstract_parts.ESeriesUtil import ESeriesRatioUtil
from edg.abstract_parts.ResistiveDivider import DividerValues
from edg.electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource  # needed by imported schematic
from edg.electronics_model.GroundPort import GroundAdapterAnalogSource  # needed by imported schematic
from edg import *


class SourceMeasureDutConnector(Connector):
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PinHeader254Horizontal(3))
    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()), [Common])
    self.io0 = self.Export(self.conn.pins.request('2').adapt_to(DigitalBidir()))
    self.io1 = self.Export(self.conn.pins.request('3').adapt_to(DigitalBidir()))


class SourceMeasureFan(Connector):
  def __init__(self):
    super().__init__()
    self.conn = self.Block(JstPhKVertical(2))
    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()), [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink(
      voltage_limits=5*Volt(tol=0.1),
      current_draw=200*mAmp(tol=0)
    )), [Power])


class SourceMeasureRangingCell(Interface, KiCadSchematicBlock):
  @init_in_parent
  def __init__(self, resistance: RangeLike):
    super().__init__()
    self.resistance = self.ArgParameter(resistance)
    self.actual_resistance = self.Parameter(RangeExpr())

    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr = self.Port(VoltageSink.empty(), [Power])

    self.pwr_in = self.Port(VoltageSink.empty())
    self.pwr_out = self.Port(VoltageSource.empty())

    self.control = self.Port(DigitalSink.empty())
    self.sense_in = self.Port(AnalogSource.empty())
    self.sense_out = self.Port(AnalogSource.empty())

  def contents(self):
    super().contents()
    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
                      locals={
                        'clamp': {
                          'clamp_current': (2.5, 25)*mAmp,
                          'clamp_target': (0, float('inf'))*Volt,
                          'zero_out': True
                        },
                        'resistance': self.resistance
                      })
    self.sense_sw: AnalogMuxer  # schematic-defined
    self.connect(self.control, self.sense_sw.control.request())
    self.isense: CurrentSenseResistor
    self.assign(self.actual_resistance, self.isense.actual_resistance)


class RangingCurrentSenseResistor(Interface, KiCadImportableBlock, GeneratorBlock):
  """Generates an array of current-sense resistors with one side muxed and the other end an array.
  The resistors are tied common on the com side, and have a solid-state relay for the power path
  on the input side. Each resistor has an analog switch on the input sense side.

  The control line is one bit for each range (range connectivity is independent).
  Multiple ranges can be connected simultaneously, this allows make-before-break connectivity."""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'edg_importable:CurrentSenseResistorMux'
    return {
      'control': self.control, 'sw': self.pwr_in, 'com': self.pwr_out,
      'sen_sw': self.sense_in, 'sen_com': self.sense_out,
      'V+': self.pwr,  'V-': self.gnd
    }

  @init_in_parent
  def __init__(self, resistances: ArrayRangeLike, currents: ArrayRangeLike):
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr = self.Port(VoltageSink.empty(), [Power])

    self.pwr_in = self.Port(VoltageSink.empty())
    self.pwr_out = self.Port(VoltageSource.empty())

    self.control = self.Port(Vector(DigitalSink.empty()))
    self.sense_in = self.Port(AnalogSource.empty())
    self.sense_out = self.Port(AnalogSource.empty())

    self.resistances = self.ArgParameter(resistances)
    self.currents = self.ArgParameter(currents)
    self.generator_param(self.resistances, self.currents)

    self.out_range = self.Parameter(RangeExpr())

  def generate(self):
    super().generate()
    self.ranges = ElementDict[SourceMeasureRangingCell]()

    self.forced = ElementDict[ForcedVoltageCurrentDraw]()
    self.pwr_out_merge = self.Block(MergedVoltageSource())
    self.connect(self.pwr_out_merge.pwr_out, self.pwr_out)
    self.sense_in_merge = self.Block(MergedAnalogSource())
    self.connect(self.sense_in_merge.output, self.sense_in)
    self.sense_out_merge = self.Block(MergedAnalogSource())
    self.connect(self.sense_out_merge.output, self.sense_out)

    out_range = RangeExpr._to_expr_type(RangeExpr.EMPTY)

    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
            ImplicitConnect(self.pwr, [Power])
    ) as imp:
      for i, (resistance, current) in enumerate(zip(self.get(self.resistances), self.get(self.currents))):
        range = self.ranges[i] = imp.Block(SourceMeasureRangingCell(resistance))
        self.connect(self.pwr_in, range.pwr_in)
        forced = self.forced[i] = self.Block(ForcedVoltageCurrentDraw(current))
        self.connect(range.pwr_out, forced.pwr_in)
        self.connect(self.pwr_out_merge.pwr_ins.request(str(i)), forced.pwr_out)

        self.connect(range.control, self.control.append_elt(DigitalSink.empty(), str(i)))
        self.connect(self.sense_in_merge.inputs.request(str(i)), range.sense_in)
        self.connect(self.sense_out_merge.inputs.request(str(i)), range.sense_out)

        out_range = out_range.hull(current * range.actual_resistance)

    self.assign(self.out_range, out_range)


class EmitterFollower(InternalSubcircuit, KiCadSchematicBlock, KiCadImportableBlock, Block):
  """Emitter follower circuit.
  """
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name == 'edg_importable:Follower'  # this requires an schematic-modified symbol
    return {
      '1': self.control, '3': self.out, 'V+': self.pwr, 'V-': self.gnd,
      'HG': self.high_gate_ctl, 'LG': self.low_gate_ctl,
      'VG+': self.pwr_gate_pos, 'VG-': self.pwr_gate_neg
    }

  @init_in_parent
  def __init__(self, current: RangeLike, rds_on: RangeLike, gate_clamp_voltage: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr_gate_pos = self.Port(VoltageSink.empty())
    self.pwr_gate_neg = self.Port(Ground.empty())
    self.out = self.Port(VoltageSource.empty())

    self.control = self.Port(AnalogSink.empty())
    self.high_gate_ctl = self.Port(DigitalSink.empty())
    self.low_gate_ctl = self.Port(DigitalSink.empty())

    self.current = self.ArgParameter(current)
    self.rds_on = self.ArgParameter(rds_on)
    self.gate_clamp_voltage = self.ArgParameter(gate_clamp_voltage)

  def contents(self) -> None:
    super().contents()

    zener_model = ZenerDiode(self.gate_clamp_voltage)
    self.clamp1 = self.Block(zener_model)
    self.clamp2 = self.Block(zener_model)

    gate_voltage = (-self.clamp1.actual_zener_voltage).hull(self.clamp2.actual_zener_voltage)
    self.high_fet = self.Block(Fet.NFet(
      drain_voltage=self.pwr.link().voltage,
      drain_current=self.current,
      gate_voltage=gate_voltage,
      rds_on=self.rds_on,
      gate_charge=RangeExpr.ALL,  # don't care, it's analog not switching
      power=self.pwr.link().voltage * self.current))
    self.low_fet = self.Block(Fet.PFet(
      drain_voltage=self.pwr.link().voltage,
      drain_current=self.current,
      gate_voltage=gate_voltage,
      rds_on=self.rds_on,
      gate_charge=RangeExpr.ALL,  # don't care, it's analog not switching
      power=self.pwr.link().voltage * self.current))
    resistance = 2.2*kOhm(tol=0.05)
    max_clamp_voltage = VoltageLink._supply_voltage_range(self.gnd, self.pwr).upper() - self.gate_clamp_voltage.lower()
    self.res = self.Block(Resistor(
      resistance=resistance,
      power=(0, max_clamp_voltage * max_clamp_voltage / resistance.lower()),
      voltage=(0, max_clamp_voltage)
    ))

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'low_fet.D': Ground(),
        'high_fet.D': VoltageSink(
          current_draw=self.current,
          voltage_limits=self.high_fet.actual_drain_voltage_rating.intersect(
            self.low_fet.actual_drain_voltage_rating)
        ),
        'out': VoltageSource(
          voltage_out=self.pwr.link().voltage,
          current_limits=self.high_fet.actual_drain_current_rating.intersect(self.low_fet.actual_drain_current_rating)
        ),
        'control': AnalogSink(),

        # TODO FIXME
        'res.2': AnalogSource(),
        'clamp1.A': AnalogSink(),
        'low_res.1': AnalogSink(),
        'low_fet.G': AnalogSink(),
        'high_res.1': AnalogSink(),
        'high_fet.G': AnalogSink(),
      })

    self.high_gate: AnalogMuxer  # defined in schematic
    self.connect(self.high_gate_ctl, self.high_gate.control.request())
    self.low_gate: AnalogMuxer
    self.connect(self.low_gate_ctl, self.low_gate.control.request())
    self.connect(self.gnd, self.high_gate.control_gnd, self.low_gate.control_gnd)


class GatedSummingAmplifier(InternalSubcircuit, KiCadSchematicBlock, KiCadImportableBlock, GeneratorBlock):
  """A noninverting summing amplifier with an optional diode gate (enforcing drive direction) and inline resistance
  (to allow its output to be overridden by a stronger driver).

  Used as the error amplifier in SMU analog control block, the target is set with inverted polarity
  (around the integrator reference). When the measured signal is at the target, the output (sum)
  is the integrator reference, producing zero error. Otherwise, the error signal is proportional to the deviation.

  The sense_out line is upstream of this element and can be used to determine if a current limit amplifier is active.

  TODO: diode parameter should be an enum. Current values: '' (no diode), 'sink', 'source' (sinks or sources current)
  """
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name in ('Simulation_SPICE:OPAMP', 'edg_importable:Opamp')
    return {'M': self.actual, 'T': self.target, 'F': self.target_fine, '3': self.output, 'S': self.sense_out,
            'V+': self.pwr, 'V-': self.gnd}

  @init_in_parent
  def __init__(self, input_resistance: RangeLike = 0*Ohm(tol=0), *,
               dir: StringLike = '', res: RangeLike = 0*Ohm(tol=0), fine_scale: FloatLike = 0,
               series: IntLike = 24, tolerance: FloatLike = 0.01):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.target = self.Port(AnalogSink.empty())
    self.target_fine = self.Port(AnalogSink.empty(), optional=True)
    self.actual = self.Port(AnalogSink.empty())
    self.output = self.Port(AnalogSource.empty())
    self.sense_out = self.Port(AnalogSource.empty(), optional=True)

    self.input_resistance = self.ArgParameter(input_resistance)
    self.dir = self.ArgParameter(dir)
    self.res = self.ArgParameter(res)  # output side
    self.fine_scale = self.ArgParameter(fine_scale)
    self.series = self.ArgParameter(series)
    self.tolerance = self.ArgParameter(tolerance)
    self.generator_param(self.input_resistance, self.res, self.dir, self.series, self.tolerance,
                         self.target_fine.is_connected(), self.sense_out.is_connected(), self.fine_scale)

  def generate(self) -> None:
    super().generate()

    # The 1/4 factor is a way to specify the series resistance of the divider assuming both resistors are equal,
    # since the DividerValues util only takes the parallel resistance
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[self.get(self.series)], self.get(self.tolerance), DividerValues)
    top_resistance, bottom_resistance = calculator.find(DividerValues(Range.from_tolerance(0.5, self.get(self.tolerance)),
                                                                      self.get(self.input_resistance) / 4))

    self.amp = self.Block(Opamp())
    self.rtop = self.Block(Resistor(resistance=Range.from_tolerance(top_resistance, self.get(self.tolerance))))
    self.rbot = self.Block(Resistor(resistance=Range.from_tolerance(bottom_resistance, self.get(self.tolerance))))

    output_impedance = self.amp.out.link().source_impedance
    dir = self.get(self.dir)
    if dir:
      self.diode = self.Block(Diode(  # TODO should be encoded as a voltage difference?
        reverse_voltage=self.amp.out.voltage_out,
        current=RangeExpr.ZERO,  # an approximation, current rating not significant here
        voltage_drop=(0, 0.5)*Volt  # arbitrary low threshold
      ))
      amp_out_model = AnalogSink(
        impedance=self.output.link().sink_impedance
      )
      if dir == 'source':
        self.connect(self.amp.out, self.diode.anode.adapt_to(amp_out_model))
        amp_out_node = self.diode.cathode
      elif dir == 'sink':
        self.connect(self.amp.out, self.diode.cathode.adapt_to(amp_out_model))
        amp_out_node = self.diode.anode
      else:
        raise ValueError(f"invalid dir '{dir}', expected '', 'source', or 'sink'")

    if self.get(self.res) != Range.exact(0):  # if resistor requested
      assert not dir, "diode + output resistance not supported"
      self.rout = self.Block(Resistor(resistance=self.res))
      self.connect(self.amp.out, self.rout.a.adapt_to(AnalogSink(
        impedance=self.rout.actual_resistance + self.output.link().sink_impedance
      )))
      amp_out_node = self.rout.b
      output_impedance += self.rout.actual_resistance

    self.connect(amp_out_node.adapt_to(AnalogSource(
      impedance=output_impedance
    )), self.output)

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
        conversions={
          'target': AnalogSink(
            impedance=self.rtop.actual_resistance + self.rbot.actual_resistance  # assumed dominates fine resistance
          ),
          'actual': AnalogSink(
            impedance=self.rtop.actual_resistance + self.rbot.actual_resistance
          ),
          'rtop.2': AnalogSource(
            voltage_out=self.target.link().voltage.hull(self.actual.link().voltage),
            signal_out=self.target.link().voltage.hull(self.actual.link().voltage),
            impedance=1 / (1 / self.rtop.actual_resistance + 1 / self.rbot.actual_resistance)
          ),
          'rbot.2': AnalogSink(),  # ideal, rtop.2 contains the parameter model
        })

    if self.get(self.target_fine.is_connected()):
      assert self.get(self.fine_scale) != 0
      self.rfine = self.Block(Resistor(resistance=Range.from_tolerance(top_resistance * self.get(self.fine_scale),
                                                                       self.get(self.tolerance))))
      self.connect(self.target_fine, self.rfine.a.adapt_to(AnalogSink(
        impedance=self.rfine.actual_resistance  # assumed non-fine resistance dominates
      )))
      self.connect(self.rfine.b.adapt_to(AnalogSink()), self.amp.inp)

    if self.get(self.sense_out.is_connected()):
      self.connect(self.amp.out, self.sense_out)


class JfetCurrentClamp(InternalSubcircuit, KiCadSchematicBlock, KiCadImportableBlock, Block):
  """JET-based current clamp, clamps to roughly 10mA while maintaining a relatively low non-clamping
  impedance of ~100ohm. Max ~35V limited by JFET Vgs,max.
  """
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name == 'edg_importable:Unk2'
    return {'1': self.input, '2': self.output}

  @init_in_parent
  def __init__(self, model_voltage_clamp: RangeLike, model_signal_clamp: RangeLike = RangeExpr.ALL):
    super().__init__()

    self.model_voltage_clamp = self.ArgParameter(model_voltage_clamp)
    self.model_signal_clamp = self.ArgParameter(model_signal_clamp)

    self.input = self.Port(AnalogSink.empty(), [Power])
    self.output = self.Port(AnalogSource.empty(), [Common])

  def contents(self) -> None:
    super().contents()

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
                      conversions={
                        'input': AnalogSink(current_draw=self.output.link().current_drawn,
                                            impedance=self.output.link().sink_impedance),
                        'output': AnalogSource(voltage_out=self.input.link().voltage.intersect(
                                                               self.model_voltage_clamp),
                                               signal_out=self.input.link().signal.intersect(
                                                              self.model_signal_clamp),
                                               impedance=self.input.link().source_impedance)
                      })


class SrLatchInverted(Block):
  """Set-reset latch with active-high set, active-high reset, set priority, and low output when set (high when idle).
  This uses two NOR gates.
  NOR1 handles set with priority, when any input is high, the output goes low.
  Latching is done when NOR1 is low, which feeds into NOR2. If reset isn't asserted, both NOR2 inputs are low
  and NOR2 output is high, which feeds back into a NOR1 input to keep NOR1 low.
  NOR2 handles reset without priority, when the input goes high, its output goes low which clears the latch.
  """
  def __init__(self):
    super().__init__()
    self.ic = self.Block(Sn74lvc2g02())
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.pwr = self.Export(self.ic.pwr, [Power])

    self.set = self.Export(self.ic.in1a)  # any in1
    self.rst = self.Export(self.ic.in2a)  # any in2
    self.out = self.Export(self.ic.out1)

  def contents(self):
    super().contents()
    self.connect(self.ic.out1, self.ic.in2b)
    self.connect(self.ic.out2, self.ic.in1b)


class SourceMeasureControl(InternalSubcircuit, KiCadSchematicBlock, Block):
  """Analog feedback circuit for the source-measure unit
  """
  @init_in_parent
  def __init__(self, current: RangeLike, rds_on: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.pwr_logic = self.Port(VoltageSink.empty())
    self.gnd = self.Port(Ground.empty(), [Common])
    self.ref_center = self.Port(AnalogSink.empty())

    self.pwr_gate_pos = self.Port(VoltageSink.empty())
    self.pwr_gate_neg = self.Port(Ground.empty())

    self.control_voltage = self.Port(AnalogSink.empty())
    self.control_voltage_fine = self.Port(AnalogSink.empty())
    self.control_current_source = self.Port(AnalogSink.empty())
    self.control_current_sink = self.Port(AnalogSink.empty())
    self.high_gate_ctl = self.Port(DigitalSink.empty())
    self.low_gate_ctl = self.Port(DigitalSink.empty())
    self.irange = self.Port(Vector(DigitalSink.empty()))
    self.off = self.Port(Vector(DigitalSink.empty()))
    self.out = self.Port(VoltageSource.empty())

    self.measured_voltage = self.Port(AnalogSource.empty())
    self.measured_current = self.Port(AnalogSource.empty())
    self.limit_source = self.Port(DigitalSource.empty())
    self.limit_sink = self.Port(DigitalSource.empty())

    self.tp_err = self.Port(AnalogSource.empty(), optional=True)
    self.tp_int = self.Port(AnalogSource.empty(), optional=True)

    self.current = self.ArgParameter(current)
    self.rds_on = self.ArgParameter(rds_on)

  def contents(self):
    super().contents()

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      locals={
        'self': self
      }, conversions={
        'tvs_p.K': VoltageSink(),
        'tvs_n.K': Ground(),
      })


class UsbSourceMeasure(JlcBoardTop):
  def contents(self) -> None:
    super().contents()

    # overall design parameters
    OUTPUT_CURRENT_RATING = (0, 3)*Amp

    # USB PD port that supplies power to the load
    # TODO the transistor is only rated at Vgs=+/-20V
    # USB PD can't actually do 8 A, but this suppresses the error and we can software-limit current draw
    self.usb = self.Block(UsbCReceptacle(voltage_out=(9, 20)*Volt, current_limits=(0, 8)*Amp))

    self.gnd = self.connect(self.usb.gnd)
    self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)

    # power supplies
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.vusb_sense = imp.Block(Ina219(10*mOhm(tol=0.01)))

      # input filtering
      (self.fuse_vusb, self.filt_vusb, self.prot_vusb), _ = self.chain(
        self.usb.pwr,
        self.Block(SeriesPowerFuse(trip_current=(7, 8)*Amp)),
        self.Block(SeriesPowerFerriteBead()),
        imp.Block(ProtectionZenerDiode(voltage=(32, 38)*Volt)),  # for parts commonality w/ the Vconv zener
        self.vusb_sense.sense_pos
      )
      self.vusb = self.connect(self.vusb_sense.sense_neg)
      self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.vusb)

      # logic supplies
      (self.reg_v5, self.tp_v5), _ = self.chain(
        self.vusb,
        imp.Block(BuckConverter(output_voltage=5.0*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
      )
      self.v5 = self.connect(self.reg_v5.pwr_out)
      (self.reg_3v3, self.prot_3v3, self.tp_3v3), _ = self.chain(
        self.vusb,
        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(ProtectionZenerDiode(voltage=(3.6, 4.5)*Volt)),
        self.Block(VoltageTestPoint())
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      # output power supplies
      self.connect(self.vusb_sense.pwr, self.v3v3)

      self.convin_sense = imp.Block(Ina219(10*mOhm(tol=0.01), addr_lsb=4))
      self.connect(self.convin_sense.pwr, self.v3v3)
      (self.conv_inforce, self.ramp), _ = self.chain(
        self.vusb,
        imp.Block(ForcedVoltage(20*Volt(tol=0))),
        imp.Block(RampLimiter()),  # avoid excess capacitance on VBus which may cause the PD source to reset
        self.convin_sense.sense_pos
      )
      self.vusb_pre = self.connect(self.convin_sense.sense_neg)  # vusb post-ramp

      (self.cap_conv, self.conv, self.conv_outforce, self.prot_conv, self.tp_conv), _ = self.chain(
        self.vusb_pre,
        imp.Block(DecouplingCapacitor(100*uFarad(tol=0.25))),
        imp.Block(CustomSyncBuckBoostConverterPwm(output_voltage=(15, 30)*Volt,  # design for 0.5x - 1.5x conv ratio
                                                  frequency=500*kHertz(tol=0),
                                                  ripple_ratio=(0.01, 0.9),
                                                  input_ripple_limit=100*mVolt,
                                                  output_ripple_limit=(25*(7/8))*mVolt  # fill out the row of caps
                                                  )),
        imp.Block(ForcedVoltage((2, 30)*Volt)),  # at least 2v to allow current sensor to work
        imp.Block(ProtectionZenerDiode(voltage=(32, 38)*Volt)),  # zener shunt in case the boost converter goes crazy
        self.Block(VoltageTestPoint())
      )
      self.connect(self.conv.pwr_logic, self.v5)
      self.vconv = self.connect(self.conv_outforce.pwr_out)

      (self.reg_v12, ), _ = self.chain(
        self.v5,
        imp.Block(BoostConverter(output_voltage=12.5*Volt(tol=0.04))),  # limits of the OLED
      )
      self.v12 = self.connect(self.reg_v12.pwr_out)

      # analog supplies
      (self.reg_analog, self.tp_analog), _ = self.chain(
        self.v5,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint())
      )
      self.vanalog = self.connect(self.reg_analog.pwr_out)

      (self.reg_vref, self.tp_vref), _ = self.chain(
        self.v5,
        imp.Block(VoltageReference(output_voltage=3.3*Volt(tol=0.01))),
        self.Block(VoltageTestPoint())
      )
      self.vref = self.connect(self.reg_vref.pwr_out)

      (self.ref_div, self.ref_buf, self.ref_rc), _ = self.chain(
        self.vref,
        imp.Block(VoltageDivider(output_voltage=1.65*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower()),
        # opamp outputs generally not stable under capacitive loading and requires an isolation series resistor
        # 4.7 tries to balance low output impedance and some level of isolation
        imp.Block(AnalogLowPassRc(4.7*Ohm(tol=0.05), 1*MHertz(tol=0.25))),
      )
      self.connect(self.vanalog, self.ref_buf.pwr)
      self.vcenter = self.connect(self.ref_rc.output)

      (self.reg_vcontrol, self.tp_vcontrol), _ = self.chain(
        self.v5,
        imp.Block(BoostConverter(output_voltage=(30, 33)*Volt,  # up to but not greater
                                 output_ripple_limit=1*mVolt)),
        self.Block(VoltageTestPoint("vc+"))
      )
      self.vcontrol = self.connect(self.reg_vcontrol.pwr_out)

      (self.filt_vcontroln, self.reg_vcontroln, self.tp_vcontroln), _ = self.chain(
        self.vanalog,
        self.Block(SeriesPowerFerriteBead()),
        imp.Block(Lm2664(output_ripple_limit=5*mVolt)),
        self.Block(VoltageTestPoint("vc-"))
      )
      self.vcontroln = self.connect(self.reg_vcontroln.pwr_out.as_ground(
        current_draw=self.reg_vcontrol.pwr_out.link().current_drawn))

    # power path domain
    with self.implicit_connect(
        ImplicitConnect(self.vconv, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.control = imp.Block(SourceMeasureControl(
        current=OUTPUT_CURRENT_RATING,
        rds_on=(0, 0.2)*Ohm
      ))
      self.connect(self.vanalog, self.control.pwr_logic)
      self.connect(self.vcenter, self.control.ref_center)

      self.connect(self.vcontroln, self.control.pwr_gate_neg)
      self.connect(self.vcontrol, self.control.pwr_gate_pos)

      (self.tp_err, ), _ = self.chain(self.control.tp_err, imp.Block(AnalogCoaxTestPoint('err')))
      (self.tp_int, ), _ = self.chain(self.control.tp_int, imp.Block(AnalogCoaxTestPoint('int')))

    # logic domain
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      # TODO next revision: optional clamping diode on CC lines (as present in PD buddy sink, but not OtterPill)
      self.pd = imp.Block(Fusb302b())
      self.connect(self.vusb, self.pd.vbus)
      self.connect(self.usb.cc, self.pd.cc)

      self.mcu = imp.Block(IoController())
      (self.led, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('led'))  # debugging LED

      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.usb.request())

      int_i2c = self.mcu.i2c.request('int_i2c')
      self.i2c_tp = self.Block(I2cTestPoint('i2c')).connected(int_i2c)
      (self.i2c_pull, ), _ = self.chain(int_i2c, imp.Block(I2cPullup()))
      self.connect(int_i2c, self.pd.i2c, self.vusb_sense.i2c, self.convin_sense.i2c)
      self.connect(self.mcu.gpio.request('pd_int'), self.pd.int)

      self.oled = imp.Block(Er_Oled022_1())  # (probably) pin compatible w/ 2.4" ER-OLED024-2B; maybe ER-OLED015-2B
      self.connect(self.oled.vcc, self.v12)
      self.connect(self.oled.pwr, self.v3v3)
      self.oled_rc = imp.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10*mSecond(tol=0.2))).connected(io=self.oled.reset)
      self.connect(int_i2c, self.oled.i2c)
      # self.connect(self.mcu.spi.request('oled_spi'), self.oled.spi)
      # self.connect(self.mcu.gpio.request('oled_cs'), self.oled.cs)
      # self.connect(self.mcu.gpio.request('oled_dc'), self.oled.dc)

      # expander for low-speed control signals
      self.ioe_ctl = imp.Block(Pca9554())
      self.connect(self.ioe_ctl.i2c, int_i2c)
      self.connect(self.ioe_ctl.io.request('high_gate_ctl'), self.control.high_gate_ctl)
      self.connect(self.ioe_ctl.io.request('low_gate_ctl'), self.control.low_gate_ctl)
      self.connect(self.ioe_ctl.io.request_vector('off'), self.control.off)
      self.connect(self.ioe_ctl.io.request('ramp'), self.ramp.control)

      rc_model = DigitalLowPassRc(150*Ohm(tol=0.05), 7*MHertz(tol=0.2))
      (self.buck_rc, ), _ = self.chain(self.mcu.gpio.request('buck_pwm'), imp.Block(rc_model), self.conv.buck_pwm)
      (self.boost_rc, ), _ = self.chain(self.mcu.gpio.request('boost_pwm'), imp.Block(rc_model), self.conv.boost_pwm)

      (self.conv_ovp, ), _ = self.chain(self.conv_outforce.pwr_out.as_analog_source(),
                                        imp.Block(VoltageComparator(trip_voltage=(32, 36)*Volt)))
      self.connect(self.conv_ovp.ref, self.vcenter)

      self.conv_latch = imp.Block(SrLatchInverted())
      (self.conv_en_pull, ), _ = self.chain(
        self.ioe_ctl.io.request('conv_en'),
        imp.Block(PulldownResistor(10*kOhm(tol=0.05))),
        self.conv_latch.rst
      )
      (self.comp_pull, ), _ = self.chain(
        self.conv_ovp.output, imp.Block(PullupResistor(resistance=10*kOhm(tol=0.05))),
        self.conv_latch.set
      )
      self.connect(self.conv_latch.out, self.conv.reset, self.ioe_ctl.io.request('conv_en_sense'))

      (self.pass_temp, ), _ = self.chain(int_i2c, imp.Block(Tmp1075n(0)))
      (self.conv_temp, ), _ = self.chain(int_i2c, imp.Block(Tmp1075n(1)))
      (self.conv_sense, ), _ = self.chain(
        self.vconv,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vconv_sense')
      )

      # expander and interface elements
      self.ioe_ui = imp.Block(Pca9554(addr_lsb=2))
      self.connect(self.ioe_ui.i2c, int_i2c)
      self.enc = imp.Block(DigitalRotaryEncoder())
      self.connect(self.enc.a, self.mcu.gpio.request('enc_a'))
      self.connect(self.enc.b, self.mcu.gpio.request('enc_b'))
      self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request('enc_sw'))
      self.dir = imp.Block(DigitalDirectionSwitch())
      self.connect(self.dir.a, self.ioe_ui.io.request('dir_a'))
      self.connect(self.dir.b, self.ioe_ui.io.request('dir_b'))
      self.connect(self.dir.c, self.ioe_ui.io.request('dir_c'))
      self.connect(self.dir.d, self.ioe_ui.io.request('dir_d'))
      self.connect(self.dir.with_mixin(DigitalDirectionSwitchCenter()).center, self.ioe_ui.io.request('dir_cen'))
      self.connect(self.ioe_ui.io.request_vector('irange'), self.control.irange)

      # expansion ports
      (self.qwiic_pull, self.qwiic, ), _ = self.chain(self.mcu.i2c.request('qwiic'),
                                                      imp.Block(I2cPullup()),
                                                      imp.Block(QwiicTarget()))

      self.dutio = imp.Block(SourceMeasureDutConnector())
      self.connect(self.mcu.gpio.request('dut0'), self.dutio.io0)
      self.connect(self.mcu.gpio.request('dut1'), self.dutio.io1)

      mcu_touch = self.mcu.with_mixin(IoControllerTouchDriver())
      (self.touch_duck, ), _ = self.chain(
        mcu_touch.touch.request('touch_duck'),
        imp.Block(FootprintToucbPad('edg:Symbol_DucklingSolid'))
      )

    # 5v domain
    with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.rgbs = imp.Block(NeopixelArray(4+1+1))  # 4 for encoder, 1 for output, 1 for USB
      (self.rgb_shift, ), _ = self.chain(
        self.mcu.gpio.request('rgb'),
        imp.Block(L74Ahct1g125()),
        self.rgbs.din)

      self.fan_drv = imp.Block(HighSideSwitch())
      self.connect(self.mcu.gpio.request('fan'), self.fan_drv.control)
      self.fan = self.Block(SourceMeasureFan())
      self.connect(self.fan.gnd, self.gnd)
      self.connect(self.fan.pwr, self.fan_drv.output)

      (self.spk_drv, self.spk), _ = self.chain(
        self.mcu.with_mixin(IoControllerI2s()).i2s.request('speaker'),
        imp.Block(Max98357a()),
        self.Block(Speaker())
      )

    # analog domain
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.dac = imp.Block(Mcp4728())
      (self.dac_ferrite, ), _ = self.chain(
        self.vref,
        imp.Block(SeriesPowerFerriteBead(Range.from_lower(1000))),
        self.dac.pwr)
      self.connect(self.dac.out0, self.control.control_voltage)
      self.connect(self.dac.out3, self.control.control_voltage_fine)
      self.connect(self.dac.out1, self.control.control_current_sink)
      self.connect(self.dac.out2, self.control.control_current_source)
      self.connect(self.dac.i2c, int_i2c)

      self.adc = imp.Block(Mcp3561())
      self.connect(self.adc.pwra, self.vanalog)
      self.connect(self.adc.pwr, self.v3v3)
      self.connect(self.adc.vref, self.vref)
      self.connect(self.adc.spi, self.mcu.spi.request('adc_spi'))
      self.connect(self.adc.cs, self.mcu.gpio.request('adc_cs'))
      self.connect(self.adc.mclkin, self.mcu.gpio.request('adc_clk'))  # up to 20MHz output from LEDC peripheral
      (self.tp_vcen, self.vcen_rc, ), _ = self.chain(self.vcenter,
                                                     imp.Block(AnalogCoaxTestPoint('cen')),
                                                     imp.Block(AnalogLowPassRc(1*kOhm(tol=0.05), 16*kHertz(tol=0.25))),
                                                     self.adc.vins.request('0'))
      (self.tp_mi, self.mi_rc, ), _ = self.chain(self.control.measured_current,
                                                 imp.Block(AnalogCoaxTestPoint('mi')),
                                                 imp.Block(AnalogLowPassRc(1*kOhm(tol=0.05), 16*kHertz(tol=0.25))),
                                                 self.adc.vins.request('1'))
      (self.tp_mv, self.mv_rc, ), _ = self.chain(self.control.measured_voltage,
                                                 imp.Block(AnalogCoaxTestPoint('mv')),
                                                 imp.Block(AnalogLowPassRc(1*kOhm(tol=0.05), 16*kHertz(tol=0.25))),
                                                 self.adc.vins.request('2'))
      self.connect(self.control.limit_source, self.mcu.gpio.request('limit_source'))
      self.connect(self.control.limit_sink, self.mcu.gpio.request('limit_sink'))

    self.outn = self.Block(BananaSafetyJack())
    self.outp = self.Block(BananaSafetyJack())
    self.outd = self.Block(PinHeader254Horizontal(2))  # 2.54 output option
    self.connect(self.gnd, self.outn.port.adapt_to(Ground()), self.outd.pins.request('1').adapt_to(Ground()))
    self.connect(
      self.control.out,
      self.outp.port.adapt_to(VoltageSink(current_draw=OUTPUT_CURRENT_RATING)),
      self.outd.pins.request('2').adapt_to(VoltageSink())
    )

    self._block_diagram_grouping = self.Metadata({
      'pwr': 'usb, filt_vusb, fuse_vusb, prot_vusb, pd, vusb_sense, reg_v5, reg_3v3, prot_3v3',
      'conv': 'conv_inforce, ramp, convin_sense, cap_conv, conv, conv_outforce, conv_sense, prot_conv, '
              'conv_en_pull, conv_latch, conv_ovp, comp_pull, buck_rc, boost_rc',
      'analog': 'reg_analog, reg_vcontrol, reg_vcontroln, reg_vref, ref_div, ref_buf, ref_cap, vcen_rc, '
                'dac_ferrite, dac, mv_rc, mi_rc, adc, control, '
                'outn, outp, outd',
      'mcu': 'mcu, led, touch_duck, ioe_ctl, usb_esd, i2c_pull, qwiic_pull, qwiic, dutio',
      'sensing': 'conv_temp, pass_temp',
      'ui': 'ioe_ui, enc, dir, rgb, reg_v12, oled, oled_rc, spk_drv, spk',
      'tp': 'tp_vusb, tp_gnd, tp_3v3, tp_v5, tp_v12, tp_conv, tp_analog, tp_vcontrol, tp_vcontroln, tp_vref, tp_lsrc, tp_lsnk, '
            'i2c_tp',
      'rf_tp': 'tp_vcen, tp_cv, tp_cvf, tp_cisrc, tp_cisnk, tp_mv, tp_mi',
      'packed_amps': 'vimeas_amps, ampdmeas_amps, cv_amps, ci_amps, cintref_amps',
      'misc': 'fan_drv, fan, jlc_th',
    })

  def multipack(self) -> None:
    self.vimeas_amps = self.PackedBlock(Opa2189())  # low noise opamp
    self.pack(self.vimeas_amps.elements.request('0'), ['control', 'amp', 'amp'])
    self.pack(self.vimeas_amps.elements.request('1'), ['control', 'hvbuf', 'amp'])

    self.cv_amps = self.PackedBlock(Tlv9152())
    self.pack(self.cv_amps.elements.request('0'), ['ref_buf', 'amp'])  # place the reference more centrally
    self.pack(self.cv_amps.elements.request('1'), ['control', 'err_volt', 'amp'])

    self.ci_amps = self.PackedBlock(Tlv9152())
    self.pack(self.ci_amps.elements.request('0'), ['control', 'err_sink', 'amp'])
    self.pack(self.ci_amps.elements.request('1'), ['control', 'err_source', 'amp'])

    self.cintref_amps = self.PackedBlock(Tlv9152())
    self.pack(self.cintref_amps.elements.request('0'), ['control', 'int', 'amp'])
    self.pack(self.cintref_amps.elements.request('1'), ['control', 'dmeas', 'amp'])  # this path matters much less

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_v5'], Tps54202h),
        (['reg_3v3'], Tps54202h),
        (['reg_v12'], Lm2733),
        (['reg_analog'], Ap2210),
        (['reg_vref'], Ref30xx),
        (['reg_vcontrol'], Lm2733),

        (['control', 'driver', 'low_fet'], CustomFet),
        (['control', 'driver', 'high_fet'], CustomFet),

        (['control', 'off_sw', 'device'], Nlas4157),  # 3v3 compatible unlike DG468

        (['cap_vusb', 'cap'], JlcAluminumCapacitor),
        (['cap_conv', 'cap'], JlcAluminumCapacitor),
        (['control', 'driver', 'cap_in1', 'cap'], JlcAluminumCapacitor),

        (['spk', 'conn'], JstPhKVertical),

        (['control', 'isense', 'ranges[0]', 'pwr_sw', 'ic'], Tlp3545a),  # higher current on 3A range
        (['control', 'driver', 'res'], SeriesResistor),  # needed for high power within a basic part
        (['oled', 'device', 'conn'], Fpc050BottomFlip),  # more compact connector, double-fold the FPC ribbon
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TagConnect, TagConnectNonLegged),  # really for initial flash / emergency upload only
        (Opamp, Tlv9061),  # higher precision opamps
        (AnalogSwitch, Dg468),
        (SolidStateRelay, Tlp170am),
        (BananaSafetyJack, Ct3151),
        (HalfBridgeDriver, Ncp3420),
        (DirectionSwitch, Skrh),
        (TestPoint, CompactKeystone5015),
        (RotaryEncoder, Pec11s),
        (Neopixel, Sk6805_Ec15),
        (RfConnector, UflConnector),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'enc_a=5',
          'enc_b=6',
          'enc_sw=4',

          'dut0=15',
          'dut1=17',

          'adc_cs=7',
          'adc_spi.sck=8',
          'adc_spi.mosi=9',
          'adc_spi.miso=10',

          # 'irange_0=12',
          # 'irange_1=11',
          # 'off_0=31',

          'buck_pwm=35',
          'boost_pwm=32',
          'vconv_sense=18',  # needs ADC

          'int_i2c.scl=39',
          'int_i2c.sda=38',

          'qwiic.scl=24',
          'qwiic.sda=25',
          'pd_int=21',
          'fan=19',
          'touch_duck=22',
          # 'conv_en_sense=23',

          'led=_GPIO0_STRAP',

        ]),
        (['mcu', 'programming'], 'uart-auto'),

        (['ioe', 'pin_assigns'], [
          'dir_c=9',
          'dir_cen=4',
          'dir_a=5',
          'dir_b=6',
          'dir_d=7',
        ]),

        # allow the regulator to go into tracking mode
        (['reg_v5', 'power_path', 'dutycycle_limit'], Range(0, float('inf'))),
        (['reg_v5', 'power_path', 'inductor_current_ripple'], Range(0.01, 0.5)),  # trade higher Imax for lower L
        # use the same inductor to reduce line items
        (['reg_3v3', 'power_path', 'inductor', 'part'], ParamValue(['reg_v5', 'power_path', 'inductor', 'actual_part'])),
        # JLC does not have frequency specs, must be checked TODO
        (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['reg_v5', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['reg_v12', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['conv', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['reg_vcontrol', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['vusb_sense', 'Rs', 'res', 'res', 'footprint_spec'], "Resistor_SMD:R_1206_3216Metric"),
        (['convin_sense', 'Rs', 'res', 'res', 'footprint_spec'], ParamValue(['vusb_sense', 'Rs', 'res', 'res', 'footprint_spec'])),

        (['ramp', 'drv', 'footprint_spec'], 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic'),

        # ignore derating on 20v - it's really broken =(
        (['reg_v5', 'power_path', 'in_cap', 'cap', 'exact_capacitance'], False),
        (['reg_v5', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 0.85),
        (['reg_v12', 'cf', 'voltage_rating_derating'], 0.85),
        (['reg_v12', 'cf', 'require_basic_part'], False),
        (['conv', 'power_path', 'in_cap', 'cap', 'exact_capacitance'], False),
        (['conv', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 0.85),
        (['conv', 'power_path', 'out_cap', 'cap', 'exact_capacitance'], False),
        (['conv', 'power_path', 'out_cap', 'cap', 'voltage_rating_derating'], 0.9),  # allow using a 35V cap
        (['conv', 'power_path', 'out_cap', 'cap', 'require_basic_part'], False),  # high volt caps are rare
        (['control', 'driver', 'cap_in2', 'cap', 'voltage_rating_derating'], 0.9),
        (['control', 'driver', 'cap_in2', 'cap', 'require_basic_part'], False),
        (['control', 'driver', 'cap_in3', 'cap', 'voltage_rating_derating'], 0.9),
        (['control', 'driver', 'cap_in3', 'cap', 'require_basic_part'], False),
        (['reg_vcontrol', 'cf', 'voltage_rating_derating'], 0.85),
        (['reg_vcontrol', 'cf', 'require_basic_part'], False),
        (['reg_vcontrol', 'power_path', 'out_cap', 'cap', 'exact_capacitance'], False),
        (['reg_vcontrol', 'power_path', 'out_cap', 'cap', 'voltage_rating_derating'], 0.85),
        (['conv', 'boost_sw', 'high_fet', 'gate_voltage'], ParamValue(
          ['conv', 'boost_sw', 'low_fet', 'gate_voltage']
        )),  # TODO model is broken for unknown reasons
        (['boot', 'c_fly_pos', 'voltage_rating_derating'], 0.85),
        (['boot', 'c_fly_neg', 'voltage_rating_derating'], 0.85),
        (['conv', 'boost_sw', 'low_fet', 'footprint_spec'], 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic'),
        # require all FETs to be the same; note boost must elaborate first
        (['conv', 'buck_sw', 'low_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'buck_sw', 'high_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'boost_sw', 'high_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'boost_sw', 'low_fet', 'manual_gate_charge'], Range.exact(100e-9)),  # reasonable worst case estimate
        (['conv', 'boost_sw', 'high_fet', 'manual_gate_charge'], ParamValue(['conv', 'boost_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'], ParamValue(['conv', 'boost_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'buck_sw', 'high_fet', 'manual_gate_charge'], ParamValue(['conv', 'boost_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'buck_sw', 'gate_res'], Range.from_tolerance(10, 0.05)),
        (['conv', 'boost_sw', 'gate_res'], ParamValue(['conv', 'buck_sw', 'gate_res'])),

        (['control', 'int_link', 'sink_impedance'], RangeExpr.INF),  # waive impedance check for integrator in

        # (['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'footprint_spec'], 'Resistor_SMD:R_1206_3216Metric'),
        (['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'require_basic_part'], False),
        (['control', 'isense', 'ranges[1]', 'isense', 'res', 'res', 'footprint_spec'], ParamValue(['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'footprint_spec'])),
        (['control', 'isense', 'ranges[1]', 'isense', 'res', 'res', 'require_basic_part'], False),
        (['control', 'isense', 'ranges[2]', 'isense', 'res', 'res', 'footprint_spec'], ParamValue(['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'footprint_spec'])),
        (['control', 'isense', 'ranges[2]', 'isense', 'res', 'res', 'require_basic_part'], False),

        (['control', 'driver', 'res', 'count'], 3),
        (['control', 'driver', 'high_fet', 'footprint_spec'], 'Package_TO_SOT_THT:TO-220-3_Horizontal_TabUp'),
        (['control', 'driver', 'high_fet', 'part_spec'], 'IRF540N'),
        (['control', 'driver', 'low_fet', 'footprint_spec'], 'Package_TO_SOT_THT:TO-220-3_Horizontal_TabUp'),
        (['control', 'driver', 'low_fet', 'part_spec'], 'IRF9540'),  # has a 30V/4A SOA

        (['control', 'ifilt', 'c', 'require_basic_part'], False),  # no 10nF caps in basic library for some reason

        (['control', 'snub_r', 'res', 'footprint_spec'], ParamValue(['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'footprint_spec'])),
        (['control', 'snub_r', 'res', 'require_basic_part'], False),
        (['control', 'snub_c', 'cap', 'require_basic_part'], False),

        (['prot_vusb', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),
        (['prot_conv', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),
        (['prot_3v3', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),

        (['oled', 'iref_res', 'require_basic_part'], False),

        (['control', 'isense', 'ranges[0]', 'pwr_sw', 'ic', 'swap'], True),  # better pinning
        # reduce maximum SSR drive current to be within the IO expander limit
        (['control', 'isense', 'ranges[0]', 'pwr_sw', 'ic', 'led_current_recommendation'], Range(0.002, 0.010)),
        (['control', 'isense', 'ranges[1]', 'pwr_sw', 'ic', 'led_current_recommendation'], Range(0.002, 0.010)),
        (['control', 'isense', 'ranges[2]', 'pwr_sw', 'ic', 'led_current_recommendation'], Range(0.002, 0.010)),
        (['vusb_sense', 'Rs', 'res', 'res', 'require_basic_part'], False),
        (['convin_sense', 'Rs', 'res', 'res', 'require_basic_part'], False),

        (['spk_drv', 'pwr', 'current_draw'], Range(6.0e-7, 0.25)),
        # assume speakers will be pretty mild
      ],
      class_values=[
        # (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015 is out of stock

        (Mcp3561, ['ic', 'ch', '0', 'impedance'], Range(260e3, 510e3)),  # GAIN=1 or lower
        (Mcp3561, ['ic', 'ch', '1', 'impedance'], Range(260e3, 510e3)),  # GAIN=1 or lower
        (Mcp3561, ['ic', 'ch', '2', 'impedance'], Range(260e3, 510e3)),  # GAIN=1 or lower
        (Mcp3561, ['ic', 'ch', '3', 'impedance'], Range(260e3, 510e3)),  # GAIN=1 or lower
      ]
    )


class UsbSourceMeasureTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbSourceMeasure)
