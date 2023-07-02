from typing import Dict

from electronics_model import *
from .Categories import *


@abstract_block
class Switch(KiCadImportableBlock, DiscreteComponent):
  """Two-ported device that closes a circuit when pressed."""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'Switch:SW_SPST'
    return {'1': self.sw, '2': self.com}

  @init_in_parent
  def __init__(self, voltage: RangeLike, current: RangeLike = 0*Amp(tol=0)) -> None:
    super().__init__()

    self.sw = self.Port(Passive.empty())
    self.com = self.Port(Passive.empty())

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
  def __init__(self, voltage: RangeLike, current: RangeLike = 0*Amp(tol=0)) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())
    self.com = self.Port(Passive.empty())

    self.current = self.ArgParameter(current)
    self.voltage = self.ArgParameter(voltage)


class RotaryEncoderSwitch(BlockInterfaceMixin[RotaryEncoder]):
  """Rotary encoder mixin adding a switch pin (sharing a common with the encoder),
  with ratings assumed to be the same between the switch and encoder."""
  def __init__(self, *args, **kwargs):
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

    self.connect(self.out, self.package.sw.adapt_to(DigitalSingleSource.low_from_supply(self.gnd)))
    self.connect(self.gnd, self.package.com.adapt_to(Ground()))


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
    self.connect(self.gnd, self.package.com.adapt_to(Ground()))


@abstract_block_default(lambda: DigitalRotaryEncoderWithSwitch)
class DigitalRotaryEncoderSwitch(BlockInterfaceMixin[DigitalRotaryEncoder]):
  """DigitalRotaryEncoder mixin adding a switch pin."""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.sw = self.Port(DigitalSingleSource.empty(), [Output])


class DigitalRotaryEncoderWithSwitch(DigitalRotaryEncoderSwitch, DigitalRotaryEncoder):
  def contents(self):
    super().contents()

    package_sw = self.package.with_mixin(RotaryEncoderSwitch())
    dio_model = DigitalSingleSource.low_from_supply(self.gnd)
    self.connect(self.sw, package_sw.sw.adapt_to(dio_model))
