const board = new PCB();

const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(0.209, 1.055), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.310), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.310), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const usb_reg_ic = board.add(SOT_23_5, {
  translate: pt(1.541, 0.957), rotate: 0,
  id: 'usb_reg_ic'
})
const usb_reg_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.692, 1.093), rotate: 0,
  id: 'usb_reg_in_cap_cap'
})
const usb_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.528, 1.102), rotate: 0,
  id: 'usb_reg_out_cap_cap'
})
const mcu_swd_conn = board.add(Tag_Connect_TC2050_IDC_NL_2x05_P1_27mm_Vertical, {
  translate: pt(0.690, 0.133), rotate: 0,
  id: 'mcu_swd_conn'
})
const mcu_ic = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'mcu_ic'
})
const mcu_swd_pull_swdio_res = board.add(R_0603_1608Metric, {
  translate: pt(0.609, 0.474), rotate: 0,
  id: 'mcu_swd_pull_swdio_res'
})
const mcu_swd_pull_swclk_res = board.add(R_0603_1608Metric, {
  translate: pt(0.765, 0.474), rotate: 0,
  id: 'mcu_swd_pull_swclk_res'
})
const mcu_pwr_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.921, 0.474), rotate: 0,
  id: 'mcu_pwr_cap_0__cap'
})
const mcu_pwr_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.647), rotate: 0,
  id: 'mcu_pwr_cap_1__cap'
})
const mcu_pwr_cap_2__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.647), rotate: 0,
  id: 'mcu_pwr_cap_2__cap'
})
const mcu_pwr_cap_3__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.647), rotate: 0,
  id: 'mcu_pwr_cap_3__cap'
})
const mcu_pwr_cap_4__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.647), rotate: 0,
  id: 'mcu_pwr_cap_4__cap'
})
const mcu_pwr_cap_5__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.647), rotate: 0,
  id: 'mcu_pwr_cap_5__cap'
})
const mcu_vbat_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 0.647), rotate: 0,
  id: 'mcu_vbat_cap_cap'
})
const mcu_pwra_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.744), rotate: 0,
  id: 'mcu_pwra_cap_0__cap'
})
const mcu_pwra_cap_1__cap = board.add(C_0805_2012Metric, {
  translate: pt(0.272, 0.483), rotate: 0,
  id: 'mcu_pwra_cap_1__cap'
})
const mcu_vref_cap_0__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.744), rotate: 0,
  id: 'mcu_vref_cap_0__cap'
})
const mcu_vref_cap_1__cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.744), rotate: 0,
  id: 'mcu_vref_cap_1__cap'
})
const mcu_vref_cap_2__cap = board.add(C_0805_2012Metric, {
  translate: pt(0.445, 0.483), rotate: 0,
  id: 'mcu_vref_cap_2__cap'
})
const mcu_crystal_package = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.083, 0.512), rotate: 0,
  id: 'mcu_crystal_package'
})
const mcu_crystal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.744), rotate: 0,
  id: 'mcu_crystal_cap_a'
})
const mcu_crystal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.744), rotate: 0,
  id: 'mcu_crystal_cap_b'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(1.761, 1.524), rotate: 0,
  id: 'usb_esd'
})
const xcvr_ic = board.add(SOP_8_6_62x9_15mm_P2_54mm, {
  translate: pt(1.332, 0.190), rotate: 0,
  id: 'xcvr_ic'
})
const xcvr_logic_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.156, 0.448), rotate: 0,
  id: 'xcvr_logic_cap_cap'
})
const xcvr_can_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.312, 0.448), rotate: 0,
  id: 'xcvr_can_cap_cap'
})
const sw_usb_package = board.add(SW_SPST_EVQP7C, {
  translate: pt(1.224, 1.550), rotate: 0,
  id: 'sw_usb_package'
})
const sw_can_package = board.add(SW_SPST_EVQP7C, {
  translate: pt(0.889, 1.550), rotate: 0,
  id: 'sw_can_package'
})
const lcd_device_conn = board.add(Hirose_FH12_8S_0_5SH_1x08_1MP_P0_50mm_Horizontal, {
  translate: pt(0.736, 1.083), rotate: 0,
  id: 'lcd_device_conn'
})
const lcd_led_res = board.add(R_0603_1608Metric, {
  translate: pt(0.595, 1.270), rotate: 0,
  id: 'lcd_led_res'
})
const lcd_vdd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.751, 1.270), rotate: 0,
  id: 'lcd_vdd_cap_cap'
})
const rgb_usb_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.041, 1.512), rotate: 0,
  id: 'rgb_usb_package'
})
const rgb_usb_red_res = board.add(R_0603_1608Metric, {
  translate: pt(0.180, 1.486), rotate: 0,
  id: 'rgb_usb_red_res'
})
const rgb_usb_green_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 1.635), rotate: 0,
  id: 'rgb_usb_green_res'
})
const rgb_usb_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 1.635), rotate: 0,
  id: 'rgb_usb_blue_res'
})
const rgb_can_package = board.add(LED_LiteOn_LTST_C19HE1WT, {
  translate: pt(0.432, 1.512), rotate: 0,
  id: 'rgb_can_package'
})
const rgb_can_red_res = board.add(R_0603_1608Metric, {
  translate: pt(0.571, 1.486), rotate: 0,
  id: 'rgb_can_red_res'
})
const rgb_can_green_res = board.add(R_0603_1608Metric, {
  translate: pt(0.449, 1.635), rotate: 0,
  id: 'rgb_can_green_res'
})
const rgb_can_blue_res = board.add(R_0603_1608Metric, {
  translate: pt(0.605, 1.635), rotate: 0,
  id: 'rgb_can_blue_res'
})
const can = board.add(Molex_DuraClik_502352_1x05_P2_00mm_Horizontal, {
  translate: pt(2.066, 1.457), rotate: 0,
  id: 'can'
})
const can_reg_ic = board.add(SOT_23_5, {
  translate: pt(1.133, 0.957), rotate: 0,
  id: 'can_reg_ic'
})
const can_reg_in_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(1.284, 1.093), rotate: 0,
  id: 'can_reg_in_cap_cap'
})
const can_reg_out_cap_cap = board.add(C_0805_2012Metric, {
  translate: pt(1.120, 1.102), rotate: 0,
  id: 'can_reg_out_cap_cap'
})
const led_can_package = board.add(LED_0603_1608Metric, {
  translate: pt(1.509, 1.486), rotate: 0,
  id: 'led_can_package'
})
const led_can_res = board.add(R_0603_1608Metric, {
  translate: pt(1.509, 1.583), rotate: 0,
  id: 'led_can_res'
})
const can_esd = board.add(SOT_23, {
  translate: pt(1.951, 1.524), rotate: 0,
  id: 'can_esd'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(2.1057086614173235, 1.7822834645669294);
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


