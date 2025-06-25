const board = new PCB();

const sw = SwitchMatrix_2_3_sw(pt(0.039, 0.039))
// jlc_th.th1
const DH1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.737, 3.240), rotate: 0,
  id: 'DH1'
})
// jlc_th.th2
const DH2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.776, 3.240), rotate: 0,
  id: 'DH2'
})
// jlc_th.th3
const DH3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.737, 3.280), rotate: 0,
  id: 'DH3'
})
// conn.conn
const DJ1 = board.add(JST_PH_B6B_PH_K_1x06_P2_00mm_Vertical, {
  translate: pt(1.666, 2.248), rotate: 0,
  id: 'DJ1'
})
// conn.dtx_shift.fet
const DQ1 = board.add(SOT_23, {
  translate: pt(1.645, 2.441), rotate: 0,
  id: 'DQ1'
})
// conn.dtx_shift.lv_pu.res
const DR1 = board.add(R_0603_1608Metric, {
  translate: pt(2.009, 2.403), rotate: 0,
  id: 'DR1'
})
// conn.htx_shift.fet
const DQ2 = board.add(SOT_23, {
  translate: pt(1.835, 2.441), rotate: 0,
  id: 'DQ2'
})
// conn.htx_shift.lv_pu.res
const DR2 = board.add(R_0603_1608Metric, {
  translate: pt(1.628, 2.576), rotate: 0,
  id: 'DR2'
})
// tp_gnd.tp
const DTP1 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.545, 2.760), rotate: 0,
  id: 'DTP1'
})
// choke.fb
const DFB1 = board.add(L_0805_2012Metric, {
  translate: pt(1.315, 3.274), rotate: 0,
  id: 'DFB1'
})
// tp_pwr.tp
const DTP2 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 3.278), rotate: 0,
  id: 'DTP2'
})
// reg_3v3.ic
const DU1 = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.180, 2.260), rotate: 0,
  id: 'DU1'
})
// reg_3v3.in_cap.cap
const DC1 = board.add(C_0603_1608Metric, {
  translate: pt(3.238, 2.470), rotate: 0,
  id: 'DC1'
})
// reg_3v3.out_cap.cap
const DC2 = board.add(C_0805_2012Metric, {
  translate: pt(3.073, 2.480), rotate: 0,
  id: 'DC2'
})
// tp_3v3.tp
const DTP3 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 3.278), rotate: 0,
  id: 'DTP3'
})
// prot_3v3.diode
const DD1 = board.add(D_SOD_323, {
  translate: pt(0.564, 3.278), rotate: 0,
  id: 'DD1'
})
// mcu.ic
const DU2 = board.add(ESP_WROOM_02, {
  translate: pt(0.561, 2.400), rotate: 0,
  id: 'DU2'
})
// mcu.vcc_cap0.cap
const DC3 = board.add(C_0805_2012Metric, {
  translate: pt(1.228, 2.354), rotate: 0,
  id: 'DC3'
})
// mcu.vcc_cap1.cap
const DC4 = board.add(C_0603_1608Metric, {
  translate: pt(1.393, 2.344), rotate: 0,
  id: 'DC4'
})
// mcu.prog.conn
const DJ2 = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(1.299, 2.197), rotate: 0,
  id: 'DJ2'
})
// mcu.en_pull.rc.r
const DR3 = board.add(R_0603_1608Metric, {
  translate: pt(1.220, 2.460), rotate: 0,
  id: 'DR3'
})
// mcu.en_pull.rc.c
const DC5 = board.add(C_0603_1608Metric, {
  translate: pt(1.376, 2.460), rotate: 0,
  id: 'DC5'
})
// ledr.package
const DD8 = board.add(LED_0603_1608Metric, {
  translate: pt(2.833, 2.752), rotate: 0,
  id: 'DD8'
})
// ledr.res
const DR4 = board.add(R_0603_1608Metric, {
  translate: pt(2.833, 2.849), rotate: 0,
  id: 'DR4'
})
// oled.device.conn.conn
const DJ3 = board.add(TE_3_1734839_0_1x30_1MP_P0_5mm_Horizontal, {
  translate: pt(1.540, 1.028), rotate: 0,
  id: 'DJ3'
})
// oled.lcd
const DU3 = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(1.644, 0.516), rotate: 0,
  id: 'DU3'
})
// oled.c1_cap
const DC6 = board.add(C_0603_1608Metric, {
  translate: pt(2.406, 0.889), rotate: 0,
  id: 'DC6'
})
// oled.c2_cap
const DC7 = board.add(C_0603_1608Metric, {
  translate: pt(2.060, 1.006), rotate: 0,
  id: 'DC7'
})
// oled.iref_res
const DR5 = board.add(R_0603_1608Metric, {
  translate: pt(2.216, 1.006), rotate: 0,
  id: 'DR5'
})
// oled.vcomh_cap.cap
const DC8 = board.add(C_0805_2012Metric, {
  translate: pt(2.069, 0.899), rotate: 0,
  id: 'DC8'
})
// oled.vdd_cap1.cap
const DC9 = board.add(C_0603_1608Metric, {
  translate: pt(2.372, 1.006), rotate: 0,
  id: 'DC9'
})
// oled.vbat_cap.cap
const DC10 = board.add(C_0603_1608Metric, {
  translate: pt(2.528, 1.006), rotate: 0,
  id: 'DC10'
})
// oled.vcc_cap.cap
const DC11 = board.add(C_0805_2012Metric, {
  translate: pt(2.242, 0.899), rotate: 0,
  id: 'DC11'
})
// i2c_pull.scl_res.res
const DR6 = board.add(R_0603_1608Metric, {
  translate: pt(3.068, 2.752), rotate: 0,
  id: 'DR6'
})
// i2c_pull.sda_res.res
const DR7 = board.add(R_0603_1608Metric, {
  translate: pt(3.068, 2.848), rotate: 0,
  id: 'DR7'
})
// io8_pu.res
const DR8 = board.add(R_0603_1608Metric, {
  translate: pt(1.560, 3.269), rotate: 0,
  id: 'DR8'
})
// spk_dac.rc.r
const DR9 = board.add(R_0603_1608Metric, {
  translate: pt(3.303, 2.752), rotate: 0,
  id: 'DR9'
})
// spk_dac.rc.c
const DC12 = board.add(C_0603_1608Metric, {
  translate: pt(3.303, 2.848), rotate: 0,
  id: 'DC12'
})
// spk_tp.tp
const DTP4 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.811, 3.278), rotate: 0,
  id: 'DTP4'
})
// spk_drv.ic
const DU4 = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(1.692, 2.792), rotate: 0,
  id: 'DU4'
})
// spk_drv.pwr_cap.cap
const DC13 = board.add(C_0603_1608Metric, {
  translate: pt(1.628, 2.929), rotate: 0,
  id: 'DC13'
})
// spk_drv.bulk_cap.cap
const DC14 = board.add(C_0805_2012Metric, {
  translate: pt(1.921, 2.761), rotate: 0,
  id: 'DC14'
})
// spk_drv.inp_res
const DR10 = board.add(R_0603_1608Metric, {
  translate: pt(1.783, 2.929), rotate: 0,
  id: 'DR10'
})
// spk_drv.inp_cap
const DC15 = board.add(C_0603_1608Metric, {
  translate: pt(1.939, 2.929), rotate: 0,
  id: 'DC15'
})
// spk_drv.inn_res
const DR11 = board.add(R_0603_1608Metric, {
  translate: pt(1.628, 3.026), rotate: 0,
  id: 'DR11'
})
// spk_drv.inn_cap
const DC16 = board.add(C_0603_1608Metric, {
  translate: pt(1.783, 3.026), rotate: 0,
  id: 'DC16'
})
// spk.conn
const DJ4 = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.481, 2.853), rotate: 0,
  id: 'DJ4'
})
// npx_shift.fet
const DQ3 = board.add(SOT_23, {
  translate: pt(2.191, 2.790), rotate: 0,
  id: 'DQ3'
})
// npx_shift.hv_pu.res
const DR12 = board.add(R_0603_1608Metric, {
  translate: pt(2.174, 2.925), rotate: 0,
  id: 'DR12'
})
// npx_tp.tp
const DTP5 = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.062, 3.278), rotate: 0,
  id: 'DTP5'
})
// npx.led[0]
const DD9 = board.add(LED_SK6812MINI_E, {
  translate: pt(2.418, 2.183), rotate: 0,
  id: 'DD9'
})
// npx.led[1]
const DD10 = board.add(LED_SK6812MINI_E, {
  translate: pt(2.744, 2.183), rotate: 0,
  id: 'DD10'
})
// npx.led[2]
const DD11 = board.add(LED_SK6812MINI_E, {
  translate: pt(2.418, 2.352), rotate: 0,
  id: 'DD11'
})
// npx.led[3]
const DD12 = board.add(LED_SK6812MINI_E, {
  translate: pt(2.744, 2.352), rotate: 0,
  id: 'DD12'
})
// npx.led[4]
const DD13 = board.add(LED_SK6812MINI_E, {
  translate: pt(2.418, 2.522), rotate: 0,
  id: 'DD13'
})
// npx.led[5]
const DD14 = board.add(LED_SK6812MINI_E, {
  translate: pt(2.744, 2.522), rotate: 0,
  id: 'DD14'
})

board.setNetlist([
  {name: "Dgnd", pads: [["DJ1", "2"], ["DTP1", "1"], ["DU1", "1"], ["DD1", "2"], ["DU2", "9"], ["DU2", "19"], ["DR4", "2"], ["DU4", "7"], ["DU4", "9"], ["DD9", "3"], ["DD10", "3"], ["DD11", "3"], ["DD12", "3"], ["DD13", "3"], ["DD14", "3"], ["DC12", "2"], ["DR5", "2"], ["DC16", "2"], ["DC1", "2"], ["DC2", "2"], ["DC3", "2"], ["DC4", "2"], ["DJ2", "5"], ["DC8", "2"], ["DC9", "2"], ["DC10", "2"], ["DC11", "2"], ["DC13", "2"], ["DC14", "2"], ["DC5", "2"], ["DJ3", "23"], ["DJ3", "30"], ["DJ3", "1"], ["DJ3", "2"], ["DJ3", "14"], ["DJ3", "15"], ["DJ3", "10"], ["DJ3", "9"], ["DJ3", "8"], ["DJ3", "7"], ["DJ3", "6"], ["DJ3", "19"], ["DJ3", "21"], ["DJ3", "16"], ["DJ3", "18"]]},
  {name: "Dpwr", pads: [["DFB1", "2"], ["DTP2", "1"], ["DU1", "3"], ["DU4", "1"], ["DU4", "6"], ["DD9", "1"], ["DD10", "1"], ["DD11", "1"], ["DD12", "1"], ["DD13", "1"], ["DD14", "1"], ["DR12", "1"], ["DC1", "1"], ["DC13", "1"], ["DC14", "1"]]},
  {name: "Dv3v3", pads: [["DU1", "2"], ["DTP3", "1"], ["DD1", "1"], ["DU2", "1"], ["DR8", "1"], ["DQ3", "1"], ["DC2", "1"], ["DC3", "1"], ["DC4", "1"], ["DJ2", "1"], ["DC9", "1"], ["DC10", "1"], ["DR6", "1"], ["DR7", "1"], ["DR3", "1"], ["DJ3", "22"], ["DJ3", "25"], ["DQ1", "1"], ["DQ2", "1"], ["DR1", "1"], ["DR2", "1"], ["DJ3", "20"]]},
  {name: "Dconn.pwr", pads: [["DFB1", "1"], ["DJ1", "4"]]},
  {name: "Dconn.uart.rx", pads: [["DU2", "4"], ["DQ2", "2"], ["DR2", "2"]]},
  {name: "Dconn.uart.tx", pads: [["DU2", "3"], ["DQ1", "2"], ["DR1", "2"]]},
  {name: "Dmcu.gpio.swc_0", pads: [["DU2", "5"], ["DSW1", "2"], ["DSW2", "2"], ["DSW3", "2"]]},
  {name: "Dmcu.gpio.swc_1", pads: [["DU2", "15"], ["DSW4", "2"], ["DSW5", "2"], ["DSW6", "2"]]},
  {name: "Dmcu.gpio.swr_0", pads: [["DU2", "14"], ["DD2", "2"], ["DD5", "2"]]},
  {name: "Dmcu.gpio.swr_1", pads: [["DU2", "13"], ["DD3", "2"], ["DD6", "2"]]},
  {name: "Dmcu.gpio.swr_2", pads: [["DU2", "10"], ["DD4", "2"], ["DD7", "2"]]},
  {name: "Dmcu.program_boot_node", pads: [["DU2", "8"], ["DD8", "2"], ["DJ2", "2"]]},
  {name: "Di2c_pull.i2c.scl", pads: [["DU2", "17"], ["DR6", "2"], ["DJ3", "13"]]},
  {name: "Di2c_pull.i2c.sda", pads: [["DU2", "18"], ["DR7", "2"], ["DJ3", "12"], ["DJ3", "11"]]},
  {name: "Doled.reset", pads: [["DU2", "16"], ["DJ3", "17"]]},
  {name: "Dspk_chain_0", pads: [["DU2", "7"], ["DR8", "2"], ["DR9", "1"]]},
  {name: "Dspk_chain_1", pads: [["DTP4", "1"], ["DC15", "2"], ["DR9", "2"], ["DC12", "1"]]},
  {name: "Dspk_chain_2.a", pads: [["DU4", "8"], ["DJ4", "1"]]},
  {name: "Dspk_chain_2.b", pads: [["DU4", "5"], ["DJ4", "2"]]},
  {name: "Dnpx_shift.lv_io", pads: [["DU2", "6"], ["DQ3", "2"]]},
  {name: "Dnpx_shift.hv_io", pads: [["DD9", "4"], ["DTP5", "1"], ["DQ3", "3"], ["DR12", "2"]]},
  {name: "Dconn.dtx_shift.hv_io", pads: [["DJ1", "3"], ["DQ1", "3"]]},
  {name: "Dconn.htx_shift.hv_io", pads: [["DJ1", "5"], ["DQ2", "3"]]},
  {name: "Dmcu.program_uart_node.a_tx", pads: [["DU2", "12"], ["DJ2", "3"]]},
  {name: "Dmcu.program_uart_node.b_tx", pads: [["DU2", "11"], ["DJ2", "4"]]},
  {name: "Dmcu.program_en_node", pads: [["DU2", "2"], ["DJ2", "6"], ["DR3", "2"], ["DC5", "1"]]},
  {name: "Dsw.d[0,0].cathode", pads: [["DD2", "1"], ["DSW1", "1"]]},
  {name: "Dsw.d[0,1].cathode", pads: [["DD3", "1"], ["DSW2", "1"]]},
  {name: "Dsw.d[0,2].cathode", pads: [["DD4", "1"], ["DSW3", "1"]]},
  {name: "Dsw.d[1,0].cathode", pads: [["DD5", "1"], ["DSW4", "1"]]},
  {name: "Dsw.d[1,1].cathode", pads: [["DD6", "1"], ["DSW5", "1"]]},
  {name: "Dsw.d[1,2].cathode", pads: [["DD7", "1"], ["DSW6", "1"]]},
  {name: "Dledr.res.a", pads: [["DR4", "1"], ["DD8", "1"]]},
  {name: "Doled.c1_cap.pos", pads: [["DC6", "1"], ["DJ3", "27"]]},
  {name: "Doled.c1_cap.neg", pads: [["DC6", "2"], ["DJ3", "26"]]},
  {name: "Doled.c2_cap.pos", pads: [["DC7", "1"], ["DJ3", "29"]]},
  {name: "Doled.c2_cap.neg", pads: [["DC7", "2"], ["DJ3", "28"]]},
  {name: "Doled.iref_res.a", pads: [["DR5", "1"], ["DJ3", "5"]]},
  {name: "Doled.device.vcomh", pads: [["DJ3", "4"], ["DC8", "1"]]},
  {name: "Doled.device.vcc", pads: [["DJ3", "3"], ["DC11", "1"]]},
  {name: "Dspk_drv.inp_cap.pos", pads: [["DC15", "1"], ["DR10", "1"]]},
  {name: "Dspk_drv.inp_res.b", pads: [["DR10", "2"], ["DU4", "4"]]},
  {name: "Dspk_drv.inn_cap.pos", pads: [["DC16", "1"], ["DR11", "1"]]},
  {name: "Dspk_drv.inn_res.b", pads: [["DR11", "2"], ["DU4", "3"]]},
  {name: "Dnpx.led[0].dout", pads: [["DD9", "2"], ["DD10", "4"]]},
  {name: "Dnpx.led[1].dout", pads: [["DD10", "2"], ["DD11", "4"]]},
  {name: "Dnpx.led[2].dout", pads: [["DD11", "2"], ["DD12", "4"]]},
  {name: "Dnpx.led[3].dout", pads: [["DD12", "2"], ["DD13", "4"]]},
  {name: "Dnpx.led[4].dout", pads: [["DD13", "2"], ["DD14", "4"]]},
  {name: "Dnpx.dout", pads: [["DD14", "2"]]}
])

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.729330708661417, 3.4330708661417324);
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
      obj.footprints[`DSW${1 + xIndex * nrows + yIndex}`] = button = board.add(
        SW_Hotswap_Kailh_MX,
        {
          translate: buttonPos, rotate: 0,
          id: `DSW${1 + xIndex * nrows + yIndex}`
        })

      diodePos = [buttonPos[0] + diodeOffset[0], buttonPos[1] + diodeOffset[1]]
      obj[`DD${2 + xIndex * nrows + yIndex}`] = diode = board.add(
        D_SOD_323,
        {
          translate: diodePos, rotate: 90,
          id: `DD${2 + xIndex * nrows + yIndex}`
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

