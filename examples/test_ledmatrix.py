import unittest
from typing import List

from edg import *


class CharlieplexedLedMatrix(GeneratorBlock):
  """A LED matrix that saves on IO pins by charlieplexing, only requiring max(rows, cols) + 1 GPIOs to control.
  Requires IOs that can tri-state, and requires scanning through rows (so not all LEDs are simultaneously on).

  Anodes (columns) are directly connected to the IO line, while the cathodes (rows) are connected through a resistor.
  """
  @init_in_parent
  def __init__(self, rows: IntLike, cols: IntLike, skip: ArrayIntLike, current_draw: RangeLike = (1, 10)*mAmp):
    super().__init__()

    self.current_draw = self.ArgParameter(current_draw)

    # note that IOs supply both the positive and negative
    self.ios = self.Port(Vector(DigitalSink.empty()))

    self.generator(self.generate, rows, cols, skip)

  def generate(self, rows: int, cols: int, skip: List[int]):
    num_ios = max(rows, cols) + 1

    io_voltage = self.ios.hull(lambda x: x.link().voltage)
    io_voltage_upper = io_voltage.upper()
    io_voltage_lower = self.ios.hull(lambda x: x.link().output_thresholds).upper()

    # first, generate the cathode resistors
    self.res = ElementDict[Resistor]()
    self.led = ElementDict[Led]()
    res_model = Resistor(
      resistance=(io_voltage_upper / self.current_draw.upper(),
                  io_voltage_lower / self.current_draw.lower())
    )
    for row in range(rows):
      self.res[str(row)] = res = self.Block(res_model)
      self.connect(self.ios.append_elt(str(row), DigitalSink.empty()),
                   res.b.as_digital_sink(
                     current_draw=io_voltage / res.actual_resistance * cols
                   ))
    for row in range(rows):
      for col in range(cols):
        self.led[str(row*col)] = self.Block(Led())
        



class LedMatrixTest(JlcBoardTop):
  """A USB-connected WiFi-enabled LED matrix that demonstrates a charlieplexing LEX matrix generator.
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.rgb = imp.Block(IndicatorSinkRgbLed())  # status RGB
      self.connect(self.mcu.gpio.allocate_vector('rgb'), self.rgb.signals)

      self.matrix = imp.Block(CharlieplexedLedMatrix(5, 5))
      self.connect(self.mcu.gpio.allocate_vector('led'), self.matrix.ios)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Ldl1117),  # TBD find one that is in stock

        (['driver', 'fet'], DigikeyFet),
        (['driver', 'diode'], DigikeySmtDiode),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [

        ]),

        (['prot_3v3', 'diode', 'require_basic_part'], False),
        (['prot_analog', 'diode', 'require_basic_part'], False),

        (['usb_esd', 'require_basic_part'], False),
      ],
      class_values=[
        (TestPoint, ['require_basic_part'], False),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class LedMatrrixTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(LedMatrixTest)
