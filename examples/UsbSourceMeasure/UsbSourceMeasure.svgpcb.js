const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(5.588, 4.566), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(5.627, 4.566), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(5.588, 4.605), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(3.954, 3.280), rotate: 0,
  id: 'usb_conn'
})
const tp_gnd_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.506, 4.603), rotate: 0,
  id: 'tp_gnd_tp'
})
const filt_vusb_fb = board.add(L_1206_3216Metric, {
  translate: pt(1.979, 4.613), rotate: 0,
  id: 'filt_vusb_fb'
})
const cap_vusb_cap = board.add(CP_Elec_8x10, {
  translate: pt(4.498, 3.288), rotate: 0,
  id: 'cap_vusb_cap'
})
const prot_vusb_diode = board.add(D_SMA, {
  translate: pt(0.842, 4.635), rotate: 0,
  id: 'prot_vusb_diode'
})
const tp_vusb_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.008, 4.603), rotate: 0,
  id: 'tp_vusb_tp'
})
const reg_v5_ic = board.add(SOT_23_6, {
  translate: pt(2.127, 3.182), rotate: 0,
  id: 'reg_v5_ic'
})
const reg_v5_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.286, 3.400), rotate: 0,
  id: 'reg_v5_fb_div_top_res'
})
const reg_v5_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.845, 3.530), rotate: 0,
  id: 'reg_v5_fb_div_bottom_res'
})
const reg_v5_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.001, 3.530), rotate: 0,
  id: 'reg_v5_hf_in_cap_cap'
})
const reg_v5_boot_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.157, 3.530), rotate: 0,
  id: 'reg_v5_boot_cap'
})
const reg_v5_power_path_inductor = board.add(L_Sunlord_SWPA5040S, {
  translate: pt(1.897, 3.224), rotate: 0,
  id: 'reg_v5_power_path_inductor'
})
const reg_v5_power_path_in_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(1.877, 3.417), rotate: 0,
  id: 'reg_v5_power_path_in_cap_cap'
})
const reg_v5_power_path_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.098, 3.417), rotate: 0,
  id: 'reg_v5_power_path_out_cap_cap'
})
const reg_v5_en_res = board.add(R_0603_1608Metric, {
  translate: pt(2.313, 3.530), rotate: 0,
  id: 'reg_v5_en_res'
})
const tp_v5_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.756, 4.603), rotate: 0,
  id: 'tp_v5_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(3.154, 3.257), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.213, 3.467), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.048, 3.476), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const prot_3v3_diode = board.add(D_SMA, {
  translate: pt(1.236, 4.635), rotate: 0,
  id: 'prot_3v3_diode'
})
const tp_3v3_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.758, 4.603), rotate: 0,
  id: 'tp_3v3_tp'
})
const conv_power_path_inductor = board.add(L_Bourns_SRP1245A, {
  translate: pt(0.289, 2.069), rotate: 0,
  id: 'conv_power_path_inductor'
})
const conv_power_path_in_cap_cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 2.725), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_0_'
})
const conv_power_path_in_cap_cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 2.725), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_1_'
})
const conv_power_path_in_cap_cap_c_2_ = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 2.725), rotate: 0,
  id: 'conv_power_path_in_cap_cap_c_2_'
})
const conv_power_path_out_cap_cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 2.725), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_0_'
})
const conv_power_path_out_cap_cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(0.972, 2.725), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_1_'
})
const conv_power_path_out_cap_cap_c_2_ = board.add(C_1206_3216Metric, {
  translate: pt(1.193, 2.725), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_2_'
})
const conv_power_path_out_cap_cap_c_3_ = board.add(C_1206_3216Metric, {
  translate: pt(1.413, 2.725), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_3_'
})
const conv_power_path_out_cap_cap_c_4_ = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 2.855), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_4_'
})
const conv_power_path_out_cap_cap_c_5_ = board.add(C_1206_3216Metric, {
  translate: pt(0.311, 2.855), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_5_'
})
const conv_power_path_out_cap_cap_c_6_ = board.add(C_1206_3216Metric, {
  translate: pt(0.531, 2.855), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_6_'
})
const conv_power_path_out_cap_cap_c_7_ = board.add(C_1206_3216Metric, {
  translate: pt(0.752, 2.855), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_7_'
})
const conv_power_path_out_cap_cap_c_8_ = board.add(C_1206_3216Metric, {
  translate: pt(0.972, 2.855), rotate: 0,
  id: 'conv_power_path_out_cap_cap_c_8_'
})
const conv_buck_sw_driver_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.098, 2.471), rotate: 0,
  id: 'conv_buck_sw_driver_ic'
})
const conv_buck_sw_driver_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.492, 2.838), rotate: 0,
  id: 'conv_buck_sw_driver_cap_cap'
})
const conv_buck_sw_driver_high_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.968), rotate: 0,
  id: 'conv_buck_sw_driver_high_cap_cap'
})
const conv_buck_sw_driver_boot = board.add(D_SOD_323, {
  translate: pt(1.166, 2.847), rotate: 0,
  id: 'conv_buck_sw_driver_boot'
})
const conv_buck_sw_low_fet = board.add(TO_252_2, {
  translate: pt(0.870, 1.951), rotate: 0,
  id: 'conv_buck_sw_low_fet'
})
const conv_buck_sw_low_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.968), rotate: 0,
  id: 'conv_buck_sw_low_gate_res'
})
const conv_buck_sw_high_fet = board.add(TO_252_2, {
  translate: pt(1.346, 1.951), rotate: 0,
  id: 'conv_buck_sw_high_fet'
})
const conv_buck_sw_high_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 2.968), rotate: 0,
  id: 'conv_buck_sw_high_gate_res'
})
const conv_boost_sw_driver_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.429, 2.471), rotate: 0,
  id: 'conv_boost_sw_driver_ic'
})
const conv_boost_sw_driver_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 2.968), rotate: 0,
  id: 'conv_boost_sw_driver_cap_cap'
})
const conv_boost_sw_driver_high_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 2.968), rotate: 0,
  id: 'conv_boost_sw_driver_high_cap_cap'
})
const conv_boost_sw_driver_boot = board.add(D_SOD_323, {
  translate: pt(1.331, 2.847), rotate: 0,
  id: 'conv_boost_sw_driver_boot'
})
const conv_boost_sw_low_fet = board.add(TO_252_2, {
  translate: pt(0.252, 2.502), rotate: 0,
  id: 'conv_boost_sw_low_fet'
})
const conv_boost_sw_low_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 2.968), rotate: 0,
  id: 'conv_boost_sw_low_gate_res'
})
const conv_boost_sw_high_fet = board.add(TO_252_2, {
  translate: pt(0.728, 2.502), rotate: 0,
  id: 'conv_boost_sw_high_fet'
})
const conv_boost_sw_high_gate_res = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 2.968), rotate: 0,
  id: 'conv_boost_sw_high_gate_res'
})
const prot_conv_diode = board.add(D_SMA, {
  translate: pt(1.630, 4.635), rotate: 0,
  id: 'prot_conv_diode'
})
const tp_conv_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.259, 4.603), rotate: 0,
  id: 'tp_conv_tp'
})
const reg_v12_ic = board.add(SOT_23_5, {
  translate: pt(5.460, 3.182), rotate: 0,
  id: 'reg_v12_ic'
})
const reg_v12_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(5.781, 3.317), rotate: 0,
  id: 'reg_v12_fb_div_top_res'
})
const reg_v12_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(5.438, 3.431), rotate: 0,
  id: 'reg_v12_fb_div_bottom_res'
})
const reg_v12_power_path_inductor = board.add(L_0805_2012Metric, {
  translate: pt(5.614, 3.322), rotate: 0,
  id: 'reg_v12_power_path_inductor'
})
const reg_v12_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(5.647, 3.154), rotate: 0,
  id: 'reg_v12_power_path_in_cap_cap'
})
const reg_v12_power_path_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(5.594, 3.431), rotate: 0,
  id: 'reg_v12_power_path_out_cap_cap'
})
const reg_v12_cf = board.add(C_0603_1608Metric, {
  translate: pt(5.750, 3.431), rotate: 0,
  id: 'reg_v12_cf'
})
const reg_v12_rect = board.add(D_SOD_323, {
  translate: pt(5.443, 3.326), rotate: 0,
  id: 'reg_v12_rect'
})
const tp_v12_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(4.509, 4.603), rotate: 0,
  id: 'tp_v12_tp'
})
const reg_analog_ic = board.add(SOT_23_5, {
  translate: pt(3.526, 3.182), rotate: 0,
  id: 'reg_analog_ic'
})
const reg_analog_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.504, 3.447), rotate: 0,
  id: 'reg_analog_in_cap_cap'
})
const reg_analog_out_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(3.536, 3.333), rotate: 0,
  id: 'reg_analog_out_cap_cap'
})
const tp_analog_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.507, 4.603), rotate: 0,
  id: 'tp_analog_tp'
})
const reg_vref_ic = board.add(SOT_23, {
  translate: pt(1.409, 4.251), rotate: 0,
  id: 'reg_vref_ic'
})
const reg_vref_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.391, 4.386), rotate: 0,
  id: 'reg_vref_in_cap_cap'
})
const tp_vref_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.007, 4.603), rotate: 0,
  id: 'tp_vref_tp'
})
const ref_div_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 4.594), rotate: 0,
  id: 'ref_div_div_top_res'
})
const ref_div_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 4.691), rotate: 0,
  id: 'ref_div_div_bottom_res'
})
const ref_cap = board.add(C_0603_1608Metric, {
  translate: pt(5.804, 4.594), rotate: 0,
  id: 'ref_cap'
})
const reg_vcontrol_ic = board.add(SOT_23_5, {
  translate: pt(4.904, 3.182), rotate: 0,
  id: 'reg_vcontrol_ic'
})
const reg_vcontrol_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(5.047, 3.317), rotate: 0,
  id: 'reg_vcontrol_fb_div_top_res'
})
const reg_vcontrol_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(5.203, 3.317), rotate: 0,
  id: 'reg_vcontrol_fb_div_bottom_res'
})
const reg_vcontrol_power_path_inductor = board.add(L_0603_1608Metric, {
  translate: pt(4.881, 3.431), rotate: 0,
  id: 'reg_vcontrol_power_path_inductor'
})
const reg_vcontrol_power_path_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(5.037, 3.431), rotate: 0,
  id: 'reg_vcontrol_power_path_in_cap_cap'
})
const reg_vcontrol_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(5.091, 3.154), rotate: 0,
  id: 'reg_vcontrol_power_path_out_cap_cap'
})
const reg_vcontrol_cf = board.add(C_0603_1608Metric, {
  translate: pt(5.193, 3.431), rotate: 0,
  id: 'reg_vcontrol_cf'
})
const reg_vcontrol_rect = board.add(D_SOD_323, {
  translate: pt(4.887, 3.326), rotate: 0,
  id: 'reg_vcontrol_rect'
})
const tp_vcontrol_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(3.257, 4.603), rotate: 0,
  id: 'tp_vcontrol_tp'
})
const reg_vcontroln_ic = board.add(SOT_23_6, {
  translate: pt(0.081, 4.251), rotate: 0,
  id: 'reg_vcontroln_ic'
})
const reg_vcontroln_cf = board.add(C_0805_2012Metric, {
  translate: pt(0.287, 4.396), rotate: 0,
  id: 'reg_vcontroln_cf'
})
const reg_vcontroln_cout_cap_c_0_ = board.add(C_1206_3216Metric, {
  translate: pt(0.291, 4.229), rotate: 0,
  id: 'reg_vcontroln_cout_cap_c_0_'
})
const reg_vcontroln_cout_cap_c_1_ = board.add(C_1206_3216Metric, {
  translate: pt(0.091, 4.402), rotate: 0,
  id: 'reg_vcontroln_cout_cap_c_1_'
})
const tp_vcontroln_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.256, 4.603), rotate: 0,
  id: 'tp_vcontroln_tp'
})
const control_dmeas_r1 = board.add(R_0603_1608Metric, {
  translate: pt(2.980, 2.519), rotate: 0,
  id: 'control_dmeas_r1'
})
const control_dmeas_r2 = board.add(R_0603_1608Metric, {
  translate: pt(3.135, 2.519), rotate: 0,
  id: 'control_dmeas_r2'
})
const control_dmeas_rf = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.647), rotate: 0,
  id: 'control_dmeas_rf'
})
const control_dmeas_rg = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.647), rotate: 0,
  id: 'control_dmeas_rg'
})
const control_dclamp_res = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 2.647), rotate: 0,
  id: 'control_dclamp_res'
})
const control_err_d_rtop = board.add(R_0603_1608Metric, {
  translate: pt(2.219, 2.647), rotate: 0,
  id: 'control_err_d_rtop'
})
const control_err_d_rbot = board.add(R_0603_1608Metric, {
  translate: pt(2.375, 2.647), rotate: 0,
  id: 'control_err_d_rbot'
})
const control_err_d_rout = board.add(R_0603_1608Metric, {
  translate: pt(2.531, 2.647), rotate: 0,
  id: 'control_err_d_rout'
})
const control_err_volt_rtop = board.add(R_0603_1608Metric, {
  translate: pt(2.687, 2.647), rotate: 0,
  id: 'control_err_volt_rtop'
})
const control_err_volt_rbot = board.add(R_0603_1608Metric, {
  translate: pt(2.843, 2.647), rotate: 0,
  id: 'control_err_volt_rbot'
})
const control_err_volt_rout = board.add(R_0603_1608Metric, {
  translate: pt(2.998, 2.647), rotate: 0,
  id: 'control_err_volt_rout'
})
const control_err_source_rtop = board.add(R_0603_1608Metric, {
  translate: pt(3.154, 2.647), rotate: 0,
  id: 'control_err_source_rtop'
})
const control_err_source_rbot = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.744), rotate: 0,
  id: 'control_err_source_rbot'
})
const control_err_source_rout = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.744), rotate: 0,
  id: 'control_err_source_rout'
})
const control_err_source_diode = board.add(D_SOD_323, {
  translate: pt(2.322, 2.528), rotate: 0,
  id: 'control_err_source_diode'
})
const control_err_sink_rtop = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 2.744), rotate: 0,
  id: 'control_err_sink_rtop'
})
const control_err_sink_rbot = board.add(R_0603_1608Metric, {
  translate: pt(2.219, 2.744), rotate: 0,
  id: 'control_err_sink_rbot'
})
const control_err_sink_rout = board.add(R_0603_1608Metric, {
  translate: pt(2.375, 2.744), rotate: 0,
  id: 'control_err_sink_rout'
})
const control_err_sink_diode = board.add(D_SOD_323, {
  translate: pt(2.487, 2.528), rotate: 0,
  id: 'control_err_sink_diode'
})
const control_off_sw_device_ic = board.add(SOT_363_SC_70_6, {
  translate: pt(2.965, 2.231), rotate: 0,
  id: 'control_off_sw_device_ic'
})
const control_off_sw_device_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.531, 2.744), rotate: 0,
  id: 'control_off_sw_device_vdd_cap_cap'
})
const control_int_r = board.add(R_0603_1608Metric, {
  translate: pt(2.687, 2.744), rotate: 0,
  id: 'control_int_r'
})
const control_int_c = board.add(C_0603_1608Metric, {
  translate: pt(2.843, 2.744), rotate: 0,
  id: 'control_int_c'
})
const control_amp_r1 = board.add(R_0603_1608Metric, {
  translate: pt(2.998, 2.744), rotate: 0,
  id: 'control_amp_r1'
})
const control_amp_r2 = board.add(R_0603_1608Metric, {
  translate: pt(3.154, 2.744), rotate: 0,
  id: 'control_amp_r2'
})
const control_hvclamp_res = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.841), rotate: 0,
  id: 'control_hvclamp_res'
})
const control_driver_clamp1 = board.add(D_SOD_323, {
  translate: pt(2.653, 2.528), rotate: 0,
  id: 'control_driver_clamp1'
})
const control_driver_clamp2 = board.add(D_SOD_323, {
  translate: pt(2.819, 2.528), rotate: 0,
  id: 'control_driver_clamp2'
})
const control_driver_high_fet = board.add(TO_252_2, {
  translate: pt(2.826, 1.951), rotate: 0,
  id: 'control_driver_high_fet'
})
const control_driver_low_fet = board.add(TO_252_2, {
  translate: pt(1.944, 2.313), rotate: 0,
  id: 'control_driver_low_fet'
})
const control_driver_res = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.841), rotate: 0,
  id: 'control_driver_res'
})
const control_isense_ranges_0__pwr_sw_ic = board.add(SMDIP_6_W7_62mm, {
  translate: pt(1.894, 1.975), rotate: 0,
  id: 'control_isense_ranges_0__pwr_sw_ic'
})
const control_isense_ranges_0__pwr_sw_res = board.add(R_0603_1608Metric, {
  translate: pt(2.063, 2.841), rotate: 0,
  id: 'control_isense_ranges_0__pwr_sw_res'
})
const control_isense_ranges_0__isense_res_res = board.add(R_1206_3216Metric, {
  translate: pt(3.157, 2.220), rotate: 0,
  id: 'control_isense_ranges_0__isense_res_res'
})
const control_isense_ranges_0__clamp_res = board.add(R_0603_1608Metric, {
  translate: pt(2.219, 2.841), rotate: 0,
  id: 'control_isense_ranges_0__clamp_res'
})
const control_isense_ranges_0__sense_sw_device_ic = board.add(SOT_23_6, {
  translate: pt(2.581, 2.243), rotate: 0,
  id: 'control_isense_ranges_0__sense_sw_device_ic'
})
const control_isense_ranges_0__sense_sw_device_vdd_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.979, 2.529), rotate: 0,
  id: 'control_isense_ranges_0__sense_sw_device_vdd_cap_cap'
})
const control_isense_ranges_1__pwr_sw_ic = board.add(SMDIP_6_W7_62mm, {
  translate: pt(2.335, 1.975), rotate: 0,
  id: 'control_isense_ranges_1__pwr_sw_ic'
})
const control_isense_ranges_1__pwr_sw_res = board.add(R_0603_1608Metric, {
  translate: pt(2.375, 2.841), rotate: 0,
  id: 'control_isense_ranges_1__pwr_sw_res'
})
const control_isense_ranges_1__isense_res_res = board.add(R_1206_3216Metric, {
  translate: pt(1.783, 2.535), rotate: 0,
  id: 'control_isense_ranges_1__isense_res_res'
})
const control_isense_ranges_1__clamp_res = board.add(R_0603_1608Metric, {
  translate: pt(2.531, 2.841), rotate: 0,
  id: 'control_isense_ranges_1__clamp_res'
})
const control_isense_ranges_1__sense_sw_device_ic = board.add(SOT_23_6, {
  translate: pt(2.781, 2.243), rotate: 0,
  id: 'control_isense_ranges_1__sense_sw_device_ic'
})
const control_isense_ranges_1__sense_sw_device_vdd_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.152, 2.529), rotate: 0,
  id: 'control_isense_ranges_1__sense_sw_device_vdd_cap_cap'
})
const control_imeas_amp = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.315, 2.282), rotate: 0,
  id: 'control_imeas_amp'
})
const control_imeas_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.687, 2.841), rotate: 0,
  id: 'control_imeas_vdd_cap_cap'
})
const control_vmeas_r1 = board.add(R_0603_1608Metric, {
  translate: pt(2.843, 2.841), rotate: 0,
  id: 'control_vmeas_r1'
})
const control_vmeas_r2 = board.add(R_0603_1608Metric, {
  translate: pt(2.998, 2.841), rotate: 0,
  id: 'control_vmeas_r2'
})
const control_vmeas_rf = board.add(R_0603_1608Metric, {
  translate: pt(3.154, 2.841), rotate: 0,
  id: 'control_vmeas_rf'
})
const control_vmeas_rg = board.add(R_0603_1608Metric, {
  translate: pt(1.751, 2.937), rotate: 0,
  id: 'control_vmeas_rg'
})
const control_vclamp_res = board.add(R_0603_1608Metric, {
  translate: pt(1.907, 2.937), rotate: 0,
  id: 'control_vclamp_res'
})
const pd_ic = board.add(WQFN_14_1EP_2_5x2_5mm_P0_5mm_EP1_45x1_45mm, {
  translate: pt(0.573, 4.257), rotate: 0,
  id: 'pd_ic'
})
const pd_vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.731, 4.398), rotate: 0,
  id: 'pd_vdd_cap_0__cap'
})
const pd_vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(0.567, 4.407), rotate: 0,
  id: 'pd_vdd_cap_1__cap'
})
const mcu_ic = board.add(ESP32_S3_WROOM_1, {
  translate: pt(3.504, 0.530), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_1206_3216Metric, {
  translate: pt(4.579, 0.242), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(4.767, 0.226), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(4.626, 0.079), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(4.546, 0.356), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(4.702, 0.356), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const led_package = board.add(LED_0603_1608Metric, {
  translate: pt(4.220, 4.213), rotate: 0,
  id: 'led_package'
})
const led_res = board.add(R_0603_1608Metric, {
  translate: pt(4.220, 4.310), rotate: 0,
  id: 'led_res'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(5.473, 4.633), rotate: 0,
  id: 'usb_esd'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.983, 4.221), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_TE_RCT_0805, {
  translate: pt(2.983, 4.335), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(6.097, 4.213), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(6.097, 4.309), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const oled_device_conn = board.add(Hirose_FH12_24S_0_5SH_1x24_1MP_P0_50mm_Horizontal, {
  translate: pt(0.356, 1.577), rotate: 0,
  id: 'oled_device_conn'
})
const oled_lcd = board.add(Lcd_Er_Oled022_1_Outline, {
  translate: pt(1.220, 0.607), rotate: 0,
  id: 'oled_lcd'
})
const oled_iref_res = board.add(R_0603_1608Metric, {
  translate: pt(1.377, 1.413), rotate: 0,
  id: 'oled_iref_res'
})
const oled_vcomh_cap_cap = board.add(C_1206_3216Metric, {
  translate: pt(0.843, 1.430), rotate: 0,
  id: 'oled_vcomh_cap_cap'
})
const oled_vdd_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.533, 1.413), rotate: 0,
  id: 'oled_vdd_cap1_cap'
})
const oled_vdd_cap2_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.039, 1.423), rotate: 0,
  id: 'oled_vdd_cap2_cap'
})
const oled_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.689, 1.413), rotate: 0,
  id: 'oled_vcc_cap1_cap'
})
const oled_vcc_cap2_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.213, 1.423), rotate: 0,
  id: 'oled_vcc_cap2_cap'
})
const buck_rc_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(5.159, 4.213), rotate: 0,
  id: 'buck_rc_rc_r'
})
const buck_rc_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(5.159, 4.309), rotate: 0,
  id: 'buck_rc_rc_c'
})
const boost_rc_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(5.394, 4.213), rotate: 0,
  id: 'boost_rc_rc_r'
})
const boost_rc_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(5.394, 4.309), rotate: 0,
  id: 'boost_rc_rc_c'
})
const conv_comp_ic = board.add(SOT_353_SC_70_5, {
  translate: pt(2.446, 4.239), rotate: 0,
  id: 'conv_comp_ic'
})
const conv_comp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.441, 4.362), rotate: 0,
  id: 'conv_comp_vdd_cap_cap'
})
const comp_ref_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(5.628, 4.213), rotate: 0,
  id: 'comp_ref_div_top_res'
})
const comp_ref_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(5.628, 4.309), rotate: 0,
  id: 'comp_ref_div_bottom_res'
})
const comp_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(4.690, 4.213), rotate: 0,
  id: 'comp_sense_div_top_res'
})
const comp_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(4.690, 4.309), rotate: 0,
  id: 'comp_sense_div_bottom_res'
})
const conv_latch_ic = board.add(VSSOP_8_2_4x2_1mm_P0_5mm, {
  translate: pt(2.713, 4.235), rotate: 0,
  id: 'conv_latch_ic'
})
const conv_latch_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.685, 4.354), rotate: 0,
  id: 'conv_latch_vdd_cap_cap'
})
const conv_en_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(5.221, 4.594), rotate: 0,
  id: 'conv_en_pull_res'
})
const comp_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(4.752, 4.594), rotate: 0,
  id: 'comp_pull_res'
})
const pass_temp_ic = board.add(SOT_563, {
  translate: pt(3.455, 4.227), rotate: 0,
  id: 'pass_temp_ic'
})
const pass_temp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.460, 4.339), rotate: 0,
  id: 'pass_temp_vdd_cap_cap'
})
const conv_temp_ic = board.add(SOT_563, {
  translate: pt(3.220, 4.227), rotate: 0,
  id: 'conv_temp_ic'
})
const conv_temp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.225, 4.339), rotate: 0,
  id: 'conv_temp_vdd_cap_cap'
})
const conv_sense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(4.924, 4.213), rotate: 0,
  id: 'conv_sense_div_top_res'
})
const conv_sense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(4.924, 4.309), rotate: 0,
  id: 'conv_sense_div_bottom_res'
})
const ioe_ic = board.add(TSSOP_16_4_4x5mm_P0_65mm, {
  translate: pt(2.121, 3.833), rotate: 0,
  id: 'ioe_ic'
})
const ioe_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.028, 4.010), rotate: 0,
  id: 'ioe_vdd_cap_cap'
})
const enc_package = board.add(RotaryEncoder_Bourns_PEC11S, {
  translate: pt(3.758, 2.158), rotate: 0,
  id: 'enc_package'
})
const dir_package = board.add(DirectionSwitch_Alps_SKRH, {
  translate: pt(2.676, 3.330), rotate: 0,
  id: 'dir_package'
})
const rgb_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(2.033, 4.239), rotate: 0,
  id: 'rgb_package'
})
const rgb_red_res = board.add(R_0603_1608Metric, {
  translate: pt(2.172, 4.213), rotate: 0,
  id: 'rgb_red_res'
})
const rgb_green_res = board.add(R_0603_1608Metric, {
  translate: pt(2.050, 4.362), rotate: 0,
  id: 'rgb_green_res'
})
const rgb_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(2.206, 4.362), rotate: 0,
  id: 'rgb_blue_res'
})
const qwiic_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 4.594), rotate: 0,
  id: 'qwiic_pull_scl_res_res'
})
const qwiic_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(0.528, 4.691), rotate: 0,
  id: 'qwiic_pull_sda_res_res'
})
const qwiic_conn = board.add(JST_SH_SM04B_SRSS_TB_1x04_1MP_P1_00mm_Horizontal, {
  translate: pt(1.061, 4.313), rotate: 0,
  id: 'qwiic_conn'
})
const dutio_conn = board.add(PinHeader_1x03_P2_54mm_Horizontal, {
  translate: pt(0.071, 3.995), rotate: 0,
  id: 'dutio_conn'
})
const touch_duck = board.add(Symbol_DucklingSolid, {
  translate: pt(5.901, 4.566), rotate: 0,
  id: 'touch_duck'
})
const fan_drv_pre = board.add(SOT_23, {
  translate: pt(4.104, 3.792), rotate: 0,
  id: 'fan_drv_pre'
})
const fan_drv_pull = board.add(R_0603_1608Metric, {
  translate: pt(4.278, 3.927), rotate: 0,
  id: 'fan_drv_pull'
})
const fan_drv_drv = board.add(SOT_23, {
  translate: pt(4.104, 3.965), rotate: 0,
  id: 'fan_drv_drv'
})
const fan_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.699, 4.314), rotate: 0,
  id: 'fan_conn'
})
const dac_ic = board.add(MSOP_10_3x3mm_P0_5mm, {
  translate: pt(0.730, 3.794), rotate: 0,
  id: 'dac_ic'
})
const dac_vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.663, 3.931), rotate: 0,
  id: 'dac_vdd_cap_0__cap'
})
const dac_vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(0.961, 3.764), rotate: 0,
  id: 'dac_vdd_cap_1__cap'
})
const dac_out_cap_0_ = board.add(C_0603_1608Metric, {
  translate: pt(0.819, 3.931), rotate: 0,
  id: 'dac_out_cap_0_'
})
const dac_out_cap_1_ = board.add(C_0603_1608Metric, {
  translate: pt(0.974, 3.931), rotate: 0,
  id: 'dac_out_cap_1_'
})
const dac_out_cap_2_ = board.add(C_0603_1608Metric, {
  translate: pt(0.663, 4.028), rotate: 0,
  id: 'dac_out_cap_2_'
})
const dac_ferrite_fb = board.add(L_0603_1608Metric, {
  translate: pt(4.986, 4.594), rotate: 0,
  id: 'dac_ferrite_fb'
})
const tp_cv_conn = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(4.533, 3.824), rotate: 0,
  id: 'tp_cv_conn'
})
const tp_cv_res = board.add(R_0603_1608Metric, {
  translate: pt(4.512, 3.990), rotate: 0,
  id: 'tp_cv_res'
})
const tp_cisrc_conn = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.108, 3.824), rotate: 0,
  id: 'tp_cisrc_conn'
})
const tp_cisrc_res = board.add(R_0603_1608Metric, {
  translate: pt(5.087, 3.990), rotate: 0,
  id: 'tp_cisrc_res'
})
const tp_cisnk_conn = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(4.821, 3.824), rotate: 0,
  id: 'tp_cisnk_conn'
})
const tp_cisnk_res = board.add(R_0603_1608Metric, {
  translate: pt(4.800, 3.990), rotate: 0,
  id: 'tp_cisnk_res'
})
const adc_ic = board.add(TSSOP_20_4_4x6_5mm_P0_65mm, {
  translate: pt(1.344, 3.253), rotate: 0,
  id: 'adc_ic'
})
const adc_avdd_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.260), rotate: 0,
  id: 'adc_avdd_res_res'
})
const adc_dvdd_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.593, 3.357), rotate: 0,
  id: 'adc_dvdd_res_res'
})
const adc_avdd_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.459), rotate: 0,
  id: 'adc_avdd_cap_0_cap'
})
const adc_avdd_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.406, 3.459), rotate: 0,
  id: 'adc_avdd_cap_1_cap'
})
const adc_dvdd_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.562, 3.459), rotate: 0,
  id: 'adc_dvdd_cap_0_cap'
})
const adc_dvdd_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.250, 3.556), rotate: 0,
  id: 'adc_dvdd_cap_1_cap'
})
const adc_vref_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.602, 3.154), rotate: 0,
  id: 'adc_vref_cap_cap'
})
const tp_vcen_conn = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.683, 3.824), rotate: 0,
  id: 'tp_vcen_conn'
})
const tp_vcen_res = board.add(R_0603_1608Metric, {
  translate: pt(5.662, 3.990), rotate: 0,
  id: 'tp_vcen_res'
})
const vcen_rc_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 4.594), rotate: 0,
  id: 'vcen_rc_rc_r'
})
const vcen_rc_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.293, 4.691), rotate: 0,
  id: 'vcen_rc_rc_c'
})
const tp_mi_conn = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.970, 3.824), rotate: 0,
  id: 'tp_mi_conn'
})
const tp_mi_res = board.add(R_0603_1608Metric, {
  translate: pt(5.949, 3.990), rotate: 0,
  id: 'tp_mi_res'
})
const mi_rc_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(4.455, 4.213), rotate: 0,
  id: 'mi_rc_rc_r'
})
const mi_rc_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(4.455, 4.309), rotate: 0,
  id: 'mi_rc_rc_c'
})
const tp_mv_conn = board.add(U_FL_Hirose_U_FL_R_SMT_1_Vertical, {
  translate: pt(5.396, 3.824), rotate: 0,
  id: 'tp_mv_conn'
})
const tp_mv_res = board.add(R_0603_1608Metric, {
  translate: pt(5.374, 3.990), rotate: 0,
  id: 'tp_mv_res'
})
const mv_rc_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(5.863, 4.213), rotate: 0,
  id: 'mv_rc_rc_r'
})
const mv_rc_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(5.863, 4.309), rotate: 0,
  id: 'mv_rc_rc_c'
})
const outn = board.add(CalTest_CT3151, {
  translate: pt(5.152, 2.199), rotate: 0,
  id: 'outn'
})
const outp = board.add(CalTest_CT3151, {
  translate: pt(0.882, 3.500), rotate: 0,
  id: 'outp'
})
const outd = board.add(PinHeader_1x02_P2_54mm_Horizontal, {
  translate: pt(3.707, 4.355), rotate: 0,
  id: 'outd'
})
const vimeas_amps_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.706, 3.831), rotate: 0,
  id: 'vimeas_amps_ic'
})
const vimeas_amps_vdd_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.627, 4.016), rotate: 0,
  id: 'vimeas_amps_vdd_cap_cap'
})
const ampdmeas_amps_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.296, 3.831), rotate: 0,
  id: 'ampdmeas_amps_ic'
})
const ampdmeas_amps_vdd_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.218, 4.016), rotate: 0,
  id: 'ampdmeas_amps_vdd_cap_cap'
})
const cd_amps_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.765, 3.831), rotate: 0,
  id: 'cd_amps_ic'
})
const cd_amps_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.678, 4.006), rotate: 0,
  id: 'cd_amps_vdd_cap_cap'
})
const cv_amps_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(3.356, 3.831), rotate: 0,
  id: 'cv_amps_ic'
})
const cv_amps_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.268, 4.006), rotate: 0,
  id: 'cv_amps_vdd_cap_cap'
})
const ci_amps_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.946, 3.831), rotate: 0,
  id: 'ci_amps_ic'
})
const ci_amps_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.859, 4.006), rotate: 0,
  id: 'ci_amps_vdd_cap_cap'
})
const cintref_amps_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(2.537, 3.831), rotate: 0,
  id: 'cintref_amps_ic'
})
const cintref_amps_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.449, 4.006), rotate: 0,
  id: 'cintref_amps_vdd_cap_cap'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(6.273818897637796, 4.838188976377953);
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


