import unittest

from edg import *


class TestBlinkyIncomplete(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
    self.connect(self.usb.pwr, self.mcu.pwr)
    self.connect(self.mcu.gpio.request('led'), self.led.signal)


class TestBlinkyComplete(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.usb.gnd, self.buck.gnd, self.mcu.gnd, self.led.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)
    self.connect(self.buck.pwr_out, self.mcu.pwr)
    self.connect(self.mcu.gpio.request('led'), self.led.signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class TestBlinkyExpanded(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.mcu = self.Block(Stm32f103_48())
    self.connect(self.usb.gnd, self.buck.gnd, self.mcu.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)
    self.connect(self.buck.pwr_out, self.mcu.pwr)

    self.sw = self.Block(DigitalSwitch())
    self.connect(self.mcu.gpio.request('sw'), self.sw.out)
    self.connect(self.usb.gnd, self.sw.gnd)

    self.led = ElementDict[IndicatorLed]()
    for i in range(4):
      self.led[i] = self.Block(IndicatorLed())
      self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)
      self.connect(self.usb.gnd, self.led[i].gnd)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class TestBlinkyImplicit(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.buck.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.buck.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Stm32f103_48())

      self.sw = imp.Block(DigitalSwitch())
      self.connect(self.mcu.gpio.request('sw'), self.sw.out)

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.gpio.request(f'led{i}'), self.led[i].signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class TestBlinkyChain(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.buck.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.buck.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Stm32f103_48())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class TestBlinkyMicro(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.buck.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.buck.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led0=26',
          'led1=27',
          'led2=28',
          'led3=29',
        ])
      ])


class Lf21215tmr_Device(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vcc = self.Port(
      VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0.5, 2.0)*uAmp))
    self.gnd = self.Port(Ground())

    self.vout = self.Port(DigitalSource.from_supply(
      self.gnd, self.vcc,
      current_limits=(-9, 9)*mAmp,
      output_threshold_offset=(0.2, -0.3)
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.vcc,
        '2': self.vout,
        '3': self.gnd,
      },
      mfr='Littelfuse', part='LF21215TMR',
      datasheet='https://www.littelfuse.com/~/media/electronics/datasheets/magnetic_sensors_and_reed_switches/littelfuse_tmr_switch_lf21215tmr_datasheet.pdf.pdf'
    )


class Lf21215tmr(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Lf21215tmr_Device())

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(VoltageSink.empty(), [Common])
    self.out = self.Port(DigitalSource.empty())

    self.cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))

    self.connect(self.ic.vcc, self.cap.pwr, self.pwr)
    self.connect(self.ic.gnd, self.cap.gnd, self.gnd)
    self.connect(self.ic.vout, self.out)

  def contents(self) -> None:
    super().contents()


class Lf21215tmr_Export(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Lf21215tmr_Device())
    self.pwr = self.Export(self.ic.vcc, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.out = self.Export(self.ic.vout)

    self.cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))
    self.connect(self.cap.pwr, self.pwr)
    self.connect(self.cap.gnd, self.gnd)

  def contents(self) -> None:
    super().contents()


class TestBlinkyWithLibrary(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.buck.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.buck.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))

      self.mag = imp.Block(Lf21215tmr())
      self.connect(self.mcu.gpio.request('mag'), self.mag.out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led0=26',
          'led1=27',
          'led2=28',
          'led3=29',
        ])
      ])


class TestBlinkyWithLibraryExport(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.buck.gnd)
    self.connect(self.usb.pwr, self.buck.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.buck.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))

      self.mag = imp.Block(Lf21215tmr_Export())
      self.connect(self.mcu.gpio.request('mag'), self.mag.out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led0=26',
          'led1=27',
          'led2=28',
          'led3=29',
        ])
      ])


class BlinkyTestCase(unittest.TestCase):
  def test_design_incomplete(self) -> None:
    with self.assertRaises(CompilerCheckError):
      compile_board_inplace(TestBlinkyIncomplete)

  def test_design_complete(self) -> None:
    compile_board_inplace(TestBlinkyComplete)

  def test_design_expnaded(self) -> None:
    compile_board_inplace(TestBlinkyExpanded)

  def test_design_implicit(self) -> None:
    compile_board_inplace(TestBlinkyImplicit)

  def test_design_chain(self) -> None:
    compile_board_inplace(TestBlinkyChain)

  def test_design_micro(self) -> None:
    compile_board_inplace(TestBlinkyMicro)

  def test_design_library(self) -> None:
    compile_board_inplace(TestBlinkyWithLibrary)

  def test_design_export(self) -> None:
    compile_board_inplace(TestBlinkyWithLibraryExport)
