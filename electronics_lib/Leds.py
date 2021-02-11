from electronics_abstract_parts import *


class SmtLed(Led, CircuitBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_SMD:LED_0603_1608Metric',
      {
        '2': self.a,
        '1': self.k,
      },
      part='LED',
    )


class ThtLed(Led, CircuitBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_THT:LED_D5.0mm',
      {
        '2': self.a,
        '1': self.k,
      },
      part='LED',
    )


# TODO should there be some kind of abstract LED class, that works for both high and low side?
class IndicatorLed(Light, GeneratorBlock):
  """High-side-driven (default, "common cathode") indicator LED"""
  @init_in_parent
  def __init__(self, wavelength: RangeLike = RangeExpr(), current_draw: RangeLike = (1, 10)*mAmp) -> None:
    """Controlled LEDs, with provisions for both current source and sink configurations.
    signal_in is a constant-voltage digital source, so this must contain some ballast.
    This should not contain amplifiers.
    TODO: support non single color wavelength (eg, color temperature?)
    TODO: support brightness
    TODO: separate RawLed class or similar for use with constant-current drivers"""
    super().__init__()

    self.wavelength = self.Parameter(RangeExpr(wavelength, constr=RangeSubset))
    self.target_current_draw = self.Parameter(RangeExpr(current_draw))

    self.signal = self.Port(DigitalSink(), [InOut])
    self.gnd = self.Port(Ground(), [Common])

    self.constrain(self.signal.current_draw.within((0, self.target_current_draw.upper())))

    self.generator(self.generate_circuit, self.target_current_draw,
                   self.signal.link().voltage, self.signal.link().output_thresholds,
                   targets=[self.signal, self.gnd])

  def generate_circuit(self, target_current: RangeVal, voltage: RangeVal, thresholds: RangeVal):
    # TODO parse wavelength
    min_voltage = thresholds[1]
    max_voltage = voltage[1]
    self.package = self.Block(Led())
    self.res = self.Block(Resistor(resistance=(max_voltage / target_current[1], min_voltage / target_current[0])))

    self.connect(self.signal, self.package.a.as_digital_sink(
      current_draw=(0, self.signal.link().voltage.upper() / self.res.resistance.lower())
    ))

    self.connect(self.res.a, self.package.k)
    self.connect(self.res.b.as_ground(), self.gnd)


class VoltageIndicatorLed(Light, GeneratorBlock):
  """LED connected to a voltage rail as an indicator that there is voltage present"""
  @init_in_parent
  def __init__(self, wavelength: RangeLike = RangeExpr(), current_draw: RangeLike = (1, 10)*mAmp) -> None:
    """
    TODO: support non single color wavelength (eg, color temperature?)
    TODO: support brightness
    TODO: separate RawLed class or similar for use with constant-current drivers"""
    super().__init__()

    self.wavelength = self.Parameter(RangeExpr(wavelength, constr=RangeSubset))
    self.target_current_draw = self.Parameter(RangeExpr(current_draw))

    self.signal = self.Port(ElectricalSink(), [InOut])  # TODO should this be Power instead?
    self.gnd = self.Port(Ground(), [Common])

    self.constrain(self.signal.current_draw.within(current_draw))

    self.generator(self.generate_circuit, self.target_current_draw, self.signal.link().voltage)

  def generate_circuit(self, target_current: RangeVal, voltage: RangeVal):
    # TODO parse wavelength
    min_voltage = voltage[0]
    self.package = self.Block(Led())
    self.res = self.Block(Resistor(resistance=(min_voltage / target_current[1], min_voltage / target_current[0])))

    self.connect(self.signal, self.package.a.as_electrical_sink(
      current_draw=self.signal.link().voltage / self.res.resistance
    ))
    self.connect(self.res.a, self.package.k)
    self.connect(self.res.b.as_ground(), self.gnd)


class SmtRgbLed(RgbLedCommonAnode, CircuitBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'calisco:LED_RGB_0606',
      {  # ABGR configuration
        '1': self.a,
        '2': self.k_blue,
        '3': self.k_green,
        '4': self.k_red,
      },
      mfr='Everlight Electronics Co Ltd', part='EAST1616RGBB2'
    )


class ThtRgbLed(RgbLedCommonAnode, CircuitBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_THT:LED_D5.0mm-4_RGB_Staggered_Pins',
      {  # RAGB configuration
        '1': self.k_red,
        '2': self.a,
        '3': self.k_green,
        '4': self.k_blue,
      },
      mfr='Sparkfun', part='COM-09264'
    )


# TODO should there be some kind of abstract LED class, that works for both CA and CC type LEDs?
class IndicatorSinkRgbLed(Light, GeneratorBlock):
  """Common anode indicator RGB LED"""
  @init_in_parent
  def __init__(self, current_draw: RangeLike = (1, 10)*mAmp) -> None:
    """RGB LEDs, with provisions for both common-anode and common-cathode configurations.
    This should not contain amplifiers."""
    # TODO: support brightness
    super().__init__()

    self.pwr = self.Port(ElectricalSink(), [Power])
    self.red = self.Port(DigitalSink())
    self.green = self.Port(DigitalSink())
    self.blue = self.Port(DigitalSink())

    self.target_current_draw = self.Parameter(RangeExpr(current_draw))
    self.constrain(self.red.current_draw.within((-1 * self.target_current_draw.upper(), 0)))
    self.constrain(self.green.current_draw.within((-1 * self.target_current_draw.upper(), 0)))
    self.constrain(self.blue.current_draw.within((-1 * self.target_current_draw.upper(), 0)))
    self.constrain(self.pwr.current_draw.within((0, 3 * self.target_current_draw.upper())))

    self.generator(self.generate_circuit, self.target_current_draw,
                   self.red.link().output_thresholds,
                   self.green.link().output_thresholds,
                   self.blue.link().output_thresholds)

  def generate_circuit(self, target_current: RangeVal,
                       red_voltage: RangeVal, green_voltage: RangeVal, blue_voltage: RangeVal):
    self.package = self.Block(RgbLedCommonAnode())

    min_red_voltage = red_voltage[1]
    min_green_voltage = green_voltage[1]
    min_blue_voltage = blue_voltage[1]

    self.red_res = self.Block(Resistor(resistance=(min_red_voltage / target_current[1], min_red_voltage / target_current[0])))
    self.green_res = self.Block(Resistor(resistance=(min_green_voltage / target_current[1], min_green_voltage / target_current[0])))
    self.blue_res = self.Block(Resistor(resistance=(min_blue_voltage / target_current[1], min_blue_voltage / target_current[0])))

    self.connect(self.red_res.a, self.package.k_red)
    self.connect(self.green_res.a, self.package.k_green)
    self.connect(self.blue_res.a, self.package.k_blue)
    self.connect(self.red_res.b.as_digital_sink(), self.red)  # TODO current draw should be here, but the constraint doesn't generate - debug this
    self.connect(self.green_res.b.as_digital_sink(), self.green)
    self.connect(self.blue_res.b.as_digital_sink(), self.blue)

    self.constrain(self.red.current_draw == (-1 * self.red.link().voltage.upper() / self.red_res.resistance.lower(), 0))
    self.constrain(self.green.current_draw == (-1 * self.green.link().voltage.upper() / self.green_res.resistance.lower(), 0))
    self.constrain(self.blue.current_draw == (-1 * self.blue.link().voltage.upper() / self.blue_res.resistance.lower(), 0))

    self.connect(self.pwr, self.package.a.as_electrical_sink(
      current_draw=(0,
                    self.red.link().voltage.upper() / self.red_res.resistance.lower() +
                    self.green.link().voltage.upper() / self.green_res.resistance.lower() +
                    self.blue.link().voltage.upper() / self.blue_res.resistance.lower())
    ))
