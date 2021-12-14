from electronics_abstract_parts import *


class Nlas4157_Device(FootprintBlock):
  def __init__(self):
    super().__init__()

    self.vcc = self.Port(VoltageSink(
      voltage_limits=(1.65, 5.5)*Volt,
      current_draw=(0.5, 1.0)*uAmp,  # Icc, at 5.5v, typ to max
    ))
    self.gnd = self.Port(Ground())

    self.s = self.Port(DigitalSink(
      voltage_limits=(-0.5, 6)*Volt,
      current_draw=(-1, 1)*uAmp,  # input leakage current
      input_thresholds=(0.6, 2.4)*Volt,  # strictest of Vdd=2.7, 4.5 V
    ))

    self.analog_voltage_limits = self.Parameter(RangeExpr((
      self.gnd.link().voltage.upper() - 0.5,
      self.vcc.link().voltage.lower() + 0.5
    )))
    self.analog_current_limits = self.Parameter(RangeExpr((-300, 300)*mAmp))
    self.analog_on_resistance = self.Parameter((0.3, 4.3)*Ohm)

    self.a = self.Port(Passive())
    self.b1 = self.Port(Passive())
    self.b0 = self.Port(Passive())

  def contents(self):
    super().contents()

    self.footprint(
      'U', 'Package_TO_SOT:SOT-363_SC-70-6',
      {
        '1': self.b1,
        '2': self.gnd,
        '3': self.b0,
        '4': self.a,
        '5': self.vcc,
        '6': self.s,
      },
      mfr='ON Semiconductor', part='NLAS4157',
      datasheet='https://www.onsemi.com/pdf/datasheet/nlas4157-d.pdf'
    )


class Nlas4157(AnalogSwitch):
  def contents(self):
    super().contents()

    self.ic = self.Block(Nlas4157_Device())
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.gnd)
    self.connect(self.com, self.ic.a)
    self.connect(self.no, self.ic.b1)
    self.connect(self.nc, self.ic.b0)
    self.connect(self.control, self.ic.s)

    # surprisingly, the datasheet doesn't actually specify any decoupling capacitors, but here's one anyways
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap = imp.Block(DecouplingCapacitor(
        capacitance=0.1*uFarad(tol=0.2),
      ))
