import unittest

from edg import *


class NewBlinkyBasic(BoardTop):
  def contents(self) -> None:
    super().contents()
    self.led2 = self.Block(IndicatorLed())

    self.usb = self.Block(UsbCReceptacle())
    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.usb.pwr, self.mcu.pwr)
    self.connect(self.usb.gnd, self.mcu.gnd, self.led.gnd)
    self.connect(self.mcu.gpio.request(), self.led.signal)


class NewBlinkyOvervolt(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Stm32f103_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.gpio.request(), self.led.signal)
    self.connect(self.mcu.gnd, self.led.gnd)
    self.usb = self.Block(UsbCReceptacle())
    self.connect(self.usb.pwr, self.mcu.pwr)
    self.connect(self.mcu.gnd, self.usb.gnd)


class NewBlinkyBuck(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(IoController())
    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.gpio.request(), self.led.signal)
    self.connect(self.mcu.gnd, self.led.gnd)
    self.usb = self.Block(UsbCReceptacle())
    self.connect(self.mcu.gnd, self.usb.gnd)
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.connect(self.usb.pwr, self.buck.pwr_in)
    self.connect(self.usb.gnd, self.buck.gnd)
    self.connect(self.mcu.pwr, self.buck.pwr_out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['buck'], Tps561201),
      ],
      instance_values=[
        # JLC does not have frequency specs, must be checked TODO
        (['buck', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
      ],
    )


class NewBlinkyRefactored(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.connect(self.usb.pwr, self.buck.pwr_in)
    self.connect(self.usb.gnd, self.buck.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.gpio.request(), self.led[i].signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['buck'], Tps561201),
      ],
      instance_values=[
        # JLC does not have frequency specs, must be checked TODO
        (['buck', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
      ],
    )


class Ref_Lf21215tmr_Device(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vcc = self.Port(
      VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0, 1.5)*uAmp),
      [Power])

    self.gnd = self.Port(
      VoltageSink(voltage_limits=Default(RangeExpr.ALL), current_draw=Default(RangeExpr.ZERO)),
      [Common])

    self.vout = self.Port(DigitalSource.from_supply(
      self.gnd, self.vcc,
      output_threshold_offset=(0.2, -0.3)
    ))
    # Or, the more explicit way of writing it
    # self.vout = self.Port(DigitalSource(
    #   voltage_out=(self.gnd.link().voltage.lower(),
    #                self.vcc.link().voltage.upper()),
    #   current_limits=15 * uAmp(tol=0),
    #   output_thresholds=(self.gnd.link().voltage.upper() + 0.2 * Volt,
    #                      self.vcc.link().voltage.lower() - 0.3 * Volt)
    # ))

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


class Ref_Lf21215tmr(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Ref_Lf21215tmr_Device())
    self.pwr = self.Export(self.ic.vcc, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.out = self.Export(self.ic.vout)

    self.cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2)
    )).connected(self.gnd, self.pwr)

    # Or, the more explicit way of writing it
    # self.pwr = self.Port(VoltageSink(), [Power])
    # self.gnd = self.Port(VoltageSink(), [Common])
    # self.out = self.Port(DigitalSource())
    # self.connect(self.ic.vcc, self.cap.pwr, self.pwr)
    # self.connect(self.ic.gnd, self.cap.gnd, self.gnd)
    # self.connect(self.ic.vout, self.out)

  def contents(self) -> None:
    super().contents()


class NewBlinkyMagsense(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.vin = self.connect(self.usb.pwr, self.buck.pwr_in)
    self.gnd = self.connect(self.usb.gnd, self.buck.gnd)
    self.v3v3 = self.connect(self.buck.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.gpio.request(), self.led[i].signal)

      self.sens = imp.Block(Ref_Lf21215tmr())
      self.connect(self.mcu.gpio.request(), self.sens.out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['buck'], Tps561201),
      ],
      instance_values=[
        # JLC does not have frequency specs, must be checked TODO
        (['buck', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
      ],
    )


class NewBlinkyLightsense(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbMicroBReceptacle())
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.v5 = self.connect(self.usb.pwr, self.buck.pwr_in)
    self.gnd = self.connect(self.usb.gnd, self.buck.gnd)
    self.v3v3 = self.connect(self.buck.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.esd = imp.Block(UsbEsdDiode())
      self.connect(self.usb.usb, self.mcu.usb.request(), self.esd.usb)

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.gpio.request(), self.led[i].signal)

      self.als = imp.Block(Ref_Bh1620fvc(20000, (2.7, 3.0)*Volt))
      self.amp = imp.Block(OpampFollower())  # "optional", output impedance is "only" 2x larger than MCU's input
      self.connect(self.als.vout, self.amp.input)
      self.connect(self.amp.output, self.mcu.adc.request())

      self.lcd = imp.Block(Qt096t_if09())
      self.connect(self.mcu.spi.request(), self.lcd.spi)
      self.connect(self.mcu.gpio.request(), self.lcd.cs)
      self.connect(self.mcu.gpio.request(), self.lcd.rs)
      self.connect(self.mcu.gpio.request(), self.lcd.reset)
      self.connect(self.mcu.gpio.request(), self.lcd.led)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['buck'], Tps561201),
      ],
      instance_values=[
        # JLC does not have frequency specs, must be checked TODO
        (['buck', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
      ],
      class_refinements=[
        (Opamp, Mcp6001),
      ])


class Ref_Bh1620fvc_Device(FootprintBlock):
  @init_in_parent
  def __init__(self, impedance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.vcc = self.Port(
      VoltageSink(voltage_limits=(2.4, 5.5)*Volt, current_draw=(0.2, 97)*uAmp))
    self.gnd = self.Port(Ground())
    gc_model = DigitalSink.from_supply(self.gnd, self.vcc,
                                       input_threshold_abs=(0.4, 2.0))
    self.gc1 = self.Port(gc_model)
    self.gc2 = self.Port(gc_model)

    self.iout = self.Port(AnalogSource(voltage_out=(0, 3.0)*Volt,
                                       current_limits=(0, 7.5)*mAmp,
                                       impedance=impedance))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-553',
      {'1': self.vcc,
       '2': self.gnd,
       '3': self.gc1,
       '4': self.gc2,
       '5': self.iout,
       },
      mfr='Rohm', part='BH1620FVC',
      datasheet='http://rohmfs.rohm.com/en/products/databook/datasheet/ic/sensor/light/bh1620fvc-e.pdf'
    )


class Ref_Bh1620fvc(Block):
  @init_in_parent
  def __init__(self, max_illuminance: FloatLike, target_voltage: RangeLike) -> None:
    super().__init__()

    self.target_voltage = self.ArgParameter(target_voltage)  # needed for the typer to not be unhappy
    # in L-gain mode, Vout = 0.0057e-6 * Ev * Rl
    rload = self.target_voltage / 0.0057e-6 / max_illuminance

    self.ic = self.Block(Ref_Bh1620fvc_Device(rload))
    self.pwr = self.Export(self.ic.vcc, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.vout = self.Export(self.ic.iout)

    self.gc1_pur = self.Block(PullupResistor(resistance=4.7*kOhm(tol=0.1))).connected(self.pwr, self.ic.gc1)
    self.gc2_pur = self.Block(PullupResistor(resistance=4.7*kOhm(tol=0.1))).connected(self.pwr, self.ic.gc2)

    self.require(rload.within((1, 1000)*kOhm))
    self.load = self.Block(Resistor(resistance=rload))
    self.connect(self.vout, self.load.a.adapt_to(AnalogSink()))
    self.connect(self.gnd, self.load.b.adapt_to(Ground()))

  def contents(self) -> None:
    super().contents()


class BlinkyNewTestCase(unittest.TestCase):
  def test_design_broken(self) -> None:
    with self.assertRaises(CompilerCheckError):
      compile_board_inplace(NewBlinkyBasic)
    with self.assertRaises(CompilerCheckError):
      compile_board_inplace(NewBlinkyOvervolt)

  def test_design_buck(self) -> None:
    compile_board_inplace(NewBlinkyBuck)

  def test_design_refactored(self) -> None:
    compile_board_inplace(NewBlinkyRefactored)

  def test_design_magsense(self) -> None:
    compile_board_inplace(NewBlinkyMagsense)

  def test_design_lightsense(self) -> None:
    compile_board_inplace(NewBlinkyLightsense)
