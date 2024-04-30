from typing import Optional

from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block_default(lambda: Ws2812b)
class Neopixel(Light, Block):
    """Abstract base class for Neopixel-type LEDs including the Vdd/Gnd/Din/Dout interface."""
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.din = self.Port(DigitalSink.empty(), [Input])
        self.dout = self.Port(DigitalSource.empty(), optional=True)


class Ws2812b(Neopixel, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd.init_from(VoltageSink(
            voltage_limits=(3.7, 5.3) * Volt,
            current_draw=(0.6, 0.6 + 12*3) * mAmp,
        ))
        self.gnd.init_from(Ground())
        self.din.init_from(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.7),
            input_threshold_abs=(0.7, 2.7),
            # note that a more restrictive input_threshold_abs of (1.5, 2.3) was used previously
        ))
        self.dout.init_from(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0*mAmp(tol=0),
        ))

    def contents(self) -> None:
        self.footprint(
            'D', 'LED_SMD:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm',
            {
                '1': self.vdd,
                '2': self.dout,
                '3': self.gnd,
                '4': self.din
            },
            mfr='Worldsemi', part='WS2812B',
            datasheet='https://datasheet.lcsc.com/lcsc/2106062036_Worldsemi-WS2812B-B-W_C2761795.pdf'
        )
        # this is actually the WS2812E-V5 which shares similar specs to the B version,
        # but brighter reed and weaker blue and is available for JLC's economy assembly process
        # note, XL-5050RGBC-WS2812B is package compatible but the digital logic thresholds are relative to Vdd
        # and Vih at 0.65 Vddmax = 5.5v is 3.575, which is not compatible with the B version
        self.assign(self.lcsc_part, 'C2920042')
        self.assign(self.actual_basic_part, False)


class Sk6812Mini_E(Neopixel, FootprintBlock):
    """SK6812MINI-E reverse-mount Neopixel RGB LED, commonly used for keyboard lighting.
    Note: while listed as JLC C5149201, it seems non-stocked and is standard assembly only."""
    def __init__(self) -> None:
        super().__init__()
        self.vdd.init_from(VoltageSink(
            voltage_limits=(3.7, 5.5) * Volt,
            current_draw=(1, 1 + 12*3) * mAmp,  # 1 mA static type + up to 12mA/ch
        ))
        self.gnd.init_from(Ground())
        self.din.init_from(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.5, 0.5),
            input_threshold_factor=(0.3, 0.7),
        ))
        self.dout.init_from(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0*mAmp(tol=0),
        ))

    def contents(self) -> None:
        self.footprint(
            'D', 'edg:LED_SK6812MINI-E',
            {
                '1': self.vdd,
                '2': self.dout,
                '3': self.gnd,
                '4': self.din
            },
            mfr='Opsco Optoelectronics', part='SK6812MINI-E',
            datasheet='https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf'
        )


class Sk6805_Ec15(Neopixel, JlcPart, FootprintBlock):
    """SK6805-EC15 Neopixel RGB LED in 1.5x1.5 (0606)."""
    def __init__(self) -> None:
        super().__init__()
        self.vdd.init_from(VoltageSink(
            voltage_limits=(3.7, 5.5) * Volt,
            current_draw=(1, 1 + 5*3) * mAmp,  # 1 mA static type + up to 5mA/ch
        ))
        self.gnd.init_from(Ground())
        self.din.init_from(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.5, 0.5),
            input_threshold_factor=(0.3, 0.7),
        ))
        self.dout.init_from(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0*mAmp(tol=0),
        ))

    def contents(self) -> None:
        self.footprint(
            'D', 'LED_SMD:LED_SK6812_EC15_1.5x1.5mm',
            {
                '1': self.din,
                '2': self.vdd,
                '3': self.dout,
                '4': self.gnd,
            },
            mfr='Opsco Optoelectronics', part='SK6805-EC15',
            datasheet='https://cdn-shop.adafruit.com/product-files/4492/Datasheet.pdf'
        )
        self.assign(self.lcsc_part, 'C2890035')
        self.assign(self.actual_basic_part, False)


class Sk6812_Side_A(Neopixel, FootprintBlock):
    """SK6812-SIDE-A side-emitting Neopixel LED."""
    def __init__(self) -> None:
        super().__init__()
        self.vdd.init_from(VoltageSink(
            voltage_limits=(3.5, 5.5) * Volt,
            current_draw=(1, 1 + 12*3) * mAmp,  # 1 mA static type + up to 12mA/ch
        ))
        self.gnd.init_from(Ground())
        self.din.init_from(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.5, 0.5),
            input_threshold_factor=(0.3, 0.7),
        ))
        self.dout.init_from(DigitalSource.from_supply(
            self.gnd, self.vdd,
            current_limits=0*mAmp(tol=0),
        ))

    def contents(self) -> None:
        self.footprint(
            'D', 'edg:LED_SK6812-SIDE-A',
            {
                '1': self.din,
                '2': self.vdd,
                '3': self.dout,
                '4': self.gnd,
            },
            mfr='Normand Electronic Co Ltd', part='SK6812 SIDE-A',
            datasheet='http://www.normandled.com/upload/201810/SK6812%20SIDE-A%20LED%20Datasheet.pdf'
        )
        # potentially footprint-compatible with C2890037


class NeopixelArray(Light, GeneratorBlock, SvgPcbTemplateBlock):
    """An array of Neopixels"""
    @init_in_parent
    def __init__(self, count: IntLike):
        super().__init__()
        self.din = self.Port(DigitalSink.empty(), [Input])
        self.dout = self.Port(DigitalSource.empty(), [Output], optional=True)
        self.vdd = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])

        self.count = self.ArgParameter(count)
        self.generator_param(self.count)

    def generate(self):
        super().generate()
        self.led = ElementDict[Neopixel]()

        last_signal_pin: Port[DigitalLink] = self.din
        for led_i in range(self.get(self.count)):
            led = self.led[str(led_i)] = self.Block(Neopixel())
            self.connect(last_signal_pin, led.din)
            self.connect(self.vdd, led.vdd)
            self.connect(self.gnd, led.gnd)
            last_signal_pin = led.dout
        self.connect(self.dout, last_signal_pin)


class NeopixelArrayCircular(NeopixelArray):
    """An array of Neopixels, with a circular layout template"""
    def _svgpcb_fn_name_adds(self) -> Optional[str]:
        return f"{self._svgpcb_get(self.count)}"

    def _svgpcb_template(self) -> str:
        led_block = self._svgpcb_footprint_block_path_of(['led[0]'])
        assert led_block is not None
        led_footprint = self._svgpcb_footprint_of(led_block)
        led_vdd_pin = self._svgpcb_pin_of(['led[0]'], ['vdd'], led_block)
        led_gnd_pin = self._svgpcb_pin_of(['led[0]'], ['gnd'], led_block)
        led_din_pin = self._svgpcb_pin_of(['led[0]'], ['din'], led_block)
        led_dout_pin = self._svgpcb_pin_of(['led[0]'], ['dout'], led_block)
        assert all([pin is not None for pin in [led_vdd_pin, led_gnd_pin, led_din_pin, led_dout_pin]])

        return f"""\
function {self._svgpcb_fn_name()}(xy, rot=90, radius=1, startAngle=0, endAngle=360, powerRadiusOffset=0.2) {{
  const kCount = {self._svgpcb_get(self.count)}

  // Global params
  const traceWidth = 0.015
  const powerWidth = 0.05
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {{
    footprints: {{}},
    pts: {{}}
  }}

  // Helper functions
  const degToRad = Math.PI / 180  // multiply by degrees to get radians
  function pAdd(pt1, delta) {{  // adds two points
    return pt1.map((e,i) => e + delta[i])
  }}
  function pDiff(pos, neg) {{  // return the difference between two points
    return pos.map((e,i) => e - neg[i])
  }}
  function pCenter(pt1, pt2) {{  // returns the midpoint
    return pt1.map((e,i) => (e + pt2[i]) / 2)
  }}
  function vRotate(v, deg) {{  // returns a vector rotated by some amount
    return [
      Math.cos(deg * degToRad) * v[0] - Math.sin(deg * degToRad) * v[1],
      Math.sin(deg * degToRad) * v[0] + Math.cos(deg * degToRad) * v[1],
    ]
  }}
  function vScale(v, scale) {{  // returns a vector scaled by some factor
    return v.map((e,i) => (e  * scale))
  }}
  function vProject(v, ref) {{  // returns the projection of v onto a reference vector
    const aDotb = v[0]*ref[0] + v[1]*ref[1]
    const bDotb = ref[0]*ref[0] + ref[1]*ref[1]
    return vScale(ref, aDotb / bDotb)
  }}
  function smoothPath(pt1, pt2, pt1Angle, pt2Angle=null) {{  // return the path(...) components for a curve between two points, with entry and exit slope
    function degToVector(deg, len=1) {{  // given a slope in degrees, convert it to a vector
      return [Math.cos(deg * Math.PI / 180) * len, Math.sin(deg * Math.PI / 180) * len]
    }}
    if (pt2Angle == null) {{
      pt2Angle = pt1Angle
    }}
    const pt1Projection = vProject(pDiff(pt2, pt1), degToVector(pt1Angle))
    const pt2Projection = vProject(pDiff(pt2, pt1), degToVector(pt2Angle))
    return [
      pt1,
      ["cubic",
       pAdd(pt1, vScale(pt1Projection, 0.33)),
       pCenter(pAdd(pt1, vScale(pt1Projection, 0.33)), pDiff(pt2, vScale(pt2Projection, 0.33))),
       pDiff(pt2, vScale(pt2Projection, 0.33)),
      ],
      pt2
    ]
  }}

  const incrAngle = (endAngle - startAngle) / (kCount)

  var prevAngle = null
  var prevLed = null
  var prevGndOrigin = null
  var prevVinOrigin = null

  for (i=0; i<kCount; i++) {{
    const angle = startAngle + incrAngle * i
    const origin = pAdd(xy, vRotate([radius, 0], angle))
    obj.footprints[`led[${{i}}]`] = led = board.add({led_footprint}, {{
      translate: origin,
      rotate: angle + rot,
      id: `{self._svgpcb_pathname()}_led[${{i}}]`
    }})

    const gndOrigin = pAdd(xy, vRotate([radius - powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(gndOrigin, led.pad({led_gnd_pin}),
                    angle)
      ), powerWidth)

    const vinOrigin = pAdd(xy, vRotate([radius + powerRadiusOffset, 0], angle))
    board.wire(path(
      ...smoothPath(vinOrigin, led.pad({led_vdd_pin}),
                    angle)
      ), powerWidth)

    if (prevLed != null) {{
      board.wire(path(
        ...smoothPath(prevLed.pad({led_dout_pin}), led.pad({led_din_pin}),
                      prevAngle + 90, angle + 90)
        ), traceWidth)
      board.wire(path(
        ...smoothPath(prevGndOrigin, gndOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
      board.wire(path(
        ...smoothPath(prevVinOrigin, vinOrigin,
                      prevAngle + 90, angle + 90)
        ), powerWidth)
    }}

    prevAngle = angle
    prevLed = led
    prevVinOrigin = vinOrigin
    prevGndOrigin = gndOrigin
  }}

  return obj
}}
"""
