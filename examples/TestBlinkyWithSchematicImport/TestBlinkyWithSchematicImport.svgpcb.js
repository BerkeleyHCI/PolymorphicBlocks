const board = new PCB();

const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.987, 1.907), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.835, 2.162), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(0.991, 2.162), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const reg_ic = board.add(SOT_23_6, {
  translate: pt(1.576, 1.809), rotate: 0,
  id: 'reg_ic'
})
const reg_fb_div_top_res = board.add(R_0603_1608Metric, {
  translate: pt(1.904, 1.944), rotate: 0,
  id: 'reg_fb_div_top_res'
})
const reg_fb_div_bottom_res = board.add(R_0603_1608Metric, {
  translate: pt(1.554, 2.061), rotate: 0,
  id: 'reg_fb_div_bottom_res'
})
const reg_hf_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.709, 2.061), rotate: 0,
  id: 'reg_hf_in_cap_cap'
})
const reg_vbst_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.865, 2.061), rotate: 0,
  id: 'reg_vbst_cap'
})
const reg_power_path_inductor = board.add(L_0805_2012Metric, {
  translate: pt(1.737, 1.949), rotate: 0,
  id: 'reg_power_path_inductor'
})
const reg_power_path_in_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.763, 1.781), rotate: 0,
  id: 'reg_power_path_in_cap_cap'
})
const reg_power_path_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.562, 1.954), rotate: 0,
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
const conn = board.add(PinHeader_1x04_P2_54mm_Vertical, {
  translate: pt(1.385, 2.112), rotate: 0,
  id: 'conn'
})
const sense_Q1 = board.add(SOT_23, {
  translate: pt(0.410, 1.809), rotate: 0,
  id: 'sense_Q1'
})
const sense_R3 = board.add(R_0603_1608Metric, {
  translate: pt(0.566, 1.944), rotate: 0,
  id: 'sense_R3'
})
const sense_R4 = board.add(R_0603_1608Metric, {
  translate: pt(0.393, 2.061), rotate: 0,
  id: 'sense_R4'
})
const sense_C2 = board.add(C_0805_2012Metric, {
  translate: pt(0.592, 1.781), rotate: 0,
  id: 'sense_C2'
})
const sense_C4 = board.add(C_0603_1608Metric, {
  translate: pt(0.549, 2.061), rotate: 0,
  id: 'sense_C4'
})
const sense_R1 = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 2.220), rotate: 0,
  id: 'sense_R1'
})
const sense_R2 = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 2.220), rotate: 0,
  id: 'sense_R2'
})
const sense_C3 = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 2.220), rotate: 0,
  id: 'sense_C3'
})
const sense_U1 = board.add(SOP_16_3_9x9_9mm_P1_27mm, {
  translate: pt(0.148, 1.947), rotate: 0,
  id: 'sense_U1'
})
const sense_C1 = board.add(C_0805_2012Metric, {
  translate: pt(0.402, 1.954), rotate: 0,
  id: 'sense_C1'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.5401574803149614, 2.366535433070866);
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


