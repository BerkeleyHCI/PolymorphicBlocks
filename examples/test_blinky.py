import unittest

from edg import *


class TestBlinkyBasic(SimpleBoardTop):
  """The simplest cirucit, a microcontroller dev board with a LED."""
  def contents(self) -> None:
    self.mcu = self.Block(Nucleo_F303k8())
    self.led = self.Block(IndicatorLed())

    self.connect(self.led.signal, self.mcu.gpio.request())
    self.connect(self.mcu.gnd_out, self.led.gnd)


class TestBlinkyEmpty(SimpleBoardTop):
  pass


class TestBlinkyIncomplete(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
    self.connect(self.usb.pwr, self.mcu.pwr)
    self.connect(self.mcu.gpio.request('led'), self.led.signal)


class TestBlinkyRegulated(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd, self.led.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)
    self.connect(self.reg.pwr_out, self.mcu.pwr)
    self.connect(self.mcu.gpio.request('led'), self.led.signal)


class TestBlinkyComplete(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd, self.led.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)
    self.connect(self.reg.pwr_out, self.mcu.pwr)
    self.connect(self.mcu.gpio.request('led'), self.led.signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg'], Tps561201),
      ])


class TestBlinkyExpanded(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.mcu = self.Block(Stm32f103_48())
    self.connect(self.usb.gnd, self.reg.gnd, self.mcu.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)
    self.connect(self.reg.pwr_out, self.mcu.pwr)

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
        (['reg'], Tps561201),
      ])


class TestBlinkyImplicit(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.reg.pwr_out, [Power]),
        ImplicitConnect(self.reg.gnd, [Common]),
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
        (['reg'], Tps561201),
      ])


class TestBlinkyChain(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.reg.pwr_out, [Power]),
        ImplicitConnect(self.reg.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Stm32f103_48())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg'], Tps561201),
      ])


class TestBlinkyMicro(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.reg.pwr_out, [Power]),
        ImplicitConnect(self.reg.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        (self.led[i], ), _ = self.chain(self.mcu.gpio.request(f'led{i}'), imp.Block(IndicatorLed()))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg'], Tps561201),
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
    self.gnd = self.Port(Ground.empty(), [Common])
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
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.reg.pwr_out, [Power]),
        ImplicitConnect(self.reg.gnd, [Common]),
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
        (['reg'], Tps561201),
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
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.reg.pwr_out, [Power]),
        ImplicitConnect(self.reg.gnd, [Common]),
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
        (['reg'], Tps561201),
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


class LedArray(GeneratorBlock):
  @init_in_parent
  def __init__(self, count: IntLike) -> None:
    super().__init__()
    self.ios = self.Port(Vector(DigitalSink.empty()), [Input])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.count = self.ArgParameter(count)
    self.generator_param(self.count)

  def generate(self) -> None:
    super().generate()
    self.led = ElementDict[IndicatorLed]()
    for i in range(self.get(self.count)):
      io = self.ios.append_elt(DigitalSink.empty())
      self.led[i] = self.Block(IndicatorLed())
      self.connect(io, self.led[i].signal)
      self.connect(self.gnd, self.led[i].gnd)


class TestBlinkyArray(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.reg.pwr_out, [Power]),
        ImplicitConnect(self.reg.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      (self.led, ), _ = self.chain(self.mcu.gpio.request_vector('led'), imp.Block(LedArray(4)))

      # optionally, you may have also instantiated your magnetic sensor

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led_0=26',
          'led_1=27',
          'led_2=28',
          'led_3=29',
        ])
      ])


class TestBlinkyPacked(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3 * Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
        ImplicitConnect(self.reg.pwr_out, [Power]),
        ImplicitConnect(self.reg.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      (self.led, ), _ = self.chain(self.mcu.gpio.request_vector('led'), imp.Block(LedArray(4)))

      # optionally, you may have also instantiated your magnetic sensor

  def multipack(self) -> None:
    self.res_pack = self.PackedBlock(ResistorArray())
    self.pack(self.res_pack.elements.request('0'), ['led', 'led[0]', 'res'])
    self.pack(self.res_pack.elements.request('1'), ['led', 'led[1]', 'res'])
    self.pack(self.res_pack.elements.request('2'), ['led', 'led[2]', 'res'])
    self.pack(self.res_pack.elements.request('3'), ['led', 'led[3]', 'res'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led_0=26',
          'led_1=27',
          'led_2=28',
          'led_3=29',
        ])
      ])


class Hx711(KiCadSchematicBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.dout = self.Port(DigitalSource.empty())
    self.sck = self.Port(DigitalSink.empty())

    self.ep = self.Port(Passive.empty())
    self.en = self.Port(Passive.empty())
    self.sp = self.Port(Passive.empty())
    self.sn = self.Port(Passive.empty())

  def contents(self) -> None:
    super().contents()
    self.Q1 = self.Block(Bjt.Npn((0, 5)*Volt, 0*Amp(tol=0)))
    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
                      auto_adapt=True)


class TestBlinkyWithSchematicImport(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
            ImplicitConnect(self.reg.pwr_out, [Power]),
            ImplicitConnect(self.reg.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.conn = self.Block(PassiveConnector(4))
      self.sense = imp.Block(Hx711())
      self.connect(self.mcu.gpio.request('hx711_dout'), self.sense.dout)
      self.connect(self.mcu.gpio.request('hx711_sck'), self.sense.sck)
      self.connect(self.conn.pins.request('1'), self.sense.ep)
      self.connect(self.conn.pins.request('2'), self.sense.en)
      self.connect(self.conn.pins.request('3'), self.sense.sp)
      self.connect(self.conn.pins.request('4'), self.sense.sn)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ])


class Hx711Modeled(KiCadSchematicBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.dout = self.Port(DigitalSource.empty())
    self.sck = self.Port(DigitalSink.empty())

    self.ep = self.Port(Passive.empty())
    self.en = self.Port(Passive.empty())
    self.sp = self.Port(Passive.empty())
    self.sn = self.Port(Passive.empty())

  def contents(self) -> None:
    super().contents()
    self.Q1 = self.Block(Bjt.Npn((0, 5)*Volt, 0*Amp(tol=0)))
    self.import_kicad(self.file_path("resources", "Hx711.kicad_sch"),
                      conversions={
                        'pwr': VoltageSink(
                          voltage_limits=(2.6, 5.5)*Volt,
                          current_draw=(0.3 + 0.2, 1400 + 100)*uAmp),  # TODO: also model draw of external bridge?
                        'gnd': Ground(),
                        'dout': DigitalSource.from_supply(self.gnd, self.pwr),
                        'sck': DigitalSink.from_supply(self.gnd, self.pwr),
                      })


class TestBlinkyWithModeledSchematicImport(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())
    self.reg = self.Block(VoltageRegulator(3.3*Volt(tol=0.05)))
    self.connect(self.usb.gnd, self.reg.gnd)
    self.connect(self.usb.pwr, self.reg.pwr_in)

    with self.implicit_connect(
            ImplicitConnect(self.reg.pwr_out, [Power]),
            ImplicitConnect(self.reg.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.conn = self.Block(PassiveConnector(4))
      self.sense = imp.Block(Hx711Modeled())
      self.connect(self.mcu.gpio.request('hx711_dout'), self.sense.dout)
      self.connect(self.mcu.gpio.request('hx711_sck'), self.sense.sck)
      self.connect(self.conn.pins.request('1'), self.sense.ep)
      self.connect(self.conn.pins.request('2'), self.sense.en)
      self.connect(self.conn.pins.request('3'), self.sense.sp)
      self.connect(self.conn.pins.request('4'), self.sense.sn)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg'], Tps561201),
        (['mcu'], Esp32_Wroom_32),
      ])


class BlinkyTestCase(unittest.TestCase):
  def test_design_basic(self) -> None:
    compile_board_inplace(TestBlinkyBasic)  # generate this netlist as a test

  def test_design_empty(self) -> None:
    compile_board_inplace(TestBlinkyEmpty, False)

  def test_design_incomplete(self) -> None:
    with self.assertRaises(CompilerCheckError):
      compile_board_inplace(TestBlinkyIncomplete, False)

  def test_design_regulated(self) -> None:
    with self.assertRaises(CompilerCheckError):
      compile_board_inplace(TestBlinkyRegulated, False)

  def test_design_complete(self) -> None:
    compile_board_inplace(TestBlinkyComplete, False)

  def test_design_expnaded(self) -> None:
    compile_board_inplace(TestBlinkyExpanded, False)

  def test_design_implicit(self) -> None:
    compile_board_inplace(TestBlinkyImplicit, False)

  def test_design_chain(self) -> None:
    compile_board_inplace(TestBlinkyChain)  # generate this netlist as a test

  def test_design_micro(self) -> None:
    compile_board_inplace(TestBlinkyMicro, False)

  def test_design_library(self) -> None:
    compile_board_inplace(TestBlinkyWithLibrary, False)

  def test_design_export(self) -> None:
    compile_board_inplace(TestBlinkyWithLibraryExport, False)

  def test_design_array(self) -> None:
    compile_board_inplace(TestBlinkyArray, False)

  def test_design_packed(self) -> None:
    compile_board_inplace(TestBlinkyPacked, False)

  def test_design_schematic_import(self) -> None:
    compile_board_inplace(TestBlinkyWithSchematicImport, False)

  def test_design_schematic_import_modeled(self) -> None:
    compile_board_inplace(TestBlinkyWithModeledSchematicImport, False)


if __name__ == "__main__":
  # this unit test can also be run as __main__ to test a non-unit-test environment
  compile_board_inplace(TestBlinkyEmpty, False)
  compile_board_inplace(TestBlinkyComplete, False)
  compile_board_inplace(TestBlinkyWithLibrary, False)
  compile_board_inplace(TestBlinkyWithLibraryExport, False)
  compile_board_inplace(TestBlinkyArray, False)
  compile_board_inplace(TestBlinkyPacked, False)
  compile_board_inplace(TestBlinkyWithSchematicImport, False)
  compile_board_inplace(TestBlinkyWithModeledSchematicImport, False)
