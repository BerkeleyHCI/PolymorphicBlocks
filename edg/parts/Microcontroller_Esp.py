from ..abstract_parts import *
from .PassiveConnector_Header import PinHeader254
from .PassiveConnector_TagConnect import TagConnect


# contains common blocks for ESP microcontrollers


@abstract_block_default(lambda: EspProgrammingPinHeader254)
class EspProgrammingHeader(ProgrammingConnector):
  """Abstract programming header for ESP series micros, defining a UART connection.
  Circuitry to reset / enter programming mode must be external."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.uart = self.Port(UartPort.empty())


class EspProgrammingAutoReset(BlockInterfaceMixin[EspProgrammingHeader]):
  """Mixin for ESP programming header with auto-reset and auto-boot pins"""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.en = self.Port(DigitalSource.empty(), optional=True)  # effectively a reset pin
    self.boot = self.Port(DigitalSource.empty(), optional=True)  # IO0 on ESP32, IO9 on ESP32C3


class EspProgrammingPinHeader254(EspProgrammingHeader):
  """Programming header for ESP series micros using 2.54mm headers, matching the pinning in the reference schematics."""
  def contents(self) -> None:
    super().contents()

    self.conn = self.Block(PinHeader254())
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    # RXD, TXD reversed to reflect the programmer's side view
    self.connect(self.uart.rx, self.conn.pins.request('2').adapt_to(DigitalSink()))
    self.connect(self.uart.tx, self.conn.pins.request('3').adapt_to(DigitalSource()))
    self.connect(self.gnd, self.conn.pins.request('4').adapt_to(Ground()))


class EspProgrammingTc2030(EspProgrammingAutoReset, EspProgrammingHeader):
  """UNOFFICIAL tag connect header, based on a modification of the FT232 cable
  (https://www.tag-connect.com/product/tc2030-ftdi-ttl-232rg-vsw3v3)
  but adding the auto-programming pins (and using DTR instead of CTS into the cable).
  Power pins compatible with the official SWD header.

  Per boot docs, EN is connected to RTS and boot is connected to DTR (CTS on the original pinning,
  since it doesn't have a DTR pin).
  """
  def contents(self) -> None:
    super().contents()

    self.conn = self.Block(TagConnect(6))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.uart.rx, self.conn.pins.request('3').adapt_to(DigitalSink()))
    self.connect(self.uart.tx, self.conn.pins.request('4').adapt_to(DigitalSource()))
    self.connect(self.gnd, self.conn.pins.request('5').adapt_to(Ground()))

    self.connect(self.en, self.conn.pins.request('6').adapt_to(DigitalSource()))  # RTS
    self.connect(self.boot, self.conn.pins.request('2').adapt_to(DigitalSource()))  # CTS


@non_library
class HasEspProgramming(IoController, GeneratorBlock):
  """A mixin for a block (typically an IoController wrapper) that has an ESP style programming header.
  Can generate into the standard UART cable, the auto-programming header, or TODO a boundary port."""
  @init_in_parent
  def __init__(self, programming: StringLike = "uart-button"):
    super().__init__()
    self.programming = self.ArgParameter(programming)  # programming connector to generate
    self.generator_param(self.programming)
    self.program_uart_node = self.connect()
    self.program_en_node = self.connect()
    self.program_boot_node = self.connect()

  def generate(self):
    super().generate()
    programming = self.get(self.programming)

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.prog = imp.Block(EspProgrammingHeader())
      self.connect(self.program_uart_node, self.prog.uart)
      if programming == "uart-button":  # default, uart-only header with boot button
        self.boot = imp.Block(DigitalSwitch())
        self.connect(self.boot.out, self.program_boot_node)
      elif programming == "uart-auto":  # UART with auto-programming
        auto_prog = self.prog.with_mixin(EspProgrammingAutoReset())
        self.connect(self.program_en_node, auto_prog.en)
        self.connect(self.program_boot_node, auto_prog.boot)
      elif programming == "uart-auto-button":  # both, where the boot button can be used with USB for example
        self.boot = imp.Block(DigitalSwitch())
        self.connect(self.boot.out, self.program_boot_node)
        auto_prog = self.prog.with_mixin(EspProgrammingAutoReset())
        self.connect(self.program_en_node, auto_prog.en)
        self.connect(self.program_boot_node, auto_prog.boot)
      else:
        self.require(False, "unknown programming connector mode")


class EspAutoProgram(Interface, KiCadSchematicBlock):
  """Auto-programming circuit for the ESP series, to drive the target EN (reset) and BOOT (e.g., IO0) pins."""
  def __init__(self):
    super().__init__()
    self.dtr = self.Port(DigitalSink.empty())
    self.rts = self.Port(DigitalSink.empty())

    self.en = self.Port(DigitalSource.empty())
    self.boot = self.Port(DigitalSource.empty())

  def contents(self):
    super().contents()
    signal_voltage = self.dtr.link().voltage.hull(self.rts.link().voltage)
    signal_thresholds = self.dtr.link().output_thresholds.hull(self.rts.link().output_thresholds)
    bjt_model = Bjt(collector_voltage=signal_voltage, collector_current=(0, 0)*Amp, channel='NPN')
    self.q_en = self.Block(bjt_model)
    self.q_boot = self.Block(bjt_model)

    output_model = DigitalSource(voltage_out=signal_voltage, current_limits=(0, 0)*Amp,  # simplified for signal only
                                 output_thresholds=signal_thresholds)
    self.import_kicad(
      self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'dtr': DigitalSink(),
        'rts': DigitalSink(),
        'en':  output_model,
        'boot': output_model
      })
