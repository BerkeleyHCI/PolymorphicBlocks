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
class IndicatorLed(Light):
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

    self.wavelength = self.Parameter(RangeExpr(wavelength))
    self.target_current_draw = self.Parameter(RangeExpr(current_draw))

    self.signal = self.Port(DigitalSink(), [InOut])
    self.gnd = self.Port(Ground(), [Common])

    self.constrain(self.signal.current_draw.within((0, self.target_current_draw.upper())))

    self.package = self.Block(Led())
    self.res = self.Block(Resistor(
      resistance=(self.signal.link().voltage.upper() / self.target_current_draw.upper(),
                  self.signal.link().output_thresholds.upper() / self.target_current_draw.lower())))

    self.connect(self.signal, self.package.a.as_digital_sink(
      current_draw=(0, self.signal.link().voltage.upper() / self.res.resistance.lower())
    ))

    self.connect(self.res.a, self.package.k)
    self.connect(self.res.b.as_ground(), self.gnd)


class VoltageIndicatorLed(Light):
  """LED connected to a voltage rail as an indicator that there is voltage present"""
  @init_in_parent
  def __init__(self, wavelength: RangeLike = RangeExpr(), current_draw: RangeLike = (1, 10)*mAmp) -> None:
    """
    TODO: support non single color wavelength (eg, color temperature?)
    TODO: support brightness
    TODO: separate RawLed class or similar for use with constant-current drivers"""
    super().__init__()

    self.wavelength = self.Parameter(RangeExpr(wavelength))
    self.target_current_draw = self.Parameter(RangeExpr(current_draw))

    self.signal = self.Port(ElectricalSink(), [InOut])  # TODO should this be Power instead?
    self.gnd = self.Port(Ground(), [Common])

    self.constrain(self.signal.current_draw.within(current_draw))

    self.package = self.Block(Led())
    self.res = self.Block(Resistor(
      resistance=(self.signal.link().voltage.upper() / self.target_current_draw.upper(),
                  self.signal.link().voltage.lower() / self.target_current_draw.lower())))

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
class IndicatorSinkRgbLed(Light):
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

    self.package = self.Block(RgbLedCommonAnode())

    self.red_res = self.Block(Resistor(
      resistance=(self.red.link().voltage.upper() / self.target_current_draw.upper(),
                  self.red.link().output_thresholds.upper() / self.target_current_draw.lower())))
    self.green_res = self.Block(Resistor(
      resistance=(self.green.link().voltage.upper() / self.target_current_draw.upper(),
                  self.green.link().output_thresholds.upper() / self.target_current_draw.lower())))
    self.blue_res = self.Block(Resistor(
      resistance=(self.blue.link().voltage.upper() / self.target_current_draw.upper(),
                  self.blue.link().output_thresholds.upper() / self.target_current_draw.lower())))

    self.connect(self.red_res.a, self.package.k_red)
    self.connect(self.green_res.a, self.package.k_green)
    self.connect(self.blue_res.a, self.package.k_blue)
    self.connect(self.red_res.b.as_digital_sink(
      current_draw=(-1 * self.red.link().voltage.upper() / self.red_res.resistance.lower(), 0)
    ), self.red)
    self.connect(self.green_res.b.as_digital_sink(
      current_draw=(-1 * self.green.link().voltage.upper() / self.green_res.resistance.lower(), 0)
    ), self.green)
    self.connect(self.blue_res.b.as_digital_sink(
      current_draw=(-1 * self.blue.link().voltage.upper() / self.blue_res.resistance.lower(), 0)
    ), self.blue)

    self.connect(self.pwr, self.package.a.as_electrical_sink(
      current_draw=(0,
                    self.red.link().voltage.upper() / self.red_res.resistance.lower() +
                    self.green.link().voltage.upper() / self.green_res.resistance.lower() +
                    self.blue.link().voltage.upper() / self.blue_res.resistance.lower())
    ))
