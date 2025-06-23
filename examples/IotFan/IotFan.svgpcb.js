const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.751, 1.742), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.791, 1.742), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.751, 1.781), rotate: 0,
  id: 'jlc_th_th3'
})
const pwr = board.add(BarrelJack_CUI_PJ_036AH_SMT_Horizontal, {
  translate: pt(1.256, 0.413), rotate: 0,
  id: 'pwr'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.271, 1.464), rotate: 0,
  id: 'tp_pwr_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.567, 1.779), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_5v_ic = board.add(SOT_23_6, {
  translate: pt(0.301, 0.874), rotate: 0,
  id: 'reg_5v_ic'
})
const reg_5v_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.452, 1.053), rotate: 0,
  id: 'reg_5v_fb_div_top_res'
})
const reg_5v_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.183), rotate: 0,
  id: 'reg_5v_fb_div_bottom_res'
})
const reg_5v_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.183), rotate: 0,
  id: 'reg_5v_hf_in_cap_cap'
})
const reg_5v_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.183), rotate: 0,
  id: 'reg_5v_boot_cap'
})
const reg_5v_power_path_inductor = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(0.091, 0.896), rotate: 0,
  id: 'reg_5v_power_path_inductor'
})
const reg_5v_power_path_in_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 1.070), rotate: 0,
  id: 'reg_5v_power_path_in_cap_cap'
})
const reg_5v_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 1.063), rotate: 0,
  id: 'reg_5v_power_path_out_cap_cap'
})
const reg_5v_en_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.280), rotate: 0,
  id: 'reg_5v_en_res'
})
const tp_5v_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 1.779), rotate: 0,
  id: 'tp_5v_tp'
})
const prot_5v_diode = board.add(D_SOD_323, {
  translate: pt(2.024, 1.464), rotate: 0,
  id: 'prot_5v_diode'
})
const reg_3v3_ic = board.add(SOT_89_3, {
  translate: pt(2.260, 0.906), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.206, 1.072), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.362, 1.072), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 1.779), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(2.519, 1.464), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(QFN_32_1EP_5x5mm_P0_5mm_EP3_65x3_65mm, {
  translate: pt(1.768, 0.122), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vdd_bulk_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.932, 0.322), rotate: 0,
  id: 'mcu_vdd_bulk_cap_cap'
})
const mcu_vdda_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.096, 0.312), rotate: 0,
  id: 'mcu_vdda_cap0_cap'
})
const mcu_vdda_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.252, 0.312), rotate: 0,
  id: 'mcu_vdda_cap1_cap'
})
const mcu_vddrtc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.408, 0.312), rotate: 0,
  id: 'mcu_vddrtc_cap_cap'
})
const mcu_vddcpu_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.704, 0.441), rotate: 0,
  id: 'mcu_vddcpu_cap_cap'
})
const mcu_vddspi_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 0.441), rotate: 0,
  id: 'mcu_vddspi_cap_cap'
})
const mcu_ant = board.add(D_1206_3216Metric, {
  translate: pt(1.736, 0.328), rotate: 0,
  id: 'mcu_ant'
})
const mcu_pi_c1 = board.add(C_0603_1608Metric, {
  translate: pt(2.016, 0.441), rotate: 0,
  id: 'mcu_pi_c1'
})
const mcu_pi_c2 = board.add(C_0603_1608Metric, {
  translate: pt(2.172, 0.441), rotate: 0,
  id: 'mcu_pi_c2'
})
const mcu_pi_l = board.add(L_0603_1608Metric, {
  translate: pt(2.328, 0.441), rotate: 0,
  id: 'mcu_pi_l'
})
const mcu_vdd3p3_l_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.704, 0.538), rotate: 0,
  id: 'mcu_vdd3p3_l_cap_cap'
})
const mcu_vdd3p3_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 0.538), rotate: 0,
  id: 'mcu_vdd3p3_cap_cap'
})
const mcu_vdd3p3_l_ind = board.add(L_0603_1608Metric, {
  translate: pt(2.016, 0.538), rotate: 0,
  id: 'mcu_vdd3p3_l_ind'
})
const mcu_crystal_package = board.add(Crystal_SMD_2520_4Pin_2_5x2_0mm, {
  translate: pt(2.311, 0.059), rotate: 0,
  id: 'mcu_crystal_package'
})
const mcu_crystal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(2.172, 0.538), rotate: 0,
  id: 'mcu_crystal_cap_a'
})
const mcu_crystal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(2.328, 0.538), rotate: 0,
  id: 'mcu_crystal_cap_b'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(2.067, 0.079), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(1.704, 0.635), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 0.635), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.011, 1.456), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(1.011, 1.553), rotate: 0,
  id: 'ledr_res'
})
const enc_package = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(0.394, 0.344), rotate: 0,
  id: 'enc_package'
})
const v12_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.246, 1.456), rotate: 0,
  id: 'v12_sense_div_top_res'
})
const v12_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.246, 1.552), rotate: 0,
  id: 'v12_sense_div_bottom_res'
})
const rgb_ring_led_0_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 0.846), rotate: 0,
  id: 'rgb_ring_led_0_'
})
const rgb_ring_led_1_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 0.846), rotate: 0,
  id: 'rgb_ring_led_1_'
})
const rgb_ring_led_2_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 0.846), rotate: 0,
  id: 'rgb_ring_led_2_'
})
const rgb_ring_led_3_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.022, 0.846), rotate: 0,
  id: 'rgb_ring_led_3_'
})
const rgb_ring_led_4_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.140, 0.846), rotate: 0,
  id: 'rgb_ring_led_4_'
})
const rgb_ring_led_5_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 0.965), rotate: 0,
  id: 'rgb_ring_led_5_'
})
const rgb_ring_led_6_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 0.965), rotate: 0,
  id: 'rgb_ring_led_6_'
})
const rgb_ring_led_7_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 0.965), rotate: 0,
  id: 'rgb_ring_led_7_'
})
const rgb_ring_led_8_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.022, 0.965), rotate: 0,
  id: 'rgb_ring_led_8_'
})
const rgb_ring_led_9_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.140, 0.965), rotate: 0,
  id: 'rgb_ring_led_9_'
})
const rgb_ring_led_10_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 1.083), rotate: 0,
  id: 'rgb_ring_led_10_'
})
const rgb_ring_led_11_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 1.083), rotate: 0,
  id: 'rgb_ring_led_11_'
})
const rgb_ring_led_12_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 1.083), rotate: 0,
  id: 'rgb_ring_led_12_'
})
const rgb_ring_led_13_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.022, 1.083), rotate: 0,
  id: 'rgb_ring_led_13_'
})
const rgb_ring_led_14_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(1.140, 1.083), rotate: 0,
  id: 'rgb_ring_led_14_'
})
const rgb_ring_led_15_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.668, 1.201), rotate: 0,
  id: 'rgb_ring_led_15_'
})
const rgb_ring_led_16_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.786, 1.201), rotate: 0,
  id: 'rgb_ring_led_16_'
})
const rgb_ring_led_17_ = board.add(LED_SK6812_EC15_1_5x1_5mm, {
  translate: pt(0.904, 1.201), rotate: 0,
  id: 'rgb_ring_led_17_'
})
const fan_0_ = board.add(FanPinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.069, 1.576), rotate: 0,
  id: 'fan_0_'
})
const fan_drv_0__pre = board.add(SOT_23, {
  translate: pt(1.798, 1.126), rotate: 0,
  id: 'fan_drv_0__pre'
})
const fan_drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.972, 1.088), rotate: 0,
  id: 'fan_drv_0__pull'
})
const fan_drv_0__drv = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.869, 0.913), rotate: 0,
  id: 'fan_drv_0__drv'
})
const fan_ctl_0__drv = board.add(SOT_23, {
  translate: pt(1.498, 1.494), rotate: 0,
  id: 'fan_ctl_0__drv'
})
const fan_1_ = board.add(FanPinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.545, 1.576), rotate: 0,
  id: 'fan_1_'
})
const fan_drv_1__pre = board.add(SOT_23, {
  translate: pt(1.373, 1.126), rotate: 0,
  id: 'fan_drv_1__pre'
})
const fan_drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.546, 1.088), rotate: 0,
  id: 'fan_drv_1__pull'
})
const fan_drv_1__drv = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.443, 0.913), rotate: 0,
  id: 'fan_drv_1__drv'
})
const fan_ctl_1__drv = board.add(SOT_23, {
  translate: pt(1.767, 1.494), rotate: 0,
  id: 'fan_ctl_1__drv'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.7001968503937013, 1.9346456692913387);
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


