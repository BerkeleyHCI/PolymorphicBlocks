const board = new PCB();

const pwr_conn = board.add(Molex_DuraClik_vert_3pin, {
  translate: pt(2.459, 1.764), rotate: 0,
  id: 'pwr_conn'
})
const pwr_ic = board.add(SOT_23_6, {
  translate: pt(0.956, 1.831), rotate: 0,
  id: 'pwr_ic'
})
const pwr_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.111, 1.966), rotate: 0,
  id: 'pwr_fb_div_top_res'
})
const pwr_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.267, 1.966), rotate: 0,
  id: 'pwr_fb_div_bottom_res'
})
const pwr_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.934, 2.072), rotate: 0,
  id: 'pwr_hf_in_cap_cap'
})
const pwr_vbst_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.090, 2.072), rotate: 0,
  id: 'pwr_vbst_cap'
})
const pwr_power_path_inductor = board.add(L_0805_2012Metric, {
  translate: pt(0.944, 1.970), rotate: 0,
  id: 'pwr_power_path_inductor'
})
const pwr_power_path_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.246, 2.072), rotate: 0,
  id: 'pwr_power_path_in_cap_cap'
})
const pwr_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.143, 1.802), rotate: 0,
  id: 'pwr_power_path_out_cap_cap'
})
const mcu_swd_conn = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(2.106, 1.028), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(1.694, 1.085), rotate: 0,
  id: 'mcu_ic'
})
const mcu_swd_pull_swdio_res = board.add(R_0603_1608Metric, {
  translate: pt(1.723, 1.356), rotate: 0,
  id: 'mcu_swd_pull_swdio_res'
})
const mcu_swd_pull_swclk_res = board.add(R_0603_1608Metric, {
  translate: pt(1.879, 1.356), rotate: 0,
  id: 'mcu_swd_pull_swclk_res'
})
const mcu_pwr_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.035, 1.356), rotate: 0,
  id: 'mcu_pwr_cap_0__cap'
})
const mcu_pwr_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.191, 1.356), rotate: 0,
  id: 'mcu_pwr_cap_1__cap'
})
const mcu_pwr_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.346, 1.356), rotate: 0,
  id: 'mcu_pwr_cap_2__cap'
})
const mcu_pwr_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.550, 1.472), rotate: 0,
  id: 'mcu_pwr_cap_3__cap'
})
const mcu_pwr_cap_4__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.706, 1.472), rotate: 0,
  id: 'mcu_pwr_cap_4__cap'
})
const mcu_pwr_cap_5__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.861, 1.472), rotate: 0,
  id: 'mcu_pwr_cap_5__cap'
})
const mcu_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.017, 1.472), rotate: 0,
  id: 'mcu_vbat_cap_cap'
})
const mcu_pwra_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.173, 1.472), rotate: 0,
  id: 'mcu_pwra_cap_0__cap'
})
const mcu_pwra_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(2.381, 1.094), rotate: 0,
  id: 'mcu_pwra_cap_1__cap'
})
const mcu_vref_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(2.329, 1.472), rotate: 0,
  id: 'mcu_vref_cap_0__cap'
})
const mcu_vref_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(1.550, 1.569), rotate: 0,
  id: 'mcu_vref_cap_1__cap'
})
const mcu_vref_cap_2__cap = board.add(C_0805_2012Metric, {
  translate: pt(1.558, 1.365), rotate: 0,
  id: 'mcu_vref_cap_2__cap'
})
const mcu_crystal_package = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(2.397, 0.949), rotate: 0,
  id: 'mcu_crystal_package'
})
const mcu_crystal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(1.706, 1.569), rotate: 0,
  id: 'mcu_crystal_cap_a'
})
const mcu_crystal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(1.861, 1.569), rotate: 0,
  id: 'mcu_crystal_cap_b'
})
const can_conn = board.add(Molex_DuraClik_vert_5pin, {
  translate: pt(0.000, 2.299), rotate: 0,
  id: 'can_conn'
})
const can_can_fuse_fuse = board.add(R_0603_1608Metric, {
  translate: pt(0.231, 2.211), rotate: 0,
  id: 'can_can_fuse_fuse'
})
const can_reg_ic = board.add(SOT_23_5, {
  translate: pt(0.589, 1.831), rotate: 0,
  id: 'can_reg_ic'
})
const can_reg_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.387, 2.211), rotate: 0,
  id: 'can_reg_in_cap_cap'
})
const can_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 2.221), rotate: 0,
  id: 'can_reg_out_cap_cap'
})
const can_esd = board.add(SOT_23, {
  translate: pt(0.583, 2.004), rotate: 0,
  id: 'can_esd'
})
const can_transceiver_ic = board.add(SOP_8_6_62x9_15mm_P2_54mm, {
  translate: pt(0.234, 1.954), rotate: 0,
  id: 'can_transceiver_ic'
})
const can_transceiver_logic_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.543, 2.211), rotate: 0,
  id: 'can_transceiver_logic_cap_cap'
})
const can_transceiver_can_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.699, 2.211), rotate: 0,
  id: 'can_transceiver_can_cap_cap'
})
const vsense_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(2.283, 1.793), rotate: 0,
  id: 'vsense_div_top_res'
})
const vsense_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(2.283, 1.889), rotate: 0,
  id: 'vsense_div_bottom_res'
})
const rgb1_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.485, 1.819), rotate: 0,
  id: 'rgb1_package'
})
const rgb1_red_res = board.add(R_0603_1608Metric, {
  translate: pt(1.624, 1.793), rotate: 0,
  id: 'rgb1_red_res'
})
const rgb1_green_res = board.add(R_0603_1608Metric, {
  translate: pt(1.502, 1.942), rotate: 0,
  id: 'rgb1_green_res'
})
const rgb1_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(1.657, 1.942), rotate: 0,
  id: 'rgb1_blue_res'
})
const rgb2_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(1.875, 1.819), rotate: 0,
  id: 'rgb2_package'
})
const rgb2_red_res = board.add(R_0603_1608Metric, {
  translate: pt(2.014, 1.793), rotate: 0,
  id: 'rgb2_red_res'
})
const rgb2_green_res = board.add(R_0603_1608Metric, {
  translate: pt(1.892, 1.942), rotate: 0,
  id: 'rgb2_green_res'
})
const rgb2_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(2.048, 1.942), rotate: 0,
  id: 'rgb2_blue_res'
})
const light_0__conn = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(0.502, 1.512), rotate: 0,
  id: 'light_0__conn'
})
const light_0__drv_0__pre = board.add(SOT_23, {
  translate: pt(0.552, 1.264), rotate: 0,
  id: 'light_0__drv_0__pre'
})
const light_0__drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(0.249, 1.541), rotate: 0,
  id: 'light_0__drv_0__pull'
})
const light_0__drv_0__drv = board.add(TO_252_2, {
  translate: pt(0.252, 1.020), rotate: 0,
  id: 'light_0__drv_0__drv'
})
const light_0__drv_1__pre = board.add(SOT_23, {
  translate: pt(0.076, 1.579), rotate: 0,
  id: 'light_0__drv_1__pre'
})
const light_0__drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(0.405, 1.541), rotate: 0,
  id: 'light_0__drv_1__pull'
})
const light_0__drv_1__drv = board.add(TO_252_2, {
  translate: pt(0.252, 1.335), rotate: 0,
  id: 'light_0__drv_1__drv'
})
const light_1__conn = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(1.248, 1.512), rotate: 0,
  id: 'light_1__conn'
})
const light_1__drv_0__pre = board.add(SOT_23, {
  translate: pt(1.298, 1.264), rotate: 0,
  id: 'light_1__drv_0__pre'
})
const light_1__drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 1.541), rotate: 0,
  id: 'light_1__drv_0__pull'
})
const light_1__drv_0__drv = board.add(TO_252_2, {
  translate: pt(0.997, 1.020), rotate: 0,
  id: 'light_1__drv_0__drv'
})
const light_1__drv_1__pre = board.add(SOT_23, {
  translate: pt(0.821, 1.579), rotate: 0,
  id: 'light_1__drv_1__pre'
})
const light_1__drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 1.541), rotate: 0,
  id: 'light_1__drv_1__pull'
})
const light_1__drv_1__drv = board.add(TO_252_2, {
  translate: pt(0.997, 1.335), rotate: 0,
  id: 'light_1__drv_1__drv'
})
const light_2__conn = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(1.248, 0.630), rotate: 0,
  id: 'light_2__conn'
})
const light_2__drv_0__pre = board.add(SOT_23, {
  translate: pt(1.298, 0.382), rotate: 0,
  id: 'light_2__drv_0__pre'
})
const light_2__drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(0.994, 0.659), rotate: 0,
  id: 'light_2__drv_0__pull'
})
const light_2__drv_0__drv = board.add(TO_252_2, {
  translate: pt(0.997, 0.138), rotate: 0,
  id: 'light_2__drv_0__drv'
})
const light_2__drv_1__pre = board.add(SOT_23, {
  translate: pt(0.821, 0.697), rotate: 0,
  id: 'light_2__drv_1__pre'
})
const light_2__drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.150, 0.659), rotate: 0,
  id: 'light_2__drv_1__pull'
})
const light_2__drv_1__drv = board.add(TO_252_2, {
  translate: pt(0.997, 0.453), rotate: 0,
  id: 'light_2__drv_1__drv'
})
const light_3__conn = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(0.502, 0.630), rotate: 0,
  id: 'light_3__conn'
})
const light_3__drv_0__pre = board.add(SOT_23, {
  translate: pt(0.552, 0.382), rotate: 0,
  id: 'light_3__drv_0__pre'
})
const light_3__drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(0.249, 0.659), rotate: 0,
  id: 'light_3__drv_0__pull'
})
const light_3__drv_0__drv = board.add(TO_252_2, {
  translate: pt(0.252, 0.138), rotate: 0,
  id: 'light_3__drv_0__drv'
})
const light_3__drv_1__pre = board.add(SOT_23, {
  translate: pt(0.076, 0.697), rotate: 0,
  id: 'light_3__drv_1__pre'
})
const light_3__drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(0.405, 0.659), rotate: 0,
  id: 'light_3__drv_1__pull'
})
const light_3__drv_1__drv = board.add(TO_252_2, {
  translate: pt(0.252, 0.453), rotate: 0,
  id: 'light_3__drv_1__drv'
})
const light_4__conn = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(2.739, 0.630), rotate: 0,
  id: 'light_4__conn'
})
const light_4__drv_0__pre = board.add(SOT_23, {
  translate: pt(2.789, 0.382), rotate: 0,
  id: 'light_4__drv_0__pre'
})
const light_4__drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(2.486, 0.659), rotate: 0,
  id: 'light_4__drv_0__pull'
})
const light_4__drv_0__drv = board.add(TO_252_2, {
  translate: pt(2.489, 0.138), rotate: 0,
  id: 'light_4__drv_0__drv'
})
const light_4__drv_1__pre = board.add(SOT_23, {
  translate: pt(2.313, 0.697), rotate: 0,
  id: 'light_4__drv_1__pre'
})
const light_4__drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(2.642, 0.659), rotate: 0,
  id: 'light_4__drv_1__pull'
})
const light_4__drv_1__drv = board.add(TO_252_2, {
  translate: pt(2.489, 0.453), rotate: 0,
  id: 'light_4__drv_1__drv'
})
const light_5__conn = board.add(Molex_DuraClik_vert_4pin, {
  translate: pt(1.994, 0.630), rotate: 0,
  id: 'light_5__conn'
})
const light_5__drv_0__pre = board.add(SOT_23, {
  translate: pt(2.043, 0.382), rotate: 0,
  id: 'light_5__drv_0__pre'
})
const light_5__drv_0__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.740, 0.659), rotate: 0,
  id: 'light_5__drv_0__pull'
})
const light_5__drv_0__drv = board.add(TO_252_2, {
  translate: pt(1.743, 0.138), rotate: 0,
  id: 'light_5__drv_0__drv'
})
const light_5__drv_1__pre = board.add(SOT_23, {
  translate: pt(1.567, 0.697), rotate: 0,
  id: 'light_5__drv_1__pre'
})
const light_5__drv_1__pull = board.add(R_0603_1608Metric, {
  translate: pt(1.896, 0.659), rotate: 0,
  id: 'light_5__drv_1__pull'
})
const light_5__drv_1__drv = board.add(TO_252_2, {
  translate: pt(1.743, 0.453), rotate: 0,
  id: 'light_5__drv_1__drv'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.9826771653543305, 2.4173228346456694);
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


