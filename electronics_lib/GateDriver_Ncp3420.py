from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ncp3420_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.pgnd = self.Port(Ground(), [Common])
    self.vcc = self.Port(VoltageSink.from_gnd(
      self.pgnd,
      voltage_limits=(4.6, 13.2)*Volt,  # recommended operating conditions
      current_draw=RangeExpr()
    ))

    input_model = DigitalSink.from_supply(
      self.pgnd, self.vcc,
      voltage_limit_abs=(-0.3, 6.5)*Volt,
      input_threshold_abs=(0.8, 2.0)*Volt
    )
    self.in_ = self.Port(input_model)
    self.nod = self.Port(input_model)

    self.drvl = self.Port(DigitalSource.from_supply(
      self.pgnd, self.vcc,
      current_limits=(-self.vcc.link().voltage.lower()/2.5, self.vcc.link().voltage.lower()/3.0)
    ))

    self.swn = self.Port(VoltageSink.from_gnd(
      self.pgnd,
      voltage_limits=(-5, 35)  # no current draw since this is a "ground" pin
    ))
    self.bst = self.Port(VoltageSink.from_gnd(
      self.swn,
      voltage_limits=(4.6, 15)*Volt,
    ))
    self.drvh = self.Port(DigitalSource.from_supply(
      self.swn, self.bst,
      current_limits=(-self.vcc.link().voltage.lower()/2.5, self.vcc.link().voltage.lower()/3.0)
    ))

    self.assign(self.vcc.current_draw, (0.7, 5.0)*mAmp + self.drvl.link().current_drawn +
                self.drvh.link().current_drawn)  # only system supply given

  def contents(self):
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.bst,
        '2': self.in_,
        '3': self.nod,
        '4': self.vcc,
        '5': self.drvl,
        '6': self.pgnd,
        '7': self.swn,
        '8': self.drvh,
      },
      mfr='ON Semiconductor', part='NCP3420',
      datasheet='https://www.onsemi.com/pdf/datasheet/ncp3420-d.pdf'
    )
    self.assign(self.lcsc_part, 'C154600')
    self.assign(self.actual_basic_part, False)


class Ncp3420(HalfBridgeDriver, HalfBridgeDriverPwm, Resettable, GeneratorBlock):
  """Half-bridge driver supporting 35V offset, 4.6-13.2v input, external boot diode, auto-deadtime."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.has_boot_diode, self.high_pwr.is_connected())

  def contents(self):
    super().contents()

    self.ic = self.Block(Ncp3420_Device())
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.pgnd)
    self.connect(self.pwm_in, self.ic.in_)
    self.connect(self.reset, self.ic.nod)
    self.connect(self.low_out, self.ic.drvl)
    self.connect(self.high_gnd, self.ic.swn)
    self.connect(self.high_out, self.ic.drvh)

    self.cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    # serves as both boot cap and decoupling cap
    self.high_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.high_gnd, self.ic.bst)

  def generate(self):
    super().generate()

    if self.get(self.high_pwr.is_connected()):
      self.connect(self.high_pwr, self.ic.bst)
    else:
      if self.get(self.has_boot_diode):
        self.boot = self.Block(Diode(
          self.high_gnd.link().voltage + self.pwr.link().voltage,
          self.ic.vcc.current_draw
        ))
        self.connect(self.boot.cathode.adapt_to(VoltageSource(
          voltage_out=self.high_gnd.link().voltage + self.pwr.link().voltage
        )), self.ic.bst)
        self.connect(self.boot.anode.adapt_to(VoltageSink(
          # no independent limits or current draw, reflected in parameters on other pins
        )), self.pwr)
