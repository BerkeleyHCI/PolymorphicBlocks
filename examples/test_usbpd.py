import os
import unittest

from edg import *
import edg_core.TransformUtil as tfu


class UsbPdTest(Block):
  def contents(self) -> None:
    super().contents()

    # USB Domain
    self.usb = self.Block(UsbCReceptacle(voltage_out=(9, 20)*Volt, current_limits=(0, 2)*Amp))  # TODO 4.5 -> 20
    (self.csr,), _ = self.chain(self.usb.pwr, self.Block(CurrentSenseResistor((1, 5)*mOhm, (0, 2)*Amp)))

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      (self.usb_reg, ), _ = self.chain(
        self.csr.pwr_out,  # TODO system should be upstream of current monitor
        imp.Block(BuckConverter(output_voltage=(4.2, 4.75)*Volt))
      )

      (self.reg_5v, ), _ = self.chain(
        self.usb.pwr,
        imp.Block(BuckConverter(output_voltage=5.0*Volt(tol=0.1)))
      )

    self.usb2 = self.Block(UsbDeviceCReceptacle())
    self.diode_merge = self.Block(DiodePowerMerge(voltage_drop=(0, 0.35)*Volt))
    self.connect(self.usb2.pwr, self.diode_merge.pwr_in1)
    self.connect(self.usb_reg.pwr_out, self.diode_merge.pwr_in2)

    self.gnd_merge = self.Block(MergedElectricalSource())
    self.connect(self.usb.gnd, self.gnd_merge.sink1)
    self.connect(self.usb2.gnd, self.gnd_merge.sink2)

    self.ldo = self.Block(LinearRegulator(3.3*Volt(tol=0.05)))
    self.connect(self.diode_merge.pwr_out, self.ldo.pwr_in)
    self.connect(self.ldo.gnd, self.gnd_merge.source)

    self.v3v3 = self.connect(self.usb_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.ldo.pwr_out, [Power]),
        ImplicitConnect(self.ldo.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48(frequency=12 * MHertz(tol=0.005)))
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetTc2050Nl()), self.mcu.swd)
      (self.crystal, ), _ = self.chain(self.mcu.xtal, imp.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005))))  # TODO can we not specify this and instead infer from MCU specs?

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb_0)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.red)
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.green)
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.blue)

    with self.implicit_connect(
        ImplicitConnect(self.ldo.pwr_out, [Power]),
        ImplicitConnect(self.ldo.gnd, [Common]),
    ) as imp:
      (self.csr_div1, self.csr_amp1), _ = self.chain(
        self.csr.sense_in,
        imp.Block(SignalDivider(ratio=(3/20*0.85, 3/20*0.9), impedance=(1000, 10000)*Ohm)),
        imp.Block(OpampFollower()),
        self.mcu.new_io(AnalogSink))
      (self.csr_div2, self.csr_amp2), _ = self.chain(
        self.csr.sense_out,
        imp.Block(SignalDivider(ratio=(3/20*0.85, 3/20*0.9), impedance=(1000, 10000)*Ohm)),
        imp.Block(OpampFollower()),
        self.mcu.new_io(AnalogSink))

      (self.vbussense, ), _ = self.chain(
        self.usb.pwr,
        imp.Block(VoltageDivider(output_voltage=(1.2, 3) * Volt, impedance=(100, 1000) * Ohm)),
        self.mcu.new_io(AnalogSink))

    with self.implicit_connect(
        ImplicitConnect(self.reg_5v.pwr_out, [Power]),
        ImplicitConnect(self.mcu.gnd, [Common]),
    ) as imp:
      (self.spk_drv, self.spk), _ = self.chain(
        self.mcu.new_io(AnalogSource),
        imp.Block(Lm4871()),
        self.Block(Speaker())
      )

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())


class UsbPdTestTestCase(unittest.TestCase):
  def test_design(self) -> None:
    ElectronicsDriver().generate_write_block(
      UsbPdTest(),
      os.path.splitext(__file__)[0],
      instance_refinements={
        tfu.Path.empty().append_block('usb_reg'): Tps54202h,
        tfu.Path.empty().append_block('reg_5v'): Tps54202h,
        tfu.Path.empty().append_block('ldo'): Ap2204k,
        tfu.Path.empty().append_block('csr_amp1').append_block('amp'): Mcp6001,
        tfu.Path.empty().append_block('csr_amp2').append_block('amp'): Mcp6001,
        tfu.Path.empty().append_block('rgb').append_block('package'): ThtRgbLed,
      }
    )
