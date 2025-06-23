const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.246, 2.093), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.285, 2.093), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.246, 2.132), rotate: 0,
  id: 'jlc_th_th3'
})
const pwr_conn_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.767, 1.870), rotate: 0,
  id: 'pwr_conn_conn'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.316, 2.130), rotate: 0,
  id: 'tp_pwr_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.816, 2.130), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(2.713, 1.244), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.772, 1.454), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.607, 1.464), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.062, 2.130), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(2.564, 2.130), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.419), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.403), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.403), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.533), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.399, 2.122), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(0.399, 2.219), rotate: 0,
  id: 'ledr_res'
})
const ledg_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.869, 2.122), rotate: 0,
  id: 'ledg_package'
})
const ledg_res = board.add(R_0603_1608Metric, {
  translate: pt(0.869, 2.219), rotate: 0,
  id: 'ledg_res'
})
const ledb_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.634, 2.122), rotate: 0,
  id: 'ledb_package'
})
const ledb_res = board.add(R_0603_1608Metric, {
  translate: pt(0.634, 2.219), rotate: 0,
  id: 'ledb_res'
})
const sw_0__package = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(3.299, 1.831), rotate: 0,
  id: 'sw_0__package'
})
const sw_1__package = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(2.617, 1.831), rotate: 0,
  id: 'sw_1__package'
})
const sw_2__package = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(0.111, 2.183), rotate: 0,
  id: 'sw_2__package'
})
const sw_3__package = board.add(SW_Push_1P1T_MP_NO_Horizontal_Alps_SKRTLAE010, {
  translate: pt(2.958, 1.831), rotate: 0,
  id: 'sw_3__package'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.338, 2.122), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.338, 2.219), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.909, 1.778), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.909, 1.892), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const env_ic = board.add(Bosch_LGA_8_3x3mm_P0_8mm_ClockwisePinNumbering, {
  translate: pt(0.069, 1.809), rotate: 0,
  id: 'env_ic'
})
const env_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.946), rotate: 0,
  id: 'env_vdd_cap_cap'
})
const env_vddio_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.946), rotate: 0,
  id: 'env_vddio_cap_cap'
})
const als_ic = board.add(HVSOF6, {
  translate: pt(2.163, 1.781), rotate: 0,
  id: 'als_ic'
})
const als_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.329, 1.769), rotate: 0,
  id: 'als_vcc_cap_cap'
})
const als_dvi_res = board.add(R_0603_1608Metric, {
  translate: pt(2.152, 1.891), rotate: 0,
  id: 'als_dvi_res'
})
const als_dvi_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.308, 1.891), rotate: 0,
  id: 'als_dvi_cap'
})
const rgb_shift_ic = board.add(SOT_23_5, {
  translate: pt(0.471, 1.807), rotate: 0,
  id: 'rgb_shift_ic'
})
const rgb_shift_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 1.942), rotate: 0,
  id: 'rgb_shift_vdd_cap_cap'
})
const rgb_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.066, 2.130), rotate: 0,
  id: 'rgb_tp_tp'
})
const digit_0__led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.039), rotate: 0,
  id: 'digit_0__led_0_'
})
const digit_0__led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.039), rotate: 0,
  id: 'digit_0__led_1_'
})
const digit_0__led_2_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.039), rotate: 0,
  id: 'digit_0__led_2_'
})
const digit_0__led_3_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.039), rotate: 0,
  id: 'digit_0__led_3_'
})
const digit_0__led_4_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.157), rotate: 0,
  id: 'digit_0__led_4_'
})
const digit_0__led_5_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.157), rotate: 0,
  id: 'digit_0__led_5_'
})
const digit_0__led_6_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.157), rotate: 0,
  id: 'digit_0__led_6_'
})
const digit_0__led_7_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.157), rotate: 0,
  id: 'digit_0__led_7_'
})
const digit_0__led_8_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.276), rotate: 0,
  id: 'digit_0__led_8_'
})
const digit_0__led_9_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.276), rotate: 0,
  id: 'digit_0__led_9_'
})
const digit_0__led_10_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.276), rotate: 0,
  id: 'digit_0__led_10_'
})
const digit_0__led_11_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.276), rotate: 0,
  id: 'digit_0__led_11_'
})
const digit_0__led_12_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.394), rotate: 0,
  id: 'digit_0__led_12_'
})
const digit_0__led_13_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.394), rotate: 0,
  id: 'digit_0__led_13_'
})
const digit_1__led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.591), rotate: 0,
  id: 'digit_1__led_0_'
})
const digit_1__led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.591), rotate: 0,
  id: 'digit_1__led_1_'
})
const digit_1__led_2_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.591), rotate: 0,
  id: 'digit_1__led_2_'
})
const digit_1__led_3_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.591), rotate: 0,
  id: 'digit_1__led_3_'
})
const digit_1__led_4_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.709), rotate: 0,
  id: 'digit_1__led_4_'
})
const digit_1__led_5_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.709), rotate: 0,
  id: 'digit_1__led_5_'
})
const digit_1__led_6_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.709), rotate: 0,
  id: 'digit_1__led_6_'
})
const digit_1__led_7_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.709), rotate: 0,
  id: 'digit_1__led_7_'
})
const digit_1__led_8_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.827), rotate: 0,
  id: 'digit_1__led_8_'
})
const digit_1__led_9_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.827), rotate: 0,
  id: 'digit_1__led_9_'
})
const digit_1__led_10_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.816, 0.827), rotate: 0,
  id: 'digit_1__led_10_'
})
const digit_1__led_11_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.934, 0.827), rotate: 0,
  id: 'digit_1__led_11_'
})
const digit_1__led_12_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.580, 0.945), rotate: 0,
  id: 'digit_1__led_12_'
})
const digit_1__led_13_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.698, 0.945), rotate: 0,
  id: 'digit_1__led_13_'
})
const digit_2__led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.591), rotate: 0,
  id: 'digit_2__led_0_'
})
const digit_2__led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.591), rotate: 0,
  id: 'digit_2__led_1_'
})
const digit_2__led_2_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.591), rotate: 0,
  id: 'digit_2__led_2_'
})
const digit_2__led_3_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.591), rotate: 0,
  id: 'digit_2__led_3_'
})
const digit_2__led_4_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.709), rotate: 0,
  id: 'digit_2__led_4_'
})
const digit_2__led_5_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.709), rotate: 0,
  id: 'digit_2__led_5_'
})
const digit_2__led_6_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.709), rotate: 0,
  id: 'digit_2__led_6_'
})
const digit_2__led_7_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.709), rotate: 0,
  id: 'digit_2__led_7_'
})
const digit_2__led_8_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.827), rotate: 0,
  id: 'digit_2__led_8_'
})
const digit_2__led_9_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.827), rotate: 0,
  id: 'digit_2__led_9_'
})
const digit_2__led_10_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.827), rotate: 0,
  id: 'digit_2__led_10_'
})
const digit_2__led_11_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.827), rotate: 0,
  id: 'digit_2__led_11_'
})
const digit_2__led_12_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.945), rotate: 0,
  id: 'digit_2__led_12_'
})
const digit_2__led_13_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.945), rotate: 0,
  id: 'digit_2__led_13_'
})
const digit_3__led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.039), rotate: 0,
  id: 'digit_3__led_0_'
})
const digit_3__led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.039), rotate: 0,
  id: 'digit_3__led_1_'
})
const digit_3__led_2_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.039), rotate: 0,
  id: 'digit_3__led_2_'
})
const digit_3__led_3_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.039), rotate: 0,
  id: 'digit_3__led_3_'
})
const digit_3__led_4_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.157), rotate: 0,
  id: 'digit_3__led_4_'
})
const digit_3__led_5_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.157), rotate: 0,
  id: 'digit_3__led_5_'
})
const digit_3__led_6_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.157), rotate: 0,
  id: 'digit_3__led_6_'
})
const digit_3__led_7_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.157), rotate: 0,
  id: 'digit_3__led_7_'
})
const digit_3__led_8_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.276), rotate: 0,
  id: 'digit_3__led_8_'
})
const digit_3__led_9_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.276), rotate: 0,
  id: 'digit_3__led_9_'
})
const digit_3__led_10_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.367, 0.276), rotate: 0,
  id: 'digit_3__led_10_'
})
const digit_3__led_11_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.485, 0.276), rotate: 0,
  id: 'digit_3__led_11_'
})
const digit_3__led_12_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.131, 0.394), rotate: 0,
  id: 'digit_3__led_12_'
})
const digit_3__led_13_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(3.249, 0.394), rotate: 0,
  id: 'digit_3__led_13_'
})
const center_led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.686, 1.780), rotate: 0,
  id: 'center_led_0_'
})
const center_led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.686, 1.898), rotate: 0,
  id: 'center_led_1_'
})
const meta_led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.489, 1.780), rotate: 0,
  id: 'meta_led_0_'
})
const meta_led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.489, 1.898), rotate: 0,
  id: 'meta_led_1_'
})
const spk_dac_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(1.104, 2.122), rotate: 0,
  id: 'spk_dac_rc_r'
})
const spk_dac_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.104, 2.219), rotate: 0,
  id: 'spk_dac_rc_c'
})
const spk_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.811, 2.130), rotate: 0,
  id: 'spk_tp_tp'
})
const spk_drv_ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(3.128, 1.171), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.063, 1.308), rotate: 0,
  id: 'spk_drv_pwr_cap_cap'
})
const spk_drv_bulk_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.357, 1.141), rotate: 0,
  id: 'spk_drv_bulk_cap_cap'
})
const spk_drv_inp_res = board.add(R_0603_1608Metric, {
  translate: pt(3.219, 1.308), rotate: 0,
  id: 'spk_drv_inp_res'
})
const spk_drv_inp_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.375, 1.308), rotate: 0,
  id: 'spk_drv_inp_cap'
})
const spk_drv_inn_res = board.add(R_0603_1608Metric, {
  translate: pt(3.063, 1.405), rotate: 0,
  id: 'spk_drv_inn_res'
})
const spk_drv_inn_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.219, 1.405), rotate: 0,
  id: 'spk_drv_inn_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.156, 1.870), rotate: 0,
  id: 'spk_conn'
})
const v5v_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.573, 2.122), rotate: 0,
  id: 'v5v_sense_div_top_res'
})
const v5v_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.573, 2.219), rotate: 0,
  id: 'v5v_sense_div_bottom_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.6425196850393706, 2.3822834645669295);
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


