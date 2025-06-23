const board = new PCB();

const batt_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.487, 3.263), rotate: 0,
  id: 'batt_conn'
})
const servos_0__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.864, 2.110), rotate: 0,
  id: 'servos_0__conn'
})
const servos_1__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.604, 2.110), rotate: 0,
  id: 'servos_1__conn'
})
const servos_2__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.084, 2.110), rotate: 0,
  id: 'servos_2__conn'
})
const servos_3__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.331, 2.944), rotate: 0,
  id: 'servos_3__conn'
})
const servos_4__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.824, 2.110), rotate: 0,
  id: 'servos_4__conn'
})
const servos_5__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.071, 2.944), rotate: 0,
  id: 'servos_5__conn'
})
const servos_6__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.305, 2.110), rotate: 0,
  id: 'servos_6__conn'
})
const servos_7__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(4.124, 2.110), rotate: 0,
  id: 'servos_7__conn'
})
const servos_8__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(3.344, 2.110), rotate: 0,
  id: 'servos_8__conn'
})
const servos_9__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.045, 2.110), rotate: 0,
  id: 'servos_9__conn'
})
const servos_10__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.850, 2.944), rotate: 0,
  id: 'servos_10__conn'
})
const servos_11__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.785, 2.110), rotate: 0,
  id: 'servos_11__conn'
})
const imu_ic = board.add(Bosch_LGA_14_3x2_5mm_P0_5mm, {
  translate: pt(0.073, 3.196), rotate: 0,
  id: 'imu_ic'
})
const imu_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 3.327), rotate: 0,
  id: 'imu_vdd_cap_cap'
})
const imu_vddio_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 3.327), rotate: 0,
  id: 'imu_vddio_cap_cap'
})
const servos_cam_0__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(0.591, 2.944), rotate: 0,
  id: 'servos_cam_0__conn'
})
const servos_cam_1__conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.565, 2.110), rotate: 0,
  id: 'servos_cam_1__conn'
})
const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.737, 3.133), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.776, 3.133), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.737, 3.172), rotate: 0,
  id: 'jlc_th_th3'
})
const tp_vbatt_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.052, 3.170), rotate: 0,
  id: 'tp_vbatt_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.801, 3.170), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_89_3, {
  translate: pt(3.500, 2.672), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.446, 2.839), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.602, 2.839), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.552, 3.170), rotate: 0,
  id: 'tp_3v3_tp'
})
const reg_14v_ic = board.add(SOT_23_5, {
  translate: pt(1.951, 2.641), rotate: 0,
  id: 'reg_14v_ic'
})
const reg_14v_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.928, 2.906), rotate: 0,
  id: 'reg_14v_fb_div_top_res'
})
const reg_14v_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.084, 2.906), rotate: 0,
  id: 'reg_14v_fb_div_bottom_res'
})
const reg_14v_cff = board.add(C_0603_1608Metric, {
  translate: pt(2.240, 2.906), rotate: 0,
  id: 'reg_14v_cff'
})
const reg_14v_inductor = board.add(L_1210_3225Metric, {
  translate: pt(2.161, 2.636), rotate: 0,
  id: 'reg_14v_inductor'
})
const reg_14v_rect = board.add(D_SOD_323, {
  translate: pt(2.327, 2.785), rotate: 0,
  id: 'reg_14v_rect'
})
const reg_14v_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.157, 2.786), rotate: 0,
  id: 'reg_14v_in_cap_cap'
})
const reg_14v_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(1.961, 2.793), rotate: 0,
  id: 'reg_14v_out_cap_cap'
})
const tp_14v_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.302, 3.170), rotate: 0,
  id: 'tp_14v_tp'
})
const reg_2v5_ic = board.add(SOT_23, {
  translate: pt(4.244, 2.641), rotate: 0,
  id: 'reg_2v5_ic'
})
const reg_2v5_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(4.227, 2.776), rotate: 0,
  id: 'reg_2v5_in_cap_cap'
})
const reg_2v5_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(4.383, 2.776), rotate: 0,
  id: 'reg_2v5_out_cap_cap'
})
const reg_1v2_ic = board.add(SOT_23, {
  translate: pt(3.854, 2.641), rotate: 0,
  id: 'reg_1v2_ic'
})
const reg_1v2_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.836, 2.776), rotate: 0,
  id: 'reg_1v2_in_cap_cap'
})
const reg_1v2_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.992, 2.776), rotate: 0,
  id: 'reg_1v2_out_cap_cap'
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
const mcu_servo_swd_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(1.444, 1.819), rotate: 0,
  id: 'mcu_servo_swd_conn'
})
const mcu_servo_ic = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(1.064, 1.943), rotate: 0,
  id: 'mcu_servo_ic'
})
const mcu_servo_pwr_cap_0__cap = board.add(C_0805_2012Metric, {
  translate: pt(1.373, 1.976), rotate: 0,
  id: 'mcu_servo_pwr_cap_0__cap'
})
const mcu_servo_pwr_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.538, 1.966), rotate: 0,
  id: 'mcu_servo_pwr_cap_1__cap'
})
const mcu_servo_pwr_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.365, 2.082), rotate: 0,
  id: 'mcu_servo_pwr_cap_2__cap'
})
const mcu_servo_pwr_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.520, 2.082), rotate: 0,
  id: 'mcu_servo_pwr_cap_3__cap'
})
const mcu_servo_vdda_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.920, 2.214), rotate: 0,
  id: 'mcu_servo_vdda_cap_0_cap'
})
const mcu_servo_vdda_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.076, 2.214), rotate: 0,
  id: 'mcu_servo_vdda_cap_1_cap'
})
const mcu_test_swd_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.138, 2.183), rotate: 0,
  id: 'mcu_test_swd_conn'
})
const mcu_test_ic = board.add(QFN_56_1EP_7x7mm_P0_4mm_EP3_2x3_2mm, {
  translate: pt(0.163, 1.903), rotate: 0,
  id: 'mcu_test_ic'
})
const mcu_test_iovdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.373, 2.133), rotate: 0,
  id: 'mcu_test_iovdd_cap_0__cap'
})
const mcu_test_iovdd_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.529, 2.133), rotate: 0,
  id: 'mcu_test_iovdd_cap_1__cap'
})
const mcu_test_iovdd_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.685, 2.133), rotate: 0,
  id: 'mcu_test_iovdd_cap_2__cap'
})
const mcu_test_iovdd_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.373, 2.230), rotate: 0,
  id: 'mcu_test_iovdd_cap_3__cap'
})
const mcu_test_iovdd_cap_4__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.529, 2.230), rotate: 0,
  id: 'mcu_test_iovdd_cap_4__cap'
})
const mcu_test_iovdd_cap_5__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.685, 2.230), rotate: 0,
  id: 'mcu_test_iovdd_cap_5__cap'
})
const mcu_test_avdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.330), rotate: 0,
  id: 'mcu_test_avdd_cap_cap'
})
const mcu_test_vreg_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.330), rotate: 0,
  id: 'mcu_test_vreg_in_cap_cap'
})
const mcu_test_mem_ic = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(0.548, 1.853), rotate: 0,
  id: 'mcu_test_mem_ic'
})
const mcu_test_mem_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.330), rotate: 0,
  id: 'mcu_test_mem_vcc_cap_cap'
})
const mcu_test_dvdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.330), rotate: 0,
  id: 'mcu_test_dvdd_cap_0__cap'
})
const mcu_test_dvdd_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.330), rotate: 0,
  id: 'mcu_test_dvdd_cap_1__cap'
})
const mcu_test_vreg_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.427), rotate: 0,
  id: 'mcu_test_vreg_out_cap_cap'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.559, 3.162), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.559, 3.259), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.846, 3.170), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.846, 3.285), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const led_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.089, 3.162), rotate: 0,
  id: 'led_package'
})
const led_res = board.add(R_0603_1608Metric, {
  translate: pt(1.089, 3.259), rotate: 0,
  id: 'led_res'
})
const servo_led_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.324, 3.162), rotate: 0,
  id: 'servo_led_package'
})
const servo_led_res = board.add(R_0603_1608Metric, {
  translate: pt(1.324, 3.259), rotate: 0,
  id: 'servo_led_res'
})
const test_led_led_0__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.055, 2.603), rotate: 0,
  id: 'test_led_led_0__package'
})
const test_led_led_0__res = board.add(R_0603_1608Metric, {
  translate: pt(3.055, 2.797), rotate: 0,
  id: 'test_led_led_0__res'
})
const test_led_led_1__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.211, 2.603), rotate: 0,
  id: 'test_led_led_1__package'
})
const test_led_led_1__res = board.add(R_0603_1608Metric, {
  translate: pt(3.211, 2.797), rotate: 0,
  id: 'test_led_led_1__res'
})
const test_led_led_2__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.055, 2.700), rotate: 0,
  id: 'test_led_led_2__package'
})
const test_led_led_2__res = board.add(R_0603_1608Metric, {
  translate: pt(3.055, 2.894), rotate: 0,
  id: 'test_led_led_2__res'
})
const test_led_led_3__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.211, 2.700), rotate: 0,
  id: 'test_led_led_3__package'
})
const test_led_led_3__res = board.add(R_0603_1608Metric, {
  translate: pt(3.211, 2.894), rotate: 0,
  id: 'test_led_led_3__res'
})
const oled_device_conn = board.add(Hirose_FH35C_31S_0_3SHW_1x31_1MP_P0_30mm_Horizontal, {
  translate: pt(2.631, 0.865), rotate: 0,
  id: 'oled_device_conn'
})
const oled_lcd = board.add(Lcd_Er_Oled0_96_1c_Outline, {
  translate: pt(3.254, 0.293), rotate: 0,
  id: 'oled_lcd'
})
const oled_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(3.571, 0.653), rotate: 0,
  id: 'oled_iref_res'
})
const oled_vcomh_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.075, 0.663), rotate: 0,
  id: 'oled_vcomh_cap_cap'
})
const oled_vp_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.727, 0.653), rotate: 0,
  id: 'oled_vp_cap_cap'
})
const oled_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.846, 0.783), rotate: 0,
  id: 'oled_vdd_cap_cap'
})
const oled_vcc_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.878, 0.670), rotate: 0,
  id: 'oled_vcc_cap_cap'
})
const oled_vsl_res = board.add(R_0603_1608Metric, {
  translate: pt(3.002, 0.783), rotate: 0,
  id: 'oled_vsl_res'
})
const oled_vsl_d1 = board.add(D_SOD_323, {
  translate: pt(3.244, 0.662), rotate: 0,
  id: 'oled_vsl_d1'
})
const oled_vsl_d2 = board.add(D_SOD_323, {
  translate: pt(3.410, 0.662), rotate: 0,
  id: 'oled_vsl_d2'
})
const cam_device_conn = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(1.396, 2.767), rotate: 0,
  id: 'cam_device_conn'
})
const cam_dovdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.098, 2.953), rotate: 0,
  id: 'cam_dovdd_cap_cap'
})
const cam_reset_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.254, 2.953), rotate: 0,
  id: 'cam_reset_cap'
})
const cam_pclk_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.409, 2.953), rotate: 0,
  id: 'cam_pclk_cap'
})
const cam_reset_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(1.565, 2.953), rotate: 0,
  id: 'cam_reset_pull_res'
})
const rgbs_led_0_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.609), rotate: 0,
  id: 'rgbs_led_0_'
})
const rgbs_led_1_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.609), rotate: 0,
  id: 'rgbs_led_1_'
})
const rgbs_led_2_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.688), rotate: 0,
  id: 'rgbs_led_2_'
})
const rgbs_led_3_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.688), rotate: 0,
  id: 'rgbs_led_3_'
})
const rgbs_led_4_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.767), rotate: 0,
  id: 'rgbs_led_4_'
})
const rgbs_led_5_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.767), rotate: 0,
  id: 'rgbs_led_5_'
})
const rgbs_led_6_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.846), rotate: 0,
  id: 'rgbs_led_6_'
})
const rgbs_led_7_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.846), rotate: 0,
  id: 'rgbs_led_7_'
})
const rgbs_led_8_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.591, 2.924), rotate: 0,
  id: 'rgbs_led_8_'
})
const rgbs_led_9_ = board.add(LED_SK6812_SIDE_A, {
  translate: pt(2.796, 2.924), rotate: 0,
  id: 'rgbs_led_9_'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.559055118110236, 3.474015748031496);
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


