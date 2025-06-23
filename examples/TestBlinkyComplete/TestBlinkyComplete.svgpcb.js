const board = new PCB();

const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.111, 0.165), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.960, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(1.116, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const reg_ic = board.add(SOT_23_6, {
  translate: pt(0.081, 0.804), rotate: 0,
  id: 'reg_ic'
})
const reg_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.939), rotate: 0,
  id: 'reg_fb_div_top_res'
})
const reg_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 0.939), rotate: 0,
  id: 'reg_fb_div_bottom_res'
})
const reg_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.939), rotate: 0,
  id: 'reg_hf_in_cap_cap'
})
const reg_vbst_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 1.036), rotate: 0,
  id: 'reg_vbst_cap'
})
const reg_power_path_inductor = board.add(L_0603_1608Metric, {
  translate: pt(0.214, 1.036), rotate: 0,
  id: 'reg_power_path_inductor'
})
const reg_power_path_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 1.036), rotate: 0,
  id: 'reg_power_path_in_cap_cap'
})
const reg_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.268, 0.776), rotate: 0,
  id: 'reg_power_path_out_cap_cap'
})
const mcu_swd_conn = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.614, 0.146), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'mcu_ic'
})
const mcu_pwr_cap_0__cap = board.add(C_0805_2012Metric, {
  translate: pt(0.067, 0.483), rotate: 0,
  id: 'mcu_pwr_cap_0__cap'
})
const mcu_pwr_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.231, 0.474), rotate: 0,
  id: 'mcu_pwr_cap_1__cap'
})
const mcu_pwr_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.387, 0.474), rotate: 0,
  id: 'mcu_pwr_cap_2__cap'
})
const mcu_pwr_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.543, 0.474), rotate: 0,
  id: 'mcu_pwr_cap_3__cap'
})
const mcu_vdda_cap_0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.699, 0.474), rotate: 0,
  id: 'mcu_vdda_cap_0_cap'
})
const mcu_vdda_cap_1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.590), rotate: 0,
  id: 'mcu_vdda_cap_1_cap'
})
const led_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.605, 0.766), rotate: 0,
  id: 'led_package'
})
const led_res = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 0.863), rotate: 0,
  id: 'led_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.4385826771653545, 1.1826771653543309);
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


