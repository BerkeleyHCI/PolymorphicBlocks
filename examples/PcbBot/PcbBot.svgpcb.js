const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.327, 3.717), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.366, 3.717), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.327, 3.757), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(3.766, 1.905), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(3.615, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(3.771, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const batt_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.268, 3.498), rotate: 0,
  id: 'batt_conn'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.759, 3.406), rotate: 0,
  id: 'tp_gnd_tp'
})
const fuse_fuse = board.add(R_1206_3216Metric, {
  translate: pt(3.235, 3.413), rotate: 0,
  id: 'fuse_fuse'
})
const gate_pwr_gate_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(2.972, 2.206), rotate: 0,
  id: 'gate_pwr_gate_pull_res'
})
const gate_pwr_gate_pwr_fet = board.add(SOT_23, {
  translate: pt(3.363, 1.807), rotate: 0,
  id: 'gate_pwr_gate_pwr_fet'
})
const gate_pwr_gate_amp_res = board.add(R_0603_1608Metric, {
  translate: pt(3.128, 2.206), rotate: 0,
  id: 'gate_pwr_gate_amp_res'
})
const gate_pwr_gate_amp_fet = board.add(SOT_23, {
  translate: pt(2.989, 2.071), rotate: 0,
  id: 'gate_pwr_gate_amp_fet'
})
const gate_pwr_gate_ctl_diode = board.add(D_SOD_323, {
  translate: pt(3.167, 2.041), rotate: 0,
  id: 'gate_pwr_gate_ctl_diode'
})
const gate_pwr_gate_btn_diode = board.add(D_SOD_323, {
  translate: pt(3.333, 2.041), rotate: 0,
  id: 'gate_pwr_gate_btn_diode'
})
const gate_btn_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(3.081, 1.852), rotate: 0,
  id: 'gate_btn_package'
})
const prot_batt_diode = board.add(D_SMA, {
  translate: pt(2.889, 3.437), rotate: 0,
  id: 'prot_batt_diode'
})
const tp_batt_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.509, 3.406), rotate: 0,
  id: 'tp_batt_tp'
})
const pwr_or_pdr = board.add(R_0603_1608Metric, {
  translate: pt(3.977, 3.044), rotate: 0,
  id: 'pwr_or_pdr'
})
const pwr_or_diode = board.add(D_SOD_323, {
  translate: pt(3.816, 3.053), rotate: 0,
  id: 'pwr_or_diode'
})
const pwr_or_fet = board.add(SOT_23, {
  translate: pt(3.828, 2.909), rotate: 0,
  id: 'pwr_or_fet'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(1.004, 2.984), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.062, 3.194), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.898, 3.204), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(4.007, 3.406), rotate: 0,
  id: 'prot_3v3_diode'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.254, 3.406), rotate: 0,
  id: 'tp_3v3_tp'
})
const charger_ic = board.add(SOT_23_5, {
  translate: pt(3.381, 2.909), rotate: 0,
  id: 'charger_ic'
})
const charger_vdd_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.568, 2.881), rotate: 0,
  id: 'charger_vdd_cap_cap'
})
const charger_vbat_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.367, 3.054), rotate: 0,
  id: 'charger_vbat_cap_cap'
})
const charger_prog_res = board.add(R_0603_1608Metric, {
  translate: pt(3.531, 3.044), rotate: 0,
  id: 'charger_prog_res'
})
const charge_led_package = board.add(LED_0603_1608Metric, {
  translate: pt(2.105, 3.397), rotate: 0,
  id: 'charge_led_package'
})
const charge_led_res = board.add(R_0603_1608Metric, {
  translate: pt(2.105, 3.494), rotate: 0,
  id: 'charge_led_res'
})
const mcu_ic = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.789), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.773), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.000, 0.370), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_boot_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.096, 0.593), rotate: 0,
  id: 'mcu_boot_package'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.773), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.903), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(4.514, 3.435), rotate: 0,
  id: 'usb_esd'
})
const led_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.870, 3.397), rotate: 0,
  id: 'led_package'
})
const led_res = board.add(R_0603_1608Metric, {
  translate: pt(1.870, 3.494), rotate: 0,
  id: 'led_res'
})
const tof_elt_0_ = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.457, 2.309), rotate: 0,
  id: 'tof_elt_0_'
})
const tof_elt_1_ = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.636, 2.309), rotate: 0,
  id: 'tof_elt_1_'
})
const tof_elt_2_ = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.815, 2.309), rotate: 0,
  id: 'tof_elt_2_'
})
const tof_elt_3_ = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.994, 2.309), rotate: 0,
  id: 'tof_elt_3_'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(2.340, 3.397), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(2.340, 3.494), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.628, 3.406), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.628, 3.520), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const imu_ic = board.add(Bosch_LGA_14_3x2_5mm_P0_5mm, {
  translate: pt(0.854, 3.431), rotate: 0,
  id: 'imu_ic'
})
const imu_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.839, 3.563), rotate: 0,
  id: 'imu_vdd_cap_cap'
})
const imu_vddio_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.995, 3.563), rotate: 0,
  id: 'imu_vddio_cap_cap'
})
const mag_ic = board.add(LGA_16_3x3mm_P0_5mm, {
  translate: pt(4.222, 2.911), rotate: 0,
  id: 'mag_ic'
})
const mag_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(4.211, 3.048), rotate: 0,
  id: 'mag_vdd_cap_cap'
})
const mag_set_cap = board.add(C_0603_1608Metric, {
  translate: pt(4.367, 3.048), rotate: 0,
  id: 'mag_set_cap'
})
const mag_c1 = board.add(C_0805_2012Metric, {
  translate: pt(4.397, 2.881), rotate: 0,
  id: 'mag_c1'
})
const expander_ic = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(2.486, 2.951), rotate: 0,
  id: 'expander_ic'
})
const expander_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.393, 3.127), rotate: 0,
  id: 'expander_vdd_cap_cap'
})
const rgb_package = board.add(LED_D5_0mm_4_RGB_Staggered_Pins, {
  translate: pt(2.796, 3.000), rotate: 0,
  id: 'rgb_package'
})
const rgb_red_res = board.add(R_0603_1608Metric, {
  translate: pt(3.124, 2.871), rotate: 0,
  id: 'rgb_red_res'
})
const rgb_green_res = board.add(R_0603_1608Metric, {
  translate: pt(3.124, 2.968), rotate: 0,
  id: 'rgb_green_res'
})
const rgb_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(3.124, 3.065), rotate: 0,
  id: 'rgb_blue_res'
})
const oled_device_conn = board.add(Hirose_FH12_30S_0_5SH_1x30_1MP_P0_50mm_Horizontal, {
  translate: pt(2.956, 1.054), rotate: 0,
  id: 'oled_device_conn'
})
const oled_lcd = board.add(Lcd_Er_Oled0_96_1_1_Outline, {
  translate: pt(3.066, 0.516), rotate: 0,
  id: 'oled_lcd'
})
const oled_c1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.815, 0.889), rotate: 0,
  id: 'oled_c1_cap'
})
const oled_c2_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.971, 0.889), rotate: 0,
  id: 'oled_c2_cap'
})
const oled_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(3.469, 1.006), rotate: 0,
  id: 'oled_iref_res'
})
const oled_vcomh_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.477, 0.899), rotate: 0,
  id: 'oled_vcomh_cap_cap'
})
const oled_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.624, 1.006), rotate: 0,
  id: 'oled_vdd_cap1_cap'
})
const oled_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.780, 1.006), rotate: 0,
  id: 'oled_vbat_cap_cap'
})
const oled_vcc_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.650, 0.899), rotate: 0,
  id: 'oled_vcc_cap_cap'
})
const batt_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.574, 3.397), rotate: 0,
  id: 'batt_sense_div_top_res'
})
const batt_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.574, 3.494), rotate: 0,
  id: 'batt_sense_div_bottom_res'
})
const servo_0__conn = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(1.886, 3.112), rotate: 0,
  id: 'servo_0__conn'
})
const servo_1__conn = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(1.626, 3.112), rotate: 0,
  id: 'servo_1__conn'
})
const servo_2__conn = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(1.366, 3.112), rotate: 0,
  id: 'servo_2__conn'
})
const servo_3__conn = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(2.146, 3.112), rotate: 0,
  id: 'servo_3__conn'
})
const npx_led_0_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 1.848), rotate: 0,
  id: 'npx_led_0_'
})
const npx_led_1_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 1.848), rotate: 0,
  id: 'npx_led_1_'
})
const npx_led_2_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 1.848), rotate: 0,
  id: 'npx_led_2_'
})
const npx_led_3_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 1.848), rotate: 0,
  id: 'npx_led_3_'
})
const npx_led_4_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.104), rotate: 0,
  id: 'npx_led_4_'
})
const npx_led_5_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.104), rotate: 0,
  id: 'npx_led_5_'
})
const npx_led_6_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.104), rotate: 0,
  id: 'npx_led_6_'
})
const npx_led_7_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.104), rotate: 0,
  id: 'npx_led_7_'
})
const npx_led_8_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.360), rotate: 0,
  id: 'npx_led_8_'
})
const npx_led_9_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.360), rotate: 0,
  id: 'npx_led_9_'
})
const npx_led_10_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.360), rotate: 0,
  id: 'npx_led_10_'
})
const npx_led_11_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.360), rotate: 0,
  id: 'npx_led_11_'
})
const npx_led_12_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.616), rotate: 0,
  id: 'npx_led_12_'
})
const npx_led_13_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.616), rotate: 0,
  id: 'npx_led_13_'
})
const npx_led_14_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.616), rotate: 0,
  id: 'npx_led_14_'
})
const npx_led_15_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.616), rotate: 0,
  id: 'npx_led_15_'
})
const npx_key = board.add(LED_SK6812MINI_E, {
  translate: pt(0.144, 3.782), rotate: 0,
  id: 'npx_key'
})
const reg_2v5_ic = board.add(SOT_23, {
  translate: pt(0.466, 3.435), rotate: 0,
  id: 'reg_2v5_ic'
})
const reg_2v5_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 3.570), rotate: 0,
  id: 'reg_2v5_in_cap_cap'
})
const reg_2v5_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.605, 3.570), rotate: 0,
  id: 'reg_2v5_out_cap_cap'
})
const reg_1v2_ic = board.add(SOT_23, {
  translate: pt(0.076, 3.435), rotate: 0,
  id: 'reg_1v2_ic'
})
const reg_1v2_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.570), rotate: 0,
  id: 'reg_1v2_in_cap_cap'
})
const reg_1v2_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 3.570), rotate: 0,
  id: 'reg_1v2_out_cap_cap'
})
const cam_device_conn = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(0.356, 3.035), rotate: 0,
  id: 'cam_device_conn'
})
const cam_dovdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.222), rotate: 0,
  id: 'cam_dovdd_cap_cap'
})
const cam_reset_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 3.222), rotate: 0,
  id: 'cam_reset_cap'
})
const cam_pclk_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 3.222), rotate: 0,
  id: 'cam_pclk_cap'
})
const cam_reset_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 3.222), rotate: 0,
  id: 'cam_reset_pull_res'
})
const switch_package = board.add(SW_Hotswap_Kailh_MX, {
  translate: pt(2.488, 2.026), rotate: 0,
  id: 'switch_package'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.6287401574803155, 3.8866141732283466);
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


