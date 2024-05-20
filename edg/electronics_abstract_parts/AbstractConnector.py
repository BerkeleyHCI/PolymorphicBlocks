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


@abstract_block
class RfConnector(Connector):
  """Base class for a RF connector, with a signal and ground. Signal is passive-typed."""
  def __init__(self) -> None:
    super().__init__()
    self.sig = self.Port(Passive.empty())
    self.gnd = self.Port(Ground(), [Common])


class RfConnectorTestPoint(BlockInterfaceMixin[RfConnector]):
  """Test point mixin that allows the footprint to take a name"""
  @init_in_parent
  def __init__(self, name: StringLike):
    super().__init__()
    self.tp_name = self.ArgParameter(name)


class UflConnector(RfConnector):
  """Base class for a U.FL / IPEX / UMCC connector, miniature RF connector."""
