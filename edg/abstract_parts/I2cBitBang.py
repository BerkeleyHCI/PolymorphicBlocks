from typing import cast

from ..electronics_model import *
from .Categories import *


class I2cControllerBitBang(BitBangAdapter, Block):
  """Bit-bang adapter for I2C controller"""
  @staticmethod
  def digital_external_from_link(link_port: DigitalBidir) -> DigitalBidir:
    """Creates a DigitalBidir model that is the external-facing port that exports from
    an internal-facing (link-side) port. The internal-facing port should be ideal.
    These are basically the semantics of a DigitalBidir bridge.
    TODO: unify code w/ DigitalBidir bridge?"""
    return DigitalBidir(
      voltage_out=link_port.link().voltage, current_draw=link_port.link().current_drawn,
      voltage_limits=link_port.link().voltage_limits, current_limits=link_port.link().current_limits,
      output_thresholds=link_port.link().output_thresholds, input_thresholds=link_port.link().input_thresholds,
      pulldown_capable=link_port.link().pulldown_capable, pullup_capable=link_port.link().pullup_capable
    )

  def __init__(self) -> None:
    super().__init__()
    self.i2c = self.Port(I2cController.empty(), [Output])
    self.scl = self.Port(DigitalBidir.empty())
    self.sda = self.Port(DigitalBidir.empty())

  def contents(self) -> None:
    super().contents()
    self.connect(self.i2c.scl, self.scl)
    self.connect(self.i2c.sda, self.sda)

  def connected_from(self, scl: Port[DigitalLink], sda: Port[DigitalLink]) -> 'I2cControllerBitBang':
    cast(Block, builder.get_enclosing_block()).connect(scl, self.scl)
    cast(Block, builder.get_enclosing_block()).connect(sda, self.sda)
    return self
