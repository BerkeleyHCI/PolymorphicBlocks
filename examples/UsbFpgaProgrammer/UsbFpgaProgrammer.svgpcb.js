const board = new PCB();

const jlc_th_th1 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 1.224), rotate: 0,
  id: 'jlc_th_th1'
})
const jlc_th_th2 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.039, 1.224), rotate: 0,
  id: 'jlc_th_th2'
})
const jlc_th_th3 = board.add(JlcToolingHole_1_152mm, {
  translate: pt(0.000, 1.263), rotate: 0,
  id: 'jlc_th_th3'
})
const usb_conn = board.add(USB_C_Receptacle_XKB_U262_16XN_4BVC11, {
  translate: pt(1.224, 0.165), rotate: 0,
  id: 'usb_conn'
})
const usb_cc_pull_cc1_res = board.add(R_0603_1608Metric, {
  translate: pt(1.072, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc1_res'
})
const usb_cc_pull_cc2_res = board.add(R_0603_1608Metric, {
  translate: pt(1.228, 0.420), rotate: 0,
  id: 'usb_cc_pull_cc2_res'
})
const vusb_protect_diode = board.add(D_SOD_323, {
  translate: pt(1.225, 0.852), rotate: 0,
  id: 'vusb_protect_diode'
})
const ft232_ic = board.add(LQFP_48_7x7mm_P0_5mm, {
  translate: pt(0.203, 0.203), rotate: 0,
  id: 'ft232_ic'
})
const ft232_vbus_fb_fb = board.add(L_0603_1608Metric, {
  translate: pt(0.676, 0.202), rotate: 0,
  id: 'ft232_vbus_fb_fb'
})
const ft232_vregin_cap0_cap = board.add(C_0805_2012Metric, {
  translate: pt(0.512, 0.212), rotate: 0,
  id: 'ft232_vregin_cap0_cap'
})
const ft232_vregin_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.832, 0.202), rotate: 0,
  id: 'ft232_vregin_cap1_cap'
})
const ft232_vphy_fb_fb = board.add(L_0603_1608Metric, {
  translate: pt(0.503, 0.319), rotate: 0,
  id: 'ft232_vphy_fb_fb'
})
const ft232_vphy_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.659, 0.319), rotate: 0,
  id: 'ft232_vphy_cap_cap'
})
const ft232_vpll_fb_fb = board.add(L_0603_1608Metric, {
  translate: pt(0.815, 0.319), rotate: 0,
  id: 'ft232_vpll_fb_fb'
})
const ft232_vpll_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.474), rotate: 0,
  id: 'ft232_vpll_cap_cap'
})
const ft232_vcccore_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.214, 0.474), rotate: 0,
  id: 'ft232_vcccore_cap_cap'
})
const ft232_vcca_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.474), rotate: 0,
  id: 'ft232_vcca_cap_cap'
})
const ft232_vccd_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.474), rotate: 0,
  id: 'ft232_vccd_cap_cap'
})
const ft232_vccio_cap0_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.474), rotate: 0,
  id: 'ft232_vccio_cap0_cap'
})
const ft232_vccio_cap1_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.838, 0.474), rotate: 0,
  id: 'ft232_vccio_cap1_cap'
})
const ft232_vccio_cap2_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.058, 0.570), rotate: 0,
  id: 'ft232_vccio_cap2_cap'
})
const ft232_ref_res = board.add(R_0603_1608Metric, {
  translate: pt(0.214, 0.570), rotate: 0,
  id: 'ft232_ref_res'
})
const ft232_crystal_package = board.add(Crystal_SMD_3225_4Pin_3_2x2_5mm, {
  translate: pt(0.528, 0.067), rotate: 0,
  id: 'ft232_crystal_package'
})
const ft232_crystal_cap_a = board.add(C_0603_1608Metric, {
  translate: pt(0.370, 0.570), rotate: 0,
  id: 'ft232_crystal_cap_a'
})
const ft232_crystal_cap_b = board.add(C_0603_1608Metric, {
  translate: pt(0.526, 0.570), rotate: 0,
  id: 'ft232_crystal_cap_b'
})
const ft232_eeprom_ic = board.add(SOT_23_6, {
  translate: pt(0.730, 0.067), rotate: 0,
  id: 'ft232_eeprom_ic'
})
const ft232_eeprom_vcc_cap_cap = board.add(C_0603_1608Metric, {
  translate: pt(0.682, 0.570), rotate: 0,
  id: 'ft232_eeprom_vcc_cap_cap'
})
const ft232_eeprom_spi_do_pull_res = board.add(R_0603_1608Metric, {
  translate: pt(0.838, 0.570), rotate: 0,
  id: 'ft232_eeprom_spi_do_pull_res'
})
const ft232_eeprom_spi_do_res = board.add(R_0603_1608Metric, {
  translate: pt(0.058, 0.667), rotate: 0,
  id: 'ft232_eeprom_spi_do_res'
})
const usb_esd = board.add(SOT_23, {
  translate: pt(1.481, 0.881), rotate: 0,
  id: 'usb_esd'
})
const led0_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.985, 0.843), rotate: 0,
  id: 'led0_package'
})
const led0_res = board.add(R_0603_1608Metric, {
  translate: pt(0.985, 0.940), rotate: 0,
  id: 'led0_res'
})
const led1_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.515, 0.843), rotate: 0,
  id: 'led1_package'
})
const led1_res = board.add(R_0603_1608Metric, {
  translate: pt(0.515, 0.940), rotate: 0,
  id: 'led1_res'
})
const led2_package = board.add(LED_0603_1608Metric, {
  translate: pt(0.750, 0.843), rotate: 0,
  id: 'led2_package'
})
const led2_res = board.add(R_0603_1608Metric, {
  translate: pt(0.750, 0.940), rotate: 0,
  id: 'led2_res'
})
const out_conn = board.add(PinHeader_2x05_P1_27mm_Vertical_SMD, {
  translate: pt(0.169, 0.960), rotate: 0,
  id: 'out_conn'
})

const limit0 = pt(-0.07874015748031496, -0.07874015748031496);
const limit1 = pt(1.5962598425196852, 1.3811023622047247);
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


