const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.002, 2.210), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.041, 2.210), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.002, 2.249), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.905), rotate: 0,
  id: 'usb_conn'
})
const batt_conn = board.add(JST_PH_S2B_PH_K_1x02_P2_00mm_Horizontal, {
  translate: pt(0.633, 2.006), rotate: 0,
  id: 'batt_conn'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.625, 2.247), rotate: 0,
  id: 'tp_pwr_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.375, 2.247), rotate: 0,
  id: 'tp_gnd_tp'
})
const vbat_prot_fet = board.add(SOT_23, {
  translate: pt(0.614, 2.277), rotate: 0,
  id: 'vbat_prot_fet'
})
const reg_3v3_ic = board.add(SOT_23_6, {
  translate: pt(3.419, 0.952), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(3.570, 1.131), rotate: 0,
  id: 'reg_3v3_fb_div_top_res'
})
const reg_3v3_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(3.176, 1.261), rotate: 0,
  id: 'reg_3v3_fb_div_bottom_res'
})
const reg_3v3_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.332, 1.261), rotate: 0,
  id: 'reg_3v3_hf_in_cap_cap'
})
const reg_3v3_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.488, 1.261), rotate: 0,
  id: 'reg_3v3_boot_cap'
})
const reg_3v3_power_path_inductor = board.add(L_Sunlord_SWPA4030S, {
  translate: pt(3.209, 0.974), rotate: 0,
  id: 'reg_3v3_power_path_inductor'
})
const reg_3v3_power_path_in_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(3.209, 1.147), rotate: 0,
  id: 'reg_3v3_power_path_in_cap_cap'
})
const reg_3v3_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.406, 1.141), rotate: 0,
  id: 'reg_3v3_power_path_out_cap_cap'
})
const reg_3v3_en_res = board.add(R_0603_1608Metric, {
  translate: pt(3.176, 1.357), rotate: 0,
  id: 'reg_3v3_en_res'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.376, 2.247), rotate: 0,
  id: 'tp_3v3_tp'
})
const vbat_sense_gate_pre = board.add(SOT_23, {
  translate: pt(1.487, 1.807), rotate: 0,
  id: 'vbat_sense_gate_pre'
})
const vbat_sense_gate_pull = board.add(R_0603_1608Metric, {
  translate: pt(1.660, 1.942), rotate: 0,
  id: 'vbat_sense_gate_pull'
})
const vbat_sense_gate_drv = board.add(SOT_23, {
  translate: pt(1.487, 1.980), rotate: 0,
  id: 'vbat_sense_gate_drv'
})
const mcu_ic = board.add(ESP32_S3_WROOM_1, {
  translate: pt(0.945, 0.530), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.683), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.667), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_FP_2x03_P1_27mm_Vertical, {
  translate: pt(2.096, 0.167), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_boot_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.096, 0.486), rotate: 0,
  id: 'mcu_boot_package'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.667), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.796), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(2.887, 2.277), rotate: 0,
  id: 'usb_esd'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(2.848, 1.769), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(2.848, 1.866), rotate: 0,
  id: 'ledr_res'
})
const ledg_package = board.add(LED_0603_1608Metric, {
  translate: pt(3.318, 1.769), rotate: 0,
  id: 'ledg_package'
})
const ledg_res = board.add(R_0603_1608Metric, {
  translate: pt(3.318, 1.866), rotate: 0,
  id: 'ledg_res'
})
const ledb_package = board.add(LED_0603_1608Metric, {
  translate: pt(3.083, 1.769), rotate: 0,
  id: 'ledb_package'
})
const ledb_res = board.add(R_0603_1608Metric, {
  translate: pt(3.083, 1.866), rotate: 0,
  id: 'ledb_res'
})
const sw_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.504, 1.852), rotate: 0,
  id: 'sw_package'
})
const vbat_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(3.553, 1.769), rotate: 0,
  id: 'vbat_sense_div_top_res'
})
const vbat_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(3.553, 1.866), rotate: 0,
  id: 'vbat_sense_div_bottom_res'
})
const touch_duck = board.add(Symbol_DucklingSolid, {
  translate: pt(3.159, 2.210), rotate: 0,
  id: 'touch_duck'
})
const touch_lemur = board.add(Symbol_LemurSolid, {
  translate: pt(3.198, 2.210), rotate: 0,
  id: 'touch_lemur'
})
const epd_gate_drv = board.add(SOT_23, {
  translate: pt(0.076, 2.277), rotate: 0,
  id: 'epd_gate_drv'
})
const mem_gate_drv = board.add(SOT_23, {
  translate: pt(0.345, 2.277), rotate: 0,
  id: 'mem_gate_drv'
})
const epd_device_conn_conn = board.add(TE_2_1734839_4_1x24_1MP_P0_5mm_Horizontal, {
  translate: pt(2.903, 0.167), rotate: 0,
  id: 'epd_device_conn_conn'
})
const epd_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.930, 0.624), rotate: 0,
  id: 'epd_vdd_cap_cap'
})
const epd_vdd1v8_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.086, 0.624), rotate: 0,
  id: 'epd_vdd1v8_cap_cap'
})
const epd_vgl_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.242, 0.624), rotate: 0,
  id: 'epd_vgl_cap_cap'
})
const epd_vgh_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.850, 0.346), rotate: 0,
  id: 'epd_vgh_cap_cap'
})
const epd_vsh_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(3.070, 0.346), rotate: 0,
  id: 'epd_vsh_cap_cap'
})
const epd_vsl_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(3.291, 0.346), rotate: 0,
  id: 'epd_vsl_cap_cap'
})
const epd_vcom_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.398, 0.624), rotate: 0,
  id: 'epd_vcom_cap_cap'
})
const epd_boost_fet = board.add(SOT_23, {
  translate: pt(3.381, 0.067), rotate: 0,
  id: 'epd_boost_fet'
})
const epd_boost_inductor = board.add(L_1210_3225Metric, {
  translate: pt(2.630, 0.363), rotate: 0,
  id: 'epd_boost_inductor'
})
const epd_boost_sense = board.add(R_0603_1608Metric, {
  translate: pt(2.598, 0.738), rotate: 0,
  id: 'epd_boost_sense'
})
const epd_boost_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.269, 0.504), rotate: 0,
  id: 'epd_boost_in_cap_cap'
})
const epd_boost_diode = board.add(D_SOD_323, {
  translate: pt(3.438, 0.502), rotate: 0,
  id: 'epd_boost_diode'
})
const epd_boost_boot_neg_diode = board.add(D_SOD_323, {
  translate: pt(2.604, 0.632), rotate: 0,
  id: 'epd_boost_boot_neg_diode'
})
const epd_boost_boot_gnd_diode = board.add(D_SOD_323, {
  translate: pt(2.769, 0.632), rotate: 0,
  id: 'epd_boost_boot_gnd_diode'
})
const epd_boost_boot_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.631, 0.510), rotate: 0,
  id: 'epd_boost_boot_cap'
})
const epd_boost_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.851, 0.510), rotate: 0,
  id: 'epd_boost_out_cap_cap'
})
const epd_boost_neg_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(3.072, 0.510), rotate: 0,
  id: 'epd_boost_neg_out_cap_cap'
})
const epd_gate_pdr = board.add(R_0603_1608Metric, {
  translate: pt(2.754, 0.738), rotate: 0,
  id: 'epd_gate_pdr'
})
const tp_epd_tp_sck_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.902, 1.778), rotate: 0,
  id: 'tp_epd_tp_sck_tp'
})
const tp_epd_tp_mosi_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.902, 1.892), rotate: 0,
  id: 'tp_epd_tp_mosi_tp'
})
const tp_epd_tp_miso_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.902, 2.006), rotate: 0,
  id: 'tp_epd_tp_miso_tp'
})
const tp_erst_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.124, 2.247), rotate: 0,
  id: 'tp_erst_tp'
})
const tp_dc_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.126, 2.247), rotate: 0,
  id: 'tp_dc_tp'
})
const tp_epd_cs_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.874, 2.247), rotate: 0,
  id: 'tp_epd_cs_tp'
})
const tp_busy_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.627, 2.247), rotate: 0,
  id: 'tp_busy_tp'
})
const sd = board.add(microSD_HC_Molex_104031_0811, {
  translate: pt(2.809, 1.143), rotate: 0,
  id: 'sd'
})
const flash_ic = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(1.110, 1.853), rotate: 0,
  id: 'flash_ic'
})
const flash_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.985, 2.033), rotate: 0,
  id: 'flash_vcc_cap_cap'
})
const tp_sd_tp_sck_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.153, 1.778), rotate: 0,
  id: 'tp_sd_tp_sck_tp'
})
const tp_sd_tp_mosi_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.153, 1.892), rotate: 0,
  id: 'tp_sd_tp_mosi_tp'
})
const tp_sd_tp_miso_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.153, 2.006), rotate: 0,
  id: 'tp_sd_tp_miso_tp'
})
const tp_sd_cs_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.876, 2.247), rotate: 0,
  id: 'tp_sd_cs_tp'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.746456692913387, 2.4618110236220474);
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


