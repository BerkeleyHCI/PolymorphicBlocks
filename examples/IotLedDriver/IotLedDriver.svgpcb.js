const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.586, 2.406), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.625, 2.406), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.586, 2.446), rotate: 0,
  id: 'jlc_th_th3'
})
const pwr = board.add(BarrelJack_CUI_PJ_036AH_SMT_Horizontal, {
  translate: pt(2.735, 1.220), rotate: 0,
  id: 'pwr'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.406, 2.444), rotate: 0,
  id: 'tp_pwr_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.402, 2.444), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_5v_ic = board.add(SOT_23_6, {
  translate: pt(1.912, 1.807), rotate: 0,
  id: 'reg_5v_ic'
})
const reg_5v_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 1.986), rotate: 0,
  id: 'reg_5v_fb_div_top_res'
})
const reg_5v_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.669, 2.116), rotate: 0,
  id: 'reg_5v_fb_div_bottom_res'
})
const reg_5v_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.825, 2.116), rotate: 0,
  id: 'reg_5v_hf_in_cap_cap'
})
const reg_5v_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.981, 2.116), rotate: 0,
  id: 'reg_5v_boot_cap'
})
const reg_5v_power_path_inductor = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(1.702, 1.829), rotate: 0,
  id: 'reg_5v_power_path_inductor'
})
const reg_5v_power_path_in_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(1.702, 2.003), rotate: 0,
  id: 'reg_5v_power_path_in_cap_cap'
})
const reg_5v_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.898, 1.996), rotate: 0,
  id: 'reg_5v_power_path_out_cap_cap'
})
const reg_5v_en_res = board.add(R_0603_1608Metric, {
  translate: pt(1.669, 2.213), rotate: 0,
  id: 'reg_5v_en_res'
})
const tp_5v_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.901, 2.444), rotate: 0,
  id: 'tp_5v_tp'
})
const prot_5v_diode = board.add(D_SOD_323, {
  translate: pt(1.159, 2.444), rotate: 0,
  id: 'prot_5v_diode'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.082, 1.882), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.140, 2.092), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.976, 2.102), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.151, 2.444), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(1.654, 2.444), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.242), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.226), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(2.067, 0.079), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(1.987, 0.356), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(2.143, 0.356), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.684, 2.435), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(0.684, 2.532), rotate: 0,
  id: 'ledr_res'
})
const enc_package = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(2.778, 0.344), rotate: 0,
  id: 'enc_package'
})
const v12_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.919, 2.435), rotate: 0,
  id: 'v12_sense_div_top_res'
})
const v12_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.919, 2.532), rotate: 0,
  id: 'v12_sense_div_bottom_res'
})
const rgb_ring_led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 1.780), rotate: 0,
  id: 'rgb_ring_led_0_'
})
const rgb_ring_led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 1.780), rotate: 0,
  id: 'rgb_ring_led_1_'
})
const rgb_ring_led_2_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 1.780), rotate: 0,
  id: 'rgb_ring_led_2_'
})
const rgb_ring_led_3_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.633, 1.780), rotate: 0,
  id: 'rgb_ring_led_3_'
})
const rgb_ring_led_4_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.751, 1.780), rotate: 0,
  id: 'rgb_ring_led_4_'
})
const rgb_ring_led_5_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 1.898), rotate: 0,
  id: 'rgb_ring_led_5_'
})
const rgb_ring_led_6_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 1.898), rotate: 0,
  id: 'rgb_ring_led_6_'
})
const rgb_ring_led_7_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 1.898), rotate: 0,
  id: 'rgb_ring_led_7_'
})
const rgb_ring_led_8_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.633, 1.898), rotate: 0,
  id: 'rgb_ring_led_8_'
})
const rgb_ring_led_9_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.751, 1.898), rotate: 0,
  id: 'rgb_ring_led_9_'
})
const rgb_ring_led_10_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 2.016), rotate: 0,
  id: 'rgb_ring_led_10_'
})
const rgb_ring_led_11_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 2.016), rotate: 0,
  id: 'rgb_ring_led_11_'
})
const rgb_ring_led_12_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 2.016), rotate: 0,
  id: 'rgb_ring_led_12_'
})
const rgb_ring_led_13_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.633, 2.016), rotate: 0,
  id: 'rgb_ring_led_13_'
})
const rgb_ring_led_14_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.751, 2.016), rotate: 0,
  id: 'rgb_ring_led_14_'
})
const rgb_ring_led_15_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.279, 2.134), rotate: 0,
  id: 'rgb_ring_led_15_'
})
const rgb_ring_led_16_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.397, 2.134), rotate: 0,
  id: 'rgb_ring_led_16_'
})
const rgb_ring_led_17_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(2.515, 2.134), rotate: 0,
  id: 'rgb_ring_led_17_'
})
const led_drv_0__ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.660, 2.105), rotate: 0,
  id: 'led_drv_0__ic'
})
const led_drv_0__rsense_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 2.242), rotate: 0,
  id: 'led_drv_0__rsense_res_res'
})
const led_drv_0__pwr_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.889, 2.075), rotate: 0,
  id: 'led_drv_0__pwr_cap_cap'
})
const led_drv_0__ind = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(0.669, 1.869), rotate: 0,
  id: 'led_drv_0__ind'
})
const led_drv_0__diode = board.add(D_SOD_323, {
  translate: pt(0.600, 2.251), rotate: 0,
  id: 'led_drv_0__diode'
})
const led_drv_1__ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.123, 2.105), rotate: 0,
  id: 'led_drv_1__ic'
})
const led_drv_1__rsense_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.224, 2.242), rotate: 0,
  id: 'led_drv_1__rsense_res_res'
})
const led_drv_1__pwr_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.352, 2.075), rotate: 0,
  id: 'led_drv_1__pwr_cap_cap'
})
const led_drv_1__ind = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(0.132, 1.869), rotate: 0,
  id: 'led_drv_1__ind'
})
const led_drv_1__diode = board.add(D_SOD_323, {
  translate: pt(0.063, 2.251), rotate: 0,
  id: 'led_drv_1__diode'
})
const led_drv_2__ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(3.247, 1.172), rotate: 0,
  id: 'led_drv_2__ic'
})
const led_drv_2__rsense_res_res = board.add(R_0603_1608Metric, {
  translate: pt(3.348, 1.309), rotate: 0,
  id: 'led_drv_2__rsense_res_res'
})
const led_drv_2__pwr_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.476, 1.142), rotate: 0,
  id: 'led_drv_2__pwr_cap_cap'
})
const led_drv_2__ind = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(3.256, 0.935), rotate: 0,
  id: 'led_drv_2__ind'
})
const led_drv_2__diode = board.add(D_SOD_323, {
  translate: pt(3.188, 1.318), rotate: 0,
  id: 'led_drv_2__diode'
})
const led_drv_3__ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(1.197, 2.105), rotate: 0,
  id: 'led_drv_3__ic'
})
const led_drv_3__rsense_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.298, 2.242), rotate: 0,
  id: 'led_drv_3__rsense_res_res'
})
const led_drv_3__pwr_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.426, 2.075), rotate: 0,
  id: 'led_drv_3__pwr_cap_cap'
})
const led_drv_3__ind = board.add(L_Sunlord_SWPA6045S, {
  translate: pt(1.206, 1.869), rotate: 0,
  id: 'led_drv_3__ind'
})
const led_drv_3__diode = board.add(D_SOD_323, {
  translate: pt(1.137, 2.251), rotate: 0,
  id: 'led_drv_3__diode'
})
const led_conn = board.add(JST_PH_S2B_PH_K_1x02_P2_00mm_Horizontal, {
  translate: pt(3.470, 2.006), rotate: 0,
  id: 'led_conn'
})
const rgb_conn = board.add(JST_PH_S6B_PH_K_1x06_P2_00mm_Horizontal, {
  translate: pt(0.096, 2.672), rotate: 0,
  id: 'rgb_conn'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.684251968503937, 2.7842519685039373);
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


