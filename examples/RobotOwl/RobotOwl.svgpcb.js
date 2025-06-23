const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.146, 2.762), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.185, 2.762), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.146, 2.801), rotate: 0,
  id: 'jlc_th_th3'
})
const mcu = board.add(Freenove_ESP32S3_WROOM_Expansion, {
  translate: pt(0.160, 1.960), rotate: 0,
  id: 'mcu'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.727, 2.799), rotate: 0,
  id: 'tp_gnd_tp'
})
const tp_usb_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.976, 2.799), rotate: 0,
  id: 'tp_usb_tp'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.477, 2.799), rotate: 0,
  id: 'tp_3v3_tp'
})
const reg_12v_ic = board.add(SOT_23_5, {
  translate: pt(1.467, 2.363), rotate: 0,
  id: 'reg_12v_ic'
})
const reg_12v_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.444, 2.615), rotate: 0,
  id: 'reg_12v_fb_div_top_res'
})
const reg_12v_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.600, 2.615), rotate: 0,
  id: 'reg_12v_fb_div_bottom_res'
})
const reg_12v_power_path_inductor = board.add(L_1210_3225Metric, {
  translate: pt(1.676, 2.359), rotate: 0,
  id: 'reg_12v_power_path_inductor'
})
const reg_12v_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.453, 2.508), rotate: 0,
  id: 'reg_12v_power_path_in_cap_cap'
})
const reg_12v_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.626, 2.508), rotate: 0,
  id: 'reg_12v_power_path_out_cap_cap'
})
const reg_12v_rect = board.add(D_SOD_323, {
  translate: pt(1.796, 2.507), rotate: 0,
  id: 'reg_12v_rect'
})
const tp_12v_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.226, 2.799), rotate: 0,
  id: 'tp_12v_tp'
})
const mic_ic = board.add(Knowles_LGA_5_3_5x2_65mm, {
  translate: pt(1.448, 2.841), rotate: 0,
  id: 'mic_ic'
})
const mic_pwr_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.444, 2.987), rotate: 0,
  id: 'mic_pwr_cap_cap'
})
const photodiode_r = board.add(R_0603_1608Metric, {
  translate: pt(3.848, 2.542), rotate: 0,
  id: 'photodiode_r'
})
const photodiode_pd = board.add(Osram_BPW34S_SMD, {
  translate: pt(3.947, 2.385), rotate: 0,
  id: 'photodiode_pd'
})
const oled22_device_conn = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(1.715, 1.577), rotate: 0,
  id: 'oled22_device_conn'
})
const oled22_lcd = board.add(Lcd_Er_Oled022_1_Outline, {
  translate: pt(2.580, 0.607), rotate: 0,
  id: 'oled22_lcd'
})
const oled22_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(2.736, 1.413), rotate: 0,
  id: 'oled22_iref_res'
})
const oled22_vcomh_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.202, 1.430), rotate: 0,
  id: 'oled22_vcomh_cap_cap'
})
const oled22_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.892, 1.413), rotate: 0,
  id: 'oled22_vdd_cap1_cap'
})
const oled22_vdd_cap2_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.398, 1.423), rotate: 0,
  id: 'oled22_vdd_cap2_cap'
})
const oled22_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.048, 1.413), rotate: 0,
  id: 'oled22_vcc_cap1_cap'
})
const oled22_vcc_cap2_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.572, 1.423), rotate: 0,
  id: 'oled22_vcc_cap2_cap'
})
const oled_rst_ic = board.add(SOT_23, {
  translate: pt(2.716, 2.829), rotate: 0,
  id: 'oled_rst_ic'
})
const oled_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(3.970, 2.791), rotate: 0,
  id: 'oled_pull_res'
})
const spk_drv_ic = board.add(Maxim_WLP_9_1_595x1_415_Layout3x3_P0_4mm_Ball0_27mm_Pad0_25mm_NSMD, {
  translate: pt(1.699, 2.829), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.860, 2.964), rotate: 0,
  id: 'spk_drv_pwr_cap0_cap'
})
const spk_drv_pwr_cap1_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.695, 2.974), rotate: 0,
  id: 'spk_drv_pwr_cap1_cap'
})
const spk_conn = board.add(PinHeader_1x02_P2_54mm_Horizontal, {
  translate: pt(2.107, 2.933), rotate: 0,
  id: 'spk_conn'
})
const servo_0__conn = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(3.256, 2.566), rotate: 0,
  id: 'servo_0__conn'
})
const servo_1__conn = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(2.652, 2.566), rotate: 0,
  id: 'servo_1__conn'
})
const ws2812bArray_led_0_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.405), rotate: 0,
  id: 'ws2812bArray_led_0_'
})
const ws2812bArray_led_1_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.405), rotate: 0,
  id: 'ws2812bArray_led_1_'
})
const ws2812bArray_led_2_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.405), rotate: 0,
  id: 'ws2812bArray_led_2_'
})
const ws2812bArray_led_3_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.405), rotate: 0,
  id: 'ws2812bArray_led_3_'
})
const ws2812bArray_led_4_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.661), rotate: 0,
  id: 'ws2812bArray_led_4_'
})
const ws2812bArray_led_5_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.661), rotate: 0,
  id: 'ws2812bArray_led_5_'
})
const ws2812bArray_led_6_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.661), rotate: 0,
  id: 'ws2812bArray_led_6_'
})
const ws2812bArray_led_7_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.661), rotate: 0,
  id: 'ws2812bArray_led_7_'
})
const ws2812bArray_led_8_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.144, 2.917), rotate: 0,
  id: 'ws2812bArray_led_8_'
})
const ws2812bArray_led_9_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.470, 2.917), rotate: 0,
  id: 'ws2812bArray_led_9_'
})
const ws2812bArray_led_10_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(0.797, 2.917), rotate: 0,
  id: 'ws2812bArray_led_10_'
})
const ws2812bArray_led_11_ = board.add(LED_WS2812B_PLCC4_5_0x5_0mm_P3_2mm, {
  translate: pt(1.124, 2.917), rotate: 0,
  id: 'ws2812bArray_led_11_'
})
const extNeopixels_conn = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(2.048, 2.566), rotate: 0,
  id: 'extNeopixels_conn'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.303543307086614, 3.142913385826772);
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


