from ..abstract_parts import *
from .JlcPart import JlcPart


class Nlas4157_Device(InternalSubcircuit, FootprintBlock, JlcPart):
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
    self.analog_on_resistance = self.Parameter(RangeExpr((0.3, 4.3)*Ohm))

    self.a = self.Port(Passive())
    self.b1 = self.Port(Passive(), optional=True)
    self.b0 = self.Port(Passive(), optional=True)

  def contents(self):
    super().contents()

    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-363_SC-70-6',
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
    self.assign(self.lcsc_part, 'C106912')
    self.assign(self.actual_basic_part, False)


class Nlas4157(AnalogSwitch):
  """NLAS4157 2:1 analog switch, 1ohm Ron, in SOT-363.
  Pin compatible with:
  - TS5A3159: 5v tolerant, 1 ohm
  - TS5A3160: 5v tolerant, 1 ohm
  """
  def contents(self):
    super().contents()

    self.ic = self.Block(Nlas4157_Device())
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.gnd)
    self.connect(self.com, self.ic.a)
    self.connect(self.inputs.append_elt(Passive.empty(), '0'), self.ic.b0)
    self.connect(self.inputs.append_elt(Passive.empty(), '1'), self.ic.b1)
    self.connect(self.control.append_elt(DigitalSink.empty(), '0'), self.ic.s)

    self.assign(self.analog_voltage_limits, self.ic.analog_voltage_limits)
    self.assign(self.analog_current_limits, self.ic.analog_current_limits)
    self.assign(self.analog_on_resistance, self.ic.analog_on_resistance)

    # surprisingly, the datasheet doesn't actually specify any decoupling capacitors, but here's one anyways
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)
