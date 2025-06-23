const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.100, 2.597), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.140, 2.597), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(4.100, 2.636), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(2.899, 1.905), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(2.748, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(2.904, 2.160), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.525, 2.634), rotate: 0,
  id: 'tp_gnd_tp'
})
const choke_fb = board.add(L_0603_1608Metric, {
  translate: pt(3.733, 2.626), rotate: 0,
  id: 'choke_fb'
})
const tp_pwr_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.026, 2.634), rotate: 0,
  id: 'tp_pwr_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.400, 1.882), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.458, 2.092), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.294, 2.102), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.021, 2.634), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(2.273, 2.634), rotate: 0,
  id: 'prot_3v3_diode'
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
  translate: pt(3.985, 2.664), rotate: 0,
  id: 'usb_esd'
})
const ledr_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 2.626), rotate: 0,
  id: 'ledr_package'
})
const ledr_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.723), rotate: 0,
  id: 'ledr_res'
})
const ledg_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.528, 2.626), rotate: 0,
  id: 'ledg_package'
})
const ledg_res = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 2.723), rotate: 0,
  id: 'ledg_res'
})
const ledb_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.293, 2.626), rotate: 0,
  id: 'ledb_package'
})
const ledb_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.723), rotate: 0,
  id: 'ledb_res'
})
const lora_ic = board.add(QFN_24_1EP_4x4mm_P0_5mm_EP2_6x2_6mm, {
  translate: pt(0.480, 1.843), rotate: 0,
  id: 'lora_ic'
})
const lora_xtal = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.705, 1.807), rotate: 0,
  id: 'lora_xtal'
})
const lora_vreg_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.013), rotate: 0,
  id: 'lora_vreg_cap_cap'
})
const lora_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 2.013), rotate: 0,
  id: 'lora_vbat_cap_cap'
})
const lora_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.748, 2.013), rotate: 0,
  id: 'lora_vdd_cap_cap'
})
const lora_vrpa_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.904, 2.013), rotate: 0,
  id: 'lora_vrpa_cap0_cap'
})
const lora_vrpa_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.110), rotate: 0,
  id: 'lora_vrpa_cap1_cap'
})
const lora_dcc_l = board.add(L_0603_1608Metric, {
  translate: pt(0.592, 2.110), rotate: 0,
  id: 'lora_dcc_l'
})
const lora_rf_sw_ic = board.add(SOT_363_SC_70_6, {
  translate: pt(0.890, 1.795), rotate: 0,
  id: 'lora_rf_sw_ic'
})
const lora_rf_sw_vdd_res = board.add(R_0603_1608Metric, {
  translate: pt(0.748, 2.110), rotate: 0,
  id: 'lora_rf_sw_vdd_res'
})
const lora_rf_sw_ctrl_res = board.add(R_0603_1608Metric, {
  translate: pt(0.904, 2.110), rotate: 0,
  id: 'lora_rf_sw_ctrl_res'
})
const lora_tx_dcblock = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.207), rotate: 0,
  id: 'lora_tx_dcblock'
})
const lora_rfc_dcblock = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 2.207), rotate: 0,
  id: 'lora_rfc_dcblock'
})
const lora_vrpa_choke = board.add(L_0603_1608Metric, {
  translate: pt(0.748, 2.207), rotate: 0,
  id: 'lora_vrpa_choke'
})
const lora_tx_l_l = board.add(L_0603_1608Metric, {
  translate: pt(0.904, 2.207), rotate: 0,
  id: 'lora_tx_l_l'
})
const lora_tx_l_c_lc = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 2.304), rotate: 0,
  id: 'lora_tx_l_c_lc'
})
const lora_tx_pi_c2 = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 2.304), rotate: 0,
  id: 'lora_tx_pi_c2'
})
const lora_tx_pi_l = board.add(L_0603_1608Metric, {
  translate: pt(0.748, 2.304), rotate: 0,
  id: 'lora_tx_pi_l'
})
const lora_balun_l = board.add(L_0603_1608Metric, {
  translate: pt(0.904, 2.304), rotate: 0,
  id: 'lora_balun_l'
})
const lora_balun_c = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.450), rotate: 0,
  id: 'lora_balun_c'
})
const lora_balun_c_p = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.450), rotate: 0,
  id: 'lora_balun_c_p'
})
const lora_ant_pi_c1 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.450), rotate: 0,
  id: 'lora_ant_pi_c1'
})
const lora_ant_pi_c2 = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.450), rotate: 0,
  id: 'lora_ant_pi_c2'
})
const lora_ant_pi_l = board.add(L_0603_1608Metric, {
  translate: pt(0.682, 2.450), rotate: 0,
  id: 'lora_ant_pi_l'
})
const lora_ant_conn = board.add(SMA_Amphenol_901_143_Horizontal, {
  translate: pt(0.169, 1.909), rotate: 0,
  id: 'lora_ant_conn'
})
const tp_lora_spi_tp_sck_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.757, 1.778), rotate: 0,
  id: 'tp_lora_spi_tp_sck_tp'
})
const tp_lora_spi_tp_mosi_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.757, 1.892), rotate: 0,
  id: 'tp_lora_spi_tp_mosi_tp'
})
const tp_lora_spi_tp_miso_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.757, 2.006), rotate: 0,
  id: 'tp_lora_spi_tp_miso_tp'
})
const tp_lora_cs_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.275, 2.634), rotate: 0,
  id: 'tp_lora_cs_tp'
})
const tp_lora_rst_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.771, 2.634), rotate: 0,
  id: 'tp_lora_rst_tp'
})
const tp_lora_dio_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.775, 2.634), rotate: 0,
  id: 'tp_lora_dio_tp'
})
const tp_lora_busy_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.521, 2.634), rotate: 0,
  id: 'tp_lora_busy_tp'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 2.626), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.763, 2.722), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.008, 1.778), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.008, 1.892), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
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
const oled_rst_ic = board.add(SOT_23, {
  translate: pt(1.015, 2.664), rotate: 0,
  id: 'oled_rst_ic'
})
const oled_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(3.499, 2.626), rotate: 0,
  id: 'oled_pull_res'
})
const sd = board.add(microSD_HC_Molex_104031_0811, {
  translate: pt(2.381, 1.998), rotate: 0,
  id: 'sd'
})
const nfc_ic = board.add(HVQFN_40_1EP_6x6mm_P0_5mm_EP4_1x4_1mm, {
  translate: pt(1.223, 1.883), rotate: 0,
  id: 'nfc_ic'
})
const nfc_cvddup_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.677, 1.779), rotate: 0,
  id: 'nfc_cvddup_cap'
})
const nfc_cvbat_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.850, 1.779), rotate: 0,
  id: 'nfc_cvbat_cap'
})
const nfc_cvbat1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.312, 2.094), rotate: 0,
  id: 'nfc_cvbat1_cap'
})
const nfc_cvdd1_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.472, 1.952), rotate: 0,
  id: 'nfc_cvdd1_cap'
})
const nfc_cvdd2_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.646, 1.952), rotate: 0,
  id: 'nfc_cvdd2_cap'
})
const nfc_ctvdd1_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.819, 1.952), rotate: 0,
  id: 'nfc_ctvdd1_cap'
})
const nfc_ctvdd2_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.147, 2.104), rotate: 0,
  id: 'nfc_ctvdd2_cap'
})
const nfc_cvddpad_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.468, 2.094), rotate: 0,
  id: 'nfc_cvddpad_cap'
})
const nfc_cvddmid_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.624, 2.094), rotate: 0,
  id: 'nfc_cvddmid_cap'
})
const nfc_xtal_package = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(1.488, 1.807), rotate: 0,
  id: 'nfc_xtal_package'
})
const nfc_xtal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(1.780, 2.094), rotate: 0,
  id: 'nfc_xtal_cap_a'
})
const nfc_xtal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(1.935, 2.094), rotate: 0,
  id: 'nfc_xtal_cap_b'
})
const nfc_rx_rrx1 = board.add(R_0603_1608Metric, {
  translate: pt(1.139, 2.211), rotate: 0,
  id: 'nfc_rx_rrx1'
})
const nfc_rx_rrx2 = board.add(R_0603_1608Metric, {
  translate: pt(1.294, 2.211), rotate: 0,
  id: 'nfc_rx_rrx2'
})
const nfc_rx_crx1 = board.add(C_0603_1608Metric, {
  translate: pt(1.450, 2.211), rotate: 0,
  id: 'nfc_rx_crx1'
})
const nfc_rx_crx2 = board.add(C_0603_1608Metric, {
  translate: pt(1.606, 2.211), rotate: 0,
  id: 'nfc_rx_crx2'
})
const nfc_emc_l1 = board.add(L_0603_1608Metric, {
  translate: pt(1.762, 2.211), rotate: 0,
  id: 'nfc_emc_l1'
})
const nfc_emc_l2 = board.add(L_0603_1608Metric, {
  translate: pt(1.918, 2.211), rotate: 0,
  id: 'nfc_emc_l2'
})
const nfc_emc_c1 = board.add(C_0603_1608Metric, {
  translate: pt(1.139, 2.307), rotate: 0,
  id: 'nfc_emc_c1'
})
const nfc_emc_c2 = board.add(C_0603_1608Metric, {
  translate: pt(1.294, 2.307), rotate: 0,
  id: 'nfc_emc_c2'
})
const nfc_ant = board.add(an13219, {
  translate: pt(1.392, 2.376), rotate: 0,
  id: 'nfc_ant'
})
const nfc_damp_r1 = board.add(R_0603_1608Metric, {
  translate: pt(1.450, 2.307), rotate: 0,
  id: 'nfc_damp_r1'
})
const nfc_damp_r2 = board.add(R_0603_1608Metric, {
  translate: pt(1.606, 2.307), rotate: 0,
  id: 'nfc_damp_r2'
})
const nfc_match_cs1 = board.add(C_0603_1608Metric, {
  translate: pt(1.762, 2.307), rotate: 0,
  id: 'nfc_match_cs1'
})
const nfc_match_cs2 = board.add(C_0603_1608Metric, {
  translate: pt(1.918, 2.307), rotate: 0,
  id: 'nfc_match_cs2'
})
const nfc_match_cp1 = board.add(C_0603_1608Metric, {
  translate: pt(1.139, 2.404), rotate: 0,
  id: 'nfc_match_cp1'
})
const nfc_match_cp2 = board.add(C_0603_1608Metric, {
  translate: pt(1.294, 2.404), rotate: 0,
  id: 'nfc_match_cp2'
})
const tx_cpack_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.264, 2.626), rotate: 0,
  id: 'tx_cpack_cap'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(4.25767716535433, 2.8696850393700797);
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


