function CharlieplexedLedMatrix_5_6_matrix(xy, colSpacing=1, rowSpacing=1) {
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
      obj.footprints[`d[${yIndex}_${xIndex}]`] = led = board.add(LED_0603_1608Metric, {
        translate: ledPos,
        id: `matrix_d[${yIndex}_${xIndex}]`
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
    obj.footprints[`r[${xIndex + 1}]`] = res = board.add(R_0603_1608Metric, {
      translate: resPos,
      id: `matrix_r[${xIndex + 1}]`
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

const matrix = CharlieplexedLedMatrix_5_6_matrix(pt(0, 0))
const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0, 0), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0, 0), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0, 0), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0, 0), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const tp_vusb_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0, 0), rotate: 0,
  id: 'tp_vusb_tp'
})
const tp_gnd_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0, 0), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(0, 0), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0, 0), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_123, {
  translate: pt(0, 0), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(ESP_WROOM_02, {
  translate: pt(0, 0), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_0805_2012Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0, 0), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_boot_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(0, 0), rotate: 0,
  id: 'mcu_boot_package'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0, 0), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const sw1_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(0, 0), rotate: 0,
  id: 'sw1_package'
})