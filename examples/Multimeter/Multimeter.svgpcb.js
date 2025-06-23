const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.913, 2.557), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.952, 2.557), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.913, 2.597), rotate: 0,
  id: 'jlc_th_th3'
})
const bat = board.add(BatteryHolder_Keystone_2460_1xAA, {
  translate: pt(1.063, 0.343), rotate: 0,
  id: 'bat'
})
const data_usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(2.365, 1.237), rotate: 0,
  id: 'data_usb_conn'
})
const data_usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(2.213, 1.492), rotate: 0,
  id: 'data_usb_cc_pull_cc1_res'
})
const data_usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(2.369, 1.492), rotate: 0,
  id: 'data_usb_cc_pull_cc2_res'
})
const gate_pwr_gate_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(3.316, 0.466), rotate: 0,
  id: 'gate_pwr_gate_pull_res'
})
const gate_pwr_gate_pwr_fet = board.add(SOT_23, {
  translate: pt(3.707, 0.067), rotate: 0,
  id: 'gate_pwr_gate_pwr_fet'
})
const gate_pwr_gate_amp_res = board.add(R_0603_1608Metric, {
  translate: pt(3.472, 0.466), rotate: 0,
  id: 'gate_pwr_gate_amp_res'
})
const gate_pwr_gate_amp_fet = board.add(SOT_23, {
  translate: pt(3.333, 0.331), rotate: 0,
  id: 'gate_pwr_gate_amp_fet'
})
const gate_pwr_gate_ctl_diode = board.add(D_SOD_323, {
  translate: pt(3.512, 0.301), rotate: 0,
  id: 'gate_pwr_gate_ctl_diode'
})
const gate_pwr_gate_btn_diode = board.add(D_SOD_323, {
  translate: pt(3.677, 0.301), rotate: 0,
  id: 'gate_pwr_gate_btn_diode'
})
const gate_btn_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(3.425, 0.112), rotate: 0,
  id: 'gate_btn_package'
})
const reg_5v_ic = board.add(SOT_23_5, {
  translate: pt(2.770, 1.752), rotate: 0,
  id: 'reg_5v_ic'
})
const reg_5v_power_path_inductor = board.add(L_0603_1608Metric, {
  translate: pt(2.920, 1.887), rotate: 0,
  id: 'reg_5v_power_path_inductor'
})
const reg_5v_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.957, 1.724), rotate: 0,
  id: 'reg_5v_power_path_in_cap_cap'
})
const reg_5v_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(2.756, 1.897), rotate: 0,
  id: 'reg_5v_power_path_out_cap_cap'
})
const reg_5v_ce_res_res = board.add(R_0603_1608Metric, {
  translate: pt(2.747, 2.004), rotate: 0,
  id: 'reg_5v_ce_res_res'
})
const tp_5v_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.704, 2.611), rotate: 0,
  id: 'tp_5v_tp'
})
const prot_5v_diode = board.add(D_MiniMELF, {
  translate: pt(2.011, 2.601), rotate: 0,
  id: 'prot_5v_diode'
})
const reg_3v3_ic = board.add(SOT_23_5, {
  translate: pt(1.030, 2.276), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.008, 2.411), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.164, 2.411), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.129, 2.611), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(2.297, 2.595), rotate: 0,
  id: 'prot_3v3_diode'
})
const reg_analog_ic = board.add(SOT_23_5, {
  translate: pt(0.360, 2.276), rotate: 0,
  id: 'reg_analog_ic'
})
const reg_analog_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.338, 2.411), rotate: 0,
  id: 'reg_analog_in_cap_cap'
})
const reg_analog_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.494, 2.411), rotate: 0,
  id: 'reg_analog_out_cap_cap'
})
const tp_analog_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.841, 2.611), rotate: 0,
  id: 'tp_analog_tp'
})
const prot_analog_diode = board.add(D_SOD_323, {
  translate: pt(2.541, 2.595), rotate: 0,
  id: 'prot_analog_diode'
})
const mcu_ic = board.add(Raytac_MDBT50Q, {
  translate: pt(0.226, 0.325), rotate: 0,
  id: 'mcu_ic'
})
const mcu_swd_conn = board.add(Tag_Connect_TC2050_IDC_NL_2x05_P1_27mm_Vertical, {
  translate: pt(0.245, 0.822), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_vcc_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.596, 0.728), rotate: 0,
  id: 'mcu_vcc_cap_cap'
})
const mcu_usb_res_res_dp = board.add(R_0603_1608Metric, {
  translate: pt(0.588, 0.834), rotate: 0,
  id: 'mcu_usb_res_res_dp'
})
const mcu_usb_res_res_dm = board.add(R_0603_1608Metric, {
  translate: pt(0.744, 0.834), rotate: 0,
  id: 'mcu_usb_res_res_dm'
})
const mcu_vbus_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.770, 0.728), rotate: 0,
  id: 'mcu_vbus_cap_cap'
})
const vbatsense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(3.628, 2.237), rotate: 0,
  id: 'vbatsense_div_top_res'
})
const vbatsense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(3.628, 2.334), rotate: 0,
  id: 'vbatsense_div_bottom_res'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(2.798, 2.624), rotate: 0,
  id: 'usb_esd'
})
const rgb_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(2.921, 2.264), rotate: 0,
  id: 'rgb_package'
})
const rgb_red_res = board.add(R_0603_1608Metric, {
  translate: pt(3.060, 2.237), rotate: 0,
  id: 'rgb_red_res'
})
const rgb_green_res = board.add(R_0603_1608Metric, {
  translate: pt(2.938, 2.387), rotate: 0,
  id: 'rgb_green_res'
})
const rgb_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(3.094, 2.387), rotate: 0,
  id: 'rgb_blue_res'
})
const sw1_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.960, 2.321), rotate: 0,
  id: 'sw1_package'
})
const sw2_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.507, 2.321), rotate: 0,
  id: 'sw2_package'
})
const lcd_device_conn = board.add(Hirose_FH12_8S_0_5SH_1x08_1MP_P0_50mm_Horizontal, {
  translate: pt(2.891, 1.265), rotate: 0,
  id: 'lcd_device_conn'
})
const lcd_led_res = board.add(R_0603_1608Metric, {
  translate: pt(2.750, 1.452), rotate: 0,
  id: 'lcd_led_res'
})
const lcd_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.906, 1.452), rotate: 0,
  id: 'lcd_vdd_cap_cap'
})
const spk_dac_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.586), rotate: 0,
  id: 'spk_dac_rc_r'
})
const spk_dac_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.683), rotate: 0,
  id: 'spk_dac_rc_c'
})
const spk_tp_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.554, 2.611), rotate: 0,
  id: 'spk_tp_tp'
})
const spk_drv_ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(3.265, 1.754), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.200, 1.891), rotate: 0,
  id: 'spk_drv_pwr_cap_cap'
})
const spk_drv_bulk_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(3.494, 1.724), rotate: 0,
  id: 'spk_drv_bulk_cap_cap'
})
const spk_drv_inp_res = board.add(R_0603_1608Metric, {
  translate: pt(3.356, 1.891), rotate: 0,
  id: 'spk_drv_inp_res'
})
const spk_drv_inp_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.512, 1.891), rotate: 0,
  id: 'spk_drv_inp_cap'
})
const spk_drv_inn_res = board.add(R_0603_1608Metric, {
  translate: pt(3.200, 1.988), rotate: 0,
  id: 'spk_drv_inn_res'
})
const spk_drv_inn_cap = board.add(C_0603_1608Metric, {
  translate: pt(3.356, 1.988), rotate: 0,
  id: 'spk_drv_inn_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(2.342, 2.339), rotate: 0,
  id: 'spk_conn'
})
const ref_div_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.586), rotate: 0,
  id: 'ref_div_div_top_res'
})
const ref_div_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.293, 2.683), rotate: 0,
  id: 'ref_div_div_bottom_res'
})
const ref_buf_amp_ic = board.add(SOT_23_6, {
  translate: pt(0.751, 2.276), rotate: 0,
  id: 'ref_buf_amp_ic'
})
const ref_buf_amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.728, 2.411), rotate: 0,
  id: 'ref_buf_amp_vdd_cap_cap'
})
const inn = board.add(CLIFF_FCR7350, {
  translate: pt(1.083, 1.927), rotate: 0,
  id: 'inn'
})
const inn_mux_device_ic = board.add(SOT_363_SC_70_6, {
  translate: pt(2.698, 2.264), rotate: 0,
  id: 'inn_mux_device_ic'
})
const inn_mux_device_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.694, 2.387), rotate: 0,
  id: 'inn_mux_device_vdd_cap_cap'
})
const inp = board.add(CLIFF_FCR7350, {
  translate: pt(2.427, 1.927), rotate: 0,
  id: 'inp'
})
const measure_res = board.add(R_2512_6332Metric, {
  translate: pt(0.150, 1.148), rotate: 0,
  id: 'measure_res'
})
const measure_range_switch_sw_0_0__ic = board.add(SOT_363_SC_70_6, {
  translate: pt(0.403, 1.128), rotate: 0,
  id: 'measure_range_switch_sw_0_0__ic'
})
const measure_range_switch_sw_0_0__vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.389, 1.292), rotate: 0,
  id: 'measure_range_switch_sw_0_0__vdd_cap_cap'
})
const measure_range_switch_sw_0_1__ic = board.add(SOT_363_SC_70_6, {
  translate: pt(0.063, 1.318), rotate: 0,
  id: 'measure_range_switch_sw_0_1__ic'
})
const measure_range_switch_sw_0_1__vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.441), rotate: 0,
  id: 'measure_range_switch_sw_0_1__vdd_cap_cap'
})
const measure_range_switch_sw_1_0__ic = board.add(SOT_363_SC_70_6, {
  translate: pt(0.228, 1.318), rotate: 0,
  id: 'measure_range_switch_sw_1_0__ic'
})
const measure_range_switch_sw_1_0__vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 1.441), rotate: 0,
  id: 'measure_range_switch_sw_1_0__vdd_cap_cap'
})
const measure_range_res_0_ = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 1.441), rotate: 0,
  id: 'measure_range_res_0_'
})
const measure_range_res_1_ = board.add(R_0603_1608Metric, {
  translate: pt(0.526, 1.441), rotate: 0,
  id: 'measure_range_res_1_'
})
const measure_range_res_2_ = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.538), rotate: 0,
  id: 'measure_range_res_2_'
})
const measure_buffer_amp_ic = board.add(SOT_23_6, {
  translate: pt(0.081, 2.276), rotate: 0,
  id: 'measure_buffer_amp_ic'
})
const measure_buffer_amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 2.411), rotate: 0,
  id: 'measure_buffer_amp_vdd_cap_cap'
})
const tp_measure_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(1.416, 2.611), rotate: 0,
  id: 'tp_measure_tp'
})
const adc_ic = board.add(TSSOP_20_4_4x6_5mm_P0_65mm, {
  translate: pt(1.712, 1.210), rotate: 0,
  id: 'adc_ic'
})
const adc_avdd_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.961, 1.218), rotate: 0,
  id: 'adc_avdd_res_res'
})
const adc_dvdd_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.961, 1.315), rotate: 0,
  id: 'adc_dvdd_res_res'
})
const adc_avdd_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.619, 1.416), rotate: 0,
  id: 'adc_avdd_cap_0_cap'
})
const adc_avdd_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.775, 1.416), rotate: 0,
  id: 'adc_avdd_cap_1_cap'
})
const adc_dvdd_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.931, 1.416), rotate: 0,
  id: 'adc_dvdd_cap_0_cap'
})
const adc_dvdd_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.619, 1.513), rotate: 0,
  id: 'adc_dvdd_cap_1_cap'
})
const adc_vref_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.970, 1.111), rotate: 0,
  id: 'adc_vref_cap_cap'
})
const driver_fet = board.add(SOT_23, {
  translate: pt(1.093, 1.139), rotate: 0,
  id: 'driver_fet'
})
const driver_amp_ic = board.add(SOT_23_6, {
  translate: pt(1.289, 1.139), rotate: 0,
  id: 'driver_amp_ic'
})
const driver_amp_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.761, 1.428), rotate: 0,
  id: 'driver_amp_vdd_cap_cap'
})
const driver_range_switch_sw_0_0__ic = board.add(SOT_363_SC_70_6, {
  translate: pt(0.765, 1.305), rotate: 0,
  id: 'driver_range_switch_sw_0_0__ic'
})
const driver_range_switch_sw_0_0__vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.917, 1.428), rotate: 0,
  id: 'driver_range_switch_sw_0_0__vdd_cap_cap'
})
const driver_range_switch_sw_0_1__ic = board.add(SOT_363_SC_70_6, {
  translate: pt(0.931, 1.305), rotate: 0,
  id: 'driver_range_switch_sw_0_1__ic'
})
const driver_range_switch_sw_0_1__vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.072, 1.428), rotate: 0,
  id: 'driver_range_switch_sw_0_1__vdd_cap_cap'
})
const driver_range_switch_sw_1_0__ic = board.add(SOT_363_SC_70_6, {
  translate: pt(1.096, 1.305), rotate: 0,
  id: 'driver_range_switch_sw_1_0__ic'
})
const driver_range_switch_sw_1_0__vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.228, 1.428), rotate: 0,
  id: 'driver_range_switch_sw_1_0__vdd_cap_cap'
})
const driver_range_res_0_ = board.add(R_0603_1608Metric, {
  translate: pt(1.384, 1.428), rotate: 0,
  id: 'driver_range_res_0_'
})
const driver_range_res_1_ = board.add(R_0603_1608Metric, {
  translate: pt(0.761, 1.525), rotate: 0,
  id: 'driver_range_res_1_'
})
const driver_range_res_2_ = board.add(R_0603_1608Metric, {
  translate: pt(0.917, 1.525), rotate: 0,
  id: 'driver_range_res_2_'
})
const driver_range_res_3_ = board.add(R_0603_1608Metric, {
  translate: pt(1.072, 1.525), rotate: 0,
  id: 'driver_range_res_3_'
})
const driver_sw_device_ic = board.add(SOT_363_SC_70_6, {
  translate: pt(1.261, 1.305), rotate: 0,
  id: 'driver_sw_device_ic'
})
const driver_sw_device_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.228, 1.525), rotate: 0,
  id: 'driver_sw_device_vdd_cap_cap'
})
const driver_diode = board.add(D_SMA, {
  translate: pt(0.841, 1.141), rotate: 0,
  id: 'driver_diode'
})
const driver_dac_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(3.328, 2.367), rotate: 0,
  id: 'driver_dac_rc_r'
})
const driver_dac_rc_c = board.add(C_1206_3216Metric, {
  translate: pt(3.361, 2.254), rotate: 0,
  id: 'driver_dac_rc_c'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(3.9010236220472447, 2.82992125984252);
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


