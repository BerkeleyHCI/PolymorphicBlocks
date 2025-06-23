const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.861, 1.261), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.901, 1.261), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.861, 1.300), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 0.956), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0402_1005Metric, {
  translate: pt(0.495, 0.810), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0402_1005Metric, {
  translate: pt(0.495, 0.886), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const vusb_protect_diode = board.add(D_SOD_323, {
  translate: pt(0.490, 1.298), rotate: 0,
  id: 'vusb_protect_diode'
})
const usb_reg_ic = board.add(SOT_23_5, {
  translate: pt(1.093, 0.858), rotate: 0,
  id: 'usb_reg_ic'
})
const usb_reg_in_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(1.222, 0.983), rotate: 0,
  id: 'usb_reg_in_cap_cap'
})
const usb_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.080, 1.003), rotate: 0,
  id: 'usb_reg_out_cap_cap'
})
const target_reg_ic = board.add(SOT_23_5, {
  translate: pt(0.730, 0.858), rotate: 0,
  id: 'target_reg_ic'
})
const target_reg_in_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.859, 0.983), rotate: 0,
  id: 'target_reg_in_cap_cap'
})
const target_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.717, 1.003), rotate: 0,
  id: 'target_reg_out_cap_cap'
})
const mcu_swd_conn = board.add(Tag_Connect_TC2030_IDC_NL_2x03_P1_27mm_Vertical, {
  translate: pt(0.138, 0.443), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(QFN_56_1EP_7x7mm_P0_4mm_EP3_2x3_2mm, {
  translate: pt(0.163, 0.163), rotate: 0,
  id: 'mcu_ic'
})
const mcu_iovdd_cap_0__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.036, 0.580), rotate: 0,
  id: 'mcu_iovdd_cap_0__cap'
})
const mcu_iovdd_cap_1__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.147, 0.580), rotate: 0,
  id: 'mcu_iovdd_cap_1__cap'
})
const mcu_iovdd_cap_2__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.258, 0.580), rotate: 0,
  id: 'mcu_iovdd_cap_2__cap'
})
const mcu_iovdd_cap_3__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.369, 0.580), rotate: 0,
  id: 'mcu_iovdd_cap_3__cap'
})
const mcu_iovdd_cap_4__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.480, 0.580), rotate: 0,
  id: 'mcu_iovdd_cap_4__cap'
})
const mcu_iovdd_cap_5__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.591, 0.580), rotate: 0,
  id: 'mcu_iovdd_cap_5__cap'
})
const mcu_avdd_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.702, 0.580), rotate: 0,
  id: 'mcu_avdd_cap_cap'
})
const mcu_vreg_in_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.813, 0.580), rotate: 0,
  id: 'mcu_vreg_in_cap_cap'
})
const mcu_mem_ic = board.add(SOIC_8_5_23x5_23mm_P1_27mm, {
  translate: pt(0.548, 0.113), rotate: 0,
  id: 'mcu_mem_ic'
})
const mcu_mem_vcc_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.036, 0.655), rotate: 0,
  id: 'mcu_mem_vcc_cap_cap'
})
const mcu_dvdd_cap_0__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.147, 0.655), rotate: 0,
  id: 'mcu_dvdd_cap_0__cap'
})
const mcu_dvdd_cap_1__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.258, 0.655), rotate: 0,
  id: 'mcu_dvdd_cap_1__cap'
})
const mcu_vreg_out_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.369, 0.655), rotate: 0,
  id: 'mcu_vreg_out_cap_cap'
})
const mcu_usb_res_dp_res = board.add(R_0603_1608Metric, {
  translate: pt(0.562, 0.393), rotate: 0,
  id: 'mcu_usb_res_dp_res'
})
const mcu_usb_res_dm_res = board.add(R_0603_1608Metric, {
  translate: pt(0.718, 0.393), rotate: 0,
  id: 'mcu_usb_res_dm_res'
})
const mcu_crystal = board.add(Resonator_SMD_Murata_CSTxExxV_3Pin_3_0x1_1mm, {
  translate: pt(0.394, 0.428), rotate: 0,
  id: 'mcu_crystal'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(0.746, 1.328), rotate: 0,
  id: 'usb_esd'
})
const led_tgt_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.058, 1.290), rotate: 0,
  id: 'led_tgt_package'
})
const led_tgt_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.377), rotate: 0,
  id: 'led_tgt_res'
})
const led_usb_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.434, 0.820), rotate: 0,
  id: 'led_usb_package'
})
const led_usb_res = board.add(R_0402_1005Metric, {
  translate: pt(1.412, 0.907), rotate: 0,
  id: 'led_usb_res'
})
const en_pull_res = board.add(R_0402_1005Metric, {
  translate: pt(1.055, 1.280), rotate: 0,
  id: 'en_pull_res'
})
const target_conn = board.add(PinHeader_2x03_P2_54mm_EdgeInline, {
  translate: pt(1.126, 0.321), rotate: 0,
  id: 'target_conn'
})
const led_target_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.669, 0.820), rotate: 0,
  id: 'led_target_package'
})
const led_target_res = board.add(R_0402_1005Metric, {
  translate: pt(1.647, 0.907), rotate: 0,
  id: 'led_target_res'
})
const target_sense_div_top_res = board.add(R_0402_1005Metric, {
  translate: pt(0.271, 1.280), rotate: 0,
  id: 'target_sense_div_top_res'
})
const target_sense_div_bottom_res = board.add(R_0402_1005Metric, {
  translate: pt(0.271, 1.356), rotate: 0,
  id: 'target_sense_div_bottom_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.8452755905511813, 1.5133858267716536);
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


