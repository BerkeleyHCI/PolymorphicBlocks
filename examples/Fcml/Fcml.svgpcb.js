const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.599, 2.702), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.638, 2.702), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(3.599, 2.742), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_mcu_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.774, 1.501), rotate: 0,
  id: 'usb_mcu_conn'
})
const usb_mcu_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(1.623, 1.756), rotate: 0,
  id: 'usb_mcu_cc_pull_cc1_res'
})
const usb_mcu_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(1.779, 1.756), rotate: 0,
  id: 'usb_mcu_cc_pull_cc2_res'
})
const usb_fpga_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.237, 1.501), rotate: 0,
  id: 'usb_fpga_conn'
})
const usb_fpga_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(1.086, 1.756), rotate: 0,
  id: 'usb_fpga_cc_pull_cc1_res'
})
const usb_fpga_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(1.242, 1.756), rotate: 0,
  id: 'usb_fpga_cc_pull_cc2_res'
})
const conv_in_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.596, 2.365), rotate: 0,
  id: 'conv_in_conn'
})
const tp_vusb_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.783, 2.740), rotate: 0,
  id: 'tp_vusb_tp'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.036, 2.740), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(2.275, 1.478), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.333, 1.688), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.169, 1.698), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.282, 2.740), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(1.284, 2.740), rotate: 0,
  id: 'prot_3v3_diode'
})
const reg_vgate_ic = board.add(SOT_23_5, {
  translate: pt(2.828, 1.403), rotate: 0,
  id: 'reg_vgate_ic'
})
const reg_vgate_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.624, 1.659), rotate: 0,
  id: 'reg_vgate_fb_div_top_res'
})
const reg_vgate_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.780, 1.659), rotate: 0,
  id: 'reg_vgate_fb_div_bottom_res'
})
const reg_vgate_power_path_inductor = board.add(L_Sunlord_SWPA3012S, {
  translate: pt(2.637, 1.406), rotate: 0,
  id: 'reg_vgate_power_path_inductor'
})
const reg_vgate_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.633, 1.553), rotate: 0,
  id: 'reg_vgate_power_path_in_cap_cap'
})
const reg_vgate_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.806, 1.553), rotate: 0,
  id: 'reg_vgate_power_path_out_cap_cap'
})
const reg_vgate_rect = board.add(D_SOD_323, {
  translate: pt(2.976, 1.552), rotate: 0,
  id: 'reg_vgate_rect'
})
const tp_vgate_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.531, 2.740), rotate: 0,
  id: 'tp_vgate_tp'
})
const conv_power_path_inductor = board.add(L_Sunlord_SWRB1207S, {
  translate: pt(0.262, 0.256), rotate: 0,
  id: 'conv_power_path_inductor'
})
const conv_power_path_in_cap_cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(1.484, 0.597), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_0_'
})
const conv_power_path_in_cap_cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(1.705, 0.597), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_1_'
})
const conv_power_path_in_cap_cap_c_2_ = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 0.849), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_2_'
})
const conv_power_path_in_cap_cap_c_3_ = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 0.849), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_3_'
})
const conv_power_path_in_cap_cap_c_4_ = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 0.849), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_4_'
})
const conv_power_path_out_cap_cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 0.849), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_0_'
})
const conv_power_path_out_cap_cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(0.972, 0.849), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_1_'
})
const conv_power_path_out_cap_cap_c_2_ = board.add(C_1206_3216Metric, {
  translate: pt(1.193, 0.849), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_2_'
})
const conv_sw_0__driver_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.709, 0.106), rotate: 0,
  id: 'conv_sw_0__driver_ic'
})
const conv_sw_0__driver_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.769, 0.963), rotate: 0,
  id: 'conv_sw_0__driver_cap_cap'
})
const conv_sw_0__driver_high_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.093), rotate: 0,
  id: 'conv_sw_0__driver_high_cap_cap'
})
const conv_sw_0__high_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.093), rotate: 0,
  id: 'conv_sw_0__high_gate_res'
})
const conv_sw_0__low_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 1.093), rotate: 0,
  id: 'conv_sw_0__low_gate_res'
})
const conv_sw_0__high_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.039, 0.106), rotate: 0,
  id: 'conv_sw_0__high_fet'
})
const conv_sw_0__low_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.370, 0.106), rotate: 0,
  id: 'conv_sw_0__low_fet'
})
const conv_sw_0__high_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 1.093), rotate: 0,
  id: 'conv_sw_0__high_boot_cap'
})
const conv_sw_0__high_boot_diode_diode = board.add(D_SOD_323, {
  translate: pt(0.945, 0.971), rotate: 0,
  id: 'conv_sw_0__high_boot_diode_diode'
})
const conv_sw_1__ldo_ic = board.add(SOT_23_5, {
  translate: pt(1.073, 0.619), rotate: 0,
  id: 'conv_sw_1__ldo_ic'
})
const conv_sw_1__ldo_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 1.093), rotate: 0,
  id: 'conv_sw_1__ldo_in_cap_cap'
})
const conv_sw_1__ldo_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(1.413, 0.849), rotate: 0,
  id: 'conv_sw_1__ldo_out_cap_cap'
})
const conv_sw_1__iso_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.701, 0.106), rotate: 0,
  id: 'conv_sw_1__iso_ic'
})
const conv_sw_1__iso_cap_a_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 1.093), rotate: 0,
  id: 'conv_sw_1__iso_cap_a_cap'
})
const conv_sw_1__iso_cap_b_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.994, 1.093), rotate: 0,
  id: 'conv_sw_1__iso_cap_b_cap'
})
const conv_sw_1__driver_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.709, 0.358), rotate: 0,
  id: 'conv_sw_1__driver_ic'
})
const conv_sw_1__driver_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.150, 1.093), rotate: 0,
  id: 'conv_sw_1__driver_cap_cap'
})
const conv_sw_1__driver_high_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.306, 1.093), rotate: 0,
  id: 'conv_sw_1__driver_high_cap_cap'
})
const conv_sw_1__high_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(1.461, 1.093), rotate: 0,
  id: 'conv_sw_1__high_gate_res'
})
const conv_sw_1__cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(1.634, 0.849), rotate: 0,
  id: 'conv_sw_1__cap_c_0_'
})
const conv_sw_1__cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 0.979), rotate: 0,
  id: 'conv_sw_1__cap_c_1_'
})
const conv_sw_1__low_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(1.617, 1.093), rotate: 0,
  id: 'conv_sw_1__low_gate_res'
})
const conv_sw_1__high_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.039, 0.358), rotate: 0,
  id: 'conv_sw_1__high_fet'
})
const conv_sw_1__low_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.370, 0.358), rotate: 0,
  id: 'conv_sw_1__low_fet'
})
const conv_sw_1__low_boot_diode_diode = board.add(D_SOD_323, {
  translate: pt(1.111, 0.971), rotate: 0,
  id: 'conv_sw_1__low_boot_diode_diode'
})
const conv_sw_1__high_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.773, 1.093), rotate: 0,
  id: 'conv_sw_1__high_boot_cap'
})
const conv_sw_1__low_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.189), rotate: 0,
  id: 'conv_sw_1__low_boot_cap'
})
const conv_sw_1__high_boot_diode_diode = board.add(D_SOD_323, {
  translate: pt(1.277, 0.971), rotate: 0,
  id: 'conv_sw_1__high_boot_diode_diode'
})
const conv_sw_2__ldo_ic = board.add(SOT_23_5, {
  translate: pt(1.274, 0.619), rotate: 0,
  id: 'conv_sw_2__ldo_ic'
})
const conv_sw_2__ldo_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.189), rotate: 0,
  id: 'conv_sw_2__ldo_in_cap_cap'
})
const conv_sw_2__ldo_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 0.979), rotate: 0,
  id: 'conv_sw_2__ldo_out_cap_cap'
})
const conv_sw_2__iso_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.701, 0.358), rotate: 0,
  id: 'conv_sw_2__iso_ic'
})
const conv_sw_2__iso_cap_a_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.189), rotate: 0,
  id: 'conv_sw_2__iso_cap_a_cap'
})
const conv_sw_2__iso_cap_b_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 1.189), rotate: 0,
  id: 'conv_sw_2__iso_cap_b_cap'
})
const conv_sw_2__driver_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.146, 0.658), rotate: 0,
  id: 'conv_sw_2__driver_ic'
})
const conv_sw_2__driver_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 1.189), rotate: 0,
  id: 'conv_sw_2__driver_cap_cap'
})
const conv_sw_2__driver_high_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 1.189), rotate: 0,
  id: 'conv_sw_2__driver_high_cap_cap'
})
const conv_sw_2__high_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 1.189), rotate: 0,
  id: 'conv_sw_2__high_gate_res'
})
const conv_sw_2__cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 0.979), rotate: 0,
  id: 'conv_sw_2__cap_c_0_'
})
const conv_sw_2__cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 0.979), rotate: 0,
  id: 'conv_sw_2__cap_c_1_'
})
const conv_sw_2__low_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 1.189), rotate: 0,
  id: 'conv_sw_2__low_gate_res'
})
const conv_sw_2__high_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.476, 0.658), rotate: 0,
  id: 'conv_sw_2__high_fet'
})
const conv_sw_2__low_fet = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.807, 0.658), rotate: 0,
  id: 'conv_sw_2__low_fet'
})
const conv_sw_2__low_boot_diode_diode = board.add(D_SOD_323, {
  translate: pt(1.443, 0.971), rotate: 0,
  id: 'conv_sw_2__low_boot_diode_diode'
})
const conv_sw_2__high_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.306, 1.189), rotate: 0,
  id: 'conv_sw_2__high_boot_cap'
})
const conv_sw_2__low_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.461, 1.189), rotate: 0,
  id: 'conv_sw_2__low_boot_cap'
})
const conv_sw_2__high_boot_diode_diode = board.add(D_SOD_323, {
  translate: pt(1.608, 0.971), rotate: 0,
  id: 'conv_sw_2__high_boot_diode_diode'
})
const conv_out_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.986, 2.365), rotate: 0,
  id: 'conv_out_conn'
})
const tp_conv_out_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.033, 2.740), rotate: 0,
  id: 'tp_conv_out_tp'
})
const tp_conv_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.535, 2.740), rotate: 0,
  id: 'tp_conv_gnd_tp'
})
const fpga_ic = board.add(QFN_48_1EP_7x7mm_P0_5mm_EP5_3x5_3mm, {
  translate: pt(0.161, 1.498), rotate: 0,
  id: 'fpga_ic'
})
const fpga_vcc_reg_ic = board.add(SOT_23_5, {
  translate: pt(0.486, 1.765), rotate: 0,
  id: 'fpga_vcc_reg_ic'
})
const fpga_vcc_reg_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.992), rotate: 0,
  id: 'fpga_vcc_reg_in_cap_cap'
})
const fpga_vcc_reg_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.992), rotate: 0,
  id: 'fpga_vcc_reg_out_cap_cap'
})
const fpga_reset_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 1.992), rotate: 0,
  id: 'fpga_reset_pu_res'
})
const fpga_mem_ic = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(0.183, 1.811), rotate: 0,
  id: 'fpga_mem_ic'
})
const fpga_mem_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 1.992), rotate: 0,
  id: 'fpga_mem_vcc_cap_cap'
})
const fpga_prog_conn = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.531, 1.482), rotate: 0,
  id: 'fpga_prog_conn'
})
const fpga_cs_jmp_device = board.add(SolderJumper_2_P1_3mm_Open_TrianglePad1_0x1_5mm, {
  translate: pt(0.671, 1.748), rotate: 0,
  id: 'fpga_cs_jmp_device'
})
const fpga_mem_pu_res = board.add(R_0603_1608Metric, {
  translate: pt(0.682, 1.992), rotate: 0,
  id: 'fpga_mem_pu_res'
})
const fpga_vio_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 1.992), rotate: 0,
  id: 'fpga_vio_cap0_cap'
})
const fpga_vio_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.089), rotate: 0,
  id: 'fpga_vio_cap1_cap'
})
const fpga_vio_cap2_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 2.089), rotate: 0,
  id: 'fpga_vio_cap2_cap'
})
const fpga_vpp_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.089), rotate: 0,
  id: 'fpga_vpp_cap_cap'
})
const fpga_pll_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 2.089), rotate: 0,
  id: 'fpga_pll_res_res'
})
const fpga_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.089), rotate: 0,
  id: 'fpga_vcc_cap_cap'
})
const fpga_pll_lf_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.843, 1.737), rotate: 0,
  id: 'fpga_pll_lf_cap'
})
const fpga_pll_hf_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 2.089), rotate: 0,
  id: 'fpga_pll_hf_cap'
})
const cdone_package = board.add(LED_0603_1608Metric, {
  translate: pt(3.590, 2.264), rotate: 0,
  id: 'cdone_package'
})
const cdone_res = board.add(R_0603_1608Metric, {
  translate: pt(3.589, 2.361), rotate: 0,
  id: 'cdone_res'
})
const fpga_osc_device = board.add(Crystal_SMD_2520_4Pin_2_5x2_0mm, {
  translate: pt(3.346, 2.294), rotate: 0,
  id: 'fpga_osc_device'
})
const fpga_osc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.337, 2.422), rotate: 0,
  id: 'fpga_osc_cap_cap'
})
const fpga_sw_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.761, 2.348), rotate: 0,
  id: 'fpga_sw_package'
})
const fpga_led_led_0__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.216, 1.365), rotate: 0,
  id: 'fpga_led_led_0__package'
})
const fpga_led_led_0__res = board.add(R_0603_1608Metric, {
  translate: pt(3.215, 1.559), rotate: 0,
  id: 'fpga_led_led_0__res'
})
const fpga_led_led_1__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.372, 1.365), rotate: 0,
  id: 'fpga_led_led_1__package'
})
const fpga_led_led_1__res = board.add(R_0603_1608Metric, {
  translate: pt(3.371, 1.559), rotate: 0,
  id: 'fpga_led_led_1__res'
})
const fpga_led_led_2__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.216, 1.462), rotate: 0,
  id: 'fpga_led_led_2__package'
})
const fpga_led_led_2__res = board.add(R_0603_1608Metric, {
  translate: pt(3.215, 1.656), rotate: 0,
  id: 'fpga_led_led_2__res'
})
const fpga_led_led_3__package = board.add(LED_0603_1608Metric, {
  translate: pt(3.372, 1.462), rotate: 0,
  id: 'fpga_led_led_3__package'
})
const fpga_led_led_3__res = board.add(R_0603_1608Metric, {
  translate: pt(3.371, 1.656), rotate: 0,
  id: 'fpga_led_led_3__res'
})
const usb_fpga_bitbang_dp_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(1.418, 2.264), rotate: 0,
  id: 'usb_fpga_bitbang_dp_pull_res'
})
const usb_fpga_bitbang_dp_res = board.add(R_0603_1608Metric, {
  translate: pt(1.418, 2.361), rotate: 0,
  id: 'usb_fpga_bitbang_dp_res'
})
const usb_fpga_bitbang_dm_res = board.add(R_0603_1608Metric, {
  translate: pt(1.418, 2.458), rotate: 0,
  id: 'usb_fpga_bitbang_dm_res'
})
const usb_fpga_esd = board.add(SOT_23, {
  translate: pt(3.293, 2.769), rotate: 0,
  id: 'usb_fpga_esd'
})
const mcu_swd_conn = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(2.498, 0.146), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(QFN_56_1EP_7x7mm_P0_4mm_EP3_2x3_2mm, {
  translate: pt(2.127, 0.163), rotate: 0,
  id: 'mcu_ic'
})
const mcu_iovdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.633, 0.393), rotate: 0,
  id: 'mcu_iovdd_cap_0__cap'
})
const mcu_iovdd_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.789, 0.393), rotate: 0,
  id: 'mcu_iovdd_cap_1__cap'
})
const mcu_iovdd_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.023, 0.658), rotate: 0,
  id: 'mcu_iovdd_cap_2__cap'
})
const mcu_iovdd_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.179, 0.658), rotate: 0,
  id: 'mcu_iovdd_cap_3__cap'
})
const mcu_iovdd_cap_4__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.335, 0.658), rotate: 0,
  id: 'mcu_iovdd_cap_4__cap'
})
const mcu_iovdd_cap_5__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.491, 0.658), rotate: 0,
  id: 'mcu_iovdd_cap_5__cap'
})
const mcu_avdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.646, 0.658), rotate: 0,
  id: 'mcu_avdd_cap_cap'
})
const mcu_vreg_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.802, 0.658), rotate: 0,
  id: 'mcu_vreg_in_cap_cap'
})
const mcu_mem_ic = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(2.148, 0.477), rotate: 0,
  id: 'mcu_mem_ic'
})
const mcu_mem_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.023, 0.755), rotate: 0,
  id: 'mcu_mem_vcc_cap_cap'
})
const mcu_dvdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.179, 0.755), rotate: 0,
  id: 'mcu_dvdd_cap_0__cap'
})
const mcu_dvdd_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.335, 0.755), rotate: 0,
  id: 'mcu_dvdd_cap_1__cap'
})
const mcu_vreg_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.491, 0.755), rotate: 0,
  id: 'mcu_vreg_out_cap_cap'
})
const mcu_usb_res_dp_res = board.add(R_0603_1608Metric, {
  translate: pt(2.646, 0.755), rotate: 0,
  id: 'mcu_usb_res_dp_res'
})
const mcu_usb_res_dm_res = board.add(R_0603_1608Metric, {
  translate: pt(2.802, 0.755), rotate: 0,
  id: 'mcu_usb_res_dm_res'
})
const mcu_crystal_package = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(2.453, 0.431), rotate: 0,
  id: 'mcu_crystal_package'
})
const mcu_crystal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(2.023, 0.852), rotate: 0,
  id: 'mcu_crystal_cap_a'
})
const mcu_crystal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(2.179, 0.852), rotate: 0,
  id: 'mcu_crystal_cap_b'
})
const mcu_sw_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.214, 2.348), rotate: 0,
  id: 'mcu_sw_package'
})
const mcu_leds_led_0__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 2.264), rotate: 0,
  id: 'mcu_leds_led_0__package'
})
const mcu_leds_led_0__res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.459), rotate: 0,
  id: 'mcu_leds_led_0__res'
})
const mcu_leds_led_1__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.215, 2.264), rotate: 0,
  id: 'mcu_leds_led_1__package'
})
const mcu_leds_led_1__res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.459), rotate: 0,
  id: 'mcu_leds_led_1__res'
})
const mcu_leds_led_2__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 2.362), rotate: 0,
  id: 'mcu_leds_led_2__package'
})
const mcu_leds_led_2__res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.556), rotate: 0,
  id: 'mcu_leds_led_2__res'
})
const mcu_leds_led_3__package = board.add(LED_0603_1608Metric, {
  translate: pt(0.215, 2.362), rotate: 0,
  id: 'mcu_leds_led_3__package'
})
const mcu_leds_led_3__res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.556), rotate: 0,
  id: 'mcu_leds_led_3__res'
})
const usb_mcu_esd = board.add(SOT_23, {
  translate: pt(3.484, 2.769), rotate: 0,
  id: 'usb_mcu_esd'
})
const tp_fpga_0__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.032, 2.740), rotate: 0,
  id: 'tp_fpga_0__tp'
})
const tp_fpga_1__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.781, 2.740), rotate: 0,
  id: 'tp_fpga_1__tp'
})
const tp_fpga_2__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.533, 2.740), rotate: 0,
  id: 'tp_fpga_2__tp'
})
const tp_fpga_3__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(0.786, 2.740), rotate: 0,
  id: 'tp_fpga_3__tp'
})
const pwm_filter_tp_0L__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.004, 2.273), rotate: 0,
  id: 'pwm_filter_tp_0L__tp'
})
const pwm_filter_tp_0H__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.175, 2.273), rotate: 0,
  id: 'pwm_filter_tp_0H__tp'
})
const pwm_filter_tp_1L__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.004, 2.387), rotate: 0,
  id: 'pwm_filter_tp_1L__tp'
})
const pwm_filter_tp_1H__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.175, 2.387), rotate: 0,
  id: 'pwm_filter_tp_1H__tp'
})
const pwm_filter_tp_2L__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.004, 2.501), rotate: 0,
  id: 'pwm_filter_tp_2L__tp'
})
const pwm_filter_tp_2H__tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(1.175, 2.501), rotate: 0,
  id: 'pwm_filter_tp_2H__tp'
})
const tp_pwm_elts_0L__rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 2.264), rotate: 0,
  id: 'tp_pwm_elts_0L__rc_r'
})
const tp_pwm_elts_0L__rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.605, 2.264), rotate: 0,
  id: 'tp_pwm_elts_0L__rc_c'
})
const tp_pwm_elts_0H__rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 2.264), rotate: 0,
  id: 'tp_pwm_elts_0H__rc_r'
})
const tp_pwm_elts_0H__rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 2.361), rotate: 0,
  id: 'tp_pwm_elts_0H__rc_c'
})
const tp_pwm_elts_1L__rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 2.361), rotate: 0,
  id: 'tp_pwm_elts_1L__rc_r'
})
const tp_pwm_elts_1L__rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.761, 2.361), rotate: 0,
  id: 'tp_pwm_elts_1L__rc_c'
})
const tp_pwm_elts_1H__rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 2.458), rotate: 0,
  id: 'tp_pwm_elts_1H__rc_r'
})
const tp_pwm_elts_1H__rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.605, 2.458), rotate: 0,
  id: 'tp_pwm_elts_1H__rc_c'
})
const tp_pwm_elts_2L__rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 2.458), rotate: 0,
  id: 'tp_pwm_elts_2L__rc_r'
})
const tp_pwm_elts_2L__rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.449, 2.555), rotate: 0,
  id: 'tp_pwm_elts_2L__rc_c'
})
const tp_pwm_elts_2H__rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 2.555), rotate: 0,
  id: 'tp_pwm_elts_2H__rc_r'
})
const tp_pwm_elts_2H__rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.761, 2.555), rotate: 0,
  id: 'tp_pwm_elts_2H__rc_c'
})
const conv_in_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.731), rotate: 0,
  id: 'conv_in_sense_div_top_res'
})
const conv_in_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.828), rotate: 0,
  id: 'conv_in_sense_div_bottom_res'
})
const conv_out_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.731), rotate: 0,
  id: 'conv_out_sense_div_top_res'
})
const conv_out_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.828), rotate: 0,
  id: 'conv_out_sense_div_bottom_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.7659448818897645, 2.9748031496062994);
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


