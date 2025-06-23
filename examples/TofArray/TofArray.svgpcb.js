const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.098, 1.682), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.137, 1.682), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(2.098, 1.721), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(2.034, 0.165), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(1.883, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(2.039, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const can_conn = board.add(Molex_SL_171971_0005_1x05_P2_54mm_Vertical, {
  translate: pt(1.539, 0.973), rotate: 0,
  id: 'can_conn'
})
const tp_vusb_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.659, 1.735), rotate: 0,
  id: 'tp_vusb_tp'
})
const tp_gnd_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(2.172, 1.365), rotate: 0,
  id: 'tp_gnd_tp'
})
const reg_3v3_ic = board.add(SOT_223_3_TabPin2, {
  translate: pt(0.173, 0.935), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.231, 1.145), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 1.155), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.735), rotate: 0,
  id: 'tp_3v3_tp'
})
const prot_3v3_diode = board.add(D_SOD_323, {
  translate: pt(1.213, 1.719), rotate: 0,
  id: 'prot_3v3_diode'
})
const mcu_swd_conn = board.add(Tag_Connect_TC2050_IDC_FP_2x05_P1_27mm_Vertical, {
  translate: pt(0.661, 0.167), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'mcu_ic'
})
const mcu_pwr_cap_0__cap = board.add(C_0805_2012Metric, {
  translate: pt(0.272, 0.483), rotate: 0,
  id: 'mcu_pwr_cap_0__cap'
})
const mcu_pwr_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.436, 0.474), rotate: 0,
  id: 'mcu_pwr_cap_1__cap'
})
const mcu_pwr_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.592, 0.474), rotate: 0,
  id: 'mcu_pwr_cap_2__cap'
})
const mcu_pwr_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.748, 0.474), rotate: 0,
  id: 'mcu_pwr_cap_3__cap'
})
const mcu_vdda_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.647), rotate: 0,
  id: 'mcu_vdda_cap_0_cap'
})
const mcu_vdda_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.647), rotate: 0,
  id: 'mcu_vdda_cap_1_cap'
})
const mcu_usb_pull_dp = board.add(R_0603_1608Metric, {
  translate: pt(0.370, 0.647), rotate: 0,
  id: 'mcu_usb_pull_dp'
})
const mcu_crystal_package = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.083, 0.512), rotate: 0,
  id: 'mcu_crystal_package'
})
const mcu_crystal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.647), rotate: 0,
  id: 'mcu_crystal_cap_a'
})
const mcu_crystal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.647), rotate: 0,
  id: 'mcu_crystal_cap_b'
})
const sw1_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(0.742, 1.424), rotate: 0,
  id: 'sw1_package'
})
const leds_led_0__package = board.add(LED_0603_1608Metric, {
  translate: pt(2.233, 0.823), rotate: 0,
  id: 'leds_led_0__package'
})
const leds_led_1__package = board.add(LED_0603_1608Metric, {
  translate: pt(2.389, 0.823), rotate: 0,
  id: 'leds_led_1__package'
})
const leds_led_2__package = board.add(LED_0603_1608Metric, {
  translate: pt(2.233, 0.920), rotate: 0,
  id: 'leds_led_2__package'
})
const leds_led_3__package = board.add(LED_0603_1608Metric, {
  translate: pt(2.389, 0.920), rotate: 0,
  id: 'leds_led_3__package'
})
const leds_led_4__package = board.add(LED_0603_1608Metric, {
  translate: pt(2.233, 1.017), rotate: 0,
  id: 'leds_led_4__package'
})
const tof_elt_0__ic = board.add(ST_VL53L0X, {
  translate: pt(1.063, 0.057), rotate: 0,
  id: 'tof_elt_0__ic'
})
const tof_elt_0__vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.025, 0.452), rotate: 0,
  id: 'tof_elt_0__vdd_cap_0__cap'
})
const tof_elt_0__vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(1.498, 0.192), rotate: 0,
  id: 'tof_elt_0__vdd_cap_1__cap'
})
const tof_elt_1__ic = board.add(ST_VL53L0X, {
  translate: pt(1.295, 0.057), rotate: 0,
  id: 'tof_elt_1__ic'
})
const tof_elt_1__vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.181, 0.452), rotate: 0,
  id: 'tof_elt_1__vdd_cap_0__cap'
})
const tof_elt_1__vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(1.033, 0.346), rotate: 0,
  id: 'tof_elt_1__vdd_cap_1__cap'
})
const tof_elt_2__ic = board.add(ST_VL53L0X, {
  translate: pt(1.528, 0.057), rotate: 0,
  id: 'tof_elt_2__ic'
})
const tof_elt_2__vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.337, 0.452), rotate: 0,
  id: 'tof_elt_2__vdd_cap_0__cap'
})
const tof_elt_2__vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(1.207, 0.346), rotate: 0,
  id: 'tof_elt_2__vdd_cap_1__cap'
})
const tof_elt_3__ic = board.add(ST_VL53L0X, {
  translate: pt(1.063, 0.211), rotate: 0,
  id: 'tof_elt_3__ic'
})
const tof_elt_3__vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.493, 0.452), rotate: 0,
  id: 'tof_elt_3__vdd_cap_0__cap'
})
const tof_elt_3__vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(1.380, 0.346), rotate: 0,
  id: 'tof_elt_3__vdd_cap_1__cap'
})
const tof_elt_4__ic = board.add(ST_VL53L0X, {
  translate: pt(1.295, 0.211), rotate: 0,
  id: 'tof_elt_4__ic'
})
const tof_elt_4__vdd_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.648, 0.452), rotate: 0,
  id: 'tof_elt_4__vdd_cap_0__cap'
})
const tof_elt_4__vdd_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(1.553, 0.346), rotate: 0,
  id: 'tof_elt_4__vdd_cap_1__cap'
})
const i2c_pull_scl_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.710, 1.341), rotate: 0,
  id: 'i2c_pull_scl_res_res'
})
const i2c_pull_sda_res_res = board.add(R_0603_1608Metric, {
  translate: pt(1.710, 1.437), rotate: 0,
  id: 'i2c_pull_sda_res_res'
})
const i2c_tp_tp_scl_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.365), rotate: 0,
  id: 'i2c_tp_tp_scl_tp'
})
const i2c_tp_tp_sda_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.511), rotate: 0,
  id: 'i2c_tp_tp_sda_tp'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(1.793, 1.749), rotate: 0,
  id: 'usb_esd'
})
const tp_can_tp_txd_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.365), rotate: 0,
  id: 'tp_can_tp_txd_tp'
})
const tp_can_tp_rxd_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.511), rotate: 0,
  id: 'tp_can_tp_rxd_tp'
})
const xcvr_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(1.157, 0.900), rotate: 0,
  id: 'xcvr_ic'
})
const xcvr_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.069, 1.074), rotate: 0,
  id: 'xcvr_vdd_cap_cap'
})
const can_esd = board.add(SOT_23, {
  translate: pt(1.983, 1.749), rotate: 0,
  id: 'can_esd'
})
const tp_spk_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.735), rotate: 0,
  id: 'tp_spk_tp'
})
const spk_dac_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(1.476, 1.341), rotate: 0,
  id: 'spk_dac_rc_r'
})
const spk_dac_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.476, 1.437), rotate: 0,
  id: 'spk_dac_rc_c'
})
const tp_spk_in_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.947, 1.735), rotate: 0,
  id: 'tp_spk_in_tp'
})
const spk_drv_ic = board.add(MSOP_8_1EP_3x3mm_P0_65mm_EP1_68x1_88mm_ThermalVias, {
  translate: pt(0.587, 0.863), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_pwr_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.523, 1.000), rotate: 0,
  id: 'spk_drv_pwr_cap_cap'
})
const spk_drv_bulk_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.817, 0.832), rotate: 0,
  id: 'spk_drv_bulk_cap_cap'
})
const spk_drv_inp_res = board.add(R_0603_1608Metric, {
  translate: pt(0.679, 1.000), rotate: 0,
  id: 'spk_drv_inp_res'
})
const spk_drv_inp_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.835, 1.000), rotate: 0,
  id: 'spk_drv_inp_cap'
})
const spk_drv_inn_res = board.add(R_0603_1608Metric, {
  translate: pt(0.523, 1.096), rotate: 0,
  id: 'spk_drv_inn_res'
})
const spk_drv_inn_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.679, 1.096), rotate: 0,
  id: 'spk_drv_inn_cap'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.124, 1.442), rotate: 0,
  id: 'spk_conn'
})
const res1 = board.add(R_Array_Concave_4x0603, {
  translate: pt(1.455, 1.756), rotate: 0,
  id: 'res1'
})
const res2 = board.add(R_Array_Concave_4x0603, {
  translate: pt(1.617, 1.756), rotate: 0,
  id: 'res2'
})
const rgb_device_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.928, 1.367), rotate: 0,
  id: 'rgb_device_package'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.565748031496063, 1.9062992125984253);
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


