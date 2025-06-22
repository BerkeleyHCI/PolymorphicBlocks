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

const sw = SwitchMatrix_2_3_sw(pt(0, 0))
const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 80.350), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.000, 80.350), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 81.350), rotate: 0,
  id: 'jlc_th_th3'
})
const conn_conn = board.add(JST_PH_B6B_PH_K_1x06_P2_00mm_Vertical, {
  translate: pt(43.950, 51.030), rotate: 0,
  id: 'conn_conn'
})
const conn_dtx_shift_fet = board.add(SOT_23, {
  translate: pt(43.420, 44.130), rotate: 0,
  id: 'conn_dtx_shift_fet'
})
const conn_dtx_shift_lv_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(42.980, 38.700), rotate: 0,
  id: 'conn_dtx_shift_lv_pu_res'
})
const conn_htx_shift_fet = board.add(SOT_23, {
  translate: pt(51.380, 44.130), rotate: 0,
  id: 'conn_htx_shift_fet'
})
const conn_htx_shift_lv_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(50.940, 38.700), rotate: 0,
  id: 'conn_htx_shift_lv_pu_res'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(69.875, 67.420), rotate: 0,
  id: 'tp_gnd_tp'
})
const choke_fb = board.add(L_0805_2012Metric, {
  translate: pt(95.385, 67.320), rotate: 0,
  id: 'choke_fb'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(76.235, 67.420), rotate: 0,
  id: 'tp_pwr_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(63.820, 41.570), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(67.300, 46.900), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(61.120, 47.150), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(63.515, 67.420), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(57.235, 67.420), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(ESP_WROOM_02, {
  translate: pt(14.250, 56.320), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_0805_2012Metric, {
  translate: pt(31.200, 54.870), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(30.980, 59.580), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(33.000, 48.890), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(30.980, 38.700), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(30.980, 41.160), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(51.145, 67.205), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(51.140, 69.670), rotate: 0,
  id: 'ledr_res'
})
const oled_device_conn_conn = board.add(TE_3_1734839_0_1x30_1MP_P0_5mm_Horizontal, {
  translate: pt(10.720, 24.260), rotate: 0,
  id: 'oled_device_conn_conn'
})
const oled_lcd = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(13.350, 7.750), rotate: 0,
  id: 'oled_lcd'
})
const oled_c1_cap = board.add(C_0603_1608Metric, {
  translate: pt(39.840, 27.550), rotate: 0,
  id: 'oled_c1_cap'
})
const oled_c2_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.480, 34.240), rotate: 0,
  id: 'oled_c2_cap'
})
const oled_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(5.440, 34.240), rotate: 0,
  id: 'oled_iref_res'
})
const oled_vcomh_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(28.140, 22.840), rotate: 0,
  id: 'oled_vcomh_cap_cap'
})
const oled_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(27.920, 27.550), rotate: 0,
  id: 'oled_vdd_cap1_cap'
})
const oled_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(33.880, 27.550), rotate: 0,
  id: 'oled_vbat_cap_cap'
})
const oled_vcc_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(34.540, 22.840), rotate: 0,
  id: 'oled_vcc_cap_cap'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(17.360, 67.200), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(17.360, 71.660), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const io8_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(101.615, 67.200), rotate: 0,
  id: 'io8_pu_res'
})
const spk_dac_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(33.280, 67.200), rotate: 0,
  id: 'spk_dac_rc_r'
})
const spk_dac_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(33.280, 69.660), rotate: 0,
  id: 'spk_dac_rc_c'
})
const spk_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(82.595, 67.420), rotate: 0,
  id: 'spk_tp_tp'
})
const spk_drv_ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(9.520, 68.220), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.480, 72.160), rotate: 0,
  id: 'spk_drv_pwr_cap_cap'
})
const spk_drv_bulk_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.700, 67.450), rotate: 0,
  id: 'spk_drv_bulk_cap_cap'
})
const spk_drv_inp_res = board.add(R_0603_1608Metric, {
  translate: pt(7.440, 72.160), rotate: 0,
  id: 'spk_drv_inp_res'
})
const spk_drv_inp_cap = board.add(C_0603_1608Metric, {
  translate: pt(11.400, 72.160), rotate: 0,
  id: 'spk_drv_inp_cap'
})
const spk_drv_inn_res = board.add(R_0603_1608Metric, {
  translate: pt(1.480, 76.620), rotate: 0,
  id: 'spk_drv_inn_res'
})
const spk_drv_inn_cap = board.add(C_0603_1608Metric, {
  translate: pt(5.440, 76.620), rotate: 0,
  id: 'spk_drv_inn_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(42.210, 68.670), rotate: 0,
  id: 'spk_conn'
})
const npx_shift_fet = board.add(SOT_23, {
  translate: pt(25.760, 72.630), rotate: 0,
  id: 'npx_shift_fet'
})
const npx_shift_hv_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(25.320, 67.200), rotate: 0,
  id: 'npx_shift_hv_pu_res'
})
const npx_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(88.955, 67.420), rotate: 0,
  id: 'npx_tp_tp'
})
const npx_led_0_ = board.add(LED_SK6812MINI_E, {
  translate: pt(77.430, 39.620), rotate: 0,
  id: 'npx_led_0_'
})
const npx_led_1_ = board.add(LED_SK6812MINI_E, {
  translate: pt(85.730, 39.620), rotate: 0,
  id: 'npx_led_1_'
})
const npx_led_2_ = board.add(LED_SK6812MINI_E, {
  translate: pt(77.430, 43.920), rotate: 0,
  id: 'npx_led_2_'
})
const npx_led_3_ = board.add(LED_SK6812MINI_E, {
  translate: pt(85.730, 43.920), rotate: 0,
  id: 'npx_led_3_'
})
const npx_led_4_ = board.add(LED_SK6812MINI_E, {
  translate: pt(77.430, 48.220), rotate: 0,
  id: 'npx_led_4_'
})
const npx_led_5_ = board.add(LED_SK6812MINI_E, {
  translate: pt(85.730, 48.220), rotate: 0,
  id: 'npx_led_5_'
})