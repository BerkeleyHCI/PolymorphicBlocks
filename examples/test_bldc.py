import unittest

from edg import *


class BldcDriverBoard(JlcBoardTop):
  """Test BLDC (brushless DC motor) driver circuit with position feedback and USB PD
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle(
      voltage_out=(5.0*0.9, 12*1.1)*Volt,
      current_limits=(0, 5)*Amp))

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.prot_vusb, self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
        imp.Block(ProtectionZenerDiode(voltage=15*Volt(tol=0.1))),
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
      (self.sw2, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw2'))
      (self.sw3, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw3'))

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

      self.pd = imp.Block(Fusb302b())
      self.connect(self.usb.pwr, self.pd.vbus)
      self.connect(self.usb.cc, self.pd.cc)
      (self.i2c_pull, self.i2c_tp), _ = self.chain(
        self.mcu.i2c.request(), imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.pd.i2c)
      self.connect(self.mcu.gpio.request('pd_int'), self.pd.int)


    # Misc board
    self.duck = self.Block(DuckLogo())
    self.lemur = self.Block(LemurLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
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


class BldcDriverTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(BldcDriverBoard)
