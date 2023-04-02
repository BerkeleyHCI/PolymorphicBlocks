from typing import Dict

from electronics_model import *
from .Categories import *


@abstract_block
class Switch(KiCadImportableBlock, DiscreteComponent):
  """Two-ported device that closes a circuit when pressed."""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'Switch:SW_SPST'
    return {'1': self.a, '2': self.b}

  @init_in_parent
  def __init__(self, voltage: RangeLike, current: RangeLike = Default(0*Amp(tol=0))) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())

    self.current = self.ArgParameter(current)
    self.voltage = self.ArgParameter(voltage)


@abstract_block
class TactileSwitch(Switch):
  """Abstract class (category) for a tactile switch."""


@abstract_block
class MechanicalKeyswitch(Switch):
  """Abstract class (category) for a mechanical keyboard switch, including sockets."""


@abstract_block
class RotaryEncoder(DiscreteComponent):
  """Rotary encoder with discrete clicks and a quadrature signal (A/B/Common).
  Includes shaft-type encoders as well as thumbwheels."""
  @init_in_parent
  def __init__(self, voltage: RangeLike, current: RangeLike = Default(0*Amp(tol=0))) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())
    self.c = self.Port(Passive.empty())

    self.current = self.ArgParameter(current)
    self.voltage = self.ArgParameter(voltage)


@abstract_block
class RotaryEncoderWithSwitch(RotaryEncoder):
  """Rotary encoder that also adds a switch pin (sharing a common with the encoder),
  with ratings assumed to be the same between the switch and encoder."""
  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.sw = self.Port(Passive.empty())


class DigitalSwitch(HumanInterface):
  """Wrapper around Switch that provides a digital port which is pulled low (to GND) when pressed."""
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.out = self.Port(DigitalSingleSource.empty(), [Output])

  def contents(self):
    super().contents()
    self.package = self.Block(Switch(current=self.out.link().current_drawn,
                                     voltage=self.out.link().voltage))

    self.connect(self.out, self.package.a.adapt_to(DigitalSingleSource.low_from_supply(self.gnd)))
    self.connect(self.gnd, self.package.b.adapt_to(Ground()))


class DigitalRotaryEncoder(HumanInterface):
  """Wrapper around RotaryEncoder that provides digital ports that are pulled low (to GND) when pressed."""
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.a = self.Port(DigitalSingleSource.empty(), [Output])
    self.b = self.Port(DigitalSingleSource.empty(), [Output])

  def contents(self):
    super().contents()
    self.package = self.Block(RotaryEncoder(current=self.a.link().current_drawn.hull(self.b.link().current_drawn),
                                            voltage=self.a.link().voltage.hull(self.b.link().voltage)))

    dio_model = DigitalSingleSource.low_from_supply(self.gnd)
    self.connect(self.a, self.package.a.adapt_to(dio_model))
    self.connect(self.b, self.package.b.adapt_to(dio_model))
    self.connect(self.gnd, self.package.c.adapt_to(Ground()))


class DigitalRotaryEncoderWithSwitch(HumanInterface):
  """Wrapper around RotaryEncoderWithSwitch that provides a digital port which is pulled low (to GND) when pressed.
  TODO: deduplicate with DigitalRotaryEncoder
  """
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.a = self.Port(DigitalSingleSource.empty(), [Output])
    self.b = self.Port(DigitalSingleSource.empty(), [Output])
    self.sw = self.Port(DigitalSingleSource.empty(), [Output])

  def contents(self):
    super().contents()
    self.package = self.Block(RotaryEncoderWithSwitch(
      current=self.a.link().current_drawn.hull(self.b.link().current_drawn).hull(self.sw.link().current_drawn),
      voltage=self.a.link().voltage.hull(self.b.link().voltage).hull(self.sw.link().voltage)))

    dio_model = DigitalSingleSource.low_from_supply(self.gnd)
    self.connect(self.a, self.package.a.adapt_to(dio_model))
    self.connect(self.b, self.package.b.adapt_to(dio_model))
    self.connect(self.sw, self.package.sw.adapt_to(dio_model))
    self.connect(self.gnd, self.package.c.adapt_to(Ground()))
