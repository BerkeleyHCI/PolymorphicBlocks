const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.635, 1.158), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.674, 1.158), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(1.635, 1.198), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.111, 0.165), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0402_1005Metric, {
  translate: pt(1.396, 0.019), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0402_1005Metric, {
  translate: pt(1.396, 0.095), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const vusb_protect_diode = board.add(D_SOD_323, {
  translate: pt(1.263, 1.196), rotate: 0,
  id: 'vusb_protect_diode'
})
const usb_reg_ic = board.add(SOT_23_5, {
  translate: pt(0.900, 0.816), rotate: 0,
  id: 'usb_reg_ic'
})
const usb_reg_in_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(1.029, 0.940), rotate: 0,
  id: 'usb_reg_in_cap_cap'
})
const usb_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.887, 0.961), rotate: 0,
  id: 'usb_reg_out_cap_cap'
})
const target_reg_ic = board.add(SOT_23_5, {
  translate: pt(0.537, 0.816), rotate: 0,
  id: 'target_reg_ic'
})
const target_reg_in_cap_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.666, 0.940), rotate: 0,
  id: 'target_reg_in_cap_cap'
})
const target_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.524, 0.961), rotate: 0,
  id: 'target_reg_out_cap_cap'
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
  translate: pt(0.256, 0.483), rotate: 0,
  id: 'mcu_pwr_cap_0__cap'
})
const mcu_pwr_cap_1__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.511, 0.463), rotate: 0,
  id: 'mcu_pwr_cap_1__cap'
})
const mcu_pwr_cap_2__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.622, 0.463), rotate: 0,
  id: 'mcu_pwr_cap_2__cap'
})
const mcu_pwr_cap_3__cap = board.add(C_0402_1005Metric, {
  translate: pt(0.733, 0.463), rotate: 0,
  id: 'mcu_pwr_cap_3__cap'
})
const mcu_vdda_cap_0_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.036, 0.613), rotate: 0,
  id: 'mcu_vdda_cap_0_cap'
})
const mcu_vdda_cap_1_cap = board.add(C_0402_1005Metric, {
  translate: pt(0.147, 0.613), rotate: 0,
  id: 'mcu_vdda_cap_1_cap'
})
const mcu_usb_pull_dp = board.add(R_0402_1005Metric, {
  translate: pt(0.399, 0.463), rotate: 0,
  id: 'mcu_usb_pull_dp'
})
const mcu_crystal = board.add(Resonator_SMD_Murata_CSTxExxV_3Pin_3_0x1_1mm, {
  translate: pt(0.079, 0.508), rotate: 0,
  id: 'mcu_crystal'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(1.520, 1.225), rotate: 0,
  id: 'usb_esd'
})
const led_tgt_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.832, 1.187), rotate: 0,
  id: 'led_tgt_package'
})
const led_tgt_res = board.add(R_0402_1005Metric, {
  translate: pt(0.810, 1.274), rotate: 0,
  id: 'led_tgt_res'
})
const led_usb_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.362, 1.187), rotate: 0,
  id: 'led_usb_package'
})
const led_usb_res = board.add(R_0402_1005Metric, {
  translate: pt(0.341, 1.274), rotate: 0,
  id: 'led_usb_res'
})
const en_pull_res = board.add(R_0402_1005Metric, {
  translate: pt(0.228, 1.485), rotate: 0,
  id: 'en_pull_res'
})
const target_drv_swclk_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.177), rotate: 0,
  id: 'target_drv_swclk_res'
})
const target_drv_swdio_res = board.add(R_0402_1005Metric, {
  translate: pt(0.149, 1.177), rotate: 0,
  id: 'target_drv_swdio_res'
})
const target_drv_swdio_drv_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.253), rotate: 0,
  id: 'target_drv_swdio_drv_res'
})
const target_drv_reset_res = board.add(R_0402_1005Metric, {
  translate: pt(0.149, 1.253), rotate: 0,
  id: 'target_drv_reset_res'
})
const target_drv_swo_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.330), rotate: 0,
  id: 'target_drv_swo_res'
})
const reset_pull_res = board.add(R_0402_1005Metric, {
  translate: pt(0.037, 1.485), rotate: 0,
  id: 'reset_pull_res'
})
const reset_sw_package = board.add(SW_SPST_SKQG_WithoutStem, {
  translate: pt(1.350, 0.861), rotate: 0,
  id: 'reset_sw_package'
})
const target_conn = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.169, 0.894), rotate: 0,
  id: 'target_conn'
})
const led_target_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.597, 1.187), rotate: 0,
  id: 'led_target_package'
})
const led_target_res = board.add(R_0402_1005Metric, {
  translate: pt(0.575, 1.274), rotate: 0,
  id: 'led_target_res'
})
const target_sense_div_top_res = board.add(R_0402_1005Metric, {
  translate: pt(1.045, 1.177), rotate: 0,
  id: 'target_sense_div_top_res'
})
const target_sense_div_bottom_res = board.add(R_0402_1005Metric, {
  translate: pt(1.045, 1.253), rotate: 0,
  id: 'target_sense_div_bottom_res'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.792322834645669, 1.6212598425196851);
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


