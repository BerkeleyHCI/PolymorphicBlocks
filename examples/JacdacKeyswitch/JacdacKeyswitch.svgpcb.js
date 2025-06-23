const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.862, 1.038), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.902, 1.038), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.862, 1.078), rotate: 0,
  id: 'jlc_th_th3'
})
const edge_conn = board.add(JD_PEC_02_Prerouted_recessed, {
  translate: pt(0.113, 0.883), rotate: 0,
  id: 'edge_conn'
})
const edge_status_led_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 0.718), rotate: 0,
  id: 'edge_status_led_package'
})
const edge_status_led_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.815), rotate: 0,
  id: 'edge_status_led_res'
})
const edge_tvs_jd_pwr_diode = board.add(D_0402_1005Metric, {
  translate: pt(0.193, 0.805), rotate: 0,
  id: 'edge_tvs_jd_pwr_diode'
})
const edge_tvs_jd_data_diode = board.add(D_0402_1005Metric, {
  translate: pt(0.037, 0.902), rotate: 0,
  id: 'edge_tvs_jd_data_diode'
})
const jd_mh1 = board.add(jacdac_hole_DATA_notched_MH1, {
  translate: pt(1.020, 1.038), rotate: 0,
  id: 'jd_mh1'
})
const jd_mh2 = board.add(jacdac_hole_GND_MH2, {
  translate: pt(1.059, 1.038), rotate: 0,
  id: 'jd_mh2'
})
const jd_mh3 = board.add(jacdac_hole_PWR_MH3, {
  translate: pt(1.098, 1.038), rotate: 0,
  id: 'jd_mh3'
})
const jd_mh4 = board.add(jacdac_hole_GND_MH4, {
  translate: pt(1.138, 1.038), rotate: 0,
  id: 'jd_mh4'
})
const edge2_conn = board.add(JD_PEC_02_Prerouted_recessed, {
  translate: pt(0.460, 0.883), rotate: 0,
  id: 'edge2_conn'
})
const edge2_status_led_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.406, 0.718), rotate: 0,
  id: 'edge2_status_led_package'
})
const edge2_status_led_res = board.add(R_0603_1608Metric, {
  translate: pt(0.406, 0.815), rotate: 0,
  id: 'edge2_status_led_res'
})
const edge2_tvs_jd_pwr_diode = board.add(D_0402_1005Metric, {
  translate: pt(0.540, 0.805), rotate: 0,
  id: 'edge2_tvs_jd_pwr_diode'
})
const edge2_tvs_jd_data_diode = board.add(D_0402_1005Metric, {
  translate: pt(0.384, 0.902), rotate: 0,
  id: 'edge2_tvs_jd_data_diode'
})
const tp_gnd_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.659, 1.091), rotate: 0,
  id: 'tp_gnd_tp'
})
const tp_jd_pwr_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.085, 1.091), rotate: 0,
  id: 'tp_jd_pwr_tp'
})
const reg_3v3_ic = board.add(SOT_23_5, {
  translate: pt(0.775, 0.756), rotate: 0,
  id: 'reg_3v3_ic'
})
const reg_3v3_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.753, 0.891), rotate: 0,
  id: 'reg_3v3_in_cap_cap'
})
const reg_3v3_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.909, 0.891), rotate: 0,
  id: 'reg_3v3_out_cap_cap'
})
const tp_3v3_tp = board.add(TestPoint_Keystone_5015_Micro_Minature, {
  translate: pt(0.372, 1.091), rotate: 0,
  id: 'tp_3v3_tp'
})
const mcu_swd_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.870, 0.325), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(QFN_28_4x4mm_P0_5mm, {
  translate: pt(0.836, 0.104), rotate: 0,
  id: 'mcu_ic'
})
const mcu_pwr_cap0_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.114, 0.285), rotate: 0,
  id: 'mcu_pwr_cap0_cap'
})
const mcu_pwr_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.791, 0.472), rotate: 0,
  id: 'mcu_pwr_cap1_cap'
})
const sw_package = board.add(SW_Hotswap_Kailh_MX, {
  translate: pt(0.307, 0.285), rotate: 0,
  id: 'sw_package'
})
const rgb_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.126, 0.744), rotate: 0,
  id: 'rgb_package'
})
const rgb_red_res = board.add(R_0603_1608Metric, {
  translate: pt(1.265, 0.718), rotate: 0,
  id: 'rgb_red_res'
})
const rgb_green_res = board.add(R_0603_1608Metric, {
  translate: pt(1.143, 0.867), rotate: 0,
  id: 'rgb_green_res'
})
const rgb_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(1.299, 0.867), rotate: 0,
  id: 'rgb_blue_res'
})
const jd_if_ferrite = board.add(L_0603_1608Metric, {
  translate: pt(1.357, 0.143), rotate: 0,
  id: 'jd_if_ferrite'
})
const jd_if_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(1.513, 0.143), rotate: 0,
  id: 'jd_if_rc_r'
})
const jd_if_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.357, 0.240), rotate: 0,
  id: 'jd_if_rc_c'
})
const jd_if_clamp_hi = board.add(D_SOD_323, {
  translate: pt(1.363, 0.037), rotate: 0,
  id: 'jd_if_clamp_hi'
})
const jd_if_clamp_lo = board.add(D_SOD_323, {
  translate: pt(1.528, 0.037), rotate: 0,
  id: 'jd_if_clamp_lo'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.709448818897638, 1.2625984251968505);
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


