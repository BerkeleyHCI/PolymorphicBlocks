from ..abstract_parts import *
from .JlcPart import JlcPart


class A4988_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground())
    vbb_model = VoltageSink(
      voltage_limits=(8, 35)*Volt,  # in operation; down to 0 during sleep
      current_draw=RangeExpr()
    )
    kVbbDraw = (0.01, 4)*mAmp
    self.vbb1 = self.Port(vbb_model)
    self.vbb2 = self.Port(vbb_model)
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(3.3, 5.5)*Volt,
      current_draw=(0.010, 8)*mAmp
    ))
    self.vreg = self.Port(VoltageSource(
      voltage_out=(7, 7)*Volt,  # "nominal output voltage"
      current_limits=0*Amp(tol=0)  # regulator decoupling terminal only
    ))
    self.vcp = self.Port(Passive())
    self.cp1 = self.Port(Passive())
    self.cp2 = self.Port(Passive())

    self.rosc = self.Port(Passive())
    self.ref = self.Port(AnalogSink(
      voltage_limits=(0, 5.5)*Volt,
      signal_limits=(0, 4)*Volt,
      impedance=1.3*MOhm(tol=0)  # assumed, from input current @ max voltage
    ))
    self.sense1 = self.Port(Passive())
    self.sense2 = self.Port(Passive())

    din_model = DigitalSink.from_supply(
      self.gnd, self.vdd,
      voltage_limit_abs=(-0.3, 5.5)*Volt,
      input_threshold_factor=(0.3, 0.7)
    )
    self.ms1 = self.Port(din_model)
    self.ms2 = self.Port(din_model)
    self.ms3 = self.Port(din_model)

    self.reset = self.Port(din_model)
    self.sleep = self.Port(din_model)
    self.step = self.Port(din_model)
    self.dir = self.Port(din_model)
    self.enable = self.Port(din_model)

    dout1_model = DigitalSource.from_supply(
      self.gnd, self.vbb1,
      current_limits=(-2, 2)*Amp
    )
    self.out1a = self.Port(dout1_model)
    self.out1b = self.Port(dout1_model)
    self.assign(self.vbb1.current_draw,
                self.out1a.link().current_drawn.hull(self.out1b.link().current_drawn).abs().hull((0, 0)) + kVbbDraw)
    dout2_model = DigitalSource.from_supply(
      self.gnd, self.vbb2,
      current_limits=(-2, 2)*Amp
    )
    self.out2a = self.Port(dout2_model)
    self.out2b = self.Port(dout2_model)
    self.assign(self.vbb2.current_draw,
                self.out2a.link().current_drawn.hull(self.out2b.link().current_drawn).abs().hull((0, 0)) + kVbbDraw)

  def contents(self) -> None:
    self.footprint(
      'U', 'Package_DFN_QFN:TQFN-28-1EP_5x5mm_P0.5mm_EP3.25x3.25mm_ThermalVias',
      {
        '4': self.cp1,
        '5': self.cp2,
        '6': self.vcp,
        # pin 7 NC
        '8': self.vreg,
        '9': self.ms1,
        '10': self.ms2,
        '11': self.ms3,
        '12': self.reset,
        '13': self.rosc,
        '14': self.sleep,
        '15': self.vdd,
        '16': self.step,
        '17': self.ref,
        '3': self.gnd,
        '18': self.gnd,
        '19': self.dir,
        # pin 20 NC
        '21': self.out1b,
        '22': self.vbb1,
        '23': self.sense1,
        '24': self.out1a,
        # pin 25 NC
        '26': self.out2a,
        '27': self.sense2,
        '28': self.vbb2,
        '1': self.out2b,
        '2': self.enable,
        '29': self.gnd,  # GNDs must be tied together externally by connecting to PAD GND
      },
      mfr='Allegro MicroSystems', part='A4988SETTR-R',
      datasheet='https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf'
    )
    self.assign(self.lcsc_part, 'C38437')


class A4988(BrushedMotorDriver, GeneratorBlock):
  @init_in_parent
  def __init__(self, step_resolution: IntLike = 16,
               itrip: RangeLike = 1*Amp(tol=0.05),
               itrip_vref: RangeLike = 0.25*Volt(tol=0.02)) -> None:
    super().__init__()
    self.step_resolution = self.ArgParameter(step_resolution, doc="microstepping resolution (1, 2, 4, 8, or 16)")
    self.itrip = self.ArgParameter(itrip, doc="maximum (trip) current across motor windings")
    self.itrip_vref = self.ArgParameter(itrip_vref, doc="voltage reference for Isense trip, not counting the 8x on Vref")
    self.generator_param(self.step_resolution)

    self.ic = self.Block(A4988_Device())
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.pwr = self.Export(self.ic.vbb1)
    self.pwr_logic = self.Export(self.ic.vdd)

    self.step = self.Export(self.ic.step)
    self.dir = self.Export(self.ic.dir)

    self.enable = self.Export(self.ic.enable, optional=True, doc="disables FET outputs when high")
    self.reset = self.Export(self.ic.reset, optional=True, doc="forces translator to Home state when low")
    self.sleep = self.Export(self.ic.sleep, optional=True, doc="disables device (to reduce current draw) when low")
    self.generator_param(self.enable.is_connected(), self.reset.is_connected(), self.sleep.is_connected())

    self.out1a = self.Export(self.ic.out1a)
    self.out1b = self.Export(self.ic.out1b)
    self.out2a = self.Export(self.ic.out2a)
    self.out2b = self.Export(self.ic.out2b)

  def contents(self) -> None:
    super().contents()

    # the upper tolerable range of these caps is extended to allow search flexibility when voltage derating
    self.vreg_cap = self.Block(DecouplingCapacitor((0.22*0.8, 1)*uFarad)).connected(self.gnd, self.ic.vreg)
    self.vdd_cap = self.Block(DecouplingCapacitor((0.22*0.8, 1)*uFarad)).connected(self.gnd, self.pwr_logic)

    self.vcpi_cap = self.Block(Capacitor(0.1*uFarad(tol=0.2), (0, 16)*Volt))  # voltage a wild guess, no specs given
    self.connect(self.vcpi_cap.pos, self.ic.cp1)
    self.connect(self.vcpi_cap.neg, self.ic.cp2)
    self.vcp_cap = self.Block(Capacitor(0.1*uFarad(tol=0.2), (0, 16)*Volt))
    self.connect(self.vcp_cap.pos, self.ic.vcp)
    self.connect(self.vcp_cap.neg.adapt_to(VoltageSink()), self.ic.vbb1, self.ic.vbb2)

    self.rosc = self.Block(Resistor(10*kOhm(tol=0.05)))  # arbitrary, from Pololu breakout board
    self.connect(self.rosc.a.adapt_to(Ground()), self.gnd)
    self.connect(self.rosc.b, self.ic.rosc)

    self.ref_div = self.Block(VoltageDivider(output_voltage=self.itrip_vref * 8, impedance=(1, 10)*kOhm))
    self.connect(self.ref_div.gnd, self.gnd)
    self.connect(self.ref_div.input, self.pwr_logic)
    self.connect(self.ref_div.output, self.ic.ref)

    self.isense = ElementDict[Resistor]()
    for i, sensen in [('1', self.ic.sense1), ('2', self.ic.sense2)]:
      isense = self.isense[i] = self.Block(Resistor(self.itrip_vref / self.itrip))  # TODO shrink tolerances
      self.connect(isense.a, sensen)
      self.connect(isense.b.adapt_to(Ground()), self.gnd)

  def generate(self) -> None:
    super().generate()

    step_resolution = self.get(self.step_resolution)
    if step_resolution == 1:  # full step
      self.connect(self.gnd.as_digital_source(), self.ic.ms1, self.ic.ms2, self.ic.ms3)
    elif step_resolution == 2:  # half step
      self.connect(self.gnd.as_digital_source(), self.ic.ms2, self.ic.ms3)
      self.connect(self.pwr.as_digital_source(), self.ic.ms1)
    elif step_resolution == 4:  # quarter step
      self.connect(self.gnd.as_digital_source(), self.ic.ms1, self.ic.ms3)
      self.connect(self.pwr.as_digital_source(), self.ic.ms2)
    elif step_resolution == 8:  # eighth step
      self.connect(self.gnd.as_digital_source(), self.ic.ms3)
      self.connect(self.pwr.as_digital_source(), self.ic.ms1, self.ic.ms2)
    elif step_resolution == 16:  # sixteenth step
      self.connect(self.pwr.as_digital_source(), self.ic.ms1, self.ic.ms2, self.ic.ms3)
    else:
      raise ValueError(f"unknown step_resolution {step_resolution}")

    if self.get(self.enable.is_connected()):
      self.connect(self.enable, self.ic.enable)
    else:
      self.connect(self.gnd.as_digital_source(), self.ic.enable)

    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.reset)
    else:
      self.connect(self.pwr.as_digital_source(), self.ic.reset)

    if self.get(self.sleep.is_connected()):
      self.connect(self.sleep, self.ic.sleep)
    else:
      self.connect(self.pwr.as_digital_source(), self.ic.sleep)
