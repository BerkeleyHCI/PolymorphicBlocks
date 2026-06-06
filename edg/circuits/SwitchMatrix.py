from typing import Optional, Tuple, Any, List

from typing_extensions import override

from ..abstract_parts import *


@abstract_block_default(lambda: DiodeSwitchCell)
class SwitchCell(InternalBlock, Block):
    """A single cell in the switch matrix."""

    def __init__(self, voltage_drop: RangeLike):
        super().__init__()
        self.voltage_drop = self.ArgParameter(voltage_drop)

        self.row = self.Port(DigitalSink.empty())
        self.col = self.Port(DigitalSource.empty())


class DiodeSwitchCell(SwitchCell, InternalBlock):
    """A single cell in the switch matrix, consisting of a switch and diode to support multiple key presses.
    Provides a layer of hierarchy for layout replication."""

    @override
    def contents(self) -> None:
        super().contents()

        self.col.init_from(
            DigitalSource(  # diode anode, externally pulled, driven to col by switch closure
                voltage_out=self.row.link().voltage.lower()
                + self.voltage_drop,  # use spec to avoid circular dependency
                output_thresholds=(self.row.link().voltage + self.voltage_drop).hull(float("inf")),
                low_driver=True,
                high_driver=False,
            )
        )
        self.row.init_from(DigitalSink())  # switch common, externally driven for column scan, assumed ideal

        self.sw = self.Block(
            Switch(voltage=self.col.link().voltage - self.row.link().voltage, current=self.col.link().current_drawn)
        )
        self.d = self.Block(
            Diode(
                current=self.col.link().current_drawn,
                reverse_voltage=(self.col.link().voltage - self.row.link().voltage).abs(),
                voltage_drop=self.voltage_drop,
            )
        )
        self.connect(self.col.net, self.sw.sw)
        self.connect(self.sw.com, self.d.anode)
        self.connect(self.d.cathode, self.row.net)


@abstract_block_default(lambda: DiodeSwitchCellNeopixel)
class SwitchCellNeopixel(BlockInterfaceMixin[SwitchCell], InternalBlock):
    """SwitchCell mixin that adds a neopixel to the switch cell, with power and data ports."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.npx_din = self.Port(DigitalSink.empty())
        self.npx_dout = self.Port(DigitalSource.empty(), optional=True)
        self.npx_pwr = self.Port(VoltageSink.empty())
        self.npx_gnd = self.Port(Ground.empty())


class DiodeSwitchCellNeopixel(SwitchCellNeopixel, DiodeSwitchCell, InternalBlock):
    """SwitchCell implementation with neopixel."""

    @override
    def contents(self) -> None:
        super().contents()
        self.npx = self.Block(Neopixel())
        self.connect(self.npx.pwr, self.npx_pwr)
        self.connect(self.npx.gnd, self.npx_gnd)
        self.connect(self.npx.din, self.npx_din)
        self.connect(self.npx.dout, self.npx_dout)


@abstract_block_default(lambda: SwitchDiodeMatrix)
class SwitchMatrix(InternalBlock, Block):

    def __init__(self, nrows: IntLike, ncols: IntLike, voltage_drop: RangeLike = (0, 0.7) * Volt):
        super().__init__()

        self.voltage_drop = self.ArgParameter(voltage_drop)
        self.nrows = self.ArgParameter(nrows)
        self.ncols = self.ArgParameter(ncols)

        self.rows = self.Port(Vector(DigitalSink.empty()))
        self.cols = self.Port(Vector(DigitalSource.empty()))


class SwitchDiodeMatrix(SwitchMatrix, HumanInterface, GeneratorBlock, SvgPcbTemplateBlock):
    """A switch matrix, such as for a keyboard, that generates (nrows * ncols) switches while only
    using max(nrows, ncols) IOs.

    Internally, the switches are in a matrix and follows COL2ROW conventions:
    - the driver drives one row low at a time, other rows are floating or weakly pulled high
    - the columns are weakly pulled high, and read low when the switch is pressed

    Internally, this uses the Switch abstract block, which can be refined into e.g. a tactile switch or mechanical keyswitch.

    This generates per-switch diodes which allows multiple keys to be pressed simultaneously.
    """

    @override
    def _svgpcb_fn_name_adds(self) -> Optional[str]:
        return f"{self._svgpcb_get(self.ncols)}_{self._svgpcb_get(self.nrows)}"

    @override
    def _svgpcb_template(self) -> str:
        switch_block = self._svgpcb_footprint_block_path_of(["sw[0,0]", "sw"])
        diode_block = self._svgpcb_footprint_block_path_of(["sw[0,0]", "d"])
        switch_reftype, switch_refnum = self._svgpcb_refdes_of(["sw[0,0]", "sw"])
        diode_reftype, diode_refnum = self._svgpcb_refdes_of(["sw[0,0]", "d"])
        assert switch_block is not None and diode_block is not None
        switch_footprint = self._svgpcb_footprint_of(switch_block)
        switch_sw_pin = self._svgpcb_pin_of(["sw[0,0]", "sw"], ["sw"])
        switch_com_pin = self._svgpcb_pin_of(["sw[0,0]", "sw"], ["com"])
        diode_footprint = self._svgpcb_footprint_of(diode_block)
        diode_a_pin = self._svgpcb_pin_of(["sw[0,0]", "d"], ["anode"])
        diode_k_pin = self._svgpcb_pin_of(["sw[0,0]", "d"], ["cathode"])
        assert all([pin is not None for pin in [switch_sw_pin, switch_com_pin, diode_a_pin, diode_k_pin]])

        return f"""\
function {self._svgpcb_fn_name()}(xy, colSpacing=0.5, rowSpacing=0.5, diodeOffset=[0.25, 0]) {{
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

  // Actual generator code
  allColWirePoints = []
  for (let yIndex=0; yIndex < nrows; yIndex++) {{
    colWirePoints = []
    rowDiodeVias = []

    for (let xIndex=0; xIndex < ncols; xIndex++) {{
      index = yIndex * ncols + xIndex + 1

      buttonPos = [xy[0] + colSpacing * xIndex, xy[1] + rowSpacing * yIndex]
      obj.footprints[`{switch_reftype}${{{switch_refnum} + xIndex * nrows + yIndex}}`] = button = board.add(
        {switch_footprint},
        {{
          translate: buttonPos, rotate: 0,
          id: `{switch_reftype}${{{switch_refnum} + xIndex * nrows + yIndex}}`
        }})

      diodePos = [buttonPos[0] + diodeOffset[0], buttonPos[1] + diodeOffset[1]]
      obj[`{diode_reftype}${{{diode_refnum} + xIndex * nrows + yIndex}}`] = diode = board.add(
        {diode_footprint},
        {{
          translate: diodePos, rotate: 90,
          id: `{diode_reftype}${{{diode_refnum} + xIndex * nrows + yIndex}}`
        }})

      // create stub wire for button -> column common line
      colWirePoint = [buttonPos[0], button.padY("{switch_com_pin}")]
      board.wire([colWirePoint, button.pad("{switch_com_pin}")], traceSize, "F.Cu")
      colWirePoints.push(colWirePoint)

      // create wire for button -> diode
      board.wire([button.pad("{switch_sw_pin}"), diode.pad("{diode_k_pin}")], traceSize, "F.Cu")
      diodeViaPos = [diode.padX("{diode_a_pin}"), buttonPos[1] + rowSpacing / 2]
      diodeVia = board.add(viaTemplate, {{translate: diodeViaPos}})
      board.wire([diode.pad("{diode_a_pin}"), diodeVia.pos], traceSize)

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

    @override
    def _svgpcb_bbox(self) -> Tuple[float, float, float, float]:
        return (
            -1.0,
            -1.0,
            self._svgpcb_get(self.ncols) * 0.5 * 25.4 + 1.0,
            (self._svgpcb_get(self.nrows) + 1) * 0.5 * 25.4 + 1.0,
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator_param(self.nrows, self.ncols)

    @override
    def generate(self) -> None:
        super().generate()

        for row in range(self.get(self.nrows)):
            self.rows.append_elt(DigitalSink.empty(), str(row))

        self.sw = ElementDict[SwitchCell]()
        for col in range(self.get(self.ncols)):
            col_port = self.cols.append_elt(DigitalSource.empty(), str(col))
            for row in range(self.get(self.nrows)):
                cell = self.sw[f"{col},{row}"] = self.Block(SwitchCell(voltage_drop=self.voltage_drop))
                self.connect(cell.col, col_port)
                self.connect(cell.row, self.rows[str(row)])

        self.rows.defined()
        self.cols.defined()


@abstract_block_default(lambda: SwitchDiodeMatrixNeopixels)
class SwitchMatrixNeopixels(BlockInterfaceMixin[SwitchMatrix]):
    """SwitchMatrix mixin that adds a neopixel with every switch, in the SwitchCell hierarchy block.
    Adds power and data ports for the chain.

    npx_order can be:
    - "row": chains neopixels across a row before moving to the next row
    - "row_snake": above, but reversing direction every other row
    - "col": chains neopixels across a column before moving to the next column
    - "col_snake": above, but reversing direction every other col
    """

    def __init__(self, *args: Any, npx_order: StringLike = "row_snake", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.npx_order = self.ArgParameter(npx_order)

        self.npx_din = self.Port(DigitalSink.empty())
        self.npx_dout = self.Port(DigitalSource.empty(), optional=True)
        self.npx_pwr = self.Port(VoltageSink.empty())
        self.npx_gnd = self.Port(Ground.empty())


class SwitchDiodeMatrixNeopixels(SwitchMatrixNeopixels, SwitchDiodeMatrix, HumanInterface, GeneratorBlock):
    """SwitchMatrix implementation with neopixel chain."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator_param(self.npx_order)

    @override
    def generate(self) -> None:
        super().generate()

        npx_order = self.get(self.npx_order)
        switch_cells: List[SwitchCell] = []

        if npx_order in ("row", "row_snake"):
            for row in range(self.get(self.nrows)):
                cols = list(range(self.get(self.ncols)))
                if npx_order == "row_snake" and row % 2 == 1:
                    cols = list(reversed(cols))
                for col in cols:
                    switch_cells.append(self.sw[f"{col},{row}"])
        elif npx_order in ("col", "col_snake"):
            for col in range(self.get(self.ncols)):
                rows = list(range(self.get(self.nrows)))
                if npx_order == "col_snake" and col % 2 == 1:
                    rows = list(reversed(rows))
                for row in rows:
                    switch_cells.append(self.sw[f"{col},{row}"])
        else:
            raise ValueError(f"Invalid npx_order {npx_order}")

        last_npx_dout: Port[DigitalLink] = self.npx_din
        for switch_cell in switch_cells:
            cell_npx = switch_cell.with_mixin(SwitchCellNeopixel())
            self.connect(self.npx_pwr, cell_npx.npx_pwr)
            self.connect(self.npx_gnd, cell_npx.npx_gnd)
            self.connect(cell_npx.npx_din, last_npx_dout)
            last_npx_dout = cell_npx.npx_dout

        self.connect(last_npx_dout, self.npx_dout)
