const board = new PCB();

const pwr_conn = board.add(Molex_DuraClik_vert_3pin, {
  translate: pt(3.367, 2.356), rotate: 0,
  id: 'pwr_conn'
})
const usb_conn_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.843, 1.867), rotate: 0,
  id: 'usb_conn_conn'
})
const usb_conn_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(1.692, 2.122), rotate: 0,
  id: 'usb_conn_cc_pull_cc1_res'
})
const usb_conn_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(1.848, 2.122), rotate: 0,
  id: 'usb_conn_cc_pull_cc2_res'
})
const bat = board.add(BatteryHolder_Keystone_106_1x20mm, {
  translate: pt(2.492, 0.369), rotate: 0,
  id: 'bat'
})
const pwr_5v_ic = board.add(SOT_23_6, {
  translate: pt(2.511, 1.770), rotate: 0,
  id: 'pwr_5v_ic'
})
const pwr_5v_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.576, 1.987), rotate: 0,
  id: 'pwr_5v_fb_div_top_res'
})
const pwr_5v_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.229, 2.104), rotate: 0,
  id: 'pwr_5v_fb_div_bottom_res'
})
const pwr_5v_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.385, 2.104), rotate: 0,
  id: 'pwr_5v_hf_in_cap_cap'
})
const pwr_5v_vbst_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.541, 2.104), rotate: 0,
  id: 'pwr_5v_vbst_cap'
})
const pwr_5v_power_path_inductor = board.add(L_Taiyo_Yuden_NR_50xx, {
  translate: pt(2.281, 1.811), rotate: 0,
  id: 'pwr_5v_power_path_inductor'
})
const pwr_5v_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.238, 1.997), rotate: 0,
  id: 'pwr_5v_power_path_in_cap_cap'
})
const pwr_5v_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.411, 1.997), rotate: 0,
  id: 'pwr_5v_power_path_out_cap_cap'
})
const buffer_sense = board.add(R_0603_1608Metric, {
  translate: pt(1.881, 1.364), rotate: 0,
  id: 'buffer_sense'
})
const buffer_fet = board.add(SOT_223_3_TabPin2, {
  translate: pt(1.996, 0.981), rotate: 0,
  id: 'buffer_fet'
})
const buffer_diode = board.add(D_SOD_323, {
  translate: pt(2.087, 1.200), rotate: 0,
  id: 'buffer_diode'
})
const buffer_set_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.037, 1.364), rotate: 0,
  id: 'buffer_set_div_top_res'
})
const buffer_set_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.263, 1.465), rotate: 0,
  id: 'buffer_set_div_bottom_res'
})
const buffer_amp_ic = board.add(SOT_23_6, {
  translate: pt(1.904, 1.229), rotate: 0,
  id: 'buffer_amp_ic'
})
const buffer_amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.419, 1.465), rotate: 0,
  id: 'buffer_amp_vdd_cap_cap'
})
const buffer_cap = board.add(CP_Radial_D14_0mm_P5_00mm, {
  translate: pt(1.406, 1.118), rotate: 0,
  id: 'buffer_cap'
})
const pwr_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(2.925, 1.844), rotate: 0,
  id: 'pwr_3v3_ic'
})
const pwr_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.983, 2.054), rotate: 0,
  id: 'pwr_3v3_in_cap_cap'
})
const pwr_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.819, 2.064), rotate: 0,
  id: 'pwr_3v3_out_cap_cap'
})
const mcu_swd_conn = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(1.941, 0.146), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(LQFP_64_10x10mm_P0_5mm, {
  translate: pt(1.469, 0.264), rotate: 0,
  id: 'mcu_ic'
})
const mcu_swd_pull_swdio_res = board.add(R_0603_1608Metric, {
  translate: pt(1.263, 0.596), rotate: 0,
  id: 'mcu_swd_pull_swdio_res'
})
const mcu_swd_pull_swclk_res = board.add(R_0603_1608Metric, {
  translate: pt(1.419, 0.596), rotate: 0,
  id: 'mcu_swd_pull_swclk_res'
})
const mcu_pwr_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.575, 0.596), rotate: 0,
  id: 'mcu_pwr_cap_0__cap'
})
const mcu_pwr_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.731, 0.596), rotate: 0,
  id: 'mcu_pwr_cap_1__cap'
})
const mcu_pwr_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.887, 0.596), rotate: 0,
  id: 'mcu_pwr_cap_2__cap'
})
const mcu_pwr_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.043, 0.596), rotate: 0,
  id: 'mcu_pwr_cap_3__cap'
})
const mcu_pwr_cap_4__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.198, 0.596), rotate: 0,
  id: 'mcu_pwr_cap_4__cap'
})
const mcu_pwr_cap_5__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.263, 0.693), rotate: 0,
  id: 'mcu_pwr_cap_5__cap'
})
const mcu_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.419, 0.693), rotate: 0,
  id: 'mcu_vbat_cap_cap'
})
const mcu_pwra_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.575, 0.693), rotate: 0,
  id: 'mcu_pwra_cap_0__cap'
})
const mcu_pwra_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(2.043, 0.369), rotate: 0,
  id: 'mcu_pwra_cap_1__cap'
})
const mcu_vref_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.731, 0.693), rotate: 0,
  id: 'mcu_vref_cap_0__cap'
})
const mcu_vref_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.887, 0.693), rotate: 0,
  id: 'mcu_vref_cap_1__cap'
})
const mcu_vref_cap_2__cap = board.add(C_0805_2012Metric, {
  translate: pt(2.217, 0.369), rotate: 0,
  id: 'mcu_vref_cap_2__cap'
})
const mcu_crystal_package = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(1.854, 0.398), rotate: 0,
  id: 'mcu_crystal_package'
})
const mcu_crystal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(2.043, 0.693), rotate: 0,
  id: 'mcu_crystal_cap_a'
})
const mcu_crystal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(2.198, 0.693), rotate: 0,
  id: 'mcu_crystal_cap_b'
})
const can_conn = board.add(Molex_DuraClik_vert_5pin, {
  translate: pt(0.000, 2.238), rotate: 0,
  id: 'can_conn'
})
const can_can_fuse_fuse = board.add(R_0603_1608Metric, {
  translate: pt(0.231, 2.150), rotate: 0,
  id: 'can_can_fuse_fuse'
})
const can_reg_ic = board.add(SOT_23_5, {
  translate: pt(0.589, 1.770), rotate: 0,
  id: 'can_reg_ic'
})
const can_reg_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.387, 2.150), rotate: 0,
  id: 'can_reg_in_cap_cap'
})
const can_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.160), rotate: 0,
  id: 'can_reg_out_cap_cap'
})
const can_esd = board.add(SOT_23, {
  translate: pt(0.583, 1.943), rotate: 0,
  id: 'can_esd'
})
const can_transceiver_ic = board.add(SOP_8_6_62x9_15mm_P2_54mm, {
  translate: pt(0.234, 1.893), rotate: 0,
  id: 'can_transceiver_ic'
})
const can_transceiver_logic_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.543, 2.150), rotate: 0,
  id: 'can_transceiver_logic_cap_cap'
})
const can_transceiver_can_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.699, 2.150), rotate: 0,
  id: 'can_transceiver_can_cap_cap'
})
const sd = board.add(SD_Kyocera_145638009511859+, {
  translate: pt(0.565, 1.122), rotate: 0,
  id: 'sd'
})
const cd_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(2.956, 2.385), rotate: 0,
  id: 'cd_pull_res'
})
const xbee_ic = board.add(XBEE, {
  translate: pt(1.876, 2.453), rotate: 0,
  id: 'xbee_ic'
})
const xbee_vdd_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.778, 2.385), rotate: 0,
  id: 'xbee_vdd_cap_0_cap'
})
const xbee_vdd_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.778, 2.482), rotate: 0,
  id: 'xbee_vdd_cap_1_cap'
})
const xbee_assoc_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.840, 2.385), rotate: 0,
  id: 'xbee_assoc_package'
})
const xbee_assoc_res = board.add(R_0603_1608Metric, {
  translate: pt(0.839, 2.482), rotate: 0,
  id: 'xbee_assoc_res'
})
const rtc_ic = board.add(SOIC_16W_7_5x10_3mm_P1_27mm, {
  translate: pt(1.109, 1.915), rotate: 0,
  id: 'rtc_ic'
})
const rtc_vdd_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.440, 1.848), rotate: 0,
  id: 'rtc_vdd_res_res'
})
const rtc_vdd_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.440, 1.945), rotate: 0,
  id: 'rtc_vdd_cap_0_cap'
})
const rtc_vdd_cap_1_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.449, 1.741), rotate: 0,
  id: 'rtc_vdd_cap_1_cap'
})
const rtc_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.440, 2.042), rotate: 0,
  id: 'rtc_vbat_cap_cap'
})
const rtc_bbs_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.934, 2.196), rotate: 0,
  id: 'rtc_bbs_cap_cap'
})
const eink_ic = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(2.644, 1.032), rotate: 0,
  id: 'eink_ic'
})
const eink_boost_sw = board.add(SOT_23, {
  translate: pt(3.115, 0.906), rotate: 0,
  id: 'eink_boost_sw'
})
const eink_boost_ind = board.add(L_0805_2012Metric, {
  translate: pt(2.979, 1.223), rotate: 0,
  id: 'eink_boost_ind'
})
const eink_boost_res = board.add(R_0603_1608Metric, {
  translate: pt(3.146, 1.219), rotate: 0,
  id: 'eink_boost_res'
})
const eink_boot_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.804, 1.228), rotate: 0,
  id: 'eink_boot_cap'
})
const eink_vdd_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.346, 1.348), rotate: 0,
  id: 'eink_vdd_cap0_cap'
})
const eink_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.502, 1.348), rotate: 0,
  id: 'eink_vdd_cap1_cap'
})
const eink_vslr_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.658, 1.348), rotate: 0,
  id: 'eink_vslr_cap'
})
const eink_vdhr_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.813, 1.348), rotate: 0,
  id: 'eink_vdhr_cap'
})
const eink_vddd_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.969, 1.348), rotate: 0,
  id: 'eink_vddd_cap'
})
const eink_vdh_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.125, 1.348), rotate: 0,
  id: 'eink_vdh_cap'
})
const eink_vgh_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.346, 1.445), rotate: 0,
  id: 'eink_vgh_cap'
})
const eink_vdl_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.502, 1.445), rotate: 0,
  id: 'eink_vdl_cap'
})
const eink_vgl_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.658, 1.445), rotate: 0,
  id: 'eink_vgl_cap'
})
const eink_vcom_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.813, 1.445), rotate: 0,
  id: 'eink_vcom_cap'
})
const eink_boost_dio = board.add(D_SOD_123, {
  translate: pt(3.132, 1.058), rotate: 0,
  id: 'eink_boost_dio'
})
const eink_vgl_dio = board.add(D_SOD_123, {
  translate: pt(2.380, 1.235), rotate: 0,
  id: 'eink_vgl_dio'
})
const eink_boot_dio = board.add(D_SOD_123, {
  translate: pt(2.605, 1.235), rotate: 0,
  id: 'eink_boot_dio'
})
const ext = board.add(PinHeader_1x06_P2_54mm_Vertical, {
  translate: pt(3.414, 1.410), rotate: 0,
  id: 'ext'
})
const rgb1_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.041, 2.411), rotate: 0,
  id: 'rgb1_package'
})
const rgb1_red_res = board.add(R_0603_1608Metric, {
  translate: pt(0.180, 2.385), rotate: 0,
  id: 'rgb1_red_res'
})
const rgb1_green_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.535), rotate: 0,
  id: 'rgb1_green_res'
})
const rgb1_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.535), rotate: 0,
  id: 'rgb1_blue_res'
})
const rgb2_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(3.258, 1.758), rotate: 0,
  id: 'rgb2_package'
})
const rgb2_red_res = board.add(R_0603_1608Metric, {
  translate: pt(3.397, 1.731), rotate: 0,
  id: 'rgb2_red_res'
})
const rgb2_green_res = board.add(R_0603_1608Metric, {
  translate: pt(3.275, 1.881), rotate: 0,
  id: 'rgb2_green_res'
})
const rgb2_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(3.431, 1.881), rotate: 0,
  id: 'rgb2_blue_res'
})
const rgb3_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.432, 2.411), rotate: 0,
  id: 'rgb3_package'
})
const rgb3_red_res = board.add(R_0603_1608Metric, {
  translate: pt(0.571, 2.385), rotate: 0,
  id: 'rgb3_red_res'
})
const rgb3_green_res = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 2.535), rotate: 0,
  id: 'rgb3_green_res'
})
const rgb3_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 2.535), rotate: 0,
  id: 'rgb3_blue_res'
})
const sw1_package = board.add(SW_Push_SPST_NO_Alps_SKRK, {
  translate: pt(2.437, 2.423), rotate: 0,
  id: 'sw1_package'
})
const sw1_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(3.191, 2.385), rotate: 0,
  id: 'sw1_pull_res'
})
const sw2_package = board.add(SW_Push_SPST_NO_Alps_SKRK, {
  translate: pt(2.102, 2.423), rotate: 0,
  id: 'sw2_package'
})
const sw2_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(2.721, 2.385), rotate: 0,
  id: 'sw2_pull_res'
})
const v12sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.309, 2.385), rotate: 0,
  id: 'v12sense_div_top_res'
})
const v12sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.309, 2.482), rotate: 0,
  id: 'v12sense_div_bottom_res'
})
const v5sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.544, 2.385), rotate: 0,
  id: 'v5sense_div_top_res'
})
const v5sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.544, 2.482), rotate: 0,
  id: 'v5sense_div_bottom_res'
})
const vscsense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.074, 2.385), rotate: 0,
  id: 'vscsense_div_top_res'
})
const vscsense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.074, 2.482), rotate: 0,
  id: 'vscsense_div_bottom_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.6070866141732285, 2.6814960629921263);
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


