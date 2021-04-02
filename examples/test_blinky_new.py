import unittest

from edg import *


class NewBlinkyOvervolt(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Lpc1549_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.digital[0], self.led.signal)
    self.connect(self.mcu.gnd, self.led.gnd)
    self.jack = self.Block(Pj_102a(voltage_out=5*Volt(tol=0.1)))
    self.swd = self.Block(SwdCortexTargetHeader())
    self.connect(self.jack.pwr, self.mcu.pwr, self.swd.pwr)
    self.connect(self.swd.swd, self.mcu.swd)
    self.connect(self.mcu.gnd, self.swd.gnd, self.jack.gnd)


class NewBlinkyBuck(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Lpc1549_48())
    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.digital[0], self.led.signal)
    self.connect(self.mcu.gnd, self.led.gnd)
    self.jack = self.Block(Pj_102a(voltage_out=5*Volt(tol=0.1)))
    self.swd = self.Block(SwdCortexTargetHeader())
    self.connect(self.mcu.pwr, self.swd.pwr)
    self.connect(self.swd.swd, self.mcu.swd)
    self.connect(self.mcu.gnd, self.swd.gnd, self.jack.gnd)
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.connect(self.jack.pwr, self.buck.pwr_in)
    self.connect(self.jack.gnd, self.buck.gnd)
    self.connect(self.mcu.pwr, self.buck.pwr_out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class NewBlinkyRefactored(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.jack = self.Block(Pj_102a(voltage_out=5*Volt(tol=0.1)))
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.connect(self.jack.pwr, self.buck.pwr_in)
    self.connect(self.jack.gnd, self.buck.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.jack.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48())
      self.swd = imp.Block(SwdCortexTargetHeader())
      self.connect(self.swd.swd, self.mcu.swd)

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.digital[i], self.led[i].signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class Ref_Lf21215tmr_Device(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vcc = self.Port(
      VoltageSink(voltage_limits=(1.8, 5.5)*Volt, current_draw=(0, 1.5)*uAmp),
      [Power])

    self.gnd = self.Port(
      VoltageSink(model=None, voltage_limits=Default(RangeExpr.ALL), current_draw=Default(RangeExpr.ZERO)),
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

    self.cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))
    self.connect(self.cap.pwr, self.pwr)
    self.connect(self.cap.gnd, self.gnd)

    # Or, the more explicit way of writing it
    # self.pwr = self.Port(VoltageSink(), [Power])
    # self.gnd = self.Port(VoltageSink(), [Common])
    # self.out = self.Port(DigitalSource())
    # self.connect(self.ic.vcc, self.cap.pwr, self.pwr)
    # self.connect(self.ic.gnd, self.cap.gnd, self.gnd)
    # self.connect(self.ic.vout, self.out)

  def contents(self) -> None:
    super().contents()


class NewBlinkyMagsense(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.jack = self.Block(Pj_102a(voltage_out=5*Volt(tol=0.1)))
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self.connect(self.jack.pwr, self.buck.pwr_in)
    self.connect(self.jack.gnd, self.buck.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.jack.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48())
      self.swd = imp.Block(SwdCortexTargetHeader())
      self.connect(self.swd.swd, self.mcu.swd)

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.digital[i], self.led[i].signal)

      self.sens = imp.Block(Ref_Lf21215tmr())
      self.connect(self.mcu.digital[4], self.sens.out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


class NewBlinkyLightsense(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbMicroBReceptacle())
    self.buck = self.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05)))
    self._v5 = self.connect(self.usb.pwr, self.buck.pwr_in)
    self._gnd = self.connect(self.usb.gnd, self.buck.gnd)
    self._v3 = self.connect(self.buck.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.buck.pwr_out, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48())
      self.esd = imp.Block(UsbEsdDiode())
      self.connect(self.usb.usb, self.mcu.usb_0, self.esd.usb)
      self.swd = imp.Block(SwdCortexTargetHeader())
      self.connect(self.swd.swd, self.mcu.swd)

      self.led = ElementDict[IndicatorLed]()
      for i in range(4):
        self.led[i] = imp.Block(IndicatorLed())
        self.connect(self.mcu.digital[i], self.led[i].signal)

      self.als = imp.Block(Ref_Bh1620fvc(20000, (2.8, 3.0)*Volt))
      self.amp = imp.Block(OpampFollower())  # "optional", output impedance is "only" 2x larger than MCU's input
      self.connect(self.als.vout, self.amp.input)
      self.connect(self.amp.output, self.mcu.adc[0])

      self.lcd = imp.Block(Qt096t_if09())
      self.connect(self.mcu.spi[0], self.lcd.spi)
      self.connect(self.mcu.digital[4], self.lcd.cs)
      self.connect(self.mcu.digital[5], self.lcd.rs)
      self.connect(self.mcu.digital[6], self.lcd.reset)
      self.connect(self.mcu.digital[7], self.lcd.led)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ], class_refinements=[
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
  def __init__(self, max_illuminance: FloatLike = FloatExpr(),
               target_voltage: RangeLike = RangeExpr()) -> None:
    super().__init__()

    # in L-gain mode, Vout = 0.0057e-6 * Ev * Rl
    rload = RangeExpr._to_expr_type(target_voltage) / (0.0057e-6) / FloatExpr._to_expr_type(max_illuminance)
    # without the typer, this would be written as:
    # rload = target_voltage / (0.0057e-6) / max_illuminance

    self.ic = self.Block(Ref_Bh1620fvc_Device(rload))
    self.pwr = self.Export(self.ic.vcc, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.vout = self.Export(self.ic.iout)

    self.gc1_pur = self.Block(PullupResistor(resistance=4.7*kOhm(tol=0.1)))
    self.gc2_pur = self.Block(PullupResistor(resistance=4.7*kOhm(tol=0.1)))
    self.connect(self.pwr, self.gc2_pur.pwr, self.gc1_pur.pwr)
    self.connect(self.gc1_pur.io, self.ic.gc1)
    self.connect(self.gc2_pur.io, self.ic.gc2)

    self.require(rload.within((1, 1000)*kOhm))
    self.load = self.Block(Resistor(resistance=rload))
    self.connect(self.vout, self.load.a.as_analog_sink())
    self.connect(self.gnd, self.load.b.as_ground())

  def contents(self) -> None:
    super().contents()


class BlinkyNewTestCase(unittest.TestCase):
  def test_design_broken(self) -> None:
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
