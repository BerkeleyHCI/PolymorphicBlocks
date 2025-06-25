const board = new PCB();

const sw = SwitchMatrix_2_3_sw(pt(0.039, 0.039))
// mcu
const U1 = board.add(XIAO_RP2040_SMD, {
  translate: pt(1.466, 0.410), rotate: 0,
  id: 'U1'
})

board.setNetlist([
  {name: "mcu.gpio.0_0", pads: [["U1", "7"], ["SW1", "2"], ["SW2", "2"], ["SW3", "2"]]},
  {name: "mcu.gpio.0_1", pads: [["U1", "8"], ["SW4", "2"], ["SW5", "2"], ["SW6", "2"]]},
  {name: "mcu.gpio.1_0", pads: [["U1", "9"], ["D1", "2"], ["D4", "2"]]},
  {name: "mcu.gpio.1_1", pads: [["U1", "11"], ["D2", "2"], ["D5", "2"]]},
  {name: "mcu.gpio.1_2", pads: [["U1", "10"], ["D3", "2"], ["D6", "2"]]},
  {name: "mcu.pwr_out", pads: [["U1", "12"]]},
  {name: "mcu.gnd", pads: [["U1", "13"]]},
  {name: "mcu.vusb_out", pads: [["U1", "14"]]},
  {name: "sw.d[0,0].cathode", pads: [["D1", "1"], ["SW1", "1"]]},
  {name: "sw.d[0,1].cathode", pads: [["D2", "1"], ["SW2", "1"]]},
  {name: "sw.d[0,2].cathode", pads: [["D3", "1"], ["SW3", "1"]]},
  {name: "sw.d[1,0].cathode", pads: [["D4", "1"], ["SW4", "1"]]},
  {name: "sw.d[1,1].cathode", pads: [["D5", "1"], ["SW5", "1"]]},
  {name: "sw.d[1,2].cathode", pads: [["D6", "1"], ["SW6", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.85748031496063, 2.1181102362204722);
const xMin = Math.min(limit0[0], limit1[0]);
const xMax = Math.max(limit0[0], limit1[0]);
const yMin = Math.min(limit0[1], limit1[1]);
const yMax = Math.max(limit0[1], limit1[1]);

const filletRadius = 0.1;
const outline = path(
  [(xMin+xMax/2), yMax],
  ["fillet", filletRadius, [xMax, yMax]],
  ["fillet", filletRadius, [xMax, yMin]],
  ["fillet", filletRadius, [xMin, yMin]],
  ["fillet", filletRadius, [xMin, yMax]],
  [(xMin+xMax/2), yMax],
);
board.addShape("outline", outline);

renderPCB({
  pcb: board,
  layerColors: {
    "F.Paste": "#000000ff",
    "F.Mask": "#000000ff",
    "B.Mask": "#000000ff",
    "componentLabels": "#00e5e5e5",
    "outline": "#002d00ff",
    "padLabels": "#ffff99e5",
    "B.Cu": "#ef4e4eff",
    "F.Cu": "#ff8c00cc",
  },
  limits: {
    x: [xMin, xMax],
    y: [yMin, yMax]
  },
  background: "#00000000",
  mmPerUnit: 25.4
})

function SwitchMatrix_2_3_sw(xy, colSpacing=0.5, rowSpacing=0.5, diodeOffset=[0.25, 0]) {
  // Circuit generator params
  const ncols = 2
  const nrows = 3

  // Global params
  const traceSize = 0.015
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }

  // Actual generator code
  allColWirePoints = []
  for (let yIndex=0; yIndex < nrows; yIndex++) {
    colWirePoints = []
    rowDiodeVias = []

    for (let xIndex=0; xIndex < ncols; xIndex++) {
      index = yIndex * ncols + xIndex + 1

      buttonPos = [xy[0] + colSpacing * xIndex, xy[1] + rowSpacing * yIndex]
      obj.footprints[`SW${1 + xIndex * nrows + yIndex}`] = button = board.add(
        SW_Hotswap_Kailh_MX,
        {
          translate: buttonPos, rotate: 0,
          id: `SW${1 + xIndex * nrows + yIndex}`
        })

      diodePos = [buttonPos[0] + diodeOffset[0], buttonPos[1] + diodeOffset[1]]
      obj[`D${1 + xIndex * nrows + yIndex}`] = diode = board.add(
        D_SOD_323,
        {
          translate: diodePos, rotate: 90,
          id: `D${1 + xIndex * nrows + yIndex}`
        })

      // create stub wire for button -> column common line
      colWirePoint = [buttonPos[0], button.padY("2")]
      board.wire([colWirePoint, button.pad("2")], traceSize, "F.Cu")
      colWirePoints.push(colWirePoint)

      // create wire for button -> diode
      board.wire([button.pad("1"), diode.pad("1")], traceSize, "F.Cu")
      diodeViaPos = [diode.padX("2"), buttonPos[1] + rowSpacing / 2]
      diodeVia = board.add(viaTemplate, {translate: diodeViaPos})
      board.wire([diode.pad("2"), diodeVia.pos], traceSize)

      if (rowDiodeVias.length > 0) {
        board.wire([rowDiodeVias[rowDiodeVias.length - 1].pos, diodeVia.pos], traceSize, "B.Cu")
      }
      rowDiodeVias.push(diodeVia)
    }
    allColWirePoints.push(colWirePoints)
  }

  // Inter-row wiring
  for (let xIndex=0; xIndex < allColWirePoints[0].length; xIndex++) {
    board.wire([
      allColWirePoints[0][xIndex],
      allColWirePoints[allColWirePoints.length - 1][xIndex]
    ], traceSize, "F.Cu")
  }

  return obj
}

