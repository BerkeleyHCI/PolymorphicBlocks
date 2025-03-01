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
      'HG': self.high_gate_ctl, 'LG': self.low_gate_ctl, 'VG': self.pwr_gate_pos
    }

  @init_in_parent
  def __init__(self, current: RangeLike, rds_on: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr_gate_pos = self.Port(VoltageSink.empty(), [Power])
    self.out = self.Port(VoltageSource.empty())

    self.control = self.Port(AnalogSink.empty())
    self.high_gate_ctl = self.Port(DigitalSink.empty())
    self.low_gate_ctl = self.Port(DigitalSink.empty())

    self.current = self.ArgParameter(current)
    self.rds_on = self.ArgParameter(rds_on)

  def contents(self) -> None:
    super().contents()

    zener_model = ZenerDiode((8, 10)*Volt)
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

    self.current = self.ArgParameter(current)
    self.rds_on = self.ArgParameter(rds_on)

  def contents(self):
    super().contents()

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      locals={
        'self': self,
        'clamp': {
          'clamp_current': (2.5, 5)*mAmp  # absolute maximum rating of ADC
        }
      })
    self.imeas: Ad8418a  # schematic-defined
    self.isense: RangingCurrentSenseResistor
    self.assign(self.imeas.in_diff_range, self.isense.out_range)


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
      (self.filt_vusb, self.fuse_vusb, self.prot_vusb, self.tp_vusb), _ = self.chain(
        self.usb.pwr,
        self.Block(SeriesPowerFerriteBead()),
        self.Block(SeriesPowerFuse(trip_current=(7, 8)*Amp)),
        imp.Block(ProtectionZenerDiode(voltage=(32, 38)*Volt)),  # for parts commonality w/ the Vconv zener
        self.Block(VoltageTestPoint()),
        self.vusb_sense.sense_pos
      )
      self.vusb = self.connect(self.vusb_sense.sense_neg)

      # logic supplies
      (self.reg_v5, self.tp_v5, self.reg_3v3, self.prot_3v3, self.tp_3v3), _ = self.chain(
        self.vusb,
        imp.Block(BuckConverter(output_voltage=5.0*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(ProtectionZenerDiode(voltage=(3.6, 4.5)*Volt)),
        self.Block(VoltageTestPoint())
      )
      self.v5 = self.connect(self.reg_v5.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      # output power supplies
      self.connect(self.vusb_sense.pwr, self.v3v3)

      self.convin_sense = imp.Block(Ina219(10*mOhm(tol=0.01), addr_lsb=1))
      self.connect(self.convin_sense.pwr, self.v3v3)
      (self.conv_inforce, self.precharge), _ = self.chain(
        self.vusb,
        imp.Block(ForcedVoltage(20*Volt(tol=0))),
        # avoid excess capacitance on VBus
        imp.Block(FetPrecharge(precharge_resistance=470*Ohm(tol=0.1), max_rds=0.1*Ohm)),
        self.convin_sense.sense_pos
      )
      (self.cap_conv, self.conv, self.conv_outforce, self.prot_conv, self.tp_conv), _ = self.chain(
        self.convin_sense.sense_neg,
        imp.Block(DecouplingCapacitor(100*uFarad(tol=0.25))),
        imp.Block(CustomSyncBuckBoostConverterPwm(output_voltage=(15, 30)*Volt,  # design for 0.5x - 1.5x conv ratio
                                                  frequency=500*kHertz(tol=0),
                                                  ripple_current_factor=(0.01, 0.9),
                                                  input_ripple_limit=250*mVolt,
                                                  output_ripple_limit=(25*(7/9))*mVolt  # fill out the row of caps
                                                  )),
        imp.Block(ForcedVoltage((2, 30)*Volt)),  # at least 2v to allow current sensor to work
        imp.Block(ProtectionZenerDiode(voltage=(32, 38)*Volt)),  # zener shunt in case the boost converter goes crazy
        self.Block(VoltageTestPoint())
      )
      self.connect(self.conv.pwr_logic, self.v5)
      self.vconv = self.connect(self.conv_outforce.pwr_out)

      (self.reg_v12, self.tp_v12), _ = self.chain(
        self.v5,
        imp.Block(BoostConverter(output_voltage=12.5*Volt(tol=0.04))),  # limits of the OLED
        self.Block(VoltageTestPoint("v12"))
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

      (self.ref_div, self.ref_buf), _ = self.chain(
        self.vref,
        imp.Block(VoltageDivider(output_voltage=1.65*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower())
      )
      self.ref_cap = self.Block(Capacitor(0.1*uFarad(tol=0.2), voltage=self.ref_div.output.link().voltage))
      self.connect(self.ref_cap.neg.adapt_to(Ground()), self.gnd)
      self.connect(self.ref_cap.pos.adapt_to(AnalogSink()), self.ref_div.output)
      self.connect(self.vanalog, self.ref_buf.pwr)
      self.vcenter = self.connect(self.ref_buf.output)

      (self.reg_vcontrol, self.tp_vcontrol), _ = self.chain(
        self.v5,
        imp.Block(BoostConverter(output_voltage=(30, 33)*Volt,  # up to but not greater
                                 output_ripple_limit=1*mVolt)),
        self.Block(VoltageTestPoint("vc+"))
      )
      self.vcontrol = self.connect(self.reg_vcontrol.pwr_out)

      (self.reg_vcontroln, self.tp_vcontroln), _ = self.chain(
        self.v3v3,
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
      self.connect(self.ioe_ctl.io.request_vector('irange'), self.control.irange)
      self.connect(self.ioe_ctl.io.request_vector('off'), self.control.off)

      rc_model = DigitalLowPassRc(150*Ohm(tol=0.05), 7*MHertz(tol=0.2))
      (self.buck_rc, ), _ = self.chain(self.mcu.gpio.request('buck_pwm'), imp.Block(rc_model), self.conv.buck_pwm)
      (self.boost_rc, ), _ = self.chain(self.mcu.gpio.request('boost_pwm'), imp.Block(rc_model), self.conv.boost_pwm)

      # TODO: this should be a wrapper VoltageComparator with more precise tolerancing
      self.conv_comp = imp.Block(Comparator())
      (self.comp_ref, ), _ = self.chain(
        self.v3v3,
        imp.Block(VoltageDivider(output_voltage=1*Volt(tol=0.05),
                                 impedance=(5, 50)*kOhm)),
        self.conv_comp.inp
      )
      # full scale needs to be below the threshold so the trip point is above the modeled max
      (self.comp_sense, ), _ = self.chain(
        self.vconv,
        imp.Block(VoltageSenseDivider(full_scale_voltage=0.90*Volt(tol=0.05),
                                      impedance=(5, 50)*kOhm)),
        self.conv_comp.inn
      )

      # TODO: should not allow simultaneous set and clr
      self.conv_latch = imp.Block(Sn74lvc1g74())
      (self.conv_en_pull, ), _ = self.chain(
        self.mcu.gpio.request('conv_en'),
        imp.Block(PullupResistor(10*kOhm(tol=0.05))),
        self.conv_latch.nclr
      )
      (self.comp_pull, ), _ = self.chain(
        self.conv_comp.out, imp.Block(PullupResistor(resistance=10*kOhm(tol=0.05))),
        self.conv_latch.nset
      )
      self.connect(self.conv_latch.nq, self.conv.reset, self.mcu.gpio.request('conv_en_sense'))
      self.connect(self.precharge.control, self.mcu.gpio.request('precharge_control'))

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

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.ioe_ui.io.request_vector('rgb'), self.rgb.signals)

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
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.fan_drv = imp.Block(HighSideSwitch())
      self.connect(self.v5, self.fan_drv.pwr)
      self.connect(self.mcu.gpio.request('fan'), self.fan_drv.control)
      self.fan = imp.Block(SourceMeasureFan())
      self.connect(self.fan.pwr, self.fan_drv.output)

    # analog domain
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.dac = imp.Block(Mcp4728())
      (self.dac_ferrite, ), _ = self.chain(
        self.vref,
        imp.Block(SeriesPowerFerriteBead(Range.from_lower(1000))),
        self.dac.pwr)
      (self.tp_cv, ), _ = self.chain(self.dac.out0, imp.Block(AnalogRfTestPoint('cv')),
                                     self.control.control_voltage)
      (self.tp_cvf, ), _ = self.chain(self.dac.out3, imp.Block(AnalogRfTestPoint('cvf')),
                                      self.control.control_voltage_fine)
      (self.tp_cisrc, ), _ = self.chain(self.dac.out1, imp.Block(AnalogRfTestPoint('cisrc')),
                                        self.control.control_current_sink)
      (self.tp_cisnk, ), _ = self.chain(self.dac.out2, imp.Block(AnalogRfTestPoint('cisnk')),
                                        self.control.control_current_source)
      self.connect(self.dac.i2c, int_i2c)

      self.adc = imp.Block(Mcp3561())
      self.connect(self.adc.pwra, self.vanalog)
      self.connect(self.adc.pwr, self.v3v3)
      self.connect(self.adc.vref, self.vref)
      self.connect(self.adc.spi, self.mcu.spi.request('adc_spi'))
      self.connect(self.adc.cs, self.mcu.gpio.request('adc_cs'))
      self.connect(self.adc.mclkin, self.mcu.gpio.request('adc_clk'))  # up to 20MHz output from LEDC peripheral
      (self.tp_vcen, self.vcen_rc, ), _ = self.chain(self.vcenter,
                                                     imp.Block(AnalogRfTestPoint('cen')),
                                                     imp.Block(AnalogLowPassRc(1*kOhm(tol=0.05), 16*kHertz(tol=0.25))),\
                                                     self.adc.vins.request('0'))
      (self.tp_mi, self.mi_rc, ), _ = self.chain(self.control.measured_current,
                                                 imp.Block(AnalogRfTestPoint('mi')),
                                                 imp.Block(AnalogLowPassRc(1*kOhm(tol=0.05), 16*kHertz(tol=0.25))),
                                                 self.adc.vins.request('1'))
      (self.tp_mv, self.mv_rc, ), _ = self.chain(self.control.measured_voltage,
                                                 imp.Block(AnalogRfTestPoint('mv')),
                                                 imp.Block(AnalogLowPassRc(1*kOhm(tol=0.05), 16*kHertz(tol=0.25))),
                                                 self.adc.vins.request('2'))
      (self.tp_lsrc, ), _ = self.chain(self.control.limit_source,
                                       imp.Block(DigitalTestPoint('src')),
                                       self.mcu.gpio.request('limit_source'))
      (self.tp_lsnk, ), _ = self.chain(self.control.limit_sink,
                                       imp.Block(DigitalTestPoint('snk')),
                                       self.mcu.gpio.request('limit_sink'))

    self.outn = self.Block(BananaSafetyJack())
    self.outp = self.Block(BananaSafetyJack())
    self.outd = self.Block(PinHeader254Horizontal(2))  # 2.54 output option
    self.connect(self.gnd, self.outn.port.adapt_to(Ground()), self.outd.pins.request('1').adapt_to(Ground()))
    self.connect(
      self.control.out,
      self.outp.port.adapt_to(VoltageSink(current_draw=OUTPUT_CURRENT_RATING)),
      self.outd.pins.request('2').adapt_to(VoltageSink())
    )

  def multipack(self) -> None:
    self.vimeas_amps = self.PackedBlock(Opa2189())
    self.pack(self.vimeas_amps.elements.request('0'), ['control', 'vmeas', 'amp'])
    self.pack(self.vimeas_amps.elements.request('1'), ['control', 'hvbuf', 'amp'])

    self.ampdmeas_amps = self.PackedBlock(Opa2171())
    self.pack(self.ampdmeas_amps.elements.request('0'), ['control', 'amp', 'amp'])
    self.pack(self.ampdmeas_amps.elements.request('1'), ['control', 'dmeas', 'amp'])

    self.cd_amps = self.PackedBlock(Tlv9152())
    self.pack(self.cd_amps.elements.request('0'), ['control', 'dbuf', 'amp'])
    self.pack(self.cd_amps.elements.request('1'), ['control', 'err_d', 'amp'])

    self.cv_amps = self.PackedBlock(Tlv9152())
    self.pack(self.cv_amps.elements.request('0'), ['control', 'vbuf', 'amp'])
    self.pack(self.cv_amps.elements.request('1'), ['control', 'err_volt', 'amp'])

    self.ci_amps = self.PackedBlock(Tlv9152())
    self.pack(self.ci_amps.elements.request('0'), ['control', 'err_sink', 'amp'])
    self.pack(self.ci_amps.elements.request('1'), ['control', 'err_source', 'amp'])

    self.cintref_amps = self.PackedBlock(Tlv9152())
    self.pack(self.cintref_amps.elements.request('0'), ['control', 'int', 'amp'])
    self.pack(self.cintref_amps.elements.request('1'), ['ref_buf', 'amp'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_v5'], Tps54202h),
        (['reg_3v3'], Ldl1117),
        (['reg_v12'], Lm2733),
        (['reg_analog'], Ap2210),
        (['reg_vref'], Ref30xx),
        (['reg_vcontrol'], Lm2733),

        (['control', 'driver', 'low_fet'], CustomFet),
        (['control', 'driver', 'high_fet'], CustomFet),

        (['control', 'off_sw', 'device'], Nlas4157),  # 3v3 compatible unlike DG468

        (['cap_vusb', 'cap'], JlcAluminumCapacitor),
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TagConnect, TagConnectNonLegged),  # really for initial flash / emergency upload only
        (Opamp, Tlv9061),  # higher precision opamps
        (AnalogSwitch, Dg468),
        (SolidStateRelay, Tlp3545a),  # TODO lower range switches can be cheaper AQY282SX
        (BananaSafetyJack, Ct3151),
        (HalfBridgeDriver, Ncp3420),
        (DirectionSwitch, Skrh),
        (TestPoint, CompactKeystone5015),
        (RotaryEncoder, Pec11s),
        (RfConnector, UflConnector),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          # note: for ESP32-S3 compatibility: IO35/36/37 (pins 28-30) are used by PSRAM
          # note: for ESP32-C6 compatibility: pin 34 (22 on dedicated -C6 pattern) is NC

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
          'conv_en=33',
          'boost_pwm=32',
          'vconv_sense=18',  # needs ADC

          'int_i2c.scl=39',
          'int_i2c.sda=38',

          'qwiic.scl=24',
          'qwiic.sda=25',
          'pd_int=21',
          'fan=19',
          'touch_duck=22',
          'conv_en_sense=23',

          'led=_GPIO0_STRAP',

        ]),
        (['mcu', 'programming'], 'uart-auto'),

        (['ioe', 'pin_assigns'], [
          'dir_c=9',
          'dir_cen=4',
          'dir_a=5',
          'dir_b=6',
          'dir_d=7',

          'rgb_blue=10',
          'rgb_red=11',
          'rgb_green=12',
        ]),

        # allow the regulator to go into tracking mode
        (['reg_v5', 'power_path', 'dutycycle_limit'], Range(0, float('inf'))),
        (['reg_v5', 'power_path', 'inductor_current_ripple'], Range(0.01, 0.5)),  # trade higher Imax for lower L
        # JLC does not have frequency specs, must be checked TODO
        (['reg_v5', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['reg_v12', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['conv', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['reg_vcontrol', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),

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
        (['reg_vcontrol', 'cf', 'voltage_rating_derating'], 0.85),
        (['reg_vcontrol', 'cf', 'require_basic_part'], False),
        (['reg_vcontrol', 'power_path', 'out_cap', 'cap', 'exact_capacitance'], False),
        (['reg_vcontrol', 'power_path', 'out_cap', 'cap', 'voltage_rating_derating'], 0.85),
        (['conv', 'boost_sw', 'high_fet', 'gate_voltage'], ParamValue(
          ['conv', 'boost_sw', 'low_fet', 'gate_voltage']
        )),  # TODO model is broken for unknown reasons
        (['boot', 'c_fly_pos', 'voltage_rating_derating'], 0.85),
        (['boot', 'c_fly_neg', 'voltage_rating_derating'], 0.85),
        (['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'], Range.exact(100e-9)),  # reasonable worst case estimate
        (['conv', 'buck_sw', 'high_fet', 'manual_gate_charge'], ParamValue(['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'boost_sw', 'low_fet', 'manual_gate_charge'], ParamValue(['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'boost_sw', 'high_fet', 'manual_gate_charge'], ParamValue(['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'])),
        # require all FETs to be the same; note boost must elaborate first
        (['conv', 'buck_sw', 'low_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'buck_sw', 'high_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'boost_sw', 'high_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'buck_sw', 'gate_res'], Range.from_tolerance(10, 0.05)),
        (['conv', 'boost_sw', 'gate_res'], ParamValue(['conv', 'buck_sw', 'gate_res'])),

        (['control', 'int_link', 'sink_impedance'], RangeExpr.INF),  # waive impedance check for integrator in

        (['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'footprint_spec'], 'Resistor_SMD:R_1206_3216Metric'),
        (['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'require_basic_part'], False),
        (['control', 'isense', 'ranges[1]', 'isense', 'res', 'res', 'footprint_spec'], ParamValue(['control', 'isense', 'ranges[0]', 'isense', 'res', 'res', 'footprint_spec'])),
        (['control', 'isense', 'ranges[1]', 'isense', 'res', 'res', 'require_basic_part'], False),

        (['control', 'driver', 'high_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:TO-252-2'),
        (['control', 'driver', 'high_fet', 'part_spec'], 'SQD50N10-8M9L_GE3'),
        (['control', 'driver', 'low_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:TO-252-2'),
        (['control', 'driver', 'low_fet', 'part_spec'], 'SQD50P06-15L_GE3'),  # has a 30V/4A SOA

        (['prot_vusb', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),
        (['prot_conv', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),
        (['prot_3v3', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),

        (['oled', 'iref_res', 'require_basic_part'], False),

        # these are since the auto-assigned parts are OOS
        (['control', 'isense', 'ranges[1]', 'isense', 'res', 'res', 'part'], "1206W4F220LT5E"),
        (['conv', 'boost_sw', 'low_fet', 'part'], "KIA50N03BD"),
        (['prot_3v3', 'diode', 'part'], "1SMA4730AG"),

        (['precharge', 'res', 'res', 'require_basic_part'], False),

        # fudge the numbers a bit to avoid a ERC - the output of the IO expander will probably limit
        (['control', 'isense', 'ranges[0]', 'pwr_sw', 'signal', 'current_draw'], Range(0.0, 0.010)),
        (['control', 'isense', 'ranges[1]', 'pwr_sw', 'signal', 'current_draw'], Range(0.0, 0.010)),
        (['vusb_sense', 'Rs', 'res', 'res', 'require_basic_part'], False),
        (['convin_sense', 'Rs', 'res', 'res', 'require_basic_part'], False),
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
