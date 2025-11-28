from typing_extensions import override

from ..abstract_parts import *
from .JlcPart import JlcPart


class Sn74lvc1g3157_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground())
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(1.65, 5.5)*Volt,
      current_draw=(1, 35)*uAmp,  # Icc, at 5.5v
    ))

    self.s = self.Port(DigitalSink.from_supply(self.gnd, self.vcc,
      voltage_limit_abs=(-0.5, 6)*Volt,
      current_draw=(-1, 1)*uAmp,  # input leakage current
      input_threshold_factor=(0.25, 0.75)
    ))

    self.analog_voltage_limits = self.Parameter(RangeExpr((
      self.gnd.link().voltage.upper() - 0.5,
      self.vcc.link().voltage.lower() + 0.5
    )))
    self.analog_current_limits = self.Parameter(RangeExpr((-128, 128)*mAmp))
    self.analog_on_resistance = self.Parameter(RangeExpr((6, 30)*Ohm))  # typ-max, across all conditions

    self.a = self.Port(Passive())
    self.b1 = self.Port(Passive(), optional=True)
    self.b0 = self.Port(Passive(), optional=True)

  @override
  def contents(self) -> None:
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
      mfr='Texas Instruments', part='SN74LVC1G3157DCKR',
      datasheet='https://www.ti.com/lit/ds/symlink/sn74lvc1g3157.pdf'
    )
    self.assign(self.lcsc_part, 'C38663')
    self.assign(self.actual_basic_part, False)


class Sn74lvc1g3157(AnalogSwitch):
  """2:1 analog switch, 6ohm Ron(typ), in SOT-363.
  """
  @override
  def contents(self) -> None:
    super().contents()

    self.require(~self.control_gnd.is_connected(), "device does not support control ground")

    self.ic = self.Block(Sn74lvc1g3157_Device())
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
