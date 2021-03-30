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


class Lf21215tmr_Device(FootprintBlock):
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


class Lf21215tmr(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Lf21215tmr_Device())
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

      self.sens = imp.Block(Lf21215tmr())
      self.connect(self.mcu.digital[4], self.sens.out)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['buck'], Tps561201),
      ])


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
