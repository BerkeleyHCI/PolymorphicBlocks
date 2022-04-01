from electronics_model import *
from .Categories import Connector


@abstract_block
class BananaJack(Connector):
  """Base class for a single terminal 4mm banana jack, such as used on test equipment."""
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(Passive.empty())


@abstract_block
class BananaSafetyJack(BananaJack):
  """Base class for a single terminal 4mm banana jack supporting a safety sheath,
  such as on multimeter leads."""
