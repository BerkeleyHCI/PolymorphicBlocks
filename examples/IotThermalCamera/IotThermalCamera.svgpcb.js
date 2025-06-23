const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.421, 2.307), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.460, 2.307), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.421, 2.346), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.905), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.811, 2.344), rotate: 0,
  id: 'tp_gnd_tp'
})
const choke_fb = board.add(L_0603_1608Metric, {
  translate: pt(1.054, 2.335), rotate: 0,
  id: 'choke_fb'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.066, 2.344), rotate: 0,
  id: 'tp_pwr_tp'
})
const reg_3v3_ic = board.add(SOT_23_6, {
  translate: pt(2.841, 0.746), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.945, 0.926), rotate: 0,
  id: 'reg_3v3_fb_div_top_res'
})
const reg_3v3_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.598, 1.042), rotate: 0,
  id: 'reg_3v3_fb_div_bottom_res'
})
const reg_3v3_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.754, 1.042), rotate: 0,
  id: 'reg_3v3_hf_in_cap_cap'
})
const reg_3v3_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.910, 1.042), rotate: 0,
  id: 'reg_3v3_boot_cap'
})
const reg_3v3_power_path_inductor = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(2.631, 0.769), rotate: 0,
  id: 'reg_3v3_power_path_inductor'
})
const reg_3v3_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.607, 0.935), rotate: 0,
  id: 'reg_3v3_power_path_in_cap_cap'
})
const reg_3v3_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.780, 0.935), rotate: 0,
  id: 'reg_3v3_power_path_out_cap_cap'
})
const reg_3v3_en_res = board.add(R_0603_1608Metric, {
  translate: pt(2.598, 1.139), rotate: 0,
  id: 'reg_3v3_en_res'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.561, 2.344), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(0.314, 2.344), rotate: 0,
  id: 'prot_3v3_diode'
})
const reg_3v0_ic = board.add(SOT_23_5, {
  translate: pt(2.243, 1.807), rotate: 0,
  id: 'reg_3v0_ic'
})
const reg_3v0_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.220, 1.942), rotate: 0,
  id: 'reg_3v0_in_cap_cap'
})
const reg_3v0_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.376, 1.942), rotate: 0,
  id: 'reg_3v0_out_cap_cap'
})
const reg_2v8_ic = board.add(SOT_23_5, {
  translate: pt(1.852, 1.807), rotate: 0,
  id: 'reg_2v8_ic'
})
const reg_2v8_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.830, 1.942), rotate: 0,
  id: 'reg_2v8_in_cap_cap'
})
const reg_2v8_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.986, 1.942), rotate: 0,
  id: 'reg_2v8_out_cap_cap'
})
const reg_1v2_ic = board.add(SOT_23_5, {
  translate: pt(1.462, 1.807), rotate: 0,
  id: 'reg_1v2_ic'
})
const reg_1v2_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.439, 1.942), rotate: 0,
  id: 'reg_1v2_in_cap_cap'
})
const reg_1v2_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.595, 1.942), rotate: 0,
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
const usb_esd = board.add(SOT_23, {
  translate: pt(1.306, 2.374), rotate: 0,
  id: 'usb_esd'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(3.096, 1.769), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(3.096, 1.866), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.619, 1.778), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.619, 1.892), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const touch_duck = board.add(Symbol_DucklingSolid, {
  translate: pt(1.578, 2.307), rotate: 0,
  id: 'touch_duck'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(2.862, 1.769), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(2.861, 1.866), rotate: 0,
  id: 'ledr_res'
})
const cam_device_conn_conn = board.add(TE_2_1734839_4_1x24_1MP_P0_5mm_Horizontal, {
  translate: pt(0.900, 1.907), rotate: 0,
  id: 'cam_device_conn_conn'
})
const cam_dovdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.595, 2.070), rotate: 0,
  id: 'cam_dovdd_cap_cap'
})
const cam_reset_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.751, 2.070), rotate: 0,
  id: 'cam_reset_cap'
})
const cam_pclk_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.907, 2.070), rotate: 0,
  id: 'cam_pclk_cap'
})
const flir_ic = board.add(Molex_1050281001, {
  translate: pt(2.772, 0.232), rotate: 0,
  id: 'flir_ic'
})
const flir_vddc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.102, 0.202), rotate: 0,
  id: 'flir_vddc_cap_cap'
})
const flir_vddio_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.102, 0.299), rotate: 0,
  id: 'flir_vddio_cap_cap'
})
const flir_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.102, 0.396), rotate: 0,
  id: 'flir_vdd_cap_cap'
})
const flir_mclk_device = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(3.127, 0.067), rotate: 0,
  id: 'flir_mclk_device'
})
const flir_mclk_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.598, 0.533), rotate: 0,
  id: 'flir_mclk_cap_cap'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.327559055118111, 2.4996062992125987);
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


