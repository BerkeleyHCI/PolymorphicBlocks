const board = new PCB();

const mcu = board.add(Nucleo32, {
  translate: pt(0.365, 0.990), rotate: 0,
  id: 'mcu'
})
const spk_drv_ic = board.add(SOIC_8_3_9x4_9mm_P1_27mm, {
  translate: pt(0.915, 1.240), rotate: 0,
  id: 'spk_drv_ic'
})
const spk_drv_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.158, 1.163), rotate: 0,
  id: 'spk_drv_in_cap_cap'
})
const spk_drv_byp_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.158, 1.259), rotate: 0,
  id: 'spk_drv_byp_cap'
})
const spk_drv_sig_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.828, 1.415), rotate: 0,
  id: 'spk_drv_sig_cap'
})
const spk_drv_sig_res = board.add(R_0603_1608Metric, {
  translate: pt(0.983, 1.415), rotate: 0,
  id: 'spk_drv_sig_res'
})
const spk_drv_fb_res = board.add(R_0603_1608Metric, {
  translate: pt(1.139, 1.415), rotate: 0,
  id: 'spk_drv_fb_res'
})
const spk_conn = board.add(JST_PH_B2B_PH_K_1x02_P2_00mm_Vertical, {
  translate: pt(1.431, 1.264), rotate: 0,
  id: 'spk_conn'
})
const rgb_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.766, 1.189), rotate: 0,
  id: 'rgb_package'
})
const rgb_red_res = board.add(R_0603_1608Metric, {
  translate: pt(1.905, 1.163), rotate: 0,
  id: 'rgb_red_res'
})
const rgb_green_res = board.add(R_0603_1608Metric, {
  translate: pt(1.783, 1.312), rotate: 0,
  id: 'rgb_green_res'
})
const rgb_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(1.939, 1.312), rotate: 0,
  id: 'rgb_blue_res'
})
const sw_package = board.add(SW_Push_SPST_NO_Alps_SKRK, {
  translate: pt(2.223, 1.201), rotate: 0,
  id: 'sw_package'
})
const sw_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(1.062, 1.590), rotate: 0,
  id: 'sw_pull_res'
})
const btn_0_ = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.395, 0.937), rotate: 0,
  id: 'btn_0_'
})
const btn_pull_0__res = board.add(R_0603_1608Metric, {
  translate: pt(0.828, 1.590), rotate: 0,
  id: 'btn_pull_0__res'
})
const btn_1_ = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.576, 0.937), rotate: 0,
  id: 'btn_1_'
})
const btn_pull_1__res = board.add(R_0603_1608Metric, {
  translate: pt(1.531, 1.590), rotate: 0,
  id: 'btn_pull_1__res'
})
const btn_2_ = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.757, 0.937), rotate: 0,
  id: 'btn_2_'
})
const btn_pull_2__res = board.add(R_0603_1608Metric, {
  translate: pt(1.297, 1.590), rotate: 0,
  id: 'btn_pull_2__res'
})
const btn_3_ = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.939, 0.937), rotate: 0,
  id: 'btn_3_'
})
const btn_pull_3__res = board.add(R_0603_1608Metric, {
  translate: pt(2.508, 1.163), rotate: 0,
  id: 'btn_pull_3__res'
})
const pwr_ic = board.add(SOT_23_5, {
  translate: pt(2.130, 0.634), rotate: 0,
  id: 'pwr_ic'
})
const pwr_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.284, 0.769), rotate: 0,
  id: 'pwr_fb_div_top_res'
})
const pwr_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.107, 0.875), rotate: 0,
  id: 'pwr_fb_div_bottom_res'
})
const pwr_power_path_inductor = board.add(L_0805_2012Metric, {
  translate: pt(2.118, 0.774), rotate: 0,
  id: 'pwr_power_path_inductor'
})
const pwr_power_path_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.263, 0.875), rotate: 0,
  id: 'pwr_power_path_in_cap_cap'
})
const pwr_power_path_out_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.419, 0.875), rotate: 0,
  id: 'pwr_power_path_out_cap_cap'
})
const pwr_rect = board.add(D_SOD_323, {
  translate: pt(2.313, 0.604), rotate: 0,
  id: 'pwr_rect'
})
const btn_drv_0__pre = board.add(SOT_23, {
  translate: pt(1.955, 0.382), rotate: 0,
  id: 'btn_drv_0__pre'
})
const btn_drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(2.128, 0.344), rotate: 0,
  id: 'btn_drv_0__pull'
})
const btn_drv_0__drv = board.add(TO_252_2, {
  translate: pt(2.131, 0.138), rotate: 0,
  id: 'btn_drv_0__drv'
})
const btn_drv_1__pre = board.add(SOT_23, {
  translate: pt(0.845, 0.949), rotate: 0,
  id: 'btn_drv_1__pre'
})
const btn_drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.018, 0.911), rotate: 0,
  id: 'btn_drv_1__pull'
})
const btn_drv_1__drv = board.add(TO_252_2, {
  translate: pt(1.021, 0.705), rotate: 0,
  id: 'btn_drv_1__drv'
})
const btn_drv_2__pre = board.add(SOT_23, {
  translate: pt(0.845, 0.382), rotate: 0,
  id: 'btn_drv_2__pre'
})
const btn_drv_2__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.018, 0.344), rotate: 0,
  id: 'btn_drv_2__pull'
})
const btn_drv_2__drv = board.add(TO_252_2, {
  translate: pt(1.021, 0.138), rotate: 0,
  id: 'btn_drv_2__drv'
})
const btn_drv_3__pre = board.add(SOT_23, {
  translate: pt(1.400, 0.382), rotate: 0,
  id: 'btn_drv_3__pre'
})
const btn_drv_3__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.573, 0.344), rotate: 0,
  id: 'btn_drv_3__pull'
})
const btn_drv_3__drv = board.add(TO_252_2, {
  translate: pt(1.576, 0.138), rotate: 0,
  id: 'btn_drv_3__drv'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.6842519685039368, 2.0192913385826774);
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


