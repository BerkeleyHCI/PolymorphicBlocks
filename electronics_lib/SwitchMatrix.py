from typing import cast

from electronics_abstract_parts import *


class SwitchMatrix(HumanInterface, GeneratorBlock, SvgPcbTemplateBlock):
  """A switch matrix, such as for a keyboard, that generates (nrows * ncols) switches while only
  using max(nrows, ncols) IOs.

  Internally, the switches are in a matrix, with the driver driving one col low at a time while
  reading which rows are low (with the other cols weakly pulled high).
  This uses the Switch abstract class, which can be refined into e.g. a tactile switch or mechanical keyswitch.

  This generates per-switch diodes which allows multiple keys to be pressed simultaneously.
  Diode anodes are attached to the rows, while cathodes go through each switch to the cols.
  """
  def _svgpcb_fn_name(self) -> str:
    return f"""SwitchMatrix_{self._svgpcb_pathname()}_{self._svgpcb_get(self.ncols)}_{self._svgpcb_get(self.nrows)}"""

  def _svgpcb_template(self) -> str:
    return f"""\
function {self._svgpcb_fn_name()}(xy, colSpacing=1, rowSpacing=1, diodeOffset=[0.25, 0]) {{
  // Circuit generator params
  const ncols = {self._svgpcb_get(self.ncols)}
  const nrows = {self._svgpcb_get(self.nrows)}

  // Global params
  const traceSize = 0.015
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {{
    footprints: {{}},
    pts: {{}}
  }}

  // Parameter adjustment handles overlaid onto the board
  // TODO needs more thought on how this works
  obj.pts['rowHandle'] = pt(xy[0], xy[1] + rowSpacing)
  obj.pts['colHandle']  = pt(xy[0] + colSpacing, xy[1])
  obj.pts['diodeOffset']  = pt(xy[0] + diodeOffset[0], xy[1] + diodeOffset[1])

  // Actual generator code
  allColWirePoints = []
  for (let yIndex=0; yIndex < nrows; yIndex++) {{
    colWirePoints = []
    rowDiodeVias = []

    for (let xIndex=0; xIndex < ncols; xIndex++) {{
      index = yIndex * ncols + xIndex + 1
  
      buttonPos = [colSpacing * xIndex, rowSpacing * yIndex]
      obj.footprints[`sw[${{xIndex}}][${{yIndex}}]`] = button = board.add(button_6mm, {{
        translate: buttonPos, rotate: 0,
        id: `{self._svgpcb_pathname()}_sw[${{xIndex}}][${{yIndex}}]`
      }})
  
      diodePos = [buttonPos[0] + diodeOffset[0], buttonPos[1] + diodeOffset[1]]
      obj[`d[${{xIndex}}][${{yIndex}}]`] = diode = board.add(D_SMA, {{
        translate: diodePos, rotate: 90,
        id: `{self._svgpcb_pathname()}_d[${{xIndex}}][${{yIndex}}]`
      }})
  
      // create stub wire for button -> column common line
      colWirePoint = [buttonPos[0], button.padY("L2")]
      board.wire([colWirePoint, button.pad("L2")], traceSize, "F.Cu")
      colWirePoints.push(colWirePoint)
  
      // create wire for button -> diode
      board.wire([button.pad("R2"), diode.pad(1)], traceSize, "F.Cu")
      diodeViaPos = [diode.padX(2), diode.padY(2) + 0.5]
      diodeVia = board.add(viaTemplate, {{translate: diodeViaPos}})
      board.wire([diode.pad(2), diodeVia.pos], traceSize)
  
      if (rowDiodeVias.length > 0) {{
        board.wire([rowDiodeVias[rowDiodeVias.length - 1].pos, diodeVia.pos], traceSize, "B.Cu")
      }}
      rowDiodeVias.push(diodeVia)
    }}
    allColWirePoints.push(colWirePoints)
    }}

    // Inter-row wiring
    for (let xIndex=0; xIndex < allColWirePoints[0].length; xIndex++) {{
      board.wire([
        allColWirePoints[0][xIndex],
        allColWirePoints[allColWirePoints.length - 1][xIndex]
      ], traceSize, "F.Cu")
    }}

    return obj
  }}
"""

  @init_in_parent
  def __init__(self, nrows: IntLike, ncols: IntLike, voltage_drop: RangeLike = (0, 0.7)*Volt):
    super().__init__()

    self.rows = self.Port(Vector(DigitalSingleSource.empty()))
    self.cols = self.Port(Vector(DigitalSink.empty()))
    self.voltage_drop = self.ArgParameter(voltage_drop)

    self.nrows = self.ArgParameter(nrows)
    self.ncols = self.ArgParameter(ncols)
    self.generator_param(self.nrows, self.ncols)

  def generate(self):
    super().generate()
    row_ports = {}
    for row in range(self.get(self.nrows)):
      row_ports[row] = self.rows.append_elt(DigitalSingleSource.empty(), str(row))

    self.sw = ElementDict[Switch]()
    self.d = ElementDict[Diode]()
    for col in range(self.get(self.ncols)):
      col_port = cast(DigitalSink, self.cols.append_elt(DigitalSink.empty(), str(col)))
      col_port_model = DigitalSink()  # ideal, negligible current draw (assumed) and thresholds checked at other side
      for (row, row_port) in row_ports.items():
        sw = self.sw[f"{col},{row}"] = self.Block(Switch(
          voltage=row_port.link().voltage,
          current=row_port.link().current_drawn
        ))
        d = self.d[f"{col},{row}"] = self.Block(Diode(
          current=row_port.link().current_drawn,
          # col voltage is used as a proxy, since (properly) using the row voltage causes a circular dependency
          reverse_voltage=col_port.link().voltage,
          voltage_drop=self.voltage_drop
        ))
        lowest_output = col_port.link().voltage.lower() + d.actual_voltage_drop.lower()
        highest_output = col_port.link().output_thresholds.lower() + d.actual_voltage_drop.upper()
        self.connect(d.anode.adapt_to(DigitalSingleSource(
          voltage_out=(lowest_output, highest_output),
          output_thresholds=(highest_output, float('inf')),
          low_signal_driver=True
        )), row_port)
        self.connect(d.cathode, sw.sw)
        self.connect(sw.com.adapt_to(col_port_model), col_port)

    self.rows.defined()
    self.cols.defined()
