const board = new PCB();

const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.907), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.162), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.162), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const reg_ic = board.add(SOT_23_6, {
  translate: pt(0.618, 1.809), rotate: 0,
  id: 'reg_ic'
})
const reg_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(0.946, 1.944), rotate: 0,
  id: 'reg_fb_div_top_res'
})
const reg_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(0.595, 2.061), rotate: 0,
  id: 'reg_fb_div_bottom_res'
})
const reg_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.751, 2.061), rotate: 0,
  id: 'reg_hf_in_cap_cap'
})
const reg_vbst_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.907, 2.061), rotate: 0,
  id: 'reg_vbst_cap'
})
const reg_power_path_inductor = board.add(L_0805_2012Metric, {
  translate: pt(0.779, 1.949), rotate: 0,
  id: 'reg_power_path_inductor'
})
const reg_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.805, 1.781), rotate: 0,
  id: 'reg_power_path_in_cap_cap'
})
const reg_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.604, 1.954), rotate: 0,
  id: 'reg_power_path_out_cap_cap'
})
const mcu_ic = board.add(ESP32_WROOM_32, {
  translate: pt(0.945, 0.414), rotate: 0,
  id: 'mcu_ic'
})
const mcu_vcc_cap0_cap = board.add(C_1206_3216Metric, {
  translate: pt(2.020, 0.789), rotate: 0,
  id: 'mcu_vcc_cap0_cap'
})
const mcu_vcc_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(2.208, 0.773), rotate: 0,
  id: 'mcu_vcc_cap1_cap'
})
const mcu_prog_conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(2.000, 0.370), rotate: 0,
  id: 'mcu_prog_conn'
})
const mcu_boot_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(2.096, 0.593), rotate: 0,
  id: 'mcu_boot_package'
})
const mcu_en_pull_rc_r = board.add(R_0603_1608Metric, {
  translate: pt(2.364, 0.773), rotate: 0,
  id: 'mcu_en_pull_rc_r'
})
const mcu_en_pull_rc_c = board.add(C_0603_1608Metric, {
  translate: pt(1.987, 0.903), rotate: 0,
  id: 'mcu_en_pull_rc_c'
})
const sw_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.289, 1.854), rotate: 0,
  id: 'sw_package'
})
const led_led_0__package = board.add(LED_0603_1608Metric, {
  translate: pt(1.633, 1.771), rotate: 0,
  id: 'led_led_0__package'
})
const led_led_1__package = board.add(LED_0603_1608Metric, {
  translate: pt(1.789, 1.771), rotate: 0,
  id: 'led_led_1__package'
})
const led_led_2__package = board.add(LED_0603_1608Metric, {
  translate: pt(1.633, 1.868), rotate: 0,
  id: 'led_led_2__package'
})
const led_led_3__package = board.add(LED_0603_1608Metric, {
  translate: pt(1.789, 1.868), rotate: 0,
  id: 'led_led_3__package'
})
const res_pack = board.add(R_Array_Concave_4x0603, {
  translate: pt(2.027, 1.816), rotate: 0,
  id: 'res_pack'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.5401574803149614, 2.308661417322835);
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


