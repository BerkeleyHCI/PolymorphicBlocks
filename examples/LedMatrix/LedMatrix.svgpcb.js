const board = new PCB();

const matrix = CharlieplexedLedMatrix_5_6_matrix(pt(0.039, 0.039))
// jlc_th.th1
const H1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.561, 1.518), rotate: 0,
  id: 'H1'
})
// jlc_th.th2
const H2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.600, 1.518), rotate: 0,
  id: 'H2'
})
// jlc_th.th3
const H3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.561, 1.557), rotate: 0,
  id: 'H3'
})
// usb.conn
const J1 = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.683), rotate: 0,
  id: 'J1'
})
// usb.cc_pull.cc1.res
const R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.938), rotate: 0,
  id: 'R1'
})
// usb.cc_pull.cc2.res
const R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.938), rotate: 0,
  id: 'R2'
})
// tp_vusb.tp
const TP1 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.539, 1.571), rotate: 0,
  id: 'TP1'
})
// tp_gnd.tp
const TP2 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.826, 1.571), rotate: 0,
  id: 'TP2'
})
// reg_3v3.ic
const U1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(0.710, 1.660), rotate: 0,
  id: 'U1'
})
// reg_3v3.in_cap.cap
const C1 = board.add(C_0603_1608Metric, {
  translate: pt(0.769, 1.870), rotate: 0,
  id: 'C1'
})
// reg_3v3.out_cap.cap
const C2 = board.add(C_0805_2012Metric, {
  translate: pt(0.604, 1.880), rotate: 0,
  id: 'C2'
})
// tp_3v3.tp
const TP3 = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(2.114, 1.571), rotate: 0,
  id: 'TP3'
})
// prot_3v3.diode
const D1 = board.add(D_SOD_323, {
  translate: pt(2.380, 1.556), rotate: 0,
  id: 'D1'
})
// mcu.ic
const U2 = board.add(ESP_WROOM_02, {
  translate: pt(1.679, 0.281), rotate: 0,
  id: 'U2'
})
// mcu.vcc_cap0.cap
const C3 = board.add(C_0805_2012Metric, {
  translate: pt(2.346, 0.783), rotate: 0,
  id: 'C3'
})
// mcu.vcc_cap1.cap
const C4 = board.add(C_0603_1608Metric, {
  translate: pt(2.511, 0.773), rotate: 0,
  id: 'C4'
})
// mcu.prog.conn
const J2 = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.350, 0.370), rotate: 0,
  id: 'J2'
})
// mcu.boot.package
const SW1 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.447, 0.593), rotate: 0,
  id: 'SW1'
})
// mcu.en_pull.rc.r
const R3 = board.add(R_0603_1608Metric, {
  translate: pt(2.338, 0.889), rotate: 0,
  id: 'R3'
})
// mcu.en_pull.rc.c
const C5 = board.add(C_0603_1608Metric, {
  translate: pt(2.494, 0.889), rotate: 0,
  id: 'C5'
})
// sw1.package
const SW2 = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.169, 1.630), rotate: 0,
  id: 'SW2'
})

board.setNetlist([
  {name: "vusb", pads: [["J1", "A4"], ["J1", "B9"], ["J1", "B4"], ["J1", "A9"], ["TP1", "1"], ["U1", "3"], ["C1", "1"]]},
  {name: "gnd", pads: [["J1", "A1"], ["J1", "B12"], ["J1", "B1"], ["J1", "A12"], ["TP2", "1"], ["U1", "1"], ["D1", "2"], ["U2", "9"], ["U2", "19"], ["SW2", "2"], ["J1", "S1"], ["C1", "2"], ["C2", "2"], ["C3", "2"], ["C4", "2"], ["J2", "4"], ["SW1", "2"], ["C5", "2"], ["R1", "1"], ["R2", "1"]]},
  {name: "v3v3", pads: [["U1", "2"], ["TP3", "1"], ["D1", "1"], ["U2", "1"], ["C2", "1"], ["U2", "7"], ["U2", "16"], ["C3", "1"], ["C4", "1"], ["J2", "1"], ["R3", "1"]]},
  {name: "sw1.out", pads: [["U2", "18"], ["SW2", "1"]]},
  {name: "mcu.gpio.led_0", pads: [["U2", "3"], ["R4", "2"], ["D8", "2"], ["D14", "2"], ["D20", "2"], ["D26", "2"]]},
  {name: "mcu.gpio.led_1", pads: [["U2", "4"], ["D2", "2"], ["R5", "2"], ["D15", "2"], ["D21", "2"], ["D27", "2"]]},
  {name: "mcu.gpio.led_2", pads: [["U2", "5"], ["D3", "2"], ["D9", "2"], ["R6", "2"], ["D22", "2"], ["D28", "2"]]},
  {name: "mcu.gpio.led_3", pads: [["U2", "6"], ["D4", "2"], ["D10", "2"], ["D16", "2"], ["R7", "2"], ["D29", "2"]]},
  {name: "mcu.gpio.led_4", pads: [["U2", "17"], ["D5", "2"], ["D11", "2"], ["D17", "2"], ["D23", "2"], ["R8", "2"]]},
  {name: "mcu.gpio.led_5", pads: [["U2", "15"], ["D6", "2"], ["D12", "2"], ["D18", "2"], ["D24", "2"], ["D30", "2"]]},
  {name: "mcu.gpio.led_6", pads: [["U2", "10"], ["D7", "2"], ["D13", "2"], ["D19", "2"], ["D25", "2"], ["D31", "2"]]},
  {name: "usb.usb.dp", pads: [["J1", "A6"], ["J1", "B6"]]},
  {name: "usb.usb.dm", pads: [["J1", "A7"], ["J1", "B7"]]},
  {name: "usb.conn.cc.cc1", pads: [["J1", "A5"], ["R1", "2"]]},
  {name: "usb.conn.cc.cc2", pads: [["J1", "B5"], ["R2", "2"]]},
  {name: "mcu.program_uart_node.a_tx", pads: [["U2", "12"], ["J2", "2"]]},
  {name: "mcu.program_uart_node.b_tx", pads: [["U2", "11"], ["J2", "3"]]},
  {name: "mcu.program_en_node", pads: [["U2", "2"], ["R3", "2"], ["C5", "1"]]},
  {name: "mcu.program_boot_node", pads: [["U2", "8"], ["SW1", "1"]]},
  {name: "matrix.led[0_0].k", pads: [["D2", "1"], ["R4", "1"], ["D3", "1"], ["D4", "1"], ["D5", "1"], ["D6", "1"], ["D7", "1"]]},
  {name: "matrix.led[0_1].k", pads: [["D8", "1"], ["R5", "1"], ["D9", "1"], ["D10", "1"], ["D11", "1"], ["D12", "1"], ["D13", "1"]]},
  {name: "matrix.led[0_2].k", pads: [["D14", "1"], ["R6", "1"], ["D15", "1"], ["D16", "1"], ["D17", "1"], ["D18", "1"], ["D19", "1"]]},
  {name: "matrix.led[0_3].k", pads: [["D20", "1"], ["R7", "1"], ["D21", "1"], ["D22", "1"], ["D23", "1"], ["D24", "1"], ["D25", "1"]]},
  {name: "matrix.led[0_4].k", pads: [["D26", "1"], ["R8", "1"], ["D27", "1"], ["D28", "1"], ["D29", "1"], ["D30", "1"], ["D31", "1"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.7322834645669296, 2.084645669291339);
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

function CharlieplexedLedMatrix_5_6_matrix(xy, colSpacing=0.2, rowSpacing=0.2) {
  const kXCount = 5  // number of columns (x dimension)
  const kYCount = 6  // number of rows (y dimension)

  // Global params
  const traceSize = 0.015
  const viaTemplate = via(0.02, 0.035)

  // Return object
  const obj = {
    footprints: {},
    pts: {}
  }
  
  allLeds = []
  allVias = []
  lastViasPreResistor = []  // state preserved between rows
  for (let yIndex=0; yIndex < kYCount; yIndex++) {
    rowLeds = []
    rowVias = []

    viasPreResistor = []
    viasPostResistor = []  // on the same net as the prior row pre-resistor

    for (let xIndex=0; xIndex < kXCount; xIndex++) {
      ledPos = [xy[0] + colSpacing * xIndex, xy[1] + rowSpacing * yIndex]
      obj.footprints[`D${2 + yIndex + xIndex * kYCount}`] = led = board.add(LED_0603_1608Metric, {
        translate: ledPos,
        id: `D${2 + yIndex + xIndex * kYCount}`
      })
      rowLeds.push(led)

      // anode line
      thisVia = board.add(viaTemplate, {
        translate: [ledPos[0] + colSpacing*1/3, ledPos[1]]
      })
      rowVias.push(thisVia)
      board.wire([led.pad("2"), thisVia.pos], traceSize, "F.Cu")
      if (xIndex <= yIndex) {
        viasPreResistor.push(thisVia)
      } else {
        viasPostResistor.push(thisVia)
      }
    }
    allLeds.push(rowLeds)
    allVias.push(rowVias)

    // Wire the anode lines, including the row-crossing one accounting for the diagonal-skip where the resistor is in the schematic matrix
    // viasPreResistor guaranteed nonempty
    board.wire([viasPreResistor[0].pos, viasPreResistor[viasPreResistor.length - 1].pos], traceSize, "B.Cu")
    if (viasPostResistor.length > 0) {
      board.wire([viasPostResistor[0].pos, viasPostResistor[viasPostResistor.length - 1].pos], traceSize, "B.Cu")
    }

    // Create the inter-row bridging trace, if applicable
    if (viasPostResistor.length > 0 && lastViasPreResistor.length > 0) {
      via1Pos = lastViasPreResistor[lastViasPreResistor.length - 1].pos
      via2Pos = viasPostResistor[0].pos
      centerY = (via1Pos[1] + via2Pos[1]) / 2
      board.wire([via1Pos,
                  [via1Pos[0], centerY],
                  [via2Pos[0], centerY],
                  via2Pos
                 ],
                 traceSize, "B.Cu")
    }

    lastViasPreResistor = viasPreResistor
  }

  allResistors = []
  for (let xIndex=0; xIndex < kXCount; xIndex++) {
    const resPos = [xy[0] + colSpacing * xIndex, xy[1] + rowSpacing * kYCount]
    obj.footprints[`R${4 + xIndex + 1}`] = res = board.add(R_0603_1608Metric, {
      translate: resPos,
      id: `R${4 + xIndex}`
    })
    allResistors.push(res)

    if (xIndex < allVias.length && xIndex < allVias[xIndex].length - 1) {
      targetVia = allVias[xIndex][xIndex + 1]
      thisVia = board.add(viaTemplate, {
        translate: [resPos[0] + colSpacing*2/3, targetVia.pos[1]]
      })

      board.wire([
        res.pad("2"),
        [resPos[0] + colSpacing*2/3, res.padY("2")],
        thisVia.pos
      ], traceSize, "F.Cu")
      board.wire([
        thisVia.pos,
        targetVia.pos,
      ], traceSize, "B.Cu")
    } else if (xIndex <= allVias.length && xIndex < allVias[xIndex - 1].length) {
      // connect the last via
      thisVia = board.add(viaTemplate, {
        translate: [resPos[0] + colSpacing*2/3, resPos[1]]
      })
      targetVia = allVias[xIndex - 1][xIndex - 1]
      board.wire([
        res.pad("2"),
        thisVia.pos
      ], traceSize, "F.Cu")
      centerY = targetVia.pos[1] + colSpacing/2
      board.wire([
        thisVia.pos,
        [thisVia.pos[0], centerY],
        [targetVia.pos[0], centerY],
        targetVia.pos,
      ], traceSize, "B.Cu")
    }
  }

  // create the along-column cathode line
  for (let xIndex=0; xIndex < kXCount; xIndex++) {
    colPads = allLeds.flatMap(row => row.length > xIndex ? [row[xIndex].pad("1")] : [])
    if (xIndex < allResistors.length) {
      colPads.push(allResistors[xIndex].pad("1"))
    }

    for (let i=0; i<colPads.length - 1; i++) {
      board.wire([
        colPads[i],
        colPads[i+1]
      ], traceSize, "F.Cu")
    }
  }

  return obj
}

