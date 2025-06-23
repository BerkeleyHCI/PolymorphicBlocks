const board = new PCB();

const sw = SwitchMatrix_2_3_sw(pt(0, 0))
const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.737, 2.535), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.776, 2.535), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.737, 2.575), rotate: 0,
  id: 'jlc_th_th3'
})
const conn_conn = board.add(JST_PH_B6B_PH_K_1x06_P2_00mm_Vertical, {
  translate: pt(1.666, 1.543), rotate: 0,
  id: 'conn_conn'
})
const conn_dtx_shift_fet = board.add(SOT_23, {
  translate: pt(1.645, 1.736), rotate: 0,
  id: 'conn_dtx_shift_fet'
})
const conn_dtx_shift_lv_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(2.009, 1.698), rotate: 0,
  id: 'conn_dtx_shift_lv_pu_res'
})
const conn_htx_shift_fet = board.add(SOT_23, {
  translate: pt(1.835, 1.736), rotate: 0,
  id: 'conn_htx_shift_fet'
})
const conn_htx_shift_lv_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(1.628, 1.871), rotate: 0,
  id: 'conn_htx_shift_lv_pu_res'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.545, 2.056), rotate: 0,
  id: 'tp_gnd_tp'
})
const choke_fb = board.add(L_0805_2012Metric, {
  translate: pt(1.315, 2.569), rotate: 0,
  id: 'choke_fb'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 2.573), rotate: 0,
  id: 'tp_pwr_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.180, 1.555), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.238, 1.765), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.073, 1.775), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.062, 2.573), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(0.564, 2.573), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(ESP_WROOM_02, {
  translate: pt(0.561, 1.695), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.228, 1.649), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.393, 1.639), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(1.299, 1.492), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(1.220, 1.756), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.376, 1.756), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(2.833, 2.047), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(2.833, 2.144), rotate: 0,
  id: 'ledr_res'
})
const oled_device_conn_conn = board.add(TE_3_1734839_0_1x30_1MP_P0_5mm_Horizontal, {
  translate: pt(2.461, 1.028), rotate: 0,
  id: 'oled_device_conn_conn'
})
const oled_lcd = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(2.565, 0.516), rotate: 0,
  id: 'oled_lcd'
})
const oled_c1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.328, 0.889), rotate: 0,
  id: 'oled_c1_cap'
})
const oled_c2_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.981, 1.006), rotate: 0,
  id: 'oled_c2_cap'
})
const oled_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(3.137, 1.006), rotate: 0,
  id: 'oled_iref_res'
})
const oled_vcomh_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.990, 0.899), rotate: 0,
  id: 'oled_vcomh_cap_cap'
})
const oled_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.293, 1.006), rotate: 0,
  id: 'oled_vdd_cap1_cap'
})
const oled_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.449, 1.006), rotate: 0,
  id: 'oled_vbat_cap_cap'
})
const oled_vcc_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.163, 0.899), rotate: 0,
  id: 'oled_vcc_cap_cap'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(3.303, 2.047), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(3.303, 2.144), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const io8_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(1.560, 2.564), rotate: 0,
  id: 'io8_pu_res'
})
const spk_dac_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(3.068, 2.047), rotate: 0,
  id: 'spk_dac_rc_r'
})
const spk_dac_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(3.068, 2.144), rotate: 0,
  id: 'spk_dac_rc_c'
})
const spk_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.811, 2.573), rotate: 0,
  id: 'spk_tp_tp'
})
const spk_drv_ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(1.692, 2.087), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.628, 2.224), rotate: 0,
  id: 'spk_drv_pwr_cap_cap'
})
const spk_drv_bulk_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.921, 2.057), rotate: 0,
  id: 'spk_drv_bulk_cap_cap'
})
const spk_drv_inp_res = board.add(R_0603_1608Metric, {
  translate: pt(1.783, 2.224), rotate: 0,
  id: 'spk_drv_inp_res'
})
const spk_drv_inp_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.939, 2.224), rotate: 0,
  id: 'spk_drv_inp_cap'
})
const spk_drv_inn_res = board.add(R_0603_1608Metric, {
  translate: pt(1.628, 2.321), rotate: 0,
  id: 'spk_drv_inn_res'
})
const spk_drv_inn_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.783, 2.321), rotate: 0,
  id: 'spk_drv_inn_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.481, 2.148), rotate: 0,
  id: 'spk_conn'
})
const npx_shift_fet = board.add(SOT_23, {
  translate: pt(2.191, 2.085), rotate: 0,
  id: 'npx_shift_fet'
})
const npx_shift_hv_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(2.174, 2.220), rotate: 0,
  id: 'npx_shift_hv_pu_res'
})
const npx_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 2.573), rotate: 0,
  id: 'npx_tp_tp'
})
const npx_led_0_ = board.add(LED_SK6812MINI_E, {
  translate: pt(2.418, 1.478), rotate: 0,
  id: 'npx_led_0_'
})
const npx_led_1_ = board.add(LED_SK6812MINI_E, {
  translate: pt(2.744, 1.478), rotate: 0,
  id: 'npx_led_1_'
})
const npx_led_2_ = board.add(LED_SK6812MINI_E, {
  translate: pt(2.418, 1.648), rotate: 0,
  id: 'npx_led_2_'
})
const npx_led_3_ = board.add(LED_SK6812MINI_E, {
  translate: pt(2.744, 1.648), rotate: 0,
  id: 'npx_led_3_'
})
const npx_led_4_ = board.add(LED_SK6812MINI_E, {
  translate: pt(2.418, 1.817), rotate: 0,
  id: 'npx_led_4_'
})
const npx_led_5_ = board.add(LED_SK6812MINI_E, {
  translate: pt(2.744, 1.817), rotate: 0,
  id: 'npx_led_5_'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.729330708661417, 2.728346456692914);
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

function SwitchMatrix_2_3_sw(xy, colSpacing=1, rowSpacing=1, diodeOffset=[0.25, 0]) {
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
      obj.footprints[`sw[${xIndex},${yIndex}]`] = button = board.add(
        SW_Hotswap_Kailh_MX,
        {
          translate: buttonPos, rotate: 0,
          id: `sw_sw_${xIndex}_${yIndex}_`
        })

      diodePos = [buttonPos[0] + diodeOffset[0], buttonPos[1] + diodeOffset[1]]
      obj[`d[${xIndex},${yIndex}]`] = diode = board.add(
        D_SOD_323,
        {
          translate: diodePos, rotate: 90,
          id: `sw_d_${xIndex}_${yIndex}_`
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

