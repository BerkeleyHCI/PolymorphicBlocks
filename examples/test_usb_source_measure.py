import unittest

from edg import *


class UsbSourceMeasureTest(Block):
  def contents(self) -> None:
    super().contents()

    # USB PD port that supplies power to the load
    self.pwr_usb = self.Block(UsbCReceptacle(voltage_out=(4.5, 22)*Volt, current_limits=(0, 5)*Amp))

    # Data-only USB port, for example to connect to a computer that can't source USB PD
    # so the PD port can be connected to a dedicated power brick.
    self.data_usb = self.Block(UsbCReceptacle())

    # TODO next revision: add a USB data port switch so the PD port can also take data

    self.gnd_merge = self.Block(MergedVoltageSource())
    self.connect(self.pwr_usb.gnd, self.gnd_merge.sink1)
    self.connect(self.data_usb.gnd, self.gnd_merge.sink2)

    self.gnd = self.connect(self.gnd_merge.source)
    self.vusb = self.connect(self.pwr_usb.pwr)

    with self.implicit_connect(
        ImplicitConnect(self.gnd_merge.source, [Common]),
    ) as imp:
      (self.reg_5v, self.reg_3v3), _ = self.chain(
        self.pwr_usb.pwr,
        imp.Block(BuckConverter(output_voltage=5.0*Volt(tol=0.1))),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        # TODO next revision: 3.0 volt high precision LDO?
      )

      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.reg_3v3.pwr_out, [Power]),
        ImplicitConnect(self.reg_3v3.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48(frequency=12 * MHertz(tol=0.005)))
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetTc2050Nl()), self.mcu.swd)
      (self.crystal, ), _ = self.chain(self.mcu.xtal, imp.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005))))  # TODO can we not specify this and instead infer from MCU specs?

      (self.usb_esd, ), _ = self.chain(self.data_usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb_0)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.red)
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.green)
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.blue)

    # TODO add FUSB302B PD interface
    # TODO add DACs
    # TODO add analog feedback control chain
    # TODO add power transistors and sensors
    # TODO add UI elements: output enable tactile switch + LCD + 4 directional buttons

    # TODO next revision: Blackberry trackball UI?

    # TODO next revision: add high precision ADCs
    # TODO next revision: add speaker?

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())


class UsbTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbSourceMeasureTest)
