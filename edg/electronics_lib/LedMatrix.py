from ..electronics_abstract_parts import *
from typing import Dict, Optional


class CharlieplexedLedMatrix(Light, GeneratorBlock, SvgPcbTemplateBlock):
  """A LED matrix that saves on IO pins by charlieplexing, only requiring max(rows + 1, cols) GPIOs to control.
  Requires IOs that can tri-state, and requires scanning through rows (so not all LEDs are simultaneously on).

  Anodes (columns) are directly connected to the IO line, while the cathodes (rows) are connected through a resistor.
  A generalization of https://en.wikipedia.org/wiki/Charlieplexing#/media/File:3-pin_Charlieplexing_matrix_with_common_resistors.svg
  """
  def _svgpcb_fn_name_adds(self) -> Optional[str]:
    return f"{self._svgpcb_get(self.ncols)}_{self._svgpcb_get(self.nrows)}"

  def _svgpcb_template(self) -> str:
    led_block = self._svgpcb_footprint_block_path_of(['led[0_0]'])
    res_block = self._svgpcb_footprint_block_path_of(['res[0]'])
    assert led_block is not None and res_block is not None
    led_footprint = self._svgpcb_footprint_of(led_block)
    led_a_pin = self._svgpcb_pin_of(['led[0_0]'], ['a'], led_block)
    led_k_pin = self._svgpcb_pin_of(['led[0_0]'], ['k'], led_block)
    res_footprint = self._svgpcb_footprint_of(res_block)
    res_a_pin = self._svgpcb_pin_of(['res[0]'], ['a'], res_block)
    res_b_pin = self._svgpcb_pin_of(['res[0]'], ['b'], res_block)
    assert all([pin is not None for pin in [led_a_pin, led_k_pin, res_a_pin, res_b_pin]])

    return f"""\
function {self._svgpcb_fn_name()}(xy, colSpacing=1, rowSpacing=1) {{
  const kXCount = {self._svgpcb_get(self.ncols)}  // number of columns (x dimension)
  const kYCount = {self._svgpcb_get(self.nrows)}  // number of rows (y dimension)

  // Global params
  const traceSize = 0.015
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {{
    footprints: {{}},
    pts: {{}}
  }}
  
  allLeds = []
  allVias = []
  lastViasPreResistor = []  // state preserved between rows
  for (let yIndex=0; yIndex < kYCount; yIndex++) {{
    rowLeds = []
    rowVias = []

    viasPreResistor = []
    viasPostResistor = []  // on the same net as the prior row pre-resistor

    for (let xIndex=0; xIndex < kXCount; xIndex++) {{
      ledPos = [xy[0] + colSpacing * xIndex, xy[1] + rowSpacing * yIndex]
      obj.footprints[`led[${{yIndex}}_${{xIndex}}]`] = led = board.add({led_footprint}, {{
        translate: ledPos,
        id: `{self._svgpcb_pathname()}_led_${{yIndex}}_${{xIndex}}_`
      }})
      rowLeds.push(led)

      // anode line
      thisVia = board.add(viaTemplate, {{
        translate: [ledPos[0] + colSpacing*1/3, ledPos[1]]
      }})
      rowVias.push(thisVia)
      board.wire([led.pad("{led_a_pin}"), thisVia.pos], traceSize, "F.Cu")
      if (xIndex <= yIndex) {{
        viasPreResistor.push(thisVia)
      }} else {{
        viasPostResistor.push(thisVia)
      }}
    }}
    allLeds.push(rowLeds)
    allVias.push(rowVias)

    // Wire the anode lines, including the row-crossing one accounting for the diagonal-skip where the resistor is in the schematic matrix
    // viasPreResistor guaranteed nonempty
    board.wire([viasPreResistor[0].pos, viasPreResistor[viasPreResistor.length - 1].pos], traceSize, "B.Cu")
    if (viasPostResistor.length > 0) {{
      board.wire([viasPostResistor[0].pos, viasPostResistor[viasPostResistor.length - 1].pos], traceSize, "B.Cu")
    }}

    // Create the inter-row bridging trace, if applicable
    if (viasPostResistor.length > 0 && lastViasPreResistor.length > 0) {{
      via1Pos = lastViasPreResistor[lastViasPreResistor.length - 1].pos
      via2Pos = viasPostResistor[0].pos
      centerY = (via1Pos[1] + via2Pos[1]) / 2
      board.wire([via1Pos,
                  [via1Pos[0], centerY],
                  [via2Pos[0], centerY],
                  via2Pos
                 ],
                 traceSize, "B.Cu")
    }}

    lastViasPreResistor = viasPreResistor
  }}

  allResistors = []
  for (let xIndex=0; xIndex < kXCount; xIndex++) {{
    const resPos = [xy[0] + colSpacing * xIndex, xy[1] + rowSpacing * kYCount]
    obj.footprints[`res[${{xIndex + 1}}]`] = res = board.add({res_footprint}, {{
      translate: resPos,
      id: `{self._svgpcb_pathname()}_res_${{xIndex + 1}}_`
    }})
    allResistors.push(res)

    if (xIndex < allVias.length && xIndex < allVias[xIndex].length - 1) {{
      targetVia = allVias[xIndex][xIndex + 1]
      thisVia = board.add(viaTemplate, {{
        translate: [resPos[0] + colSpacing*2/3, targetVia.pos[1]]
      }})

      board.wire([
        res.pad("{res_b_pin}"),
        [resPos[0] + colSpacing*2/3, res.padY("{res_b_pin}")],
        thisVia.pos
      ], traceSize, "F.Cu")
      board.wire([
        thisVia.pos,
        targetVia.pos,
      ], traceSize, "B.Cu")
    }} else if (xIndex <= allVias.length && xIndex < allVias[xIndex - 1].length) {{
      // connect the last via
      thisVia = board.add(viaTemplate, {{
        translate: [resPos[0] + colSpacing*2/3, resPos[1]]
      }})
      targetVia = allVias[xIndex - 1][xIndex - 1]
      board.wire([
        res.pad("{res_b_pin}"),
        thisVia.pos
      ], traceSize, "F.Cu")
      centerY = targetVia.pos[1] + colSpacing/2
      board.wire([
        thisVia.pos,
        [thisVia.pos[0], centerY],
        [targetVia.pos[0], centerY],
        targetVia.pos,
      ], traceSize, "B.Cu")
    }}
  }}

  // create the along-column cathode line
  for (let xIndex=0; xIndex < kXCount; xIndex++) {{
    colPads = allLeds.flatMap(row => row.length > xIndex ? [row[xIndex].pad("{led_k_pin}")] : [])
    if (xIndex < allResistors.length) {{
      colPads.push(allResistors[xIndex].pad("{res_a_pin}"))
    }}

    for (let i=0; i<colPads.length - 1; i++) {{
      board.wire([
        colPads[i],
        colPads[i+1]
      ], traceSize, "F.Cu")
    }}
  }}

  return obj
}}
"""

  @init_in_parent
  def __init__(self, nrows: IntLike, ncols: IntLike,
               color: LedColorLike = Led.Any, current_draw: RangeLike = (1, 10)*mAmp):
    super().__init__()

    self.current_draw = self.ArgParameter(current_draw)
    self.color = self.ArgParameter(color)

    # note that IOs supply both the positive and negative
    self.ios = self.Port(Vector(DigitalSink.empty()))

    self.nrows = self.ArgParameter(nrows)
    self.ncols = self.ArgParameter(ncols)
    self.generator_param(self.nrows, self.ncols)

  def generate(self):
    super().generate()
    nrows = self.get(self.nrows)
    ncols = self.get(self.ncols)

    io_voltage = self.ios.hull(lambda x: x.link().voltage)
    io_voltage_upper = io_voltage.upper()
    io_voltage_lower = self.ios.hull(lambda x: x.link().output_thresholds).upper()

    # internally, this uses passive ports on all the components, and only casts to a DigitalSink at the end
    # which is necessary to account for that not all LEDs can be simultaneously on
    passive_ios: Dict[int, Passive] = {}  # keeps the passive-side port for each boundary IO
    def connect_passive_io(index: int, io: Passive):
      # connects a Passive-typed IO to the index, handling the first and subsequent case
      if index in passive_ios:
        self.connect(passive_ios[index], io)  # subsequent case, actually do the connection
      else:
        passive_ios[index] = io  # first case, just bootstrap the data structure

    self.res = ElementDict[Resistor]()
    res_model = Resistor(
      resistance=(io_voltage_upper / self.current_draw.upper(),
                  io_voltage_lower / self.current_draw.lower())
    )
    self.led = ElementDict[Led]()
    led_model = Led(color=self.color)

    # generate the resistor and LEDs for each column
    for col in range(ncols):
      # generate the cathode resistor, guaranteed one per column
      self.res[str(col)] = res = self.Block(res_model)
      connect_passive_io(col, res.b)
      for row in range(nrows):
        self.led[f"{row}_{col}"] = led = self.Block(led_model)
        self.connect(led.k, res.a)
        if row >= col:  # displaced by resistor
          connect_passive_io(row + 1, led.a)
        else:
          connect_passive_io(row, led.a)

    # generate the adapters and connect the internal passive IO to external typed IO
    for index, passive_io in passive_ios.items():
      # if there is a cathode resistor attached to this index, then include the sunk current
      if index < ncols:
        sink_res = self.res[str(index)]
        sink_current = -(io_voltage / sink_res.actual_resistance).upper() * ncols
      else:
        sink_current = 0 * mAmp

      # then add the maximum of the LED source currents, for the rest of the cathode lines
      source_current = 0 * mAmp
      for col in range(ncols):
        col_res = self.res[str(col)]
        source_current = (io_voltage / col_res.actual_resistance).upper().max(source_current)

      self.connect(self.ios.append_elt(DigitalSink.empty(), str(index)),
                   passive_io.adapt_to(DigitalSink(current_draw=(sink_current, source_current))))
