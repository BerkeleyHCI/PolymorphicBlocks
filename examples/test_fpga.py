import unittest

from edg import *


class FpgaTest(JlcBoardTop):
  """A test design that uses a FPGA.
  """
  def contents(self) -> None:
    super().contents()

    self.usb_fpga = self.Block(UsbCReceptacle())
    self.usb_mcu = self.Block(UsbCReceptacle())

    self.vusb_merge = self.Block(MergedVoltageSource()).connected_from(self.usb_fpga.pwr, self.usb_mcu.pwr)
    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(self.usb_fpga.gnd, self.usb_mcu.gnd)

    self.vusb = self.connect(self.vusb_merge.pwr_out)
    self.gnd = self.connect(self.gnd_merge.pwr_out)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.vusb_merge.pwr_out)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.gnd_merge.pwr_out)

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
      # FPGA BLOCK
      self.fpga = imp.Block(Ice40up5k_Sg48())

      (self.fpga_sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.fpga.gpio.request('sw'))
      (self.fpga_led, ), _ = self.chain(self.fpga.gpio.request('led'), imp.Block(IndicatorLed()))
      (self.cdone, ), _ = self.chain(self.fpga.cdone, imp.Block(IndicatorLed()))

      (self.usb_fpga_bitbang, self.usb_fpga_esd), _ = self.chain(
        imp.Block(UsbBitBang()).connected_from(
          self.fpga.gpio.request('usb_dp_pull'), self.fpga.gpio.request('usb_dp'), self.fpga.gpio.request('usb_dm')),
        imp.Block(UsbEsdDiode()),
        self.usb_fpga.usb)

      # MICROCONTROLLER BLOCK
      self.mcu = imp.Block(Rp2040())

      (self.mcu_sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))
      (self.mcu_led, ), _ = self.chain(self.mcu.gpio.request('led'), imp.Block(IndicatorLed()))

      (self.usb_mcu_esd, ), _ = self.chain(self.mcu.usb.request('usb'), imp.Block(UsbEsdDiode()),
                                           self.usb_mcu.usb)

      # FPGA <-> MCU CONNECTIONS
      # Ideally this could request an anonymous sub-array (instead of 4 separate connections),
      # but sadly that isn't supported (yet?).
      # The 4 GPIOs could be, for example, an SPI connection.
      self.connect(self.fpga.gpio.request('mcu0'), self.mcu.gpio.request('fpga0'))
      self.connect(self.fpga.gpio.request('mcu1'), self.mcu.gpio.request('fpga1'))
      self.connect(self.fpga.gpio.request('mcu2'), self.mcu.gpio.request('fpga2'))
      self.connect(self.fpga.gpio.request('mcu3'), self.mcu.gpio.request('fpga3'))

    # Misc board
    self.lemur = self.Block(LemurLogo())
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
        (['fpga', 'pin_assigns'], [

        ]),
        (['mcu', 'pin_assigns'], [

        ]),
      ],
      class_refinements=[
      ],
    )


class FpgaTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(FpgaTest)
