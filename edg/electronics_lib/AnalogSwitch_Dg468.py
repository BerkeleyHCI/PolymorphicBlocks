from ..electronics_abstract_parts import *
from .JlcPart import JlcPart


class Dg468_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self):
    super().__init__()

    self.gnd = self.Port(Ground())
    self.vp = self.Port(VoltageSink(
      voltage_limits=(7, 36)*Volt,  # 44v abs max
      current_draw=(5, 20)*uAmp,
    ))

    self.in_ = self.Port(DigitalSink.from_supply(
      self.gnd, self.vp,
      voltage_limit_tolerance=(-2, 2)*Volt,  # or 30mA
      input_threshold_abs=(0.8, 2.5)*Volt
    ))

    self.analog_voltage_limits = self.Parameter(RangeExpr(
      self.vp.link().voltage.hull(self.gnd.link().voltage)
    ))
    self.analog_current_limits = self.Parameter(RangeExpr((-30, 30)*mAmp))  # max current any pin
    self.analog_on_resistance = self.Parameter(RangeExpr((7, 20)*Ohm))  # typ to max

    self.com = self.Port(Passive())
    self.no = self.Port(Passive(), optional=True)

  def contents(self):
    super().contents()

    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.no,
        '2': self.gnd,  # v-
        '3': self.in_,
        '4': self.gnd,
        '5': self.vp,
        '6': self.com,
      },
      mfr='Vishay Siliconix', part='DG468DV',
      datasheet='https://www.vishay.com/docs/74413/dg467.pdf'
    )
    self.assign(self.lcsc_part, 'C2651906')
    self.assign(self.actual_basic_part, False)


class Dg468(AnalogSwitch):
  """DG468 36V 10ohm SPST switch in normally-open configuration
  """
  def contents(self):
    super().contents()

    self.ic = self.Block(Dg468_Device())
    self.connect(self.pwr, self.ic.vp)
    self.connect(self.gnd, self.ic.gnd)
    self.connect(self.com, self.ic.com)
    self.connect(self.inputs.append_elt(Passive.empty(), '1'), self.ic.no)
    self.connect(self.control.append_elt(DigitalSink.empty(), '0'), self.ic.in_)

    self.assign(self.analog_voltage_limits, self.ic.analog_voltage_limits)
    self.assign(self.analog_current_limits, self.ic.analog_current_limits)
    self.assign(self.analog_on_resistance, self.ic.analog_on_resistance)

    # surprisingly, the datasheet doesn't actually specify any decoupling capacitors, but here's one anyways
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)
