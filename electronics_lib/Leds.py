from electronics_abstract_parts import *


class SmtLed(Led, FootprintBlock):
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



class ThtLed(Led, FootprintBlock):
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
  def __init__(self, current_draw: RangeLike = (1, 10)*mAmp) -> None:
    """Controlled LEDs, with provisions for both current source and sink configurations.
    signal_in is a constant-voltage digital source, so this must contain some ballast.
    This should not contain amplifiers.
    TODO: support non single color wavelength (eg, color temperature?)
    TODO: support brightness
    TODO: separate RawLed class or similar for use with constant-current drivers"""
    super().__init__()

    self.target_current_draw = self.Parameter(RangeExpr(current_draw))

    self.signal = self.Port(DigitalSink.empty(), [InOut])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.require(self.signal.current_draw.within((0, self.target_current_draw.upper())))

    self.package = self.Block(Led())
    self.res = self.Block(Resistor(
      resistance=(self.signal.link().voltage.upper() / self.target_current_draw.upper(),
                  self.signal.link().output_thresholds.upper() / self.target_current_draw.lower())))

    self.connect(self.signal, self.package.a.as_digital_sink(
      current_draw=self.signal.link().voltage / self.res.actual_resistance
    ))

    self.connect(self.res.a, self.package.k)
    self.connect(self.res.b.as_ground(), self.gnd)


class VoltageIndicatorLed(Light):
  """LED connected to a voltage rail as an indicator that there is voltage present"""
  @init_in_parent
  def __init__(self, current_draw: RangeLike = (1, 10)*mAmp) -> None:
    """
    TODO: support non single color wavelength (eg, color temperature?)
    TODO: support brightness
    TODO: separate RawLed class or similar for use with constant-current drivers"""
    super().__init__()

    self.target_current_draw = self.Parameter(RangeExpr(current_draw))

    self.signal = self.Port(VoltageSink.empty(), [Power, InOut])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.require(self.signal.current_draw.within(current_draw))

    self.package = self.Block(Led())
    self.res = self.Block(Resistor(
      resistance=(self.signal.link().voltage.upper() / self.target_current_draw.upper(),
                  self.signal.link().voltage.lower() / self.target_current_draw.lower())))

    self.connect(self.signal, self.package.a.as_voltage_sink(
      current_draw=self.signal.link().voltage / self.res.actual_resistance
    ))
    self.connect(self.res.a, self.package.k)
    self.connect(self.res.b.as_ground(), self.gnd)


class SmtRgbLed(RgbLedCommonAnode, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'D', 'LED_SMD:LED_LiteOn_LTST-C19HE1WT',
      {  # ABGR configuration - also pins 1/2 and 3/4 are swapped on this pattern
        '2': self.a,
        '1': self.k_blue,
        '4': self.k_green,
        '3': self.k_red,
      },
      mfr='Everlight Electronics Co Ltd', part='EAST1616RGBB2'
    )


class ThtRgbLed(RgbLedCommonAnode, FootprintBlock):
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

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.signals = self.Port(Vector(DigitalSink.empty()))
    signal_red = self.signals.append_elt(DigitalSink.empty(), 'red')
    signal_green = self.signals.append_elt(DigitalSink.empty(), 'green')
    signal_blue = self.signals.append_elt(DigitalSink.empty(), 'blue')

    self.target_current_draw = self.Parameter(RangeExpr(current_draw))
    self.require(signal_red.current_draw.within((-1 * self.target_current_draw.upper(), 0)))
    self.require(signal_green.current_draw.within((-1 * self.target_current_draw.upper(), 0)))
    self.require(signal_blue.current_draw.within((-1 * self.target_current_draw.upper(), 0)))
    self.require(self.pwr.current_draw.within((0, 3 * self.target_current_draw.upper())))

    self.package = self.Block(RgbLedCommonAnode())

    self.red_res = self.Block(Resistor(
      resistance=(signal_red.link().voltage.upper() / self.target_current_draw.upper(),
                  signal_red.link().output_thresholds.upper() / self.target_current_draw.lower())))
    self.green_res = self.Block(Resistor(
      resistance=(signal_green.link().voltage.upper() / self.target_current_draw.upper(),
                  signal_green.link().output_thresholds.upper() / self.target_current_draw.lower())))
    self.blue_res = self.Block(Resistor(
      resistance=(signal_blue.link().voltage.upper() / self.target_current_draw.upper(),
                  signal_blue.link().output_thresholds.upper() / self.target_current_draw.lower())))

    self.connect(self.red_res.a, self.package.k_red)
    self.connect(self.green_res.a, self.package.k_green)
    self.connect(self.blue_res.a, self.package.k_blue)
    self.connect(self.red_res.b.as_digital_sink(
      current_draw=(-1 * signal_red.link().voltage.upper() / self.red_res.actual_resistance.lower(), 0)
    ), signal_red)
    self.connect(self.green_res.b.as_digital_sink(
      current_draw=(-1 * signal_green.link().voltage.upper() / self.green_res.actual_resistance.lower(), 0)
    ), signal_green)
    self.connect(self.blue_res.b.as_digital_sink(
      current_draw=(-1 * signal_blue.link().voltage.upper() / self.blue_res.actual_resistance.lower(), 0)
    ), signal_blue)

    self.connect(self.pwr, self.package.a.as_voltage_sink(
      current_draw=(0,
                    signal_red.link().voltage.upper() / self.red_res.actual_resistance.lower() +
                    signal_green.link().voltage.upper() / self.green_res.actual_resistance.lower() +
                    signal_blue.link().voltage.upper() / self.blue_res.actual_resistance.lower())
    ))
