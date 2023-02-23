from electronics_model import Block, abstract_block


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
class ProgrammableController(Block):
  """General programmable controller."""
  pass


@abstract_block
class Microcontroller(ProgrammableController):
  """Microcontroller (with embedded-class processor) with its surrounding application circuit."""
  pass


@abstract_block
class Fpga(ProgrammableController):
  """FPGA with its surrounding application circuit."""
  pass


@abstract_block
class Memory(Block):
  """Memory device (including sockets and card sockets) with its surrounding application circuit."""
  pass


@abstract_block
class RealtimeClock(Block):
  """Realtime clock device."""
  pass


@abstract_block
class Interface(Block):
  """Interface devices, eg CAN transceiver (CAN <-> SPI / I2C interface),
  and including analog interfaces (ADCs, DACs)."""
  pass


@abstract_block
class AnalogToDigital(Interface):
  pass


@abstract_block
class DigitalToAnalog(Interface):
  pass


@abstract_block
class Radiofrequency(Block):
  """Radiofrequency devices."""
  pass


@abstract_block
class PowerConditioner(Block):
  """Power conditioning circuits that provide a stable and/or safe power supply, eg voltage regulators"""
  pass


@abstract_block
class PowerSwitch(Block):
  """Power switching circuits, eg FET switches and motor drivers"""
  pass


@abstract_block
class MotorDriver(PowerSwitch):
  pass


@abstract_block
class BrushedMotorDriver(MotorDriver):
  """A brushed motor driver, or at least the power stage for one."""
  pass


@abstract_block
class BldcDriver(MotorDriver):
  """A brushless motor driver, or at least the power stage for one - may be as simple a 3 half-bridges."""
  pass


@abstract_block
class Connector(Block):
  """Connectors, including card sockets."""
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
class Sensor(Block):
  """Any kind of sensor with any interface. Multi-packed sensors may inherit from multiple categories"""
  pass


@abstract_block
class Accelerometer(Sensor):
  pass


@abstract_block
class Gyroscope(Sensor):
  pass


@abstract_block
class Magnetometer(Sensor):
  pass


@abstract_block
class DistanceSensor(Sensor):
  pass


@abstract_block
class Mechanical(Block):
  """Nonelectrical footprint, including plated and NPTH mounting holes."""
  pass


@abstract_block
class Testing(Block):
  """Blocks for testing (eg, test points) and programming (eg, programming headers)."""
  pass


@abstract_block
class ProgrammingConnector(Connector, Testing):
  """Programming / debug / JTAG connectors."""
  pass


@abstract_block
class TypedTestPoint(Testing):
  """Test point with a typed port (eg, VoltageSink, instead of Passive)."""
  pass


@abstract_block
class TypedJumper(Testing):
  """Jumper with typed ports (eg, VoltageSource-VoltageSink, instead of Passive)."""
  pass


@abstract_block
class Internal(Block):
  """Internal blocks that are primarily an implementation detail or not re-usable"""
  pass


@abstract_block
class DiscreteComponent(Internal, Block):
  """Discrete component that typically provides untyped ports (not to be be used directly), as a component to be used in an application circuit."""
  pass


@abstract_block
class DiscreteSemiconductor(DiscreteComponent):
  """Discrete semiconductor product, eg diodes and FETs, typically used as part of an application circuit."""
  pass


@abstract_block
class PassiveComponent(DiscreteComponent):
  """Passives components, typically used as part of an application circuit."""
  pass


@abstract_block
class DummyDevice(Internal):
  """Non-physical "device" used to affect parameters."""
  pass


@abstract_block
class Label(Block):
  """Nonfunctional footprint, including copper and silkscreen labels."""
  pass
