import unittest

from edg import *


class DiscreteMutlilevelBuckConverter(GeneratorBlock):
  """Flying capacitor multilevel buck converter. Trades more switches for smaller inductor size:
  for number of levels N, inductor value is reduced by a factor of (N-1)^2.
  2 levels is standard switching converter (1 pair of switches in a synchronous topology).
  Each additional level adds another switch pair.
  Even number of levels generally have good balancing, odd number of levels may have balancing issues.

  Controls are broken out at the top level, at logic level referenced to the converter ground.
  Requires both a power voltage source and gate drive voltage source.

  Instead of a target output voltage (since the output is controlled by external PWMs), this takes
  in operating duty ratios for component sizing. Current is calculated by current drawn at the output.

  Generates a bootstrap capacitor ladder to generate the gate drive voltages for each switch.
  Generates a gate driver for each switch pair, in normal operation each gate driver should be
  either be high or low (but not both or none).
  Generates a digital isolator for each gate driver that is offset from ground.
  """
  def __init__(self, levels: IntLike = 2, ratios: RangeLike = (0.25, 0.75)):
    super().__init__()
    self.pwr_in = self.Port(VoltageSink.empty())
    self.pwr_out = self.Port(VoltageSource.empty())
    self.gnd = self.Port(Ground.empty(), [Common])

    self.pwr_gate = self.Port(VoltageSink.empty())
    self.pwms = self.Port(Vector(DigitalSink.empty()))

    self.generator(self.generate, levels, ratios)

  def generate(self, levels: int, ratios: Range):
    pass


class FcmlTest(JlcBoardTop):
  """FPGA + FCML (flying cpacitor multilevel converter) test circuit
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

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

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))
      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),  # TODO replace with FPGA
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class FcmlTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(FcmlTest)
