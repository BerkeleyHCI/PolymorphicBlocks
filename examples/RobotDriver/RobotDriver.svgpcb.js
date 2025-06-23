const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.673, 3.040), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.713, 3.040), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.673, 3.079), rotate: 0,
  id: 'jlc_th_th3'
})
const batt_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.394, 2.719), rotate: 0,
  id: 'batt_conn'
})
const isense_sense_res_res = board.add(R_2512_6332Metric, {
  translate: pt(2.693, 1.818), rotate: 0,
  id: 'isense_sense_res_res'
})
const isense_amp_amp_ic = board.add(SOT_23_5, {
  translate: pt(2.963, 1.809), rotate: 0,
  id: 'isense_amp_amp_ic'
})
const isense_amp_amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.600, 1.961), rotate: 0,
  id: 'isense_amp_amp_vdd_cap_cap'
})
const isense_amp_r1 = board.add(R_0603_1608Metric, {
  translate: pt(2.756, 1.961), rotate: 0,
  id: 'isense_amp_r1'
})
const isense_amp_r2 = board.add(R_0603_1608Metric, {
  translate: pt(2.912, 1.961), rotate: 0,
  id: 'isense_amp_r2'
})
const isense_amp_rf = board.add(R_0603_1608Metric, {
  translate: pt(2.600, 2.058), rotate: 0,
  id: 'isense_amp_rf'
})
const isense_amp_rg = board.add(R_0603_1608Metric, {
  translate: pt(2.756, 2.058), rotate: 0,
  id: 'isense_amp_rg'
})
const tp_vbatt_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.827, 3.077), rotate: 0,
  id: 'tp_vbatt_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.332, 3.077), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_23_5, {
  translate: pt(2.170, 1.809), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.321, 1.944), rotate: 0,
  id: 'reg_3v3_fb_div_top_res'
})
const reg_3v3_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.148, 2.061), rotate: 0,
  id: 'reg_3v3_fb_div_bottom_res'
})
const reg_3v3_power_path_inductor = board.add(L_0603_1608Metric, {
  translate: pt(2.304, 2.061), rotate: 0,
  id: 'reg_3v3_power_path_inductor'
})
const reg_3v3_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.357, 1.781), rotate: 0,
  id: 'reg_3v3_power_path_in_cap_cap'
})
const reg_3v3_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.156, 1.954), rotate: 0,
  id: 'reg_3v3_power_path_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.328, 3.077), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(1.580, 3.077), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_ic = board.add(ESP32_WROOM_32, {
  translate: pt(0.945, 0.414), rotate: 0,
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
const tof_elt_0_ = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(0.803, 2.311), rotate: 0,
  id: 'tof_elt_0_'
})
const tof_elt_1_ = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(0.982, 2.311), rotate: 0,
  id: 'tof_elt_1_'
})
const tof_elt_2_ = board.add(PinSocket_1x06_P2_54mm_Vertical, {
  translate: pt(1.161, 2.311), rotate: 0,
  id: 'tof_elt_2_'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.089, 3.069), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.089, 3.165), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.456, 3.077), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.456, 3.191), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const lcd_device_conn = board.add(Hirose_FH12_15S_0_5SH_1x15_1MP_P0_50mm_Horizontal, {
  translate: pt(2.808, 0.685), rotate: 0,
  id: 'lcd_device_conn'
})
const lcd_lcd = board.add(Lcd_Er_Oled0_91_3_Outline, {
  translate: pt(3.064, 0.260), rotate: 0,
  id: 'lcd_lcd'
})
const lcd_c1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.693, 0.521), rotate: 0,
  id: 'lcd_c1_cap'
})
const lcd_c2_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.173, 0.637), rotate: 0,
  id: 'lcd_c2_cap'
})
const lcd_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(3.329, 0.637), rotate: 0,
  id: 'lcd_iref_res'
})
const lcd_vcomh_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.182, 0.531), rotate: 0,
  id: 'lcd_vcomh_cap_cap'
})
const lcd_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.485, 0.637), rotate: 0,
  id: 'lcd_vdd_cap1_cap'
})
const lcd_vdd_cap2_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.355, 0.531), rotate: 0,
  id: 'lcd_vdd_cap2_cap'
})
const lcd_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.641, 0.637), rotate: 0,
  id: 'lcd_vcc_cap1_cap'
})
const lcd_vcc_cap2_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.528, 0.531), rotate: 0,
  id: 'lcd_vcc_cap2_cap'
})
const imu_ic = board.add(Bosch_LGA_14_3x2_5mm_P0_5mm, {
  translate: pt(1.200, 2.652), rotate: 0,
  id: 'imu_ic'
})
const imu_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.186, 2.783), rotate: 0,
  id: 'imu_vdd_cap_cap'
})
const imu_vddio_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.342, 2.783), rotate: 0,
  id: 'imu_vddio_cap_cap'
})
const expander_ic = board.add(SOIC_16W_7_5x10_3mm_P1_27mm, {
  translate: pt(1.582, 1.955), rotate: 0,
  id: 'expander_ic'
})
const expander_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.913, 1.771), rotate: 0,
  id: 'expander_vdd_cap_cap'
})
const leds_led_0__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.699, 3.069), rotate: 0,
  id: 'leds_led_0__package'
})
const leds_led_1__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.855, 3.069), rotate: 0,
  id: 'leds_led_1__package'
})
const leds_led_2__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.699, 3.166), rotate: 0,
  id: 'leds_led_2__package'
})
const leds_led_3__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.855, 3.166), rotate: 0,
  id: 'leds_led_3__package'
})
const spk_tp_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.077, 3.077), rotate: 0,
  id: 'spk_tp_tp'
})
const spk_drv_ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.704, 2.657), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.639, 2.794), rotate: 0,
  id: 'spk_drv_pwr_cap_cap'
})
const spk_drv_bulk_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.933, 2.627), rotate: 0,
  id: 'spk_drv_bulk_cap_cap'
})
const spk_drv_inp_res = board.add(R_0603_1608Metric, {
  translate: pt(0.795, 2.794), rotate: 0,
  id: 'spk_drv_inp_res'
})
const spk_drv_inp_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.951, 2.794), rotate: 0,
  id: 'spk_drv_inp_cap'
})
const spk_drv_inn_res = board.add(R_0603_1608Metric, {
  translate: pt(0.639, 2.891), rotate: 0,
  id: 'spk_drv_inn_res'
})
const spk_drv_inn_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.795, 2.891), rotate: 0,
  id: 'spk_drv_inn_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(0.096, 3.170), rotate: 0,
  id: 'spk_conn'
})
const ws2812bArray_led_0_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 1.850), rotate: 0,
  id: 'ws2812bArray_led_0_'
})
const ws2812bArray_led_1_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 1.850), rotate: 0,
  id: 'ws2812bArray_led_1_'
})
const ws2812bArray_led_2_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.106), rotate: 0,
  id: 'ws2812bArray_led_2_'
})
const ws2812bArray_led_3_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.106), rotate: 0,
  id: 'ws2812bArray_led_3_'
})
const ws2812bArray_led_4_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.362), rotate: 0,
  id: 'ws2812bArray_led_4_'
})
const led_pixel_conn = board.add(JST_PH_B3B_PH_K_1x03_P2_00mm_Vertical, {
  translate: pt(3.174, 2.719), rotate: 0,
  id: 'led_pixel_conn'
})
const motor_driver1_ic = board.add(TSSOP_16_1EP_4_4x5mm_P0_65mm_EP3x3mm_ThermalVias, {
  translate: pt(0.154, 2.697), rotate: 0,
  id: 'motor_driver1_ic'
})
const motor_driver1_vm_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.883), rotate: 0,
  id: 'motor_driver1_vm_cap_cap'
})
const motor_driver1_vint_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.240, 2.883), rotate: 0,
  id: 'motor_driver1_vint_cap_cap'
})
const motor_driver1_vcp_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.405, 2.873), rotate: 0,
  id: 'motor_driver1_vcp_cap'
})
const m1_a_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(3.642, 2.719), rotate: 0,
  id: 'm1_a_conn'
})
const m1_b_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.784, 2.719), rotate: 0,
  id: 'm1_b_conn'
})
const motor_driver2_ic = board.add(TSSOP_16_1EP_4_4x5mm_P0_65mm_EP3x3mm_ThermalVias, {
  translate: pt(3.575, 1.850), rotate: 0,
  id: 'motor_driver2_ic'
})
const motor_driver2_vm_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.489, 2.037), rotate: 0,
  id: 'motor_driver2_vm_cap_cap'
})
const motor_driver2_vint_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.662, 2.037), rotate: 0,
  id: 'motor_driver2_vint_cap_cap'
})
const motor_driver2_vcp_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.826, 2.027), rotate: 0,
  id: 'motor_driver2_vcp_cap'
})
const m2_a_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.004, 2.719), rotate: 0,
  id: 'm2_a_conn'
})
const m2_b_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.615, 2.719), rotate: 0,
  id: 'm2_b_conn'
})
const servo_conn = board.add(PinHeader_1x03_P2_54mm_Vertical, {
  translate: pt(3.233, 2.012), rotate: 0,
  id: 'servo_conn'
})
const led_res = board.add(R_Array_Concave_4x0603, {
  translate: pt(2.573, 3.113), rotate: 0,
  id: 'led_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.002755905511811, 3.374409448818898);
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


