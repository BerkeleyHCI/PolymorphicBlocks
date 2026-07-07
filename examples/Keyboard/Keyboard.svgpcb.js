const board = new PCB();

const sw = SwitchDiodeMatrixNeopixels_3_4_sw(pt(0.039, 0.039))
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.674, 2.783), rotate: 0,
  id: 'J1'
})
// usb.esd
const U1 = board.add(SOT_23, {
  translate: pt(0.998, 2.685), rotate: 0,
  id: 'U1'
})
// usb.cc_pull.cc1
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.981, 2.820), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.981, 2.917), rotate: 0,
  id: 'R2'
})
// reg.ic
const U2 = board.add(SOT_223_3_TabPin2, {
  translate: pt(0.173, 2.760), rotate: 0,
  id: 'U2'
})
// reg.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.279, 2.970), rotate: 0,
  id: 'C1'
})
// reg.out_cap.cap
const C2 = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 2.986), rotate: 0,
  id: 'C2'
})
// mcu.crystal.package
const X1 = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(3.235, 1.357), rotate: 0,
  id: 'X1'
})
// mcu.crystal.cap_a
const C3 = board.add(C_0603_1608Metric, {
  translate: pt(3.210, 1.492), rotate: 0,
  id: 'C3'
})
// mcu.crystal.cap_b
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(3.210, 1.589), rotate: 0,
  id: 'C4'
})
// mcu.ic
const U3 = board.add(LQFP_32_7x7mm_P0_8mm, {
  translate: pt(2.909, 1.494), rotate: 0,
  id: 'U3'
})
// mcu.sdi.conn
const J2 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.594, 1.660), rotate: 0,
  id: 'J2'
})
// mcu.vdd_cap[0].cap
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(2.582, 1.799), rotate: 0,
  id: 'C5'
})
// mcu.vdd_cap[1].cap
const C6 = board.add(C_0603_1608Metric, {
  translate: pt(2.738, 1.799), rotate: 0,
  id: 'C6'
})
// mcu.vdda_cap.cap
const C7 = board.add(C_0603_1608Metric, {
  translate: pt(2.894, 1.799), rotate: 0,
  id: 'C7'
})
// mcu.reset_cap.cap
const C8 = board.add(C_0603_1608Metric, {
  translate: pt(3.050, 1.799), rotate: 0,
  id: 'C8'
})
// ledr.package
const D1 = board.add(LED_0603_1608Metric, {
  translate: pt(1.530, 2.647), rotate: 0,
  id: 'D1'
})
// ledr.res
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(1.530, 2.744), rotate: 0,
  id: 'R3'
})
// enc.package
const SW13 = board.add(RotaryEncoder_Bourns_PEC11S, {
  translate: pt(2.012, 1.634), rotate: 0,
  id: 'SW13'
})
// oled.device.conn
const J3 = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.033, 1.054), rotate: 0,
  id: 'J3'
})
// oled.lcd
const U4 = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(2.144, 0.516), rotate: 0,
  id: 'U4'
})
// oled.c1_cap
const C21 = board.add(C_0603_1608Metric, {
  translate: pt(2.893, 0.889), rotate: 0,
  id: 'C21'
})
// oled.c2_cap
const C22 = board.add(C_0603_1608Metric, {
  translate: pt(3.049, 0.889), rotate: 0,
  id: 'C22'
})
// oled.iref_res.res
const R4 = board.add(R_0603_1608Metric, {
  translate: pt(2.546, 1.006), rotate: 0,
  id: 'R4'
})
// oled.vcomh_cap.cap
const C23 = board.add(C_0805_2012Metric, {
  translate: pt(2.555, 0.899), rotate: 0,
  id: 'C23'
})
// oled.vdd_cap1.cap
const C24 = board.add(C_0603_1608Metric, {
  translate: pt(2.702, 1.006), rotate: 0,
  id: 'C24'
})
// oled.vbat_cap.cap
const C25 = board.add(C_0603_1608Metric, {
  translate: pt(2.858, 1.006), rotate: 0,
  id: 'C25'
})
// oled.vcc_cap.cap
const C26 = board.add(C_0805_2012Metric, {
  translate: pt(2.728, 0.899), rotate: 0,
  id: 'C26'
})
// i2c_pull.scl_res.res
const R5 = board.add(R_0603_1608Metric, {
  translate: pt(1.765, 2.647), rotate: 0,
  id: 'R5'
})
// i2c_pull.sda_res.res
const R6 = board.add(R_0603_1608Metric, {
  translate: pt(1.765, 2.744), rotate: 0,
  id: 'R6'
})
// npx_shift.ic
const U5 = board.add(SOT_23_5, {
  translate: pt(1.273, 2.685), rotate: 0,
  id: 'U5'
})
// npx_shift.vdd_cap.cap
const C27 = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 2.820), rotate: 0,
  id: 'C27'
})

board.setNetlist([
  {name: "usb.pwr", pads: [["J1", "A4"], ["J1", "A9"], ["J1", "B4"], ["J1", "B9"], ["U2", "3"], ["C1", "1"], ["D3", "1"], ["C9", "1"], ["D5", "1"], ["C10", "1"], ["D7", "1"], ["C11", "1"], ["D9", "1"], ["C12", "1"], ["D11", "1"], ["C13", "1"], ["D13", "1"], ["C14", "1"], ["D15", "1"], ["C15", "1"], ["D17", "1"], ["C16", "1"], ["D19", "1"], ["C17", "1"], ["D21", "1"], ["C18", "1"], ["D23", "1"], ["C19", "1"], ["D25", "1"], ["C20", "1"], ["U5", "5"], ["C27", "1"]]},
  {name: "usb.gnd", pads: [["J1", "A1"], ["J1", "A12"], ["J1", "B1"], ["J1", "B12"], ["J1", "S1"], ["U1", "3"], ["R1", "1"], ["R2", "1"], ["U2", "1"], ["C1", "2"], ["C2", "2"], ["X1", "2"], ["X1", "4"], ["C3", "2"], ["C4", "2"], ["U3", "16"], ["U3", "31"], ["U3", "32"], ["J2", "2"], ["C5", "2"], ["C6", "2"], ["C7", "2"], ["C8", "2"], ["D3", "3"], ["C9", "2"], ["D5", "3"], ["C10", "2"], ["D7", "3"], ["C11", "2"], ["D9", "3"], ["C12", "2"], ["D11", "3"], ["C13", "2"], ["D13", "3"], ["C14", "2"], ["D15", "3"], ["C15", "2"], ["D17", "3"], ["C16", "2"], ["D19", "3"], ["C17", "2"], ["D21", "3"], ["C18", "2"], ["D23", "3"], ["C19", "2"], ["D25", "3"], ["C20", "2"], ["SW13", "C"], ["SW13", "S2"], ["J3", "1"], ["J3", "10"], ["J3", "12"], ["J3", "13"], ["J3", "15"], ["J3", "16"], ["J3", "17"], ["J3", "21"], ["J3", "22"], ["J3", "23"], ["J3", "24"], ["J3", "25"], ["J3", "29"], ["J3", "30"], ["J3", "8"], ["R4", "1"], ["C23", "2"], ["C24", "2"], ["C25", "2"], ["C26", "2"], ["U5", "1"], ["U5", "3"], ["C27", "2"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"], ["U1", "2"], ["U3", "22"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"], ["U1", "1"], ["U3", "21"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "reg.pwr_out", pads: [["U2", "2"], ["C2", "1"], ["U3", "1"], ["U3", "17"], ["U3", "5"], ["J2", "1"], ["C5", "1"], ["C6", "1"], ["C7", "1"], ["D1", "2"], ["J3", "11"], ["J3", "6"], ["J3", "9"], ["C24", "1"], ["C25", "1"], ["R5", "1"], ["R6", "1"]]},
  {name: "mcu.gpio.sw_col_0", pads: [["U3", "18"], ["SW1", "1"], ["SW4", "1"], ["SW7", "1"], ["SW10", "1"]]},
  {name: "mcu.gpio.sw_col_1", pads: [["U3", "12"], ["SW2", "1"], ["SW5", "1"], ["SW8", "1"], ["SW11", "1"]]},
  {name: "mcu.gpio.sw_col_2", pads: [["U3", "10"], ["SW3", "1"], ["SW6", "1"], ["SW9", "1"], ["SW12", "1"]]},
  {name: "mcu.gpio.sw_row_0", pads: [["U3", "20"], ["D2", "1"], ["D4", "1"], ["D6", "1"]]},
  {name: "mcu.gpio.sw_row_1", pads: [["U3", "19"], ["D8", "1"], ["D10", "1"], ["D12", "1"]]},
  {name: "mcu.gpio.sw_row_2", pads: [["U3", "13"], ["D14", "1"], ["D16", "1"], ["D18", "1"]]},
  {name: "mcu.gpio.sw_row_3", pads: [["U3", "11"], ["D20", "1"], ["D22", "1"], ["D24", "1"]]},
  {name: "mcu.xtal_node.xi", pads: [["X1", "1"], ["C3", "1"], ["U3", "2"]]},
  {name: "mcu.xtal_node.xo", pads: [["X1", "3"], ["C4", "1"], ["U3", "3"]]},
  {name: "mcu.ic.nrst", pads: [["U3", "4"], ["C8", "1"]]},
  {name: "mcu.ic.swdio", pads: [["U3", "23"], ["J2", "3"]]},
  {name: "mcu.ic.swclk", pads: [["U3", "24"], ["J2", "4"]]},
  {name: "ledr.signal", pads: [["U3", "27"], ["R3", "2"]]},
  {name: "ledr.package.k", pads: [["D1", "1"], ["R3", "1"]]},
  {name: "sw.npx_din", pads: [["D3", "4"], ["U5", "4"]]},
  {name: "sw.npx_dout", pads: [["D21", "2"]]},
  {name: "sw.sw[0,0].npx_dout", pads: [["D3", "2"], ["D5", "4"]]},
  {name: "sw.sw[0,0].sw.com", pads: [["SW1", "2"], ["D2", "2"]]},
  {name: "sw.sw[1,0].npx_dout", pads: [["D5", "2"], ["D7", "4"]]},
  {name: "sw.sw[1,0].sw.com", pads: [["SW2", "2"], ["D4", "2"]]},
  {name: "sw.sw[2,0].npx_dout", pads: [["D7", "2"], ["D13", "4"]]},
  {name: "sw.sw[2,0].sw.com", pads: [["SW3", "2"], ["D6", "2"]]},
  {name: "sw.sw[0,1].npx_din", pads: [["D9", "4"], ["D11", "2"]]},
  {name: "sw.sw[0,1].npx_dout", pads: [["D9", "2"], ["D15", "4"]]},
  {name: "sw.sw[0,1].sw.com", pads: [["SW4", "2"], ["D8", "2"]]},
  {name: "sw.sw[1,1].npx_din", pads: [["D11", "4"], ["D13", "2"]]},
  {name: "sw.sw[1,1].sw.com", pads: [["SW5", "2"], ["D10", "2"]]},
  {name: "sw.sw[2,1].sw.com", pads: [["SW6", "2"], ["D12", "2"]]},
  {name: "sw.sw[0,2].npx_dout", pads: [["D15", "2"], ["D17", "4"]]},
  {name: "sw.sw[0,2].sw.com", pads: [["SW7", "2"], ["D14", "2"]]},
  {name: "sw.sw[1,2].npx_dout", pads: [["D17", "2"], ["D19", "4"]]},
  {name: "sw.sw[1,2].sw.com", pads: [["SW8", "2"], ["D16", "2"]]},
  {name: "sw.sw[2,2].npx_dout", pads: [["D19", "2"], ["D25", "4"]]},
  {name: "sw.sw[2,2].sw.com", pads: [["SW9", "2"], ["D18", "2"]]},
  {name: "sw.sw[0,3].npx_din", pads: [["D21", "4"], ["D23", "2"]]},
  {name: "sw.sw[0,3].sw.com", pads: [["SW10", "2"], ["D20", "2"]]},
  {name: "sw.sw[1,3].npx_din", pads: [["D23", "4"], ["D25", "2"]]},
  {name: "sw.sw[1,3].sw.com", pads: [["SW11", "2"], ["D22", "2"]]},
  {name: "sw.sw[2,3].sw.com", pads: [["SW12", "2"], ["D24", "2"]]},
  {name: "enc.a", pads: [["U3", "9"], ["SW13", "A"]]},
  {name: "enc.b", pads: [["U3", "8"], ["SW13", "B"]]},
  {name: "enc.sw", pads: [["U3", "7"], ["SW13", "S1"]]},
  {name: "oled.reset", pads: [["U3", "15"], ["J3", "14"]]},
  {name: "oled.i2c.scl", pads: [["U3", "29"], ["J3", "18"], ["R5", "2"]]},
  {name: "oled.i2c.sda", pads: [["U3", "30"], ["J3", "19"], ["J3", "20"], ["R6", "2"]]},
  {name: "oled.device.vcc", pads: [["J3", "28"], ["C26", "1"]]},
  {name: "oled.device.iref", pads: [["J3", "26"], ["R4", "2"]]},
  {name: "oled.device.vcomh", pads: [["J3", "27"], ["C23", "1"]]},
  {name: "oled.device.c1p", pads: [["J3", "4"], ["C21", "1"]]},
  {name: "oled.device.c1n", pads: [["J3", "5"], ["C21", "2"]]},
  {name: "oled.device.c2p", pads: [["J3", "2"], ["C22", "1"]]},
  {name: "oled.device.c2n", pads: [["J3", "3"], ["C22", "2"]]},
  {name: "npx_shift.input", pads: [["U3", "28"], ["U5", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.4354330708661416, 3.1496062992125986);
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

function SwitchDiodeMatrixNeopixels_3_4_sw(xy, colSpacing=0.5, rowSpacing=0.5, diodeOffset=[0.25, 0]) {
  // Circuit generator params
  const ncols = 3
  const nrows = 4

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
      obj[`D${2 + xIndex * nrows + yIndex}`] = diode = board.add(
        D_SOD_323,
        {
          translate: diodePos, rotate: 90,
          id: `D${2 + xIndex * nrows + yIndex}`
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

