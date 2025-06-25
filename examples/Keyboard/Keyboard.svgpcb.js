const board = new PCB();

const sw = SwitchMatrix_2_3_sw(pt(0.039, 0.039))
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.328, 0.958), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(1.176, 1.213), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(1.332, 1.213), rotate: 0,
  id: 'R2'
})
// reg.ic
const U1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(1.828, 0.935), rotate: 0,
  id: 'U1'
})
// reg.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(1.887, 1.145), rotate: 0,
  id: 'C1'
})
// reg.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(1.722, 1.155), rotate: 0,
  id: 'C2'
})
// mcu.swd.conn
const J2 = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(1.732, 0.146), rotate: 0,
  id: 'J2'
})
// mcu.ic
const U2 = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(1.321, 0.203), rotate: 0,
  id: 'U2'
})
// mcu.pwr_cap[0].cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(1.390, 0.483), rotate: 0,
  id: 'C3'
})
// mcu.pwr_cap[1].cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(1.554, 0.474), rotate: 0,
  id: 'C4'
})
// mcu.pwr_cap[2].cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(1.710, 0.474), rotate: 0,
  id: 'C5'
})
// mcu.pwr_cap[3].cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(1.866, 0.474), rotate: 0,
  id: 'C6'
})
// mcu.vdda_cap_0.cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(1.176, 0.647), rotate: 0,
  id: 'C7'
})
// mcu.vdda_cap_1.cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(1.332, 0.647), rotate: 0,
  id: 'C8'
})
// mcu.usb_pull.dp
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(1.488, 0.647), rotate: 0,
  id: 'R3'
})
// mcu.crystal.package
const X1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(1.201, 0.512), rotate: 0,
  id: 'X1'
})
// mcu.crystal.cap_a
const C9 = board.add(C_0603_1608Metric, {
  translate: pt(1.644, 0.647), rotate: 0,
  id: 'C9'
})
// mcu.crystal.cap_b
const C10 = board.add(C_0603_1608Metric, {
  translate: pt(1.800, 0.647), rotate: 0,
  id: 'C10'
})

board.setNetlist([
  {name: "usb.gnd", pads: [["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["U1", "1"], ["U2", "8"], ["U2", "23"], ["U2", "35"], ["U2", "47"], ["U2", "44"], ["J1", "S1"], ["C1", "2"], ["C2", "2"], ["C3", "2"], ["C4", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["X1", "2"], ["X1", "4"], ["R1", "1"], ["R2", "1"], ["J2", "3"], ["J2", "5"], ["J2", "9"], ["C9", "2"], ["C10", "2"]]},
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["U1", "3"], ["C1", "1"]]},
  {name: "reg.pwr_out", pads: [["U1", "2"], ["U2", "1"], ["U2", "9"], ["U2", "24"], ["U2", "36"], ["U2", "48"], ["C2", "1"], ["J2", "1"], ["C3", "1"], ["C4", "1"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["C8", "1"], ["R3", "1"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"], ["U2", "33"], ["R3", "2"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"], ["U2", "32"]]},
  {name: "mcu.gpio.0_0", pads: [["U2", "10"], ["SW1", "2"], ["SW2", "2"], ["SW3", "2"]]},
  {name: "mcu.gpio.0_1", pads: [["U2", "11"], ["SW4", "2"], ["SW5", "2"], ["SW6", "2"]]},
  {name: "mcu.gpio.1_0", pads: [["U2", "12"], ["D1", "2"], ["D4", "2"]]},
  {name: "mcu.gpio.1_1", pads: [["U2", "13"], ["D2", "2"], ["D5", "2"]]},
  {name: "mcu.gpio.1_2", pads: [["U2", "14"], ["D3", "2"], ["D6", "2"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "mcu.xtal_node.xi", pads: [["U2", "5"], ["X1", "1"], ["C9", "1"]]},
  {name: "mcu.xtal_node.xo", pads: [["U2", "6"], ["X1", "3"], ["C10", "1"]]},
  {name: "mcu.swd_node.swdio", pads: [["U2", "34"], ["J2", "2"]]},
  {name: "mcu.swd_node.swclk", pads: [["U2", "37"], ["J2", "4"]]},
  {name: "mcu.reset_node", pads: [["U2", "7"], ["J2", "10"]]},
  {name: "mcu.swd.swo", pads: [["J2", "6"]]},
  {name: "mcu.swd.tdi", pads: [["J2", "8"]]},
  {name: "sw.d[0,0].cathode", pads: [["D1", "1"], ["SW1", "1"]]},
  {name: "sw.d[0,1].cathode", pads: [["D2", "1"], ["SW2", "1"]]},
  {name: "sw.d[0,2].cathode", pads: [["D3", "1"], ["SW3", "1"]]},
  {name: "sw.d[1,0].cathode", pads: [["D4", "1"], ["SW4", "1"]]},
  {name: "sw.d[1,1].cathode", pads: [["D5", "1"], ["SW5", "1"]]},
  {name: "sw.d[1,2].cathode", pads: [["D6", "1"], ["SW6", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.119685039370079, 2.1181102362204722);
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

