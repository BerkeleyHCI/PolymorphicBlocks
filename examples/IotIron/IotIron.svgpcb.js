const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.408, 3.059), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.448, 3.059), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.408, 3.099), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(3.321, 1.905), rotate: 0,
  id: 'usb_conn'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.068, 3.097), rotate: 0,
  id: 'tp_pwr_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.817, 3.097), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_23_6, {
  translate: pt(2.331, 1.807), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.049, 2.156), rotate: 0,
  id: 'reg_3v3_fb_div_top_res'
})
const reg_3v3_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.205, 2.156), rotate: 0,
  id: 'reg_3v3_fb_div_bottom_res'
})
const reg_3v3_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.361, 2.156), rotate: 0,
  id: 'reg_3v3_hf_in_cap_cap'
})
const reg_3v3_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.517, 2.156), rotate: 0,
  id: 'reg_3v3_boot_cap'
})
const reg_3v3_power_path_inductor = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(2.101, 1.849), rotate: 0,
  id: 'reg_3v3_power_path_inductor'
})
const reg_3v3_power_path_in_cap_cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(2.081, 2.042), rotate: 0,
  id: 'reg_3v3_power_path_in_cap_cap_c_0_'
})
const reg_3v3_power_path_in_cap_cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(2.302, 2.042), rotate: 0,
  id: 'reg_3v3_power_path_in_cap_cap_c_1_'
})
const reg_3v3_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.498, 2.035), rotate: 0,
  id: 'reg_3v3_power_path_out_cap_cap'
})
const reg_3v3_en_res = board.add(R_0603_1608Metric, {
  translate: pt(2.049, 2.252), rotate: 0,
  id: 'reg_3v3_en_res'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.813, 3.097), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(1.315, 3.097), rotate: 0,
  id: 'prot_3v3_diode'
})
const reg_gate_ic = board.add(SOT_89_3, {
  translate: pt(3.761, 1.839), rotate: 0,
  id: 'reg_gate_ic'
})
const reg_gate_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.716, 2.015), rotate: 0,
  id: 'reg_gate_in_cap_cap'
})
const reg_gate_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.880, 2.005), rotate: 0,
  id: 'reg_gate_out_cap_cap'
})
const tp_gate_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 3.097), rotate: 0,
  id: 'tp_gate_tp'
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
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(2.880, 2.661), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(2.880, 2.757), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const pd_ic = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(0.890, 2.705), rotate: 0,
  id: 'pd_ic'
})
const pd_vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.049, 2.846), rotate: 0,
  id: 'pd_vdd_cap_0__cap'
})
const pd_vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(0.884, 2.856), rotate: 0,
  id: 'pd_vdd_cap_1__cap'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(3.293, 3.126), rotate: 0,
  id: 'usb_esd'
})
const vusb_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(3.818, 2.661), rotate: 0,
  id: 'vusb_sense_div_top_res'
})
const vusb_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(3.818, 2.757), rotate: 0,
  id: 'vusb_sense_div_bottom_res'
})
const temp_ic = board.add(WSON_6_1EP_3x3mm_P0_95mm, {
  translate: pt(1.300, 2.705), rotate: 0,
  id: 'temp_ic'
})
const temp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.283, 2.846), rotate: 0,
  id: 'temp_vdd_cap_cap'
})
const enc_package = board.add(RotaryEncoder_Alps_EC11J15_Switch, {
  translate: pt(1.479, 2.085), rotate: 0,
  id: 'enc_package'
})
const oled_device_conn = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.800, 1.054), rotate: 0,
  id: 'oled_device_conn'
})
const oled_lcd = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(2.910, 0.516), rotate: 0,
  id: 'oled_lcd'
})
const oled_c1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.659, 0.889), rotate: 0,
  id: 'oled_c1_cap'
})
const oled_c2_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.815, 0.889), rotate: 0,
  id: 'oled_c2_cap'
})
const oled_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(3.313, 1.006), rotate: 0,
  id: 'oled_iref_res'
})
const oled_vcomh_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.321, 0.899), rotate: 0,
  id: 'oled_vcomh_cap_cap'
})
const oled_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.469, 1.006), rotate: 0,
  id: 'oled_vdd_cap1_cap'
})
const oled_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.624, 1.006), rotate: 0,
  id: 'oled_vbat_cap_cap'
})
const oled_vcc_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.494, 0.899), rotate: 0,
  id: 'oled_vcc_cap_cap'
})
const spk_drv_ic = board.add(QFN_16_1EP_3x3mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(0.493, 2.716), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.641, 2.868), rotate: 0,
  id: 'spk_drv_pwr_cap0_cap'
})
const spk_drv_pwr_cap1_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.476, 2.878), rotate: 0,
  id: 'spk_drv_pwr_cap1_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.589, 2.762), rotate: 0,
  id: 'spk_conn'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.941, 2.661), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(1.941, 2.758), rotate: 0,
  id: 'ledr_res'
})
const conv_power_path_inductor = board.add(L_TDK_SLF12575, {
  translate: pt(0.280, 1.996), rotate: 0,
  id: 'conv_power_path_inductor'
})
const conv_power_path_in_cap_cap_c_0_ = board.add(C_0805_2012Metric, {
  translate: pt(0.398, 2.340), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_0_'
})
const conv_power_path_in_cap_cap_c_1_ = board.add(C_0805_2012Metric, {
  translate: pt(0.571, 2.340), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_1_'
})
const conv_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.744, 2.340), rotate: 0,
  id: 'conv_power_path_out_cap_cap'
})
const conv_sw_driver_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.744, 1.846), rotate: 0,
  id: 'conv_sw_driver_ic'
})
const conv_sw_driver_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.909, 2.330), rotate: 0,
  id: 'conv_sw_driver_cap_cap'
})
const conv_sw_driver_boot_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.389, 2.446), rotate: 0,
  id: 'conv_sw_driver_boot_cap_cap'
})
const conv_sw_low_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.744, 2.098), rotate: 0,
  id: 'conv_sw_low_fet'
})
const conv_sw_low_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.545, 2.446), rotate: 0,
  id: 'conv_sw_low_gate_res'
})
const conv_sw_high_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.146, 2.407), rotate: 0,
  id: 'conv_sw_high_fet'
})
const conv_sw_high_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.701, 2.446), rotate: 0,
  id: 'conv_sw_high_gate_res'
})
const tp_conv_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.314, 3.097), rotate: 0,
  id: 'tp_conv_tp'
})
const low_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(2.807, 3.088), rotate: 0,
  id: 'low_pull_res'
})
const low_rc_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(2.176, 2.661), rotate: 0,
  id: 'low_rc_rc_r'
})
const low_rc_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(2.176, 2.757), rotate: 0,
  id: 'low_rc_rc_c'
})
const high_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(3.041, 3.088), rotate: 0,
  id: 'high_pull_res'
})
const high_rc_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(3.114, 2.661), rotate: 0,
  id: 'high_rc_rc_r'
})
const high_rc_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(3.114, 2.757), rotate: 0,
  id: 'high_rc_rc_c'
})
const tp_pwm_l_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.063, 3.097), rotate: 0,
  id: 'tp_pwm_l_tp'
})
const tp_pwm_h_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.564, 3.097), rotate: 0,
  id: 'tp_pwm_h_tp'
})
const touch_sink = board.add(Symbol_DucklingSolid, {
  translate: pt(3.566, 3.059), rotate: 0,
  id: 'touch_sink'
})
const iron_conn = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(2.764, 2.010), rotate: 0,
  id: 'iron_conn'
})
const iron_isense_res_res_res = board.add(R_2512_6332Metric, {
  translate: pt(2.843, 2.196), rotate: 0,
  id: 'iron_isense_res_res_res'
})
const vsense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.410, 2.661), rotate: 0,
  id: 'vsense_div_top_res'
})
const vsense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.410, 2.757), rotate: 0,
  id: 'vsense_div_bottom_res'
})
const tp_v_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.317, 3.097), rotate: 0,
  id: 'tp_v_tp'
})
const vfilt_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(3.584, 2.661), rotate: 0,
  id: 'vfilt_rc_r'
})
const vfilt_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(3.584, 2.757), rotate: 0,
  id: 'vfilt_rc_c'
})
const ifilt_r1 = board.add(R_0603_1608Metric, {
  translate: pt(2.645, 2.661), rotate: 0,
  id: 'ifilt_r1'
})
const ifilt_r2 = board.add(R_0603_1608Metric, {
  translate: pt(2.645, 2.757), rotate: 0,
  id: 'ifilt_r2'
})
const tp_i_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(3.349, 2.661), rotate: 0,
  id: 'tp_i_rc_r'
})
const tp_i_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(3.349, 2.757), rotate: 0,
  id: 'tp_i_rc_c'
})
const iamp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.567, 3.097), rotate: 0,
  id: 'iamp_tp'
})
const tamp_r1 = board.add(R_0603_1608Metric, {
  translate: pt(4.053, 2.661), rotate: 0,
  id: 'tamp_r1'
})
const tamp_r2 = board.add(R_0603_1608Metric, {
  translate: pt(4.209, 2.661), rotate: 0,
  id: 'tamp_r2'
})
const tamp_rf = board.add(R_0603_1608Metric, {
  translate: pt(4.053, 2.757), rotate: 0,
  id: 'tamp_rf'
})
const tamp_rg = board.add(R_0603_1608Metric, {
  translate: pt(4.209, 2.757), rotate: 0,
  id: 'tamp_rg'
})
const tp_t_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.563, 3.097), rotate: 0,
  id: 'tp_t_tp'
})
const packed_opamp_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.146, 2.738), rotate: 0,
  id: 'packed_opamp_ic'
})
const packed_opamp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.913), rotate: 0,
  id: 'packed_opamp_vdd_cap_cap'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.385236220472439, 3.2523622047244096);
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


