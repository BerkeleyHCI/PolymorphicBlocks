import unittest

from edg import *


class FpgaTest(JlcBoardTop):
  """A test design that uses a FPGA.
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
      self.fpga = imp.Block(Ice40up5k_Sg48())

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.fpga.gpio.request('sw1'))
      (self.cdone, ), _ = self.chain(self.fpga.cdone, imp.Block(IndicatorLed()))

      (self.usb_bitbang, self.usb_esd), _ = self.chain(imp.Block(UsbBitBang()), imp.Block(UsbEsdDiode()),
                                                       self.usb.usb)
      self.connect(self.usb_bitbang.dp_pull, self.fpga.gpio.request('usb_dp_pull'))
      self.connect(self.usb_bitbang.dp, self.fpga.gpio.request('usb_dp'))
      self.connect(self.usb_bitbang.dm, self.fpga.gpio.request('usb_dm'))

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_3v3'], Ld1117),
        (['fpga', 'vcc_reg'], Ld1117),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [

        ]),
        (['fpga', 'mem', 'size'], Range.from_lower(128*1024*1024)),  # use the JLC basic part
      ],
      class_refinements=[
      ],
    )


class FpgaTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(FpgaTest)
