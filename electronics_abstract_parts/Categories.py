from electronics_model import *
from itertools import chain


@abstract_block
class E24_SeriesDevice(Block):
  """Non-physical "E24 series device" used to affect parameters."""

  E24_SERIES = [
    [1.0],  # E1
    [2.2, 4.7],  # E3
    [1.5, 3.3, 6.8],  # E6
    [1.2, 1.8, 2.7, 3.9, 5.6, 8.2],  # E12
    [1.1, 1.3, 1.6, 2.0, 2.4, 3.0, 3.6, 4.3, 5.1, 6.2, 7.5, 9.1],  # E24
  ]

  # Zigzag (lower E-series first) of the E12 series
  E24_SERIES_ZIGZAG = list(chain(*E24_SERIES))

@abstract_block
class DummyDevice(Block):
  """Non-physical "device" used to affect parameters."""
  pass


@abstract_block
class DiscreteComponent(Block):
  """Discrete component that typically provides untyped ports (not to be be used directly), as a component to be used in an application circuit."""
  pass


@abstract_block
class DiscreteChip(DiscreteComponent):
  """Chip, typically used as the main device in an application circuit."""
  pass


@abstract_block
class DiscreteSemiconductor(DiscreteComponent):
  """Discrete semiconductor product, eg diodes and FETs, typically used as part of an application circuit."""
  pass


@abstract_block
class PassiveComponent(DiscreteComponent, E24_SeriesDevice):
  """Passives components, typically used as part of an application circuit."""
  pass


@abstract_block
class DiscreteApplication(Block):
  """Subcircuit around a single discrete (and usually passive) component."""
  pass


@abstract_block
class TvsDiode(DiscreteApplication):
  """Any kind of TVS diode, including multiple channel configurations."""
  pass


@abstract_block
class Filter(Block):
  """Signal conditioning subcircuit."""
  pass


@abstract_block
class AnalogFilter(Filter):
  """Analog signal conditioning subcircuit."""
  pass


@abstract_block
class DigitalFilter(Filter):
  """Digital signal conditioning block."""
  pass


@abstract_block
class IntegratedCircuit(Block):
  """Application circuit around an integrated circuit (chip)."""
  pass


@abstract_block
class Microcontroller(IntegratedCircuit):
  """Microcontroller with its surrounding application circuit."""
  pass


@abstract_block
class Memory(IntegratedCircuit):
  """Memory device (including sockets and card sockets) with its surrounding application circuit."""
  pass


@abstract_block
class RealtimeClock(IntegratedCircuit):
  """Realtime clock device."""
  pass


@abstract_block
class PowerConditioner(IntegratedCircuit):
  pass


@abstract_block
class Connector(Block):
  """Connecctors, including card sockets."""
  pass


@abstract_block
class BarrelJack(Connector):
  """Barrel jack input (socket - pin side)."""
  pass


@abstract_block
class ProgrammingConnector(Connector):
  """Programming / debug / JTAG connectors."""
  pass


@abstract_block
class Optoelectronic(Block):
  """Optoelectronic components."""
  pass


@abstract_block
class Display(Optoelectronic):
  """Pixel displays."""
  pass


@abstract_block
class Lcd(Display):
  """LCD display, where pixels absorb / reflect light, but do not directly emit light (eg, use a backlight, or are transflective)."""
  pass


@abstract_block
class Oled(Display):
  """OLED display, with the pixel density of an LCD but with infinite contrast and no backlight."""
  pass


@abstract_block
class EInk(Display):
  """E-ink display, which retains the image after power is removed."""
  pass


@abstract_block
class Light(Optoelectronic):
  """Discrete lights."""
  pass


@abstract_block
class SpecificApplicationSubcircuit(Block):
  """Subcircuit with a specific application, likely not generally applicable."""
  pass


@abstract_block
class Mechanical(Block):
  """Nonelectrical footprint, including plated and NPTH mounting holes."""
  pass


@abstract_block
class Label(Block):
  """Nonfunctional footprint, including copper and silkscreen labels."""
  pass