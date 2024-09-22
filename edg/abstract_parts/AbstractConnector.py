from ..electronics_model import *
from .Categories import Connector
from .AbstractAntenna import Antenna


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
    self.sig = self.Port(Passive.empty(), [Input])
    self.gnd = self.Port(Ground(), [Common])


class RfConnectorTestPoint(BlockInterfaceMixin[RfConnector]):
  """Test point mixin that allows the footprint to take a name"""
  @init_in_parent
  def __init__(self, name: StringLike):
    super().__init__()
    self.tp_name = self.ArgParameter(name)


class RfConnectorAntenna(Antenna):
  """RF connector used as an antenna"""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.conn = self.Block(RfConnector())
    self.connect(self.conn.sig, self.a)
    self.connect(self.conn.gnd, self.gnd)


@abstract_block
class UflConnector(RfConnector):
  """Base class for a U.FL / IPEX / UMCC connector, miniature RF connector."""


@abstract_block
class SmaConnector(RfConnector):
  """Base class for a SMA coax connector."""


@abstract_block
class SmaMConnector(SmaConnector):
  """Base class for a SMA M connector, pin with external threads.
  Typically used on the antenna itself."""


@abstract_block
class SmaFConnector(SmaConnector):
  """Base class for a SMA F connector, socket with internal threads.
  Typically used for an antenna connector for sub-2.4GHz applications; 2.4GHz uses RP-SMA."""
